import sys
from nonebot import logger
from nonebot import get_plugin_config
from nonebot.log import logger_id, default_filter
from pydantic import BaseModel, Field
from ._level import Level

class LoggerConfig(BaseModel):
    repeater_logger_level: Level = Field(Level.INFO)
    repeater_logger_format: str = Field("<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan><u>{name}</u></cyan>:<cyan><u>{extra[module]}</u></cyan> | <level>{message}</level>")
    repeater_logger_path: str = Field("logs/repeater-log-{time:YYYY-MM-DD-HH-mm-ss}.log")
    repeater_logger_enable_queue: bool = Field(True)
    repeater_logger_delay: bool = Field(True)
    repeater_logger_rotation: str = Field("100 MB")
    repeater_logger_retention: str = Field("1 month")
    repeater_logger_compression: str = Field("zip")

logger_config = get_plugin_config(LoggerConfig)

logger.remove(logger_id)

# console
console_logger_id = logger.add(
    sys.stdout,
    diagnose = False,
    filter = default_filter,
    level = logger_config.repeater_logger_level.value,
    format = logger_config.repeater_logger_format,
    enqueue = logger_config.repeater_logger_enable_queue,
)

# file
file_logger_id = logger.add(
    logger_config.repeater_logger_path,
    colorize = False,
    diagnose = False,
    filter = default_filter,
    level = logger_config.repeater_logger_level.value,
    format = logger_config.repeater_logger_format,
    enqueue = logger_config.repeater_logger_enable_queue,
    delay = logger_config.repeater_logger_delay,
    rotation = logger_config.repeater_logger_rotation,
    retention = logger_config.repeater_logger_retention,
    compression = logger_config.repeater_logger_compression
)

logger.configure(
    extra={
        "module": "[System]"
    }
)