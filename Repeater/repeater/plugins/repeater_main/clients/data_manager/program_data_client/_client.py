import httpx

from ....logger import logger as base_logger
from typing import (
    Any,
)
from ....assist import Response
# 服务端配置
from ....client_configs import *

from .._base_user_data_client import UserDataClient

logger = base_logger.bind(module = "ProgramData.Core")

class ProgramDataClient(UserDataClient):
    timeout = storage_configs.server_api_timeout.config
    data_type = "program"