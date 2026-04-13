@echo off
echo 启动云南省企业就业失业数据采集系统...
echo.
echo 后端: http://localhost:8000
echo 前端: http://localhost:5173
echo API文档: http://localhost:8000/docs
echo.
start "YEP-Backend" cmd /k "cd /d D:\Projects\YEP_Enterprise_Employment_System\backend && python -m uvicorn app.main:app --reload --port 8000"
timeout /t 3
start "YEP-Frontend" cmd /k "cd /d D:\Projects\YEP_Enterprise_Employment_System\frontend && npm run dev"
echo 启动完成，请稍候浏览器自动打开...
timeout /t 5
start http://localhost:5173
