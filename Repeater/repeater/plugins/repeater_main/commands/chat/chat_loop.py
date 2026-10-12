import re
import random
import asyncio
from .._bases import BaseChat
from ...assist import PersonaInfo, SendMsg, Namespace, str_to_bool
from ...command_register import CommandCaller
from ...logger import logger as base_logger
from nonebot.adapters.onebot.v11 import Message, MessageSegment

logger = base_logger.bind(module = "ChatLoop")

@CommandCaller.register
class ChatLoop(BaseChat):
    cmd = "chatLoop"
    aliases = {
        "clp",
        "CLP",
        "ChatLoop",
        "CHAT_LOOP"
    }
    description = f"""
        Talk to LLM and no longer need to `@bot`
        
        Usage:
        ```
        /{cmd} submit_time shake_time true
        ```
        or
        ```
        /{cmd} submit_time shake_time false
        ```
        The first parameter indicates how long to wait before committing the data.
        The second parameter is whether to listen for group-wide messages.
    """

    pattern = re.compile(r"^(?P<submit_time>[\d\.]+)\s*(?P<shake_time>[\d\.]+)(?P<group_wide>.*)$")
    ai_reply_pattern = re.compile(r"^\[(?P<message_id>\d+|no_reply)\]\s*:\s*(?P<message>.*)$", re.DOTALL)

    @staticmethod
    async def listen_message(namespace: Namespace, message_queue: asyncio.Queue[PersonaInfo], group_wide: bool) -> None:
        while True:
            persona_info = await CommandCaller.wait_message(
                namespace,
                listen_group = group_wide
            )
            await message_queue.put(persona_info)
    
    @staticmethod
    def parse_messages(persona_infos: list[PersonaInfo]) -> str:
        text_buffer: list[str] = [
            f"{len(persona_infos)} messages received:",
            "The response form is:",
            "Use the tool to invoke the `/echo` command to send the message.",
            "One reply per line",
            "Some messages don't need a reply",
            "The number of replies should not exceed 6.",
            "Just choose the ones you're interested in.",
            "----------------------------------------",
        ]
        for persona_info in persona_infos:
            text_buffer.append(
                f"{persona_info.display_name}: [msgid:{persona_info.message_id}|user_id:{persona_info.user_id}|time:{persona_info.time.isoformat()}]"
            )
            text_buffer.append(
                f"{persona_info.message_cqcode}"
            )
            text_buffer.append(
                ""
            )
        return "\n".join(text_buffer)

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg) -> None:
        matched = persona_info.match_message(self.pattern)
        if matched:
            submit_time_str = matched.group("submit_time")
            shake_time_str = matched.group("shake_time")
            group_wide_str = matched.group("group_wide")

            assert isinstance(submit_time_str, str), "submit_time must be a string"
            assert isinstance(shake_time_str, str), "shake_time must be a string"
            assert isinstance(group_wide_str, str), "group_wide must be a string"

            try:
                submit_time = float(submit_time_str)
            except ValueError:
                await send_msg.send_error(f"Invalid submit_time: {submit_time_str}")

            try:
                shake_time = float(shake_time_str)
            except ValueError:
                await send_msg.send_error(f"Invalid shake_time: {shake_time_str}")

            if group_wide_str:
                try:
                    group_wide = str_to_bool(group_wide_str)
                except ValueError:
                    await send_msg.send_error(f"Invalid group_wide: {group_wide_str}")
            else:
                group_wide = False

            message_queue: asyncio.Queue[PersonaInfo] = asyncio.Queue()
            message_wait_task = asyncio.create_task(
                coro = self.listen_message(
                    namespace = persona_info.namespace,
                    message_queue = message_queue,
                    group_wide = group_wide
                )
            )

            client = await self.get_client(persona_info)

            while True:
                shake = random.uniform(0, shake_time)
                await asyncio.sleep(delay = submit_time + shake)

                if message_queue.empty():
                    logger.info(
                        "No new messages, skipping this round..."
                    )
                    continue

                messages: list[PersonaInfo] = []
                for _ in range(message_queue.qsize()):
                    messages.append(
                        await message_queue.get()
                    )

                logger.info(
                    f"Got {len(messages)} messages, sending..."
                )

                submit_message = self.parse_messages(messages)
                response = await client.send_message(
                    message = submit_message,
                    raw_message = True
                )

                chat_send_msg = self.make_send_msg(
                    send_msg = send_msg,
                    response = response
                )

                await chat_send_msg.check_response()
        else:
            await send_msg.send_error("Invalid message format")