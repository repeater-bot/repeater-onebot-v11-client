from ....client_configs import *
from ....assist import Response
from ....logger import logger as base_logger
from .._base_user_data_client import UserDataClient

logger = base_logger.bind(module = "Prompt.Core")

class PromptClient(UserDataClient):
    timeout = storage_configs.server_api_timeout.prompt
    data_type = "prompt"
    
    # region set prompt  
    async def set_prompt(self, prompt: str) -> Response[None]:
        logger.info("Setting prompt")
        response = await self.client.put(
            self.join_url_static(SET_PROMPT_ROUTE, self.namespace_str),
            data={
                "prompt": prompt
            }
        )
        return Response(response)
    # endregion
    
    # region get prompt  
    async def get_prompt(self) -> Response[str]:
        logger.info("Getting prompt")
        response = await self.client.get(
            self.join_url_static(GET_PROMPT_ROUTE, self.namespace_str)
        )
        return Response(response)
    
    def get_prompt_url(self) -> str:
        return self.join_url(GET_PROMPT_ROUTE, f"{self.namespace_str}.md")
    # endregion

    # region render prompt  
    async def render_prompt(self, model_id: str | None = None) -> Response[str]:
        logger.info("Rendering prompt")
        response = await self.client.get(
            self.join_url_static(RENDER_PROMPT_ROUTE, self.namespace_str),
            params = {
                "model_id": model_id,
                "username": self._persona_info.nickname,
                "nickname": self._persona_info.display_name,
                "age": self._persona_info.age,
                "gender": self._persona_info.gender,
            }
        )
        return Response(response)
    # endregion

    # region render prompt file
    def render_prompt_file_url(self) -> str:
        return self.join_url(RENDER_PROMPT_ROUTE, f"{self.namespace_str}.md")
    # endregion