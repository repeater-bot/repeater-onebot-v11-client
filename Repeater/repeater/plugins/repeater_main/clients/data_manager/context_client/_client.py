import httpx

from ....client_configs import *
from ....assist import PersonaInfo, Response, http_transport
from ....logger import logger as base_logger
from ._response import (
    WithdrawResponse,
    ContextTotalLengthResponse,
    RoleStructureCheckerResponse,
    ContextPairsResponse
)
from .._base_user_data_client import UserDataClient
from ...content_unit import ContentUnit

logger = base_logger.bind(module = "Context.Core")

class ContextClient(UserDataClient):
    timeout = storage_configs.server_api_timeout.context
    data_type = "context"
    
    # region inject context
    async def inject_context(
            self,
            content_unit: ContentUnit,
        ) -> Response[None]:
        logger.info("Injecting {role} context", role = content_unit.role)
        response = await self.client.post(
            self.join_url_static(INJECT_CONTEXT_ROUTE, self.namespace_str),
            json = content_unit.model_dump(),
        )
        return Response(response)
    # endregion
    
    # region withdraw
    async def withdraw(self, context_pair_num: int = 1, paired: bool = True) -> Response[WithdrawResponse]:
        logger.info("Withdrawing context")
        response = await self.client.post(
            self.join_url_static(WIHTDRAW_CONTEXT_ROUTE, self.namespace_str),
            data={
                "context_pair_num": context_pair_num,
                "paired": paired
            }
        )
        return Response(
            response,
            model = WithdrawResponse
        )
    # endregion

    # region get context total length
    async def get_context_total_length(self) -> Response[ContextTotalLengthResponse]:
        logger.info("Getting context total length")
        response = await self.client.get(
            self.join_url_static(GET_CONTEXT_LENGTH_ROUTE, self.namespace_str)
        )
        return Response(
            response,
            model = ContextTotalLengthResponse
        )
    # endregion

    # region get context
    async def get_context(self) -> Response[list[ContentUnit]]:
        logger.info("Getting context")
        response = await self.client.get(
            self.join_url_static(GET_CONTEXT_ROUTE, self.namespace_str)
        )
        data = response.json()
        if isinstance(data, list):
            return Response(
                response,
                parsed_data = [ContentUnit(**data) for data in data]
            )
        else:
            return Response(response)

    # region get context
    async def get_context_pairs(self) -> Response[ContextPairsResponse]:
        logger.info("Getting context pairs")
        response = await self.client.get(
            self.join_url_static(GET_CONTEXT_PAIRS_ROUTE, self.namespace_str)
        )
        return Response(
            httpx_response = response,
            model = ContextPairsResponse
        )
    
    def get_context_url(self) -> str:
        return self.join_url(GET_CONTEXT_ROUTE, f"{self._persona_info.namespace_str}.json")
    # endregion

    # region check role structure
    async def check_role_structure(self) -> Response[RoleStructureCheckerResponse]:
        logger.info("Checking role structure")
        response = await self.client.get(
            self.join_url_static(ROLE_STRUCTRUE_ROUTE, self.namespace_str)
        )
        return Response(
            response,
            model = RoleStructureCheckerResponse
        )
    # endregion