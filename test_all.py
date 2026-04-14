import urllib.request
import json

BASE = "http://127.0.0.1:8000/api/v1"

def api_call(path, method="GET", data=None, token=None):
    url = f"{BASE}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return {"error": e.code, "detail": body}

print("=== 完整系统API测试 ===\n")

# 1. Admin登录
result = api_call("/auth/login", "POST", {"username": "admin", "password": "admin123"})
if "access_token" in result:
    token = result["access_token"]
    print("1. Admin登录: OK")
else:
    print(f"1. Admin登录: FAIL - {result}")
    exit(1)

# 2. 企业列表
result = api_call("/admin/enterprises", token=token)
if isinstance(result, list):
    print(f"2. 企业列表: OK ({len(result)}家)")
    ent_id = result[0]["id"] if result else None
else:
    print(f"2. 企业列表: FAIL - {result}")

# 3. 编辑企业
if ent_id:
    result = api_call(f"/admin/enterprises/{ent_id}", "PUT", {"contact_name": "测试编辑"}, token=token)
    if "error" not in result:
        print(f"3. 编辑企业: OK")
    else:
        print(f"3. 编辑企业: FAIL - {result}")

# 4. 报表列表
result = api_call("/admin/reports", token=token)
if "items" in result:
    print(f"4. 报表列表: OK (总数={result['total']})")
    report_id = result["items"][0]["id"] if result["items"] else None
else:
    print(f"4. 报表列表: FAIL - {result}")

# 5. 提交报表
if report_id:
    result = api_call(f"/admin/reports/{report_id}/submit", "PUT", token=token)
    if "error" not in result:
        print(f"5. 提交报表: OK (状态={result.get('status')})")
    else:
        print(f"5. 提交报表: FAIL - {result}")

# 6. 撤回报表
if report_id:
    result = api_call(f"/admin/reports/{report_id}/withdraw", "PUT", token=token)
    if "error" not in result:
        print(f"6. 撤回报表: OK (状态={result.get('status')})")
    else:
        print(f"6. 撤回报表: FAIL - {result}")

# 7. 用户列表
result = api_call("/admin/users", token=token)
if isinstance(result, list):
    print(f"7. 用户列表: OK ({len(result)}个)")
    user_id = result[0]["id"] if result else None
else:
    print(f"7. 用户列表: FAIL - {result}")

# 8. 编辑用户
if user_id:
    result = api_call(f"/admin/users/{user_id}", "PUT", {"real_name": "管理员-已编辑"}, token=token)
    if "error" not in result:
        print(f"8. 编辑用户: OK (姓名={result.get('real_name')})")
    else:
        print(f"8. 编辑用户: FAIL - {result}")

# 9. 统计汇总
result = api_call("/data/stats/summary", token=token)
if "total_enterprises" in result:
    print(f"9. 统计汇总: OK (企业={result['total_enterprises']}, 报表={result['total_reports']})")
else:
    print(f"9. 统计汇总: FAIL - {result}")

# 10. 趋势数据
result = api_call("/data/stats/trend?year=2026", token=token)
if "trend" in result:
    print(f"10. 趋势数据: OK ({len(result['trend'])}个月)")
else:
    print(f"10. 趋势数据: FAIL - {result}")

# 11. 企业端登录
result = api_call("/auth/login", "POST", {"username": "enterprise1", "password": "ent123456"})
if "access_token" in result:
    ent_token = result["access_token"]
    print("11. 企业端登录: OK")
else:
    print(f"11. 企业端登录: FAIL - {result}")

# 12. 市级登录
result = api_call("/auth/login", "POST", {"username": "city_km", "password": "city123456"})
if "access_token" in result:
    print("12. 市级登录: OK")
else:
    print(f"12. 市级登录: FAIL - {result}")

# 13. 省级登录
result = api_call("/auth/login", "POST", {"username": "province", "password": "prov123456"})
if "access_token" in result:
    print("13. 省级登录: OK")
else:
    print(f"13. 省级登录: FAIL - {result}")

# 14. 分析师登录
result = api_call("/auth/login", "POST", {"username": "analyst", "password": "analyst123"})
if "access_token" in result:
    print("14. 分析师登录: OK")
else:
    print(f"14. 分析师登录: FAIL - {result}")

print("\n=== 测试完成 ===")
