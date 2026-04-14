@echo off
chcp 65001 > nul
title YEP系统启动器

echo.
echo ============================================
echo    云南省企业就业失业数据采集系统
echo ============================================
echo.

echo [提示] 使用 Python 启动脚本更稳定
echo.
echo 选项:
echo   1 - 使用 Python 启动 (推荐)
echo   2 - 直接启动后端
echo   Q - 退出
echo.
choice /c 12Q /n /m "请选择: "

if errorlevel 3 exit
if errorlevel 2 goto direct
if errorlevel 1 goto python

:python
echo.
echo [1/2] 正在启动后端服务...
start "YEP-后端服务" cmd /k "python start_server.py"
goto end

:direct
echo.
echo [1/1] 正在启动后端服务...
cd /d D:\Projects\YEP_Enterprise_Employment_System\backend
start "YEP-后端服务" cmd /k "python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

:end
echo.
echo ============================================
echo    系统已启动！
echo ============================================
echo.
echo    访问地址: http://127.0.0.1:8000
echo    API文档:  http://127.0.0.1:8000/docs
echo.
echo    测试账号:
echo      admin       / admin123    (系统管理员)
echo      analyst     / analyst123  (数据分析)
echo      province    / prov123456  (省级审批)
echo      city_km     / city123456  (市级审核)
echo      enterprise1 / ent123456   (企业端)
echo.
echo ============================================
pause
