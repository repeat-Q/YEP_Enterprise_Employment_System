@echo off
chcp 65001 > nul
echo ============================================
echo 云南省企业就业失业数据采集系统
echo ============================================
echo.

cd /d D:\Projects\YEP_Enterprise_Employment_System\backend
start "YEP-Backend" cmd /k "python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

timeout /t 8 /nobreak > nul

cd /d D:\Projects\YEP_Enterprise_Employment_System\frontend\dist
start "YEP-Frontend" cmd /k "python -m http.server 8080"

timeout /t 3 /nobreak > nul

echo.
echo 系统已启动！
echo   后端API:  http://127.0.0.1:8000
echo   API文档:  http://127.0.0.1:8000/docs
echo   前端页面: http://127.0.0.1:8080
echo.
echo 测试账号:
echo   admin    / admin123    (系统管理员)
echo   analyst  / analyst123  (数据分析)
echo   province / prov123456  (省级审批)
echo   city_km  / city123456  (市级审核)
echo   enterprise1 / ent123456 (企业端)
echo.
echo 注意: 后端和前端窗口已在新窗口中运行
pause