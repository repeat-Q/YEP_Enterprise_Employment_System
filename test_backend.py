import urllib.request
import json

BASE = "http://127.0.0.1:8000/api/v1"

print("=== 后端API完整测试 ===")

# 1. 登录
req = urllib.request.Request(
    f"{BASE}/auth/login",
    data=json.dumps({"username": "admin", "password": "admin123"}).encode(),
    headers={"Content-Type": "application/json"}
)
resp = urllib.request.urlopen(req, timeout=10)
token = json.loads(resp.read())["access_token"]
print(f"1. 登录: OK")

# 2. 报表列表
req = urllib.request.Request(
    f"{BASE}/admin/reports",
    headers={"Authorization": f"Bearer {token}"}
)
resp = urllib.request.urlopen(req, timeout=10)
data = json.loads(resp.read())
total_reports = data.get("total", 0) if isinstance(data, dict) else len(data)
print(f"2. 报表列表: OK, 总数={total_reports}")

# 3. 新建报表
report_data = {
    "enterprise_id": 1,
    "report_year": 2026,
    "report_month": 4,
    "period_type": "monthly",
    "current_employed": 50,
    "new_employed": 5,
    "lost_employment": 2,
    "unemployed_count": 3,
    "rural_employment": 10
}
req = urllib.request.Request(
    f"{BASE}/admin/reports",
    data=json.dumps(report_data).encode(),
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
)
resp = urllib.request.urlopen(req, timeout=10)
result = json.loads(resp.read())
report_id = result.get("id", "unknown")
print(f"3. 新建报表: OK, id={report_id}")

# 4. 企业列表
req = urllib.request.Request(
    f"{BASE}/admin/enterprises",
    headers={"Authorization": f"Bearer {token}"}
)
resp = urllib.request.urlopen(req, timeout=10)
ent_data = json.loads(resp.read())
total_ents = ent_data.get("total", 0) if isinstance(ent_data, dict) else len(ent_data)
print(f"4. 企业列表: OK, 总数={total_ents}")

# 5. 用户列表
req = urllib.request.Request(
    f"{BASE}/admin/users",
    headers={"Authorization": f"Bearer {token}"}
)
resp = urllib.request.urlopen(req, timeout=10)
user_data = json.loads(resp.read())
total_users = user_data.get("total", 0) if isinstance(user_data, dict) else len(user_data)
print(f"5. 用户列表: OK, 总数={total_users}")

# 6. 统计汇总
req = urllib.request.Request(
    f"{BASE}/data/stats/summary",
    headers={"Authorization": f"Bearer {token}"}
)
resp = urllib.request.urlopen(req, timeout=10)
stats = json.loads(resp.read())
print(f"6. 统计汇总: OK")
print(f"   - 总企业数: {stats.get('total_enterprises', 0)}")
print(f"   - 总报表数: {stats.get('total_reports', 0)}")

# 7. 提交刚创建的报表
if report_id != "unknown":
    req = urllib.request.Request(
        f"{BASE}/admin/reports/{report_id}/submit",
        headers={"Authorization": f"Bearer {token}"},
        method="PUT"
    )
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        print(f"7. 提交报表: OK")
    except Exception as e:
        print(f"7. 提交报表: 失败 - {e}")

# 8. 获取前端页面
req = urllib.request.Request("http://127.0.0.1:8000/")
try:
    resp = urllib.request.urlopen(req, timeout=10)
    html = resp.read().decode("utf-8")
    if "vue" in html.lower() or "app" in html.lower():
        print(f"8. 前端页面: OK (HTML加载正常)")
    else:
        print(f"8. 前端页面: 需要检查")
except Exception as e:
    print(f"8. 前端页面: 失败 - {e}")

print("\n=== 全部API测试完成 ===")
