from nonebot.adapters.onebot.v11 import Bot

async def send_group_file(
    bot: Bot,
    group_id: str,
    url: str,
    file_name: str,
) -> str | None:
    data = {
        "group_id": group_id,
        "file": url,
        "name": file_name
    }
    response: dict = await bot.upload_group_file(**data)
    return response.get("file_id")