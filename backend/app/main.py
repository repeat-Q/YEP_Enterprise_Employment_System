from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import api_router
from app.core.database import Base, engine

# 创建所有数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="云南省企业就业失业数据采集系统",
    description="YEP Enterprise Employment System API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "云南省企业就业失业数据采集系统 API", "version": "1.0.0", "docs": "/docs"}
