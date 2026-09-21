import random
import asyncio

from ...assist import PersonaInfo, SendMsg
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

    @staticmethod
    def choice(items: list[str]) -> str:
        return random.choice(items)

    @classmethod
    def replace(cls, template: str, symbol: str, items: list[str]) -> str | None:
        if template.index(symbol) == -1:
            return None

        new_message = template.replace(symbol, cls.choice(items))
        return new_message

    @classmethod
    def replace_all(cls, template: str, items: list[str]) -> str | None:
        for symbol in brackets:
            new_message = cls.replace(template, symbol, items)
            if new_message is None:
                continue
            return new_message

        return None

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        text = persona_info.message_stripped_str

        if not text:
            await send_msg.send_error("Please enter the candidate list first")
            return

        items = text.splitlines()

        while True:
            new_message = await CommandCaller.wait_message(persona_info.namespace)
            template = new_message.message_stripped_str

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
                reply = False,
                continue_handler = True
            )