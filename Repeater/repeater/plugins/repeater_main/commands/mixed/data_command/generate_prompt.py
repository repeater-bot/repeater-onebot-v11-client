from nonebot import logger
from ....assist import PersonaInfo, SendMsg
from ....cmd_info import CmdTypes
from ....command_register import(
    CommandCaller,
    CommandPackage
)
from ....storage import async_text_storage
from ....clients import PromptClient, ChatClient, ContentRole
from ._default_meta_prompt import META_PROMPT


@CommandCaller.register
class GeneratePrompt(CommandPackage):
    cmd = "generatePrompt"
    aliases = {
        "genp",
        "GENP",
        "generate_prompt",
        "Generate_Prompt",
        "GeneratePrompt",
        "GENERATE_PROMPT",
    }
    cmd_type = CmdTypes.MIXED
    description = f"""
    Let Ai generate a complete set of prompts based on the user's description,
    and automatically set to the custom prompt for the current user.

    Usage:
    ```
    /generatePrompt <description>
    ```
    """

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        message = persona_info.message_stripped_str

        user_configs = await persona_info.get_user_configs()

        meta_prompt_file_path = "prompts/generate_prompt/meta_prompt.txt"
        try:
            meta_prompt = await async_text_storage.load(path=meta_prompt_file_path)
        except Exception as e:
            logger.error(f"load meta_prompt.txt failed: {e}")
            meta_prompt = META_PROMPT
            await async_text_storage.save(path=meta_prompt_file_path, data=meta_prompt)

        chat_client = ChatClient(persona_info, user_configs)
        image_url = persona_info.get_images_url()
        chat_response = await chat_client.send_message(
            message,
            raw_message = False,
            save_context = False,
            history_messages = [],
            allow_tool_calls = False,
            image_url = image_url,
            temporary_prompt = meta_prompt
        )

        if not chat_response:
            await send_msg.send_response_check_code(chat_response, "Generate Prompt failed.")
            return

        data = chat_response.get_data()
        if data is None:
            await send_msg.send_error("Unable to process data.")
            return

        if not data.context:
            await send_msg.send_error("No prompt content generated.")
            return

        prompt_client = PromptClient(persona_info, user_configs)
        text_buffer:list[str] = []
        for buffer in data.context.context_list:
            if buffer.role == ContentRole.USER:
                text_buffer.append(buffer.content)
        text = "\n\n".join(text_buffer)
        prompt_response = await prompt_client.set_prompt(text)
        if prompt_response:
            await send_msg.send_mixed_render(
                prefix_text = "Prompt generated:",
                text_to_render = text
            )
        else:
            await send_msg.send_response_check_code(prompt_response, "Set Prompt failed")