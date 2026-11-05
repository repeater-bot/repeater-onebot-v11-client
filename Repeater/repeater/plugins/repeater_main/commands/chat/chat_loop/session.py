import asyncio
import re
import time
from collections import deque
from contextlib import suppress
from datetime import datetime

import orjson

from ....clients import ChatClient
from ....assist import EnterType, PersonaInfo
from ....command_register import CommandCaller
from ....logger import logger as base_logger
from ....client_configs import ChatLoopConfigs
from .submit_policy import (
    MessageRecord,
    SubmissionPolicy,
    adaptive_window_seconds,
    apply_keyword_bias,
    apply_timing_shake,
    compute_probability,
    empty_streak_multiplier,
    environment_rate_per_minute,
    extract_features,
    ns_to_seconds,
    retry_delay_seconds,
    seconds_to_ns,
)

logger = base_logger.bind(module = "ChatLoop.Session")

class ChatLoopSession:
    """一次聊天循环的全部状态：收消息、判定、提交、关停。"""

    def __init__(self, persona_info: PersonaInfo, configs: ChatLoopConfigs):
        self.persona_info = persona_info
        self.configs = configs
        self.scene = persona_info.scene
        self.status_name = f"SmartAT_Block_{persona_info.scene_str}"
        self._keyword_pattern, self._keyword_weights = self._compile_keywords(configs.keyword_weights)
        self.client: ChatClient | None = None
        self.message_queue: asyncio.Queue[PersonaInfo] = asyncio.Queue()
        self._wake = asyncio.Event()
        self._tome_pending = False
        self._recent: deque[MessageRecord] = deque(maxlen = int(configs.summary_buffer_limit))
        self._policy = SubmissionPolicy(configs)
        self._last_send_ns = time.perf_counter_ns()
        self._consecutive_holds = 0
        self._empty_streak = 0
        self._retry_backlog: list[PersonaInfo] = []
        self._tome_ids: set = set()
        # 叫过我的消息号，供格式化时打标记；和 _tome_ids 分开存，因为 _tome_ids
        # 会在分批时被消费掉，而标记要跟着消息一直留到真正发出去
        self._call_me_ids: set = set()
        self._collector: asyncio.Task | None = None
        self._listener_id = None
        self._closing = False

    async def start(self) -> None:
        """
        建状态、起监听、补开场提示。

        状态必须先于监听：顺序反过来的话，监听已经在收消息、外部却读不到占用，
        这段时间里 SmartAT 会认为这个场景没人占着，接着往里回话。
        """

        await CommandCaller.create_status(self.status_name)
        self._collector = asyncio.create_task(
            self._collect(),
            name = f"chat_loop:{self.status_name}"
        )
        await self.enter_chat_loop()

    async def close(self) -> None:
        """
        关停：摘监听、收监听任务、摘状态、补退出提示。

        每一步单独兜异常，前一步失败不该让后面的清理不执行。顺序上状态先于退出提示，
        这样循环一停 SmartAT 就能接手，不用等退出提示那几秒。
        """

        self._closing = True
        for step in (self._stop_collector, self._finish_status, self._send_exit_prompt):
            try:
                await step()
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception(
                    "Chat loop cleanup failed: {step}",
                    step = step.__name__
                )

    async def run(self) -> None:
        """
        主循环：攒批 → 判定 → 提交。

        攒批窗口没到、积压也没到单批上限时不判定，等窗口到点或新消息叫醒。
        进入判定后三条放行路径：
        - 批次里有叫我的消息，无条件提交，不经过概率判定；
        - 概率过动态阈值才提交；
        - 窗口到点却一条积压都没有，按配置补一个空批次，让模型自己接话。
        被阈值拦下的批次留在队列里，按重试间隔等一段时间再判。
        """

        while True:
            now_ns = time.perf_counter_ns()
            window = apply_timing_shake(
                adaptive_window_seconds(
                    environment_rate_per_minute(self._recent, now_ns, self.configs),
                    self.configs
                ) * empty_streak_multiplier(self._empty_streak, self.configs),
                self.configs
            )
            elapsed_ns = now_ns - self._last_send_ns
            # 时钟一律整数纳秒；窗口是浮点秒（配置本来就用秒），只在比较这一处换算
            window_ns = seconds_to_ns(window)
            pending = self.message_queue.qsize() + len(self._retry_backlog)
            batch_cap = max(1, int(self.configs.batch_max_messages))
            urgent = self._tome_pending and pending > 0

            if not urgent and pending < batch_cap and elapsed_ns < window_ns:
                # asyncio 只吃浮点秒，这里再换回去
                await self._wait_next(ns_to_seconds(window_ns - elapsed_ns))
                continue

            if pending <= 0:
                if self.configs.submit_empty_batch:
                    if not await self._submit([], "empty batch"):
                        await self._wait_next(self._retry_wait(pending))
                else:
                    await self._wait_next(self._retry_wait(pending))
                continue

            features = extract_features(
                recent = self._recent,
                pending = pending,
                now_ns = now_ns,
                since_bot_ns = elapsed_ns,
                configs = self.configs,
            )
            # 关键词只影响「这一批要不要交」的比较值；额度统计仍然只吃原始概率，
            # 否则命中一次关键词会把取样窗口的目标提交量一起抬高
            base_probability = compute_probability(features, self.configs)
            probability = apply_keyword_bias(
                base_probability,
                features.keyword_gain,
                self.configs
            )

            if urgent:
                # 在这里消费标记，而不是在 _submit 里：send_messages 是个 await，
                # 期间到达的点名会被「发送完成后无条件清零」静默吞掉
                self._tome_pending = False
                sent = await self._submit(
                    self._drain(min(pending, batch_cap)),
                    f"direct call by mention, p={probability:.3f}",
                    direct_call = True,
                )
                if not sent:
                    self._tome_pending = True
                    await self._wait_next(self._retry_wait(pending))
                continue

            self._policy.observe_candidate(base_probability, now_ns)
            decision = self._policy.evaluate(
                probability,
                float(self.configs.reply_rate),
                now_ns
            )
            if decision.should_submit:
                if not await self._submit(self._drain(min(pending, batch_cap)), str(decision)):
                    await self._wait_next(self._retry_wait(pending))
                continue

            self._consecutive_holds += 1
            logger.info(
                "Chat loop held a batch: {decision} kw={gain:.2f} base={base:.3f}",
                decision = str(decision),
                gain = features.keyword_gain,
                base = base_probability
            )
            await self._wait_next(self._retry_wait(pending))

    async def _wait_next(self, timeout: float) -> None:
        """
        等到下一批该判定，或者被新消息叫醒。
        """

        self._wake.clear()
        with suppress(asyncio.TimeoutError):
            await asyncio.wait_for(
                self._wake.wait(),
                timeout = max(0.0, float(timeout))
            )

    def _retry_wait(self, pending: int) -> float:
        """
        被拦下或者队列空转时，隔多久再判一次。

        间隔为 0（积压已经够多）时用基准间隔兜底：等待真的归零会把这个循环变成
        空转，白白烧 CPU 又不会更快放行。
        """

        delay = retry_delay_seconds(self._consecutive_holds, pending, self.configs)
        if delay <= 0.0:
            delay = float(self.configs.retry_delay_base_seconds)
        return apply_timing_shake(delay, self.configs)

    async def _submit(
        self,
        messages: list[PersonaInfo],
        reason: str,
        *,
        direct_call: bool = False
    ) -> bool:
        """
        把一批交给 LLM；失败时把这批留着重试，不往外抛。

        发送失败（接口连不上、超时）不该让整个循环退出——循环一死，这个场景就再也
        不会自己说话了，而且异常冒上去还会触发框架的错误消息。所以失败时把消息放回
        待发缓冲、记一条日志、按重试间隔再来。
        """

        logger.info(
            "Submitting {messages_count} messages to LLM: {reason}",
            messages_count = len(messages),
            reason = reason,
        )
        rest, pinned = self._split_mentions(messages)
        try:
            await self.send_messages(rest, pinned)
        except Exception:
            logger.exception("Chat loop failed to submit a batch, keeping it for retry")
            self._retry_backlog = messages + self._retry_backlog
            self._tome_ids.update(message.message_id for message in pinned)
            self._consecutive_holds += 1
            return False

        now_ns = time.perf_counter_ns()
        self._last_send_ns = now_ns
        self._consecutive_holds = 0
        if messages:
            self._empty_streak = 0
        else:
            self._empty_streak += 1
        self._recent.append(
            MessageRecord(
                at_ns = now_ns,
                is_self = True,
                is_tome = False,
                question = False,
                at_other = False,
                has_text = True,
            )
        )
        self._policy.observe_submission(now_ns)
        if direct_call:
            self._policy.observe_direct_call(now_ns)
        return True

    async def _collect(self) -> None:
        """
        每条消息一个 listener，并且自己持有 listener id。

        不用 `wait_message` 是因为它不返回 listener id：任务被取消后那条监听会留在
        `message_listener` 里，等这个场景再来消息时，框架会对一个已取消的 Future
        调 `set_result` 并抛 `InvalidStateError`，把消息分发弄坏。自己持有 id 才能在
        关停时先把它从表里摘掉，让 Future 干净地结束。
        """

        while not self._closing:
            listener = await CommandCaller.message_future(target = self.scene)
            if self._closing:
                await CommandCaller.cancel_message_future(listener.id)
                return
            self._listener_id = listener.id
            try:
                message = await listener
            finally:
                self._listener_id = None
            await self._record(message)

    async def _record(self, persona_info: PersonaInfo) -> None:
        """
        记下摘要，再分发给队列并叫醒主循环。

        全部消息都进 `message_queue`；只有被 @ / 引用才另置「立刻提交」的标记。
        叫醒是无条件的：窗口会随环境变长（安静时甚至退避到几十分钟），不叫醒的话
        真有人说话都要等窗口到点才被发现。
        """

        if persona_info.enter_type not in (EnterType.Message, EnterType.Command):
            # 真实消息只可能是 Message 或 Command；Horizontal 来自别的命令、External 来自
            # ET 服务器，内容都不是群成员打的字，塞进批次会把时间线弄脏
            logger.debug(
                "Chat loop skipped an entry that is not a real message: {enter_type}",
                enter_type = persona_info.enter_type
            )
            return

        is_tome = await self._resolve_tome(persona_info)
        text = persona_info.message_stripped_str
        self._recent.append(
            MessageRecord(
                at_ns = time.perf_counter_ns(),
                is_self = False,
                is_tome = is_tome,
                question = "?" in text or "？" in text,
                at_other = bool(persona_info.noself_at_list),
                has_text = bool(text),
                keyword_gain = self._keyword_gain(text),
            )
        )
        if is_tome:
            self._tome_pending = True
            self._tome_ids.add(persona_info.message_id)
            self._call_me_ids.add(persona_info.message_id)
        self._empty_streak = 0
        self._wake.set()
        self.message_queue.put_nowait(persona_info)

    @staticmethod
    def _compile_keywords(weights: dict[str, float]) -> tuple[re.Pattern[str] | None, dict[str, float]]:
        """
        把关键词表编成一条按长度降序的 alternation 正则。

        正则的 alternation 在每个位置按顺序试，长的放在前面就能遮蔽短的：
        「哈尔滨」不会再同时命中「哈」。finditer 天然不重叠，所以不相邻的多个
        关键词仍然各算一次。键统一转小写，匹配用 IGNORECASE，取回的原文再转
        小写查权重表。
        """

        normalized: dict[str, float] = {}
        for keyword, weight in weights.items():
            text = str(keyword).strip().lower()
            if text:
                normalized[text] = float(weight)
        if not normalized:
            return None, {}

        ordered = sorted(normalized, key = len, reverse = True)
        pattern = "|".join(re.escape(keyword) for keyword in ordered)
        return re.compile(pattern, re.IGNORECASE), normalized

    def _keyword_gain(self, text: str) -> float:
        """
        这条消息命中的关键词权重之和；负数抑制、正数更容易触发。

        匹配走「最长优先」：同一位置能命中多个词时，长的那个遮蔽短的，所以
        「哈尔滨」只算它自己那条权重，不会叠上「哈」；不相邻的多个关键词仍然
        各算一次。窗口内的汇总和夹取在特征提取那一侧做。
        """

        pattern = self._keyword_pattern
        if pattern is None or not text:
            return 0.0

        gain = 0.0
        for match in pattern.finditer(text):
            gain += self._keyword_weights.get(match.group(0).lower(), 0.0)
        return gain

    def _split_mentions(self, messages: list[PersonaInfo]) -> tuple[list[PersonaInfo], list[PersonaInfo]]:
        """
        把叫我的消息从批次里挑出来，返回（其余消息, 点名消息）。

        模型按顺序读，最后一条最容易被接住。这两段在发送时会用分隔线隔开，
        所以点名那几条既排在末尾，也和前面的闲聊在视觉上分开。
        """

        if not messages or not self._tome_ids:
            return messages, []

        pinned_ids = {
            message.message_id for message in messages
            if message.message_id in self._tome_ids
        }
        if not pinned_ids:
            return messages, []

        self._tome_ids.difference_update(pinned_ids)
        rest = [
            message for message in messages
            if message.message_id not in pinned_ids
        ]
        pinned = [
            message for message in messages
            if message.message_id in pinned_ids
        ]
        return rest, pinned

    def _drain(self, limit: int) -> list[PersonaInfo]:
        """
        取至多 limit 条，不够就取到多少算多少。

        发送失败留下的那批排在前面：它们比新消息更早到达，重试时顺序不能乱。
        其余部分只用 `get_nowait`——limit 是现算的，两次读之间队列只会被这里消费，
        换成 `await get()` 就变成「按旧估计去等」，一旦估计偏大就会挂住。
        """

        messages: list[PersonaInfo] = []
        capacity = max(0, limit)
        while self._retry_backlog and len(messages) < capacity:
            messages.append(self._retry_backlog.pop(0))
        for _ in range(capacity - len(messages)):
            try:
                messages.append(self.message_queue.get_nowait())
            except asyncio.QueueEmpty:
                break
        return messages

    async def _stop_collector(self) -> None:
        if self._listener_id is not None:
            await CommandCaller.cancel_message_future(self._listener_id)
            self._listener_id = None
        task = self._collector
        if task is None:
            return
        self._collector = None
        # 监听被摘掉后 collect 会自己结束；这一步只是兜底，保证不留下活着的任务
        with suppress(asyncio.CancelledError, asyncio.TimeoutError):
            await asyncio.wait_for(
                task,
                timeout = float(self.configs.cleanup_timeout)
            )

    async def _finish_status(self) -> None:
        await CommandCaller.finish_status(self.status_name)

    async def _send_exit_prompt(self) -> None:
        """
        退出提示是清理任务，允许它自己跑完，但必须有个上限并自己退出。
        """

        if self.client is None:
            return
        try:
            await asyncio.wait_for(
                self.client.send_message(
                    message = self.configs.exit_prompt,
                    raw_message = True
                ),
                timeout = float(self.configs.cleanup_timeout)
            )
        except asyncio.TimeoutError:
            logger.warning(
                "Chat loop exit prompt timed out and was cancelled: {status}",
                status = self.status_name
            )

    async def enter_chat_loop(self) -> None:
        if self.client is None:
            return
        await self.client.send_message(
            message = self.configs.enter_prompt,
            raw_message = True
        )

    async def send_messages(
        self,
        messages: list[PersonaInfo],
        pinned: list[PersonaInfo] | None = None
    ) -> None:
        """
        把一批交给模型。

        有被点名的消息时，用一条水平线把它和前面的内容隔开：这样模型一眼能看出
        「下面是有人直接叫我」，而不是继续把整段当成一片闲聊。
        """

        if self.client is None:
            return

        text = await self.format_messages(messages)
        if pinned:
            block = await self.format_messages(pinned)
            divider = self.configs.mention_divider
            text = f"{text}\n\n{divider}\n\n{block}" if text else block
        if not text:
            # 空批次也必须带内容：只发一个空串的话，模型既不知道现在几点、
            # 也拿不到任何可依据的东西。配置里用 {time} 占位，这里只替换它。
            text = str(self.configs.empty_batch_prompt).replace(
                "{time}",
                datetime.now().isoformat(timespec = "seconds")
            )
        
        await self.client.send_message(
            message = text,
            raw_message = True
        )

    async def format_messages(self, messages: list[PersonaInfo]) -> str:
        """
        把一批消息格式化成模型读的文本；被引用过的消息展开成下面一行。

        被引用的消息不用再查平台：onebot v11 在事件进站时就把 `get_msg` 的结果放在
        `event.reply` 上（同时把 reply 消息段从 message 里删掉），所以这里只读内存。
        adapter 查询失败时 `event.reply` 为 None、而 reply 段还留在 message 里，
        这种情况退化成标注一句「引用了不可获取的消息」并把段打出来。
        """

        formatted_messages: list[str] = []
        for message in messages:
            formatted_messages.append(self._format_message_line(message))
            quoted = await self._quoted_line(message)
            if quoted is not None:
                formatted_messages.append(quoted)
        return "\n".join(formatted_messages)

    def _format_user_name(self, message: PersonaInfo) -> str:
        """
        格式化用户名；让提交时存在群昵称和用户昵称。
        """

        if message.card:
            name = (
                orjson.dumps(message.card).decode("utf-8") + 
                f"({orjson.dumps(message.nickname).decode('utf-8')})"
            )
        else:
            name = orjson.dumps(message.nickname).decode("utf-8")
        return name


    def _format_message_line(self, message: PersonaInfo) -> str:
        """
        一条消息的主行；叫过我的消息在名字后面多带一个属性。

        属性直接融进同一对方括号里，和 time/usrid/msgid 并列，所以仍然是「一条消息
        一个标签」，不需要额外的前缀括号。判定用的是收消息时算好的结果，不回查平台。
        """

        call_me = "|**call_me_msg**" if message.message_id in self._call_me_ids else ""
        
        return (
            f"[{self._format_user_name(message)}"
            f"{call_me}"
            f"|time={message.time.isoformat()}"
            f"|usrid={message.user_id}"
            f"|msgid={message.message_id}]: "
            f"{orjson.dumps(message.message_cqcode).decode('utf-8')}"
        )

    async def _quoted_line(self, message: PersonaInfo) -> str | None:
        """
        被引用消息的二级条目；这条不是回复时返回 None。
        """
        buffer: list[str] = []

        reply_msgs = await message.from_reply_msgs()
        if not reply_msgs:
            return self._unresolved_quote_line(message.message_cqcode)
        
        for reply in reply_msgs:
            buffer.append(
                f"  >> Reply [{self._format_user_name(reply)}"
                f"|time={reply.time.isoformat()}"
                f"|usrid={reply.user_id}"
                f"|msgid={reply.message_id}]: "
                f"{orjson.dumps(self._truncate(reply.message_cqcode)).decode('utf-8')}"
            )
        return "\n".join(buffer)

    def _unresolved_quote_line(self, cqcode: str) -> str | None:
        """
        adapter 没查到被引用消息时的降级：只标注引用段的原文。
        """

        if not cqcode or "[CQ:reply" not in cqcode:
            return None
        start = cqcode.find("[CQ:reply")
        end = cqcode.find("]", start)
        if end <= start:
            return None
        return f"  >> Unreachable message was referenced: {cqcode[start:end + 1]}"

    def _truncate(self, text: str) -> str:
        """
        被引用内容按配置截断；0 表示不截断。

        截的是**原始 CQ 串**，发生在 json 转义之前：省略号落在字符串内部，转义出来
        的引号因此始终成对。代价是转义后的长度可能略超上限（换行、引号会膨胀），
        但这个上限管的是内容长度，不是转义后长度。
        """

        limit = max(0, int(self.configs.reply_inline_max_chars))
        if limit and len(text) > limit:
            return text[:limit] + "…"
        return text

    async def _resolve_tome(self, persona_info: PersonaInfo) -> bool:
        """
        判断这条消息是不是在叫我。

        先问事件自己：群消息看的是实现端给出的 `to_me` 标志。这比我们逐段扫 at 可靠
        ——段可能被实现端摘掉或改写，标志不会。再退回人肉扫描，它额外覆盖
        「引用回复我的消息」，代价是要回查被引用消息。
        """

        try:
            if persona_info.event.is_tome():
                return True
        except Exception:
            logger.exception("Failed to resolve tome from the event")

        try:
            return await persona_info.is_tome()
        except Exception:
            # is_tome 遇到引用段要回查被引用消息，可能因平台侧失败而抛；
            # 降级成「不是叫我」比让整个监听协程静静地死掉要好
            logger.exception("Failed to resolve whether the message mentions the bot")
            return False
