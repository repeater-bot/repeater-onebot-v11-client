from fastapi import APIRouter, Request, HTTPException, Depends
from .config import external_trigger_config

def check_admin_api_key(request: Request):

    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="No authorization token")
    elif not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid bearer format")
    elif token.removeprefix("Bearer ") != external_trigger_config.external_trigger_token:
        raise HTTPException(status_code=401, detail="Invalid authorization token")
    return token

root_router = APIRouter(
    prefix="/repeater/api/external_trigger",
    tags = ["external_trigger"],
    dependencies = [Depends(check_admin_api_key)],
)