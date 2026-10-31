from fastapi import HTTPException, Request
from nonebot.adapters.onebot.v11 import Message
from ...assist import Namespace
from .router import root_router
from .request import ExternalTriggerRequest
from .response import ExternalTriggerResponse
from .register import register_external_trigger
from .make_message_event import make_message_event
from .config import external_trigger_config

@root_router.post("/call")
async def external_trigger_call(
    request: ExternalTriggerRequest,
    fastapi_request: Request
):
    """
    External trigger call endpoint
    """
    # TODO: Enable this feature later.
    # token = fastapi_request.headers.get("Authorization")
    # if not token:
    #     raise HTTPException(status_code=401, detail="No authorization token")
    # elif not token.startswith("Bearer "):
    #     raise HTTPException(status_code=401, detail="Invalid bearer format")
    # elif token.removeprefix("Bearer ") != external_trigger_config.external_trigger_token:
    #     raise HTTPException(status_code=401, detail="Invalid authorization token")
    
    error: BaseException | None = None
    results: list[Message] = []
    rendered_texts: list[str] = []
    retcode: int = 1
    try:
        callback = register_external_trigger.get(request.bot_id)

        if callback is None:
            raise HTTPException(
                status_code = 404,
                detail = "Bot is not registered"
            )

        message = Message(request.message)
        if request.args is None:
            args = None
        else:
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

        result = await callback(
            handler = request.handler,
            event = event,
            args = args,
            output = request.output
        )
        results = result.messages
        rendered_texts = result.rendered_texts
        retcode = result.retcode
    except BaseException as e:
        error = e

    return ExternalTriggerResponse(
        messages = [str(result) for result in results],
        rendered_texts = rendered_texts,
        error = f"{error.__class__.__name__}: {str(error)}" if error is not None else None,
        retcode = retcode
    )