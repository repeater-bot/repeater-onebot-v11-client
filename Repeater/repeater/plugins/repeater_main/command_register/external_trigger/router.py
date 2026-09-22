from fastapi import APIRouter
from .app import et_app

root_router = APIRouter(
    prefix="/repeater/api/external_trigger"
)