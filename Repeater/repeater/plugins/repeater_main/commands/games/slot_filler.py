import random
import asyncio

from ...assist import PersonaInfo, SendMsg, Downloader
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ._brackets import brackets

@CommandCaller.register
class SlotFiller(CommandPackage):
    cmd = "slotFiller"
    aliases = {
        "sfl",
        "SFL",
        "slot_filler",
        "Slot_Filler"
        "SlotFiller",
        "SLOT_FILLER"
    }
    cmd_type = CmdTypes.GAMES
    description = f"""
        Replaces all parentheses in the text
        First you need to enter the candidate list
        The command then waits for the user to enter the next message
        This is then used as a template for random replacements
        Exit when there are no parentheses in the input.

        Usage:
        ```
        /{cmd}
        name-1
        name-2
        name-3
        ...
        name-n
        ```

        ```
        () drives to pick up () to work
        ```
    """
    def __init__(self):
        self.downloader = Downloader()

    @staticmethod
    def choices(items: list[str], k: int = 1) -> list[str]:
        return random.choices(items, k=k)

    @classmethod
    def replace(cls, template: str, symbol: str, items: list[str]) -> str | None:
        count = template.count(symbol)
        if count <= 0:
            return None

        choices = cls.choices(items, count)

        for choice in choices:
            template = template.replace(symbol, choice, 1)
        return template

    @classmethod
    def replace_all(cls, template: str, items: list[str]) -> str | None:
        if not brackets:
            return template

        results: list[str | None] = []
        for symbol in brackets:
            new_message = cls.replace(template, symbol, items)
            if new_message is None:
                continue
            results.append(new_message)
            template = new_message

        if not any(results):
            return None

        return template

    async def _get_text(self, persona_info: PersonaInfo) -> str:
        text_buffer: list[str] = []

        files = persona_info.get_file_infos()
        for file in files:
            try:
                text = await self.downloader.download_text(file.url)
            except UnicodeDecodeError:
                continue

            text_buffer.append(text)

        text_buffer.append(persona_info.message_stripped_str)

        return "\n".join(text_buffer)

    async def get_text(self, persona_info: PersonaInfo) -> str:
        text_buffer: list[str] = []
        for replys in await persona_info.from_reply_reversed_chain():
            text_buffer.append(
                await self._get_text(
                    replys
                )
            )

        text_buffer.append(
            await self._get_text(
                persona_info
            )
        )

        return "\n".join(text_buffer)

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        text = await self.get_text(persona_info)

        if not text:
            await send_msg.send_error("Please enter the candidate list first")
            return

        items = text.splitlines()

        await send_msg.send_text(
            "Please enter the template and exit if there are no parentheses in the input.",
            continue_handler = True
        )

        while True:
            new_message = await CommandCaller.wait_message(persona_info.namespace)
            template = await self.get_text(new_message)

            new_text = await asyncio.to_thread(
                self.replace_all,
                template,
                items
            )
            
            new_send_msg = send_msg.copy(
                reply = new_message.reply
            )

            if new_text is None:
                await new_send_msg.send_text("An input that does not contain any parentheses has been exited.")
                new_send_msg.break_handler()

            await new_send_msg.send_check_length_prompt(
                prompt = new_text,
                continue_handler = True
            )