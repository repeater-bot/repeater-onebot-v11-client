# 服务端配置
from .net_config import net_config

# ==== CHAT API ==== #
CHAT_ROUTE = "/generate/chat/completion"
BREAK_CHAT_TASK_ROUTE = "/generate/chat/break"
GET_CHAT_BUFFER_ROUTE = "/generate/chat/buffer"

# ==== IMAGE API ==== #
IMAGE_ROUTE = "/generate/image/generate"

# ==== Similarity API ==== #
SIMILARITY_ROUTE = "/generate/similarity"

# ==== CONTEXT API ==== #
GET_CONTEXT_ROUTE = "/userdata/context/get"
GET_CONTEXT_PAIRS_ROUTE = "/userdata/context/get_pairs"
GET_CONTEXT_LENGTH_ROUTE = "/userdata/context/length"
ROLE_STRUCTRUE_ROUTE = "/userdata/context/structure_check/role"
INJECT_CONTEXT_ROUTE = "/userdata/context/inject"
WIHTDRAW_CONTEXT_ROUTE = "/userdata/context/withdraw"

# ==== PROMPT API ==== #
SET_PROMPT_ROUTE = "/userdata/prompt/set"
GET_PROMPT_ROUTE = "/userdata/prompt/get"
RENDER_PROMPT_ROUTE = "/userdata/prompt/render"

# ==== CONFIG API ==== #
SET_CONFIG_ROUTE = "/userdata/config/set"
GET_CONFIG_ROUTE = "/userdata/config/get"
REMOVE_CONFIG_KEY_ROUTE = "/userdata/config/delkey"

# ==== MODEL API ==== #
GET_MODEL_LIST = "/models"
PING_PROVIDER = "/ping_provider"
REFRESH = "/models_refresh"

# ==== Download User Data File ==== #
DOWNLOAD_USER_DATA_FILE_ROUTE = "/userdata/file"
PACKAGE_USER_SPACE_ROUTE = "/userdata/package_space"

# ==== Request Log API ==== #
REQUEST_LOG_ROUTE = "/request_log"
REQUEST_LOG_STREAM_ROUTE = "/request_log/stream"

# ==== RENDER API ==== #
TEXT_RENDER_ROUTE = "/render"

# ==== TEMPLATE RENDER API ==== #
TEMPLATE_RENDER = "/template/render"

# ==== VERSION API ==== #
VERSION_ROUTE = "/version"

# ==== CONFIG ==== #
REPEATER_DEBUG_MODE: bool = net_config.repeater_debug_mode # 是否开启调试模式，调试模式下，将直接返回消息内容，而不进行后端访问操作

