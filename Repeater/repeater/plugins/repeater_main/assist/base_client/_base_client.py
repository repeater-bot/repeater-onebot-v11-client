import json
import httpx
from typing import (
    ClassVar,
    Iterable
)

from .client_pool import (
    ClientPool,
    ClientInfo,
    ClientTimeout,
    ClientLimits
)
from ...client_configs import (
    storage_configs,
    ClientLimits as StorageClientLimits
)
from urllib.parse import urljoin, quote
from ..namespace import Namespace
from ..persona_info import PersonaInfo
from ..user_config import UserConfigs

class BaseClient:
    _httpx_clients: ClassVar[ClientPool] = ClientPool(storage_configs.client_pool_size)
    follow_redirects: ClassVar[bool] = False
    base_router: ClassVar[str | None] = None
    timeout: ClassVar[int | float | ClientTimeout | None] = 5
    encoding: ClassVar[str] = "utf-8"

    def __init__(self, persona_info: PersonaInfo, user_configs: UserConfigs, namespace: str | Namespace | None = None):
        self._persona_info = persona_info
        self.user_configs = user_configs
        self._namespace = namespace

        client_info = ClientInfo(
            url = self.base_url,
            follow_redirects = self.follow_redirects,
            timeout = self.timeout,
            encoding = self.encoding
        )
        self.client = self._httpx_clients.get_client(client_info)
        self.__post_init__()
    
    def __post_init__(self):
        pass
    
    @property
    def backend_url(self) -> str:
        backend_url = self._get_backend_url(self.user_configs)
        return backend_url
    
    @property
    def base_url(self) -> str:
        backend_url = self.backend_url
        if self.base_router is None:
            url = urljoin(backend_url, self.base_router)
        else:
            url = backend_url
        return url
    
    def join_url(
        self,
        *urls: str,
        escape: bool = True,
        add_slashes: bool = True,
        follow_slashes: bool = False,
        safe: str | Iterable[int] = "/",
        encoding: str | None = None,
        errors: str | None = None
    ) -> str:
        return urljoin(
            self.base_url,
            self.join_url_static(
                *urls,
                add_slashes = add_slashes,
                follow_slashes = follow_slashes,
                escape = escape,
                safe = safe,
                encoding = encoding,
                errors = errors
            )
        )
    
    @staticmethod
    def join_url_static(
        *urls: str,
        escape: bool = True,
        add_slashes: bool = True,
        follow_slashes: bool = False,
        safe: str | Iterable[int] = "/",
        encoding: str | None = None,
        errors: str | None = None
    ) -> str:
        url = "/"
        for u in urls:
            if add_slashes and not u.startswith("/"):
                u = f"/{u}"
            
            if url.endswith("/") and u.startswith("/"):
                url = url.removesuffix("/")
            
            if escape:
                url = (
                    url + 
                    quote(
                        u,
                        safe = safe,
                        encoding = encoding,
                        errors = errors
                    )
                )
            else:
                url = url + u
        
        if follow_slashes and not url.endswith("/"):
            url = url + "/"
        return url
    
    @property
    def namespace(self) -> str:
        if self._namespace is not None:
            if isinstance(self._namespace, Namespace):
                return self._namespace.namespace_str
            elif isinstance(self._namespace, str):
                return self._namespace
            else:
                raise TypeError(f"Invalid type for namespace: {type(self._namespace).__name__}")
        else:
            return self._persona_info.namespace_str
    
    def _get_backend_url(self, configs: UserConfigs) -> str:
        backend_choice = configs.backend
        if backend_choice is None:
            backend_choice = storage_configs.default_backend
        
        url = storage_configs.backends[backend_choice]
        return url