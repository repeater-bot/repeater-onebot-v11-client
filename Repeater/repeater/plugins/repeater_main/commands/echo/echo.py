from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ...cmd_info import CmdTypes
from ...assist import PersonaInfo, SendMsg

@CommandCaller.register
class Echo(CommandPackage):
    cmd = "echo"
    aliases = {
        "Echo",
        "ECHO"
    }
    cmd_type = CmdTypes.ECHO
    description = f"""
    Echo a message.
    If not arguments, echo the last message.

    Usage:
    ```
    /{cmd} [message]
    ```
    """

    # 定义一个主逻辑函数
    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):

        # 判断命令输入是否为空
        if not persona_info:
            # 如果为空，则等待用户输入消息

            # 输出一条消息，告诉用户在等待消息输入
            await send_msg.send_prompt("Wait for input message...", continue_handler = True)

            # 等待用户输入一条消息
            new_message = await CommandCaller.wait_message(persona_info.namespace)

            # 将用户输入的消息放进 message 中
            message = new_message.message
        else:
            # 如果不为空，直接从命令参数提取消息
            message =  persona_info.message

        # 将消息发送出去
        await send_msg.send_any(message, reply = False)