from pathlib import Path

from pydantic import BaseModel, Field

from .enter_prompt import enter_prompt as default_enter_prompt
from .exit_prompt import exit_prompt as default_exit_prompt

class ChatLoopConfigs(BaseModel):
    enter_prompt: str = default_enter_prompt
    exit_prompt: str = default_exit_prompt

    # 攒批：窗口到点或积压到单批上限才进入判定，一次最多交这么多条
    batch_max_messages: int = Field(default = 12, ge = 1) # 单批上限，条
    speak_rate_ratio: float = Field(default = 0.05, gt = 0.0, le = 1.0) # 机器人发言速率 ÷ 环境发言速率；0.1 约等于「环境十条它一条」，0.05 约等于二十条一条，0.02 约等于五十条一条
    min_batch_window_seconds: int | float = Field(default = 20, gt = 0) # 窗口最短（也就是最快节奏），秒
    max_batch_window_seconds: int | float = Field(default = 300, gt = 0) # 窗口最长（也就是最慢节奏），秒
    window_softness: float = Field(default = 12.0, gt = 0) # 上下界的软钳制强度，越大越接近硬边界，越小过渡越长
    empty_streak_start_after: int = Field(default = 2, ge = 1) # 连续多少个空批次之后开始拉长窗口
    empty_streak_growth: float = Field(default = 1.6, gt = 1.0) # 每多一个空批次，窗口放大多少倍
    empty_streak_max_multiplier: float = Field(default = 8.0, ge = 1.0) # 空批次拉长的封顶倍数（相对自适应窗口）
    timing_shake_ratio: float = Field(default = 0.15, ge = 0.0, le = 1.0) # 等待时长的对称抖动比例，0 关闭
    submit_empty_batch: bool = Field(default = True) # 窗口到点却一条积压都没有时也提交空批次，给模型一个接话的机会
    mention_divider: str = Field(default = "---") # 点名消息和前面内容之间的分隔线

    # 特征窗口：最近多久的消息算进「最近消息」里
    feature_window_seconds: int | float = Field(default = 240, gt = 0) # 秒
    summary_buffer_limit: int = Field(default = 256, ge = 1) # 最近消息记录环形缓冲的长度，条
    pending_feature_cap: int = Field(default = 24, ge = 1) # 积压条数进特征时的上限，免得长队列把分数顶穿

    # 线性打分的初始值，待用真实聊天记录重新拟合
    score_bias: float = Field(default = -1.15)
    score_weight_mention: float = Field(default = 2.2) # 窗口内有人点名；点名本身会直接提交，这项影响的是之后几批
    score_weight_at_other: float = Field(default = -0.95) # 最新一条 @ 了别人，负向
    score_weight_question: float = Field(default = 0.55) # 最新一条是问句
    score_weight_media_only: float = Field(default = -0.85) # 最新一条只有媒体没有文字，负向
    score_weight_self_ratio: float = Field(default = 2.20) # 窗口内自己发言占比
    score_weight_message_count: float = Field(default = -0.03) # 窗口内消息条数，负向
    score_weight_seconds_since_bot: float = Field(default = 0.22) # 距自己上次发言的秒数，已取 log1p
    score_weight_pending: float = Field(default = 0.09) # 当前积压条数

    # 阈值：由目标回复率推出，不是一个常量
    reply_rate: float = Field(default = 1.0, ge = 0.0, le = 1.0) # 目标回复率，1.0 不筛（阈值退化为 0），0 全拦（阈值退化为 1）
    sample_window_seconds: int | float = Field(default = 1800, gt = 0) # 取样窗口，秒
    sample_min_count: int = Field(default = 20, ge = 1) # 样本达到多少条才改用窗口内的经验分布
    overrun_tighten_factor: float = Field(default = 0.88, gt = 0.0, le = 1.0) # 已提交次数多于目标时的收紧因子
    threshold_curve: list[tuple[float, float]] = Field(default_factory = lambda: [
        (0.00, 1.00),
        (0.05, 0.80),
        (0.10, 0.72),
        (0.20, 0.62),
        (0.35, 0.52),
        (0.50, 0.45),
        (0.65, 0.38),
        (0.80, 0.28),
        (0.90, 0.18),
        (1.00, 0.00),
    ]) # 允许份额 → 阈值的静态曲线，按份额升序、阈值单调不增
    direct_call_cost: float = Field(default = 1.0, ge = 0.0) # 一次点名直接调用折算成的预计提交量

    # 重试间隔：连续没提交时把判定间隔拉长，积压够多时取消拉长
    retry_delay_base_seconds: int | float = Field(default = 20, gt = 0) # 间隔起点，秒
    retry_delay_growth: float = Field(default = 1.7, gt = 1.0) # 每多拦一轮放大的倍数
    retry_delay_cap_seconds: int | float = Field(default = 240, gt = 0) # 间隔上限，秒
    retry_delay_after_skips: int = Field(default = 2, ge = 1) # 连续多少轮没提交才开始拉长
    retry_delay_bypass_pending: int = Field(default = 5, ge = 1) # 积压达到多少条就取消拉长

    cleanup_timeout: int | float = Field(default = 10, gt = 0) # 秒
