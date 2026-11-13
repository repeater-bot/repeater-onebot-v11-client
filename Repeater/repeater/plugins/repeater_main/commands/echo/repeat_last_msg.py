from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ...cmd_info import CmdTypes
from ...assist import PersonaInfo, SendMsg

@CommandCaller.register
class RepeatLastMsg(CommandPackage):
    cmd = "repeatLastMsg"
    aliases = {
        "rlm",
        "RLM",
        "repeat_last_msg",
        "Repeat_Last_Msg",
        "RepeatLastMsg",
        "REPEAT_LAST_MSG"
    }
    cmd_type = CmdTypes.ECHO
    description = f"""
    Repeats the last message sent to the bot.

    Usage:
    ```
    /{cmd}
    ```
    """

    # 定义一个主逻辑函数
    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):

        last_messages = await persona_info.from_message_history(persona_info.scene, count = 1)
        if not last_messages:
            await send_msg.send_error("No message found.")
            return

        message = last_messages[0]

        # 将消息发送出去
        await send_msg.send_any(message.message, reply = False)