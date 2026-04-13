from fastapi import APIRouter
from app.api.v1 import auth, reports, admin

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(reports.router, prefix="/data", tags=["数据采集"])
api_router.include_router(admin.router, prefix="/admin", tags=["系统管理"])

# Also mount reports router at root level for direct access
from app.api.v1 import reports as reports_module
api_router.include_router(reports_module.router, prefix="", tags=["报表"])

# Also mount stats routes at a more accessible path
from app.api.v1 import reports as reports_module_for_stats
_ = reports_module_for_stats.router  # reference to ensure router is used
