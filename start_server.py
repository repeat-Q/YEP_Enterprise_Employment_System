import subprocess
import time
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("正在启动YEP系统后端...")
print("=" * 50)

# 启动后端
proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
    cwd=r"D:\Projects\YEP_Enterprise_Employment_System\backend",
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

print(f"后端进程已启动 (PID: {proc.pid})")
print("等待服务启动...")

# 等待并检查
for i in range(10):
    time.sleep(1)
    poll = proc.poll()
    if poll is None:
        print(f"✓ 后端服务正在运行: http://127.0.0.1:8000")
        print(f"✓ API文档: http://127.0.0.1:8000/docs")
        print("=" * 50)
        print("\n按 Ctrl+C 停止服务")
        break
else:
    print("✗ 后端启动失败")
    proc.terminate()
