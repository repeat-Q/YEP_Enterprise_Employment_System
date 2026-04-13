@echo off
echo ============================================
echo 启动云南省企业就业失业数据采集系统（生产模式）
echo ============================================

echo.
echo [1/3] 检查后端服务...
powershell -Command "try { Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/health' -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop | Out-Null; Write-Host '[OK] Backend running on port 8000' } catch { Write-Host '[WARN] Backend not responding, trying to start...' }"

echo.
echo [2/3] 启动前端静态服务...
start "YEP-Frontend-Static" cmd /k "cd /d D:\Projects\YEP_Enterprise_Employment_System\frontend\dist && python -m http.server 8080"
timeout /t 3 /nobreak > nul

echo.
echo [3/3] 检查前端服务...
powershell -Command "try { Invoke-WebRequest -Uri 'http://127.0.0.1:8080/' -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop | Out-Null; Write-Host '[OK] Frontend running on http://127.0.0.1:8080' } catch { Write-Host '[WARN] Frontend may not be ready yet' }"

echo.
echo ============================================
echo 系统已启动！
echo   后端API: http://127.0.0.1:8000
echo   API文档: http://127.0.0.1:8000/docs
echo   前端页面: http://127.0.0.1:8080
echo ============================================
echo.
echo 提示: 所有服务窗口已在新窗口中运行
pause