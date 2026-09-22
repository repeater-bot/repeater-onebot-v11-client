from fastapi import HTTPException
from nonebot.adapters.onebot.v11 import Message
from .router import root_router
from .request import ExternalTriggerRequest
from .response import ExternalTriggerResponse
from .register import register_external_trigger

@root_router.post("/call")
async def external_trigger_call(request: ExternalTriggerRequest):
    """
    External trigger call endpoint
    """
    callback = register_external_trigger.get(request.bot_id)

    if callback is None:
        raise HTTPException(
            status_code = 404,
            detail = "Bot is not registered"
        )

    args = Message(request.args)

    results, retcode = await callback(request.handler, request.event_data, args)

    return ExternalTriggerResponse(
        messages = [str(result) for result in results],
        retcode = retcode
    )