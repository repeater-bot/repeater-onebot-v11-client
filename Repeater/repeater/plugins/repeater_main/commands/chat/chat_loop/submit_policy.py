"""聊天循环里「这一批消息要不要现在就提交给 LLM」的判定。

本模块只回答两件事：此刻这一批该不该交出去；不该交的时候，隔多久再看一次。
收消息、关停、消息格式化都在调用方。

调用方每次判定把这几样交进来：最近消息的记录序列（环形缓冲、时间有序）、
当前积压条数、当前单调时钟秒、距上次提交过了多少秒。

模块不引用插件的任何包，只依赖标准库，因此可以单独加载跑数值。它按属性读取
传入的 pydantic 配置对象，用到的字段：

    feature_window_seconds          特征窗口时长（秒）
    pending_feature_cap             积压条数入特征时的上限
    score_bias                      线性打分的截距
    score_weight_mention            窗口内有人点名
    score_weight_at_other           最新一条 @ 了别人（负向）
    score_weight_question           最新一条是问句
    score_weight_media_only         最新一条只有媒体没有文字（负向）
    score_weight_self_ratio         窗口内自己发言占比
    score_weight_message_count      窗口内消息条数
    score_weight_seconds_since_bot  距上次发言的秒数（已取 log1p）
    score_weight_pending            当前积压条数
    keyword_bias_scale              关键词总权重折算成 logit 的系数
    sample_window_seconds           取样窗口时长（秒）
    sample_min_count                样本达到多少条才改用窗口内的经验分布
    overrun_tighten_factor          已提交次数多于目标时的收紧因子
    threshold_curve                 允许份额 → 阈值的静态曲线
    direct_call_cost                一次点名直接调用折算成的预计提交量
    retry_delay_base_seconds        重试间隔起点（秒）
    retry_delay_growth              重试间隔倍数
    retry_delay_cap_seconds         重试间隔上限（秒）
    retry_delay_after_skips         连续多少轮没提交才开始拉长间隔
    retry_delay_bypass_pending      积压达到多少条就取消拉长
"""

import math
import random
from collections import deque
from dataclasses import dataclass
from typing import Any, Callable, Sequence

# 数值稳定性用的封顶，不是可调参数：只是别让 exp 在大分数上溢出
_SIGMOID_LIMIT = 60.0

# 把概率夹进开区间再取 logit，避免 log(0)。不是可调参数
_LOGIT_EPSILON = 1e-6

@dataclass(frozen = True, slots = True)
class MessageRecord:
    """一条消息到达时刻的记录，只留判定用得到的字段。"""

    at: float
    is_self: bool
    is_tome: bool
    question: bool
    at_other: bool
    has_text: bool
    keyword_gain: float = 0.0
    """这条消息命中的关键词权重之和；窗口内的汇总在 extract_features 里做。"""

@dataclass(frozen = True, slots = True)
class SampleFeatures:
    """一次判定的特征向量，与线性打分里的每一项一一对应。"""

    mention_bot: float
    at_other: float
    question: float
    media_only: float
    self_ratio: float
    message_count: float
    log_seconds_since_bot: float
    pending_count: float
    keyword_gain: float

@dataclass(frozen = True, slots = True)
class SubmitDecision:
    """一次判定给出的结论，调用方直接拿去打日志或决定交不交。"""

    should_submit: bool
    probability: float
    threshold: float
    allowance_share: float
    expected_replies: float
    target_replies: float
    submission_count: int
    direct_cost: float
    sample_count: int

    def __str__(self) -> str:
        return (
            f"submit={self.should_submit}, p={self.probability:.3f}, "
            f"threshold={self.threshold:.3f}, share={self.allowance_share:.3f}, "
            f"expected={self.expected_replies:.2f}, target={self.target_replies:.2f}, "
            f"submitted={self.submission_count}, direct={self.direct_cost:.2f}, "
            f"samples={self.sample_count}"
        )

def clamp_unit(value: float) -> float:
    """把值夹到 [0, 1]。"""

    return max(0.0, min(1.0, float(value)))

def _sigmoid(score: float) -> float:
    """数值稳定的 sigmoid。

    正负两边分开算，负半轴用 e^s / (1 + e^s) 避免 e^-s 溢出。两侧都要保证严格落在
    开区间内：负半轴天然不会到 0；正半轴在 score 够大时 `1 + e^-score` 会在 float64
    里舍入成正好 1.0，于是概率精确等于 1.0，与「阈值取 1.0」比较时会翻成误拦，所以
    用 nextafter 夹到 1.0 之前，保持和负半轴对称。
    """

    if score >= 0.0:
        return min(
            math.nextafter(1.0, 0.0),
            1.0 / (1.0 + math.exp(-min(score, _SIGMOID_LIMIT)))
        )
    decayed = math.exp(max(score, -_SIGMOID_LIMIT))
    return decayed / (1.0 + decayed)

def extract_features(
    recent: Sequence[MessageRecord],
    pending: int,
    now: float,
    seconds_since_bot: float,
    configs: Any
) -> SampleFeatures:
    """把窗口内的消息、积压和时钟压成一个特征向量。

    只算最近 `feature_window_seconds` 秒内的消息。「最新一条」跳过自己发的，
    否则刚提交过一轮时特征会去读自己的发言，把「有人在等我说话」读成「我在说话」。
    点名取的是「窗口内有没有人叫过我」：叫过一次之后，接下来的几批仍然值得主动
    接话，而不只是被叫醒的那一批。
    """

    window_start = float(now) - float(configs.feature_window_seconds)
    message_count = 0
    self_count = 0
    mention_bot = 0.0
    keyword_gain = 0.0
    latest_other: MessageRecord | None = None
    for record in recent:
        if record.at < window_start:
            continue
        message_count += 1
        if record.is_self:
            self_count += 1
            continue
        if record.is_tome:
            mention_bot = 1.0
        keyword_gain += record.keyword_gain
        latest_other = record

    if latest_other is None:
        at_other = 0.0
        question = 0.0
        media_only = 0.0
    else:
        at_other = 1.0 if latest_other.at_other else 0.0
        question = 1.0 if latest_other.question else 0.0
        media_only = 0.0 if latest_other.has_text else 1.0

    if message_count > 0:
        self_ratio = float(self_count) / float(message_count)
    else:
        self_ratio = 0.0

    pending_cap = max(1, int(configs.pending_feature_cap))
    pending_count = float(min(max(0, int(pending)), pending_cap))
    log_seconds = math.log1p(max(0.0, float(seconds_since_bot)))

    return SampleFeatures(
        mention_bot = mention_bot,
        at_other = at_other,
        question = question,
        media_only = media_only,
        self_ratio = self_ratio,
        message_count = float(message_count),
        log_seconds_since_bot = log_seconds,
        pending_count = pending_count,
        keyword_gain = max(-1.0, min(1.0, keyword_gain)),
    )

def compute_probability(features: SampleFeatures, configs: Any) -> float:
    """线性打分再过 sigmoid，得到「这一批值得提交」的概率。

    权重是配置里的初始值，待用真实聊天记录重新拟合。秒数先取 log1p 再入线性式：
    刚说过话和半天没说话在线性式里差几个数量级，不取对数会把别的项完全盖住。
    """

    score = float(configs.score_bias)
    score += float(configs.score_weight_mention) * features.mention_bot
    score += float(configs.score_weight_at_other) * features.at_other
    score += float(configs.score_weight_question) * features.question
    score += float(configs.score_weight_media_only) * features.media_only
    score += float(configs.score_weight_self_ratio) * features.self_ratio
    score += float(configs.score_weight_message_count) * features.message_count
    score += float(configs.score_weight_seconds_since_bot) * features.log_seconds_since_bot
    score += float(configs.score_weight_pending) * features.pending_count
    return _sigmoid(score)

def apply_keyword_bias(probability: float, keyword_gain: float, configs: Any) -> float:
    """按关键词总权重把概率往两边推，得到「要不要交」这一层真正用来比较的值。

    只在 logit 上做加减，不重建线性式：正负对称，也不会像乘性调整那样在概率接近
    0 或 1 时被压住。权重 1.0 折算多少 logit 由 `keyword_bias_scale` 决定。

    这个值只用于最终比较，不写回概率：调用方仍然把原始概率交给额度统计，否则命中
    一次关键词会把整个取样窗口的目标提交量一起抬高。
    """

    value = clamp_unit(probability)
    gain = max(-1.0, min(1.0, float(keyword_gain)))
    scale = float(configs.keyword_bias_scale)
    if scale <= 0.0 or gain == 0.0:
        return value

    bounded = min(max(value, _LOGIT_EPSILON), 1.0 - _LOGIT_EPSILON)
    logit = math.log(bounded / (1.0 - bounded))
    return _sigmoid(logit + scale * gain)

def interpolate_threshold(allowance_share: float, curve: Any) -> float:
    """把允许份额按静态曲线分段线性插值成阈值。

    曲线按允许份额升序整理。份额越高，说明这一轮越舍得多提交一次，阈值就该越低，
    所以插值结果随份额单调不增。样本不够时用它兜底，避免前几轮的阈值在 0 和 1
    之间乱跳。
    """

    share = clamp_unit(allowance_share)
    ordered = sorted(
        (float(point_share), float(point_threshold))
        for point_share, point_threshold in curve
    )
    if not ordered:
        return clamp_unit(1.0 - share)
    if share <= ordered[0][0]:
        return clamp_unit(ordered[0][1])
    if share >= ordered[-1][0]:
        return clamp_unit(ordered[-1][1])

    for (share_from, threshold_from), (share_to, threshold_to) in zip(ordered, ordered[1:]):
        if share_from <= share <= share_to:
            span = share_to - share_from
            if span <= 0.0:
                return clamp_unit(threshold_to)
            offset = (share - share_from) / span
            return clamp_unit(threshold_from + (threshold_to - threshold_from) * offset)
    return clamp_unit(ordered[-1][1])

def _empirical_threshold(samples: Sequence[float], quota: float) -> float:
    """在窗口内的经验分布上找阈值。

    按概率从高到低累计「该条预计提交量」，攒到额度为止；阈值取被拦下的那一条里
    概率最高的一个。额度大于全部样本时说明不该拦，返回 0。
    """

    ordered = sorted((float(sample) for sample in samples), reverse = True)
    cumulative = 0.0
    accepted = 0
    for probability in ordered:
        cumulative += probability
        accepted += 1
        if cumulative >= quota:
            break
    if accepted >= len(ordered):
        return 0.0
    return ordered[accepted]

def retry_delay_seconds(consecutive_skips: int, pending: int, configs: Any) -> float:
    """连续被拦下时，两次判定之间该等多久。

    起点前按基准间隔走；之后每多拦一轮按倍数放大，封顶到上限。积压够多时返回 0，
    表示不该再拉长——队列已经堆起来了，拖着不判只是让用户多等。
    """

    if pending >= int(configs.retry_delay_bypass_pending):
        return 0.0

    start_after = int(configs.retry_delay_after_skips)
    base = float(configs.retry_delay_base_seconds)
    if consecutive_skips < start_after:
        return base

    steps = consecutive_skips - start_after
    delay = base * (float(configs.retry_delay_growth) ** steps)
    return min(delay, float(configs.retry_delay_cap_seconds))

def environment_rate_per_minute(recent: Sequence[MessageRecord], now: float, configs: Any) -> float:
    """最近窗口里「别人」的发言速率，单位条/分钟。

    自己发的不算环境：否则刚说完一句就会把自己的窗口拉快，越说越急。
    """

    window_seconds = max(1.0, float(configs.feature_window_seconds))
    window_start = float(now) - window_seconds
    count = 0
    for record in recent:
        if record.at < window_start or record.is_self:
            continue
        count += 1
    return float(count) * 60.0 / window_seconds

def _soft_max(first: float, second: float, beta: float) -> float:
    """对数和意义上的软取大：不小于两者的最大值，且在交叠处平滑过渡。"""

    high = max(first, second)
    low = min(first, second)
    return high + math.log1p(math.exp(-beta * (high - low))) / beta

def _soft_min(first: float, second: float, beta: float) -> float:
    """软取小：不大于两者的最小值。"""

    return -_soft_max(-first, -second, beta)

def adaptive_window_seconds(rate_per_minute: float, configs: Any) -> float:
    """按环境发言速率推出攒批窗口。

    目标速率是环境的一个固定比例：机器人自己的发言速率 = 环境速率 × `speak_rate_ratio`，
    窗口取它的倒数，所以环境越冷窗口越长、越热越短。

    上下界不用硬钳制，而是在对数空间做软钳制：把 `ln(窗口)` 与 `ln(下界)` 取软大、
    再与 `ln(上界)` 取软小。硬钳制会在边界外侧形成一段完全不变的平台，速率再变窗口
    也不动；软钳制让它指数式地趋近边界而永不平坦，曲线没有折点。
    `window_softness` 越大越接近硬钳制，越小过渡越长。
    """

    low = min(float(configs.min_batch_window_seconds), float(configs.max_batch_window_seconds))
    high = max(float(configs.min_batch_window_seconds), float(configs.max_batch_window_seconds))
    if high <= low or low <= 0.0:
        return max(0.0, low)

    rate = max(0.0, float(rate_per_minute))
    if rate <= 0.0:
        return high

    ratio = max(1e-6, float(configs.speak_rate_ratio))
    ln_low = math.log(low)
    ln_high = math.log(high)
    ln_target = math.log(60.0 / (rate * ratio))

    beta = max(1e-6, float(configs.window_softness)) / max(1e-9, ln_high - ln_low)
    ln_value = _soft_min(_soft_max(ln_target, ln_low, beta), ln_high, beta)
    return math.exp(ln_value)

def empty_streak_multiplier(empty_streak: int, configs: Any) -> float:
    """连续多少轮提交都是空的，就把窗口放大多少倍。

    群里彻底安静时窗口会顶在上界反复空跑。这里让它随连续空批次指数级拉长，
    封顶到 `empty_streak_max_multiplier` 倍——安静越久越没必要频繁试探。
    一有真实消息进来，调用方会把连击清零，窗口立刻回到自适应值。
    """

    start_after = max(1, int(configs.empty_streak_start_after))
    streak = int(empty_streak)
    if streak < start_after:
        return 1.0
    growth = max(1.0, float(configs.empty_streak_growth))
    steps = streak - start_after
    return min(float(configs.empty_streak_max_multiplier), growth ** steps)

def apply_timing_shake(
    seconds: float,
    configs: Any,
    rng: Callable[[], float] = random.random
) -> float:
    """给一段时长加对称抖动，避免每次等待都是同一个数。

    抖动必须对称：只往小抖会把等待整体压短，等于偷偷调快了配置。比例设 0 表示关闭。
    """

    value = max(0.0, float(seconds))
    ratio = max(0.0, float(configs.timing_shake_ratio))
    if ratio <= 0.0:
        return value
    factor = 1.0 + ratio * (2.0 * rng() - 1.0)
    return max(0.0, value * factor)

class SubmissionPolicy:
    """按「允许的回复量」把概率折算成阈值的提交策略。

    取样窗口里记三样东西：每次候选判定的概率（既是样本，也是该次预计提交量）、
    点名直接调用占用的额度、实际提交次数。

    目标量 = 回复率 × 窗口内预计总提交量；扣掉点名直接调用已经占用的额度，剩下的
    额度摊到候选判定的预计量上，得到允许份额，再换成阈值。实际提交已经多于目标时
    按因子收紧，少于目标时不放松——一波消息刚到时预计量先涨、实际提交还没跟上，
    此时若放松，等提交追上来就收不回去，长期结果只会偏多。
    """

    def __init__(self, configs: Any):
        self.configs = configs
        self._candidates: deque[tuple[float, float]] = deque()
        self._direct_calls: deque[float] = deque()
        self._submissions: deque[float] = deque()

    def observe_candidate(self, probability: float, now: float) -> None:
        """登记一次候选判定：概率既是阈值样本，也是该次预计提交量。"""

        self._drop_expired(now)
        self._candidates.append((float(now), clamp_unit(probability)))

    def observe_direct_call(self, now: float) -> None:
        """登记一次点名直接调用，按配置里的固定值占用提交额度。"""

        self._drop_expired(now)
        self._direct_calls.append(float(now))

    def observe_submission(self, now: float) -> None:
        """登记一次实际提交，空批次和点名直接调用也算。"""

        self._drop_expired(now)
        self._submissions.append(float(now))

    def evaluate(self, probability: float, rate: float, now: float) -> SubmitDecision:
        """判这一批要不要现在提交。

        调用方先 `observe_candidate` 再 `evaluate`，本轮的概率因此在取样窗口里，
        参与本轮阈值的计算——否则第一条永远样本为空，只能靠静态曲线起步。
        """

        self._drop_expired(now)
        current = clamp_unit(probability)
        reply_rate = clamp_unit(rate)
        expected_replies = sum(sample for _, sample in self._candidates)
        direct_cost = float(len(self._direct_calls)) * float(self.configs.direct_call_cost)
        expected_total = expected_replies + direct_cost
        target = reply_rate * expected_total
        submitted = len(self._submissions)

        allowance = target - direct_cost
        if expected_replies > 0.0:
            allowance_share = allowance / expected_replies
        else:
            allowance_share = 0.0
        if submitted > target:
            allowance_share *= float(self.configs.overrun_tighten_factor)
        allowance_share = clamp_unit(allowance_share)

        # 回复率的两个端点按规格退化：1.0 全提交、0 全拦。端点不走数值比较，免得
        # sigmoid 在极值上取到精确的 1 或 0，让 p > threshold 的结果反转。
        endpoint_result: bool | None = None
        if reply_rate >= 1.0:
            allowance_share = 1.0
            threshold = 0.0
            endpoint_result = True
        elif reply_rate <= 0.0:
            allowance_share = 0.0
            threshold = 1.0
            endpoint_result = False
        else:
            threshold = self._choose_threshold(allowance_share, expected_replies)

        if endpoint_result is not None:
            should_submit = endpoint_result
        else:
            should_submit = current > threshold

        return SubmitDecision(
            should_submit = should_submit,
            probability = current,
            threshold = threshold,
            allowance_share = allowance_share,
            expected_replies = expected_total,
            target_replies = target,
            submission_count = submitted,
            direct_cost = direct_cost,
            sample_count = len(self._candidates),
        )

    def _choose_threshold(self, allowance_share: float, expected_replies: float) -> float:
        """允许份额换成阈值：样本够就用窗口内的经验分布，不够就查静态曲线。"""

        if allowance_share <= 0.0:
            return 1.0
        if allowance_share >= 1.0:
            return 0.0

        if len(self._candidates) >= int(self.configs.sample_min_count):
            quota = allowance_share * expected_replies
            return clamp_unit(
                _empirical_threshold(
                    [sample for _, sample in self._candidates],
                    quota
                )
            )

        return interpolate_threshold(allowance_share, self.configs.threshold_curve)

    def _drop_expired(self, now: float) -> None:
        """把滑出取样窗口的记录摘掉，三个队列共用同一个窗口。"""

        horizon = float(now) - float(self.configs.sample_window_seconds)
        while self._candidates and self._candidates[0][0] < horizon:
            self._candidates.popleft()
        while self._direct_calls and self._direct_calls[0] < horizon:
            self._direct_calls.popleft()
        while self._submissions and self._submissions[0] < horizon:
            self._submissions.popleft()
