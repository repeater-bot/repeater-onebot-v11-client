from __future__ import annotations

import sys

from typing import Generic, TypeVar, Type, Any
from httpx import Response as HTTPXResponse
from pydantic import BaseModel
from .error_response import ErrorResponse
from .exception_info import ExceptionInfo

T_Response = TypeVar("T_Response")

class Response(Generic[T_Response]):
    def __init__(
            self,
            httpx_response: HTTPXResponse | None = None,
            model: Type[T_Response] | None = None,
            parsed_data: T_Response | None = None,
        ):
        self._httpx_response = httpx_response
        self._model = model
        self._parsed_data = parsed_data
        self._exception_info: ExceptionInfo | None = None
        self.record_exception()
    
    @property
    def initialized(self) -> bool:
        return self._httpx_response is not None
    
    @property
    def code(self) -> int:
        if self._httpx_response is None:
            raise ValueError("response not initialized")
        return self._httpx_response.status_code

    @property
    def text(self) -> str:
        if self._httpx_response is None:
            raise ValueError("response not initialized")
        return self._httpx_response.text
    
    @property
    def content(self) -> bytes:
        if self._httpx_response is None:
            raise ValueError("response not initialized")
        return self._httpx_response.content
    
    @property
    def exception_info(self) -> ExceptionInfo | None:
        return self._exception_info
    
    def record_exception(self):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        self._exception_info = ExceptionInfo(
            exc_type,
            exc_value,
            exc_traceback
        )
    
    def json(self) -> Any:
        if self._httpx_response is None:
            raise ValueError("response not initialized")
        return self._httpx_response.json()
    
    def get_data(self) -> T_Response | None:
        if self._httpx_response is None:
            raise ValueError("response not initialized")
        
        if self._parsed_data is not None:
            return self._parsed_data
        
        if self._model is not None:
            if issubclass(self._model, BaseModel):
                data: Any = self.json()
                return self._model(**data)
        
        return None
    
    def get_error(self) -> ErrorResponse | None:
        if self.code >= 400:
            try:
                return ErrorResponse(**self.json())
            except Exception:
                return None
    
    def to_error(self) -> Response[ErrorResponse]:
        if self._httpx_response is None:
            raise ValueError("response not initialized")
        return Response(
            httpx_response=self._httpx_response,
            model=ErrorResponse,
        )

    def __bool__(self) -> bool:
        if self.initialized:
            return self.code == 200
        return False