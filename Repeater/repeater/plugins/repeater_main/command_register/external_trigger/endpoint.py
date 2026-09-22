from fastapi import HTTPException
from nonebot.adapters.onebot.v11 import Message
from pkg_resources import to_filename
from ...assist import Namespace
from .router import root_router
from .request import ExternalTriggerRequest
from .response import ExternalTriggerResponse
from .register import register_external_trigger
from .make_message_event import make_message_event

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

    message = Message(request.message)
    args = Message(request.args)
    namespace = Namespace.from_str(request.namespace)

    event = make_message_event(
        self_id = int(request.bot_id),
        namespace = namespace,
        message = message,
        message_id = request.message_id,
    
        font = request.font,
        nickname = request.nickname,
        sex = request.sex,
        age = request.age,
        card = request.card,
        area = request.area,
        level = request.level,
        role = request.role,
        title = request.title,
        to_me = request.to_me,
        sub_type = request.sub_type,
    )

    results, retcode = await callback(
        request.handler,
        event,
        args
    )

    return ExternalTriggerResponse(
        messages = [str(result) for result in results],
        retcode = retcode
    )