from ...assist import PersonaInfo, SendMsg
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from .serial import Serial
from ...clients import SimilarityClient

@CommandCaller.register
class Similar(CommandPackage):
    cmd = "similar"
    aliases = {
        "sim",
        "SIM",
        "Similar",
        "SIMILAR",
    }
    cmd_type = CmdTypes.CONTROL
    description = f"""
    Semantic judgement of whether two sentences are similar
    One message per line, and the label must be exclusive to the entire line
    If the similarity is above the threshold, serial is called to perform the part after "similar:".
    If the similarity is below the threshold, serial is called to perform the section after "dissimilar:".

    Usage: 
    ```
    /{cmd} threshold
    first text
    second text
    similar:
      ...
    dissimilar:
      ...
    ```
    """

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        lines = persona_info.message_cqcode.splitlines()

        messages: list[str] = []
        similar_code: list[str] = []
        dissimilar_code: list[str] = []
        
        now_code: bool | None = None
        for line in lines:
            match line:
                case "similar:":
                    now_code = True
                case "dissimilar:":
                    now_code = False
                case _:
                    if now_code is None:
                        messages.append(
                            line.strip()
                        )
                    elif now_code:
                        similar_code.append(
                            line.removeprefix(" " * 2)
                        )
                    else:
                        dissimilar_code.append(
                            line.removeprefix(" " * 2)
                        )

        if len(messages) > 3:
            await send_msg.send_error(
                "Message too long"
            )
            send_msg.break_handler()
        elif len(messages) < 3:
            await send_msg.send_error(
                "Message too short"
            )
            send_msg.break_handler()
        
        try:
            threshold = float(messages[0])
        except ValueError:
            await send_msg.send_error(
                "Threshold must be a float number"
            )
        configs = await persona_info.get_user_configs()
        client = SimilarityClient(persona_info, configs)
        response = await client.similarity(
            messages[1],
            messages[2],
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

        if similarity > threshold:
            code = similar_code
        else:
            code = dissimilar_code

        execable_code = persona_info.make_message(
            "\n".join(code)
        )

        await CommandCaller.horizontal_call(
            package = Serial,
            persona_info = persona_info.copy(
                args = execable_code
            ),
            send_msg = send_msg,
        )
