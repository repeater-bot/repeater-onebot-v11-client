from ...client_configs import *
from ...assist import Response, BaseClient
from .request import DestinationRequest
from .response import (
    FileInfo,
    DeleteResult,
    MoveResult,
    CopyResult
)

class WorkspaceClient(BaseClient):
    timeout = storage_configs.server_api_timeout.workspace

    async def get_file(
            self,
            path: str
        ) -> Response[bytes]:
        response = await self.client.get(
            url = self.join_url(WORKSPACE_GET_FILE_ROUTE, path)
        )
        return Response(
            httpx_response = response
        )

    async def get_text(
            self,
            path: str,
            text_encoding: str = "utf-8"
        ) -> Response[str]:
        response = await self.client.get(
            url = self.join_url(WORKSPACE_GET_TEXT_ROUTE, path),
            params = {
                "text_encoding": text_encoding,
            }
        )
        return Response(
            httpx_response = response
        )

    async def list_dir(
            self,
            path: str = "",
            recursive: bool = False
        ) -> Response:
        response = await self.client.get(
            url = self.join_url(WORKSPACE_LIST_DIR_ROUTE, path),
            params = {
                "recursive": recursive,
            }
        )
        return Response(
            httpx_response = response
        )

    async def glob(
            self,
            path: str,
            pattern: str,
            recursive: bool = False
        ) -> Response:
        response = await self.client.get(
            url = self.join_url(WORKSPACE_GLOB_ROUTE, path),
            params = {
                "pattern": pattern,
                "recursive": recursive,
            }
        )
        return Response(
            httpx_response = response
        )

    async def rematch(
            self,
            path: str,
            pattern: str
        ) -> Response:
        response = await self.client.get(
            url = self.join_url(WORKSPACE_REMATCH_ROUTE, path),
            params = {
                "pattern": pattern,
            }
        )
        return Response(
            httpx_response = response
        )

    async def get_info(
            self,
            path: str
        ) -> Response[FileInfo]:
        response = await self.client.get(
            url = self.join_url(WORKSPACE_GET_INFO_ROUTE, path)
        )
        return Response(
            httpx_response = response,
            model = FileInfo
        )

    async def exists(
            self,
            path: str
        ) -> Response:
        response = await self.client.get(
            url = self.join_url(WORKSPACE_EXISTS_ROUTE, path)
        )
        return Response(
            httpx_response = response
        )

    async def write_file(
            self,
            path: str,
            data: bytes,
            filename: str | None = None,
            content_type: str = "application/octet-stream"
        ) -> Response:
        response = await self.client.post(
            url = self.join_url(WORKSPACE_WRITE_FILE_ROUTE, path),
            files = {
                "file": (
                    filename or path.rstrip("/").rsplit("/", 1)[-1],
                    data,
                    content_type
                )
            }
        )
        return Response(
            httpx_response = response
        )

    async def mkdir(
            self,
            path: str
        ) -> Response:
        response = await self.client.post(
            url = self.join_url(WORKSPACE_MKDIR_ROUTE, path)
        )
        return Response(
            httpx_response = response
        )

    async def move(
            self,
            path: str,
            destination: str
        ) -> Response[MoveResult]:
        response = await self.client.post(
            url = self.join_url(WORKSPACE_MOVE_ROUTE, path),
            json = DestinationRequest(
                destination = destination
            ).model_dump(exclude_none = True)
        )
        return Response(
            httpx_response = response,
            model = MoveResult
        )

    async def copy(
            self,
            path: str,
            destination: str
        ) -> Response[CopyResult]:
        response = await self.client.post(
            url = self.join_url(WORKSPACE_COPY_ROUTE, path),
            json = DestinationRequest(
                destination = destination
            ).model_dump(exclude_none = True)
        )
        return Response(
            httpx_response = response,
            model = CopyResult
        )

    async def delete(
            self,
            path: str,
            recursive: bool = False
        ) -> Response[DeleteResult]:
        response = await self.client.delete(
            url = self.join_url(WORKSPACE_DELETE_ROUTE, path),
            params = {
                "recursive": recursive,
            }
        )
        return Response(
            httpx_response = response,
            model = DeleteResult
        )
