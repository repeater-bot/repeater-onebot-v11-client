import base64

from ...client_configs import *
from ...assist import Response, BaseClient
from .request import DestinationRequest, EditRequest, CopyRangeRequest
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
            path: str,
            start: int | None = None,
            length: int | None = None,
            headers: dict[str, str] | None = None
        ) -> Response[bytes]:
        request_headers = dict(headers or {})
        if start is None and length is not None:
            start = 0
        if start is not None:
            end = "" if length is None else str(start + length - 1)
            request_headers["Range"] = f"bytes={start}-{end}"

        response = await self.client.get(
            url = self.join_url(WORKSPACE_GET_FILE_ROUTE, path),
            headers = request_headers or None
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

    def file_url(
            self,
            path: str
        ) -> str:
        return self.join_url(WORKSPACE_GET_FILE_ROUTE, path)

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

    async def hash(
            self,
            path: str,
            algorithm: str = "sha256"
        ) -> Response:
        response = await self.client.get(
            url = self.join_url(WORKSPACE_HASH_ROUTE, path),
            params = {
                "algorithm": algorithm,
            }
        )
        return Response(
            httpx_response = response
        )

    async def du(
            self,
            path: str
        ) -> Response:
        response = await self.client.get(
            url = self.join_url(WORKSPACE_DU_ROUTE, path)
        )
        return Response(
            httpx_response = response
        )

    async def tree(
            self,
            path: str,
            max_depth: int = -1
        ) -> Response:
        response = await self.client.get(
            url = self.join_url(WORKSPACE_TREE_ROUTE, path),
            params = {
                "max_depth": max_depth,
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

    async def is_file(
            self,
            path: str
        ) -> Response:
        response = await self.client.get(
            url = self.join_url(WORKSPACE_IS_FILE_ROUTE, path)
        )
        return Response(
            httpx_response = response
        )

    async def is_dir(
            self,
            path: str
        ) -> Response:
        response = await self.client.get(
            url = self.join_url(WORKSPACE_IS_DIR_ROUTE, path)
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

    async def append(
            self,
            path: str,
            data: bytes,
            content_type: str = "application/octet-stream"
        ) -> Response:
        response = await self.client.post(
            url = self.join_url(WORKSPACE_APPEND_ROUTE, path),
            content = data,
            headers = {
                "Content-Type": content_type,
            }
        )
        return Response(
            httpx_response = response
        )

    async def truncate(
            self,
            path: str,
            size: int
        ) -> Response:
        response = await self.client.post(
            url = self.join_url(WORKSPACE_TRUNCATE_ROUTE, path),
            params = {
                "size": size,
            }
        )
        return Response(
            httpx_response = response
        )

    async def touch(
            self,
            path: str
        ) -> Response:
        response = await self.client.post(
            url = self.join_url(WORKSPACE_TOUCH_ROUTE, path)
        )
        return Response(
            httpx_response = response
        )

    async def edit(
            self,
            path: str,
            data: bytes,
            start: int,
            end: int
        ) -> Response:
        response = await self.client.post(
            url = self.join_url(WORKSPACE_EDIT_ROUTE, path),
            json = EditRequest(
                start = start,
                end = end,
                data = base64.b64encode(data).decode()
            ).model_dump(exclude_none = True)
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

    async def copy_range(
            self,
            path: str,
            destination: str,
            start: int,
            end: int
        ) -> Response:
        response = await self.client.post(
            url = self.join_url(WORKSPACE_COPY_RANGE_ROUTE, path),
            json = CopyRangeRequest(
                destination = destination,
                start = start,
                end = end
            ).model_dump(exclude_none = True)
        )
        return Response(
            httpx_response = response
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
