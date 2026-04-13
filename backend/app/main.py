import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from app.api.v1 import api_router
from app.core.database import Base, engine

# 创建所有数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="云南省企业就业失业数据采集系统",
    description="YEP Enterprise Employment System API",
    version="1.0.0"
)

# CORS配置 - 允许所有来源（因为前后端在同端口）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

# 获取前端dist目录的绝对路径
FRONTEND_DIST = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist")

@app.get("/")
def root():
    """返回前端index.html"""
    index_path = os.path.join(FRONTEND_DIST, "index.html")
    return FileResponse(index_path)

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "1.0.0"}

# 挂载静态文件目录
if os.path.exists(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")
    app.mount("/icons.svg", FileResponse(os.path.join(FRONTEND_DIST, "icons.svg")))
    app.mount("/logo.svg", FileResponse(os.path.join(FRONTEND_DIST, "logo.svg")))
    app.mount("/favicon.svg", FileResponse(os.path.join(FRONTEND_DIST, "favicon.svg")))

# 前端路由fallback - 解决Vue Router的history模式刷新404问题
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """对于所有未匹配的路径，返回前端index.html"""
    file_path = os.path.join(FRONTEND_DIST, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    # 如果文件不存在，返回index.html让Vue Router处理
    return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
