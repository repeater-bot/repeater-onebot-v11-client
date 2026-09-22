import uvicorn
from ...client_configs import storage_configs
from .app import et_app

configs = uvicorn.Config(
    app = et_app,
    host = storage_configs.external_trigger_server.host,
    port = storage_configs.external_trigger_server.port,
    log_config = None,
)

et_server = uvicorn.Server(
    config = configs
)