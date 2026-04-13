from fastapi import APIRouter
from app.api.v1 import auth, reports, admin

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(reports.router, prefix="/data", tags=["数据采集"])
api_router.include_router(admin.router, prefix="/admin", tags=["系统管理"])
