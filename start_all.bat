@echo off
chcp 65001 > nul
echo ============================================
echo 云南省企业就业失业数据采集系统
echo ============================================
echo.

cd /d D:\Projects\YEP_Enterprise_Employment_System\backend
start "YEP-后端服务" cmd /k "python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

timeout /t 5 /nobreak > nul

echo.
echo ============================================
echo 系统已启动！
echo ============================================
echo.
echo  访问地址: http://127.0.0.1:8000
echo  API文档:  http://127.0.0.1:8000/docs
echo.
echo 测试账号:
echo   admin       / admin123    (系统管理员)
echo   analyst     / analyst123  (数据分析)
echo   province    / prov123456  (省级审批)
echo   city_km     / city123456  (市级审核)
echo   enterprise1 / ent123456   (企业端)
echo.
echo 注意: 关闭此窗口不会停止系统
echo       要停止系统请关闭 "YEP-后端服务" 窗口
echo ============================================
pause
