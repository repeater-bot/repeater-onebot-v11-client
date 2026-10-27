from uuid import UUID

from ...client_configs import *
from typing import ClassVar
from ...assist import Response, PersonaInfo, UserConfigs
from ...cmd_info import CmdTypes
from ._nexus_response import (
    NexusUploadResponse,
    NexusDownloadResponse
)
from ...assist import Namespace, BaseClient
from ...logger import logger as base_logger
from ._branch_info import BranchInfo

logger = base_logger.bind(module = "UserData.Core")

class UserDataClient(BaseClient):
    timeout = storage_configs.server_api_timeout.data_manager
    data_type: ClassVar[str] = ""
    
    @property
    def namespace_str(self) -> str:
        if self._namespace is None:
            return self._persona_info.namespace_str
        elif isinstance(self._namespace, Namespace):
            return self._namespace.namespace_str
        elif isinstance(self._namespace, str):
            return self._namespace
        else:
            raise TypeError(f"namespace must be str or Namespace, but got {type(self._namespace)}")

    # region change subsession
    async def change_branch(self, new_branch_id: str) -> Response[None]:
        response = await self.client.put(
            self.join_url_static("userdata", self.data_type, "change", self._persona_info.namespace_str),
            data={
                "new_branch_id": new_branch_id
            }
        )
        return Response(response)
    # endregion

    # region Delete
    async def delete(self) -> Response[None]:
        response = await self.client.delete(
            self.join_url_static("userdata", self.data_type, "delete", self._persona_info.namespace_str)
        )
        return Response(response)
    # endregion

    # region get active branch
    async def get_active_branch(self) -> Response[str]:
        response = await self.client.get(
            self.join_url_static("userdata", self.data_type, "active", self._persona_info.namespace_str)
        )
        return Response(response)

    # region get branch list
    async def get_branch_list(self) -> Response[list[str]]:
        response = await self.client.get(
            self.join_url_static("userdata", self.data_type, "branchs", self._persona_info.namespace_str)
        )
        return Response(response)

    # region clone
    async def clone(self, dst_branch_id: str) -> Response[None]:
        response = await self.client.put(
            self.join_url_static("userdata", self.data_type, "clone", self._persona_info.namespace_str),
            data={
                "dst_branch_id": dst_branch_id
            }
        )
        return Response(response)
    # endregion

    # region clone from
    async def clone_from(self, src_branch_id: str) -> Response[None]:
        response = await self.client.put(
            self.join_url_static("userdata", self.data_type, "clone_from", self._persona_info.namespace_str),
            data={
                "src_branch_id": src_branch_id
            }
        )
        return Response(response)
    # endregion

    # region bind
    async def bind(self, dst_branch_id: str) -> Response[None]:
        response = await self.client.put(
            self.join_url_static("userdata", self.data_type, "bind", self._persona_info.namespace_str),
            data={
                "dst_branch_id": dst_branch_id
            }
        )
        return Response(response)
    # endregion

    # region bind from
    async def bind_from(self, src_branch_id: str) -> Response[None]:
        response = await self.client.put(
            self.join_url_static("userdata", self.data_type, "bind_from", self._persona_info.namespace_str),
            data={
                "src_branch_id": src_branch_id
            }
        )
        return Response(response)
    # endregion

    # region branch info
    async def branch_info(self) -> Response[BranchInfo]:
        response = await self.client.get(
            self.join_url_static("userdata", self.data_type, "info", self._persona_info.namespace_str),
        )
        return Response(
            response,
            model = BranchInfo
        )
    # endregion

    # region upload to nexus
    async def upload_to_nexus(self, timeout: int | None = None) -> Response[NexusUploadResponse]:
        response = await self.client.post(
            self.join_url_static("userdata", self._persona_info.namespace_str, "single", self.data_type),
            json = {
                "timeout": timeout
            }
        )
        return Response(
            httpx_response = response,
            model = NexusUploadResponse
        )
    # endregion
    
    # region download from nexus
    async def download_from_nexus(self, uuid: str) -> Response[NexusDownloadResponse]:
        try:
            resource_uuid = UUID(uuid)
        except ValueError:
            raise ValueError("UUID is not valid")
        
        response = await self.client.post(
            self.join_url_static("userdata", self._persona_info.namespace_str, "single", self.data_type),
            json = {
                "id": str(resource_uuid)
            }
        )
        return Response(
            httpx_response = response,
            model = NexusDownloadResponse
        )
    # endregion