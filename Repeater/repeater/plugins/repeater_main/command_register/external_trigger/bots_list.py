from fastapi.responses import JSONResponse
from .router import root_router
from .register import register_external_trigger

@root_router.get("/bots_list")
async def external_trigger_bots_list():
    """
    External trigger bots list endpoint
    """
    bots = register_external_trigger.keys()
    return JSONResponse(
        status_code = 200,
        content = {
            "bots_list": bots
        }
    )