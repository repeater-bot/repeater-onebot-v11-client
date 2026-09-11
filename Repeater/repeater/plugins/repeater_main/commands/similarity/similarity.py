from ...assist import PersonaInfo, SendMsg
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ...clients import SimilarityClient
from ..._adaptation_info import __adaptation__


@CommandCaller.register
class Similarity(CommandPackage):
    cmd = "similarity"
    aliases = {
        "simi",
        "SIMI",
        "Similarity",
        "SIMILARITY",
    }
    cmd_type = CmdTypes.SIMILARITY
    description = f"""
    Calculate the similarity of two sentences.

    Usage:
    ```
    /{cmd}
    text1:
      ...
    text2:
      ...
    ```
    """

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        lines = persona_info.message_cqcode.splitlines()

        first_text: list[str] = []
        second_text: list[str] = []
        
        now_code: bool | None = None
        for line in lines:
            match line:
                case "first_text:":
                    now_code = True
                case "second_text:":
                    now_code = False
                case _:
                    if now_code is None:
                        pass
                    elif now_code:
                        first_text.append(
                            line.removeprefix(" " * 2)
                        )
                    else:
                        second_text.append(
                            line.removeprefix(" " * 2)
                        )
        
        configs = await persona_info.get_user_configs()
        client = SimilarityClient(persona_info, configs)
        response = await client.similarity(
            first_text = "\n".join(first_text),
            second_text = "\n".join(second_text),
        )

        if not response:
            await send_msg.send_response(
                response,
                "Similarity API Response Error"
            )
            send_msg.break_handler()

        data = response.get_data()
        if not data:
            await send_msg.send_error(
                "Similarity API Data is Invalid"
            )
            send_msg.break_handler()

        similarity = data.similarity

        await send_msg.send_text(
            f"Similarity: {similarity:.2f}"
        )