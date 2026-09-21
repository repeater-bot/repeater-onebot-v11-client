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
class SlotCaster(CommandPackage):
    cmd = "slotCaster"
    aliases = {
        "sct",
        "SCT",
        "slot_caster",
        "Slot_Caster"
        "SlotCaster",
        "SLOT_CASTER"
    }
    cmd_type = CmdTypes.GAMES
    description = f"""
        Replaces all parentheses in the text
        First, you need to enter a template that includes the parentheses
        Then, the command waits for the user to enter the next message.
        This is then used as a list of random replacements
        Exit when the input no longer contains at least two items

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
        if k < 1:
            return []
        elif k <= len(items):
            return random.sample(items, k)
        else:
            choices: list[str] = []
            for _ in range(k // len(items)):
                choices.extend(random.sample(items, k=len(items)))
            
            if k % len(items) == 0:
                return items
            
            choices.extend(random.sample(items, k=k % len(items)))
            
            return choices

    @classmethod
    def replace(cls, template: str, symbol: str, items: list[str]) -> str | None:
        count = template.count(symbol)

        choices = cls.choices(items, count)

        for choice in choices:
            template = template.replace(symbol, choice, 1)
        return template

    @classmethod
    def replace_all(cls, template: str, items: list[str]) -> str | None:
        for symbol in brackets:
            new_message = cls.replace(template, symbol, items)
            if new_message is None:
                continue
            return new_message

        return None

    async def get_text(self, persona_info: PersonaInfo) -> str:
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

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        template = await self.get_text(persona_info)

        if not template:
            await send_msg.send_error("Please enter the template.")
            return

        await send_msg.send_text(
            "Please enter the items. If there are only spaces in the items, exit.",
            continue_handler = True
        )

        while True:
            new_message = await CommandCaller.wait_message(persona_info.namespace)
            text = await self.get_text(new_message)
            items = text.splitlines()

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