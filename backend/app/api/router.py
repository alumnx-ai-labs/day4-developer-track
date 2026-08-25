from fastapi import APIRouter

from .requests import router as requests_router

router = APIRouter()
router.include_router(requests_router)