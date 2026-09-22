from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Bot
from .caller import CommandCaller

DRIVER = get_driver()

@DRIVER.on_startup
async def on_startup():
    await CommandCaller.on_startup()

@DRIVER.on_shutdown
async def on_shutdown():
    await CommandCaller.on_shutdown()

@DRIVER.on_bot_connect
async def on_bot_connect(bot: Bot):
    await CommandCaller.on_bot_connect(bot)

@DRIVER.on_bot_disconnect
async def on_bot_disconnect(bot: Bot):
    await CommandCaller.on_bot_disconnect(bot)