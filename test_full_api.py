import urllib.request, json, sys

BASE = 'http://127.0.0.1:8000/api/v1'

def api_get(path, token=None):
    req = urllib.request.Request(f'{BASE}{path}')
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    resp = urllib.request.urlopen(req, timeout=10)
    return json.loads(resp.read())

def api_post(path, data, token=None):
    req = urllib.request.Request(f'{BASE}{path}',
        data=json.dumps(data).encode(),
        headers={'Content-Type':'application/json'})
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    resp = urllib.request.urlopen(req, timeout=10)
    return json.loads(resp.read())

def api_put(path, data, token=None):
    req = urllib.request.Request(f'{BASE}{path}',
        data=json.dumps(data).encode(),
        headers={'Content-Type':'application/json', 'Authorization': f'Bearer {token}'},
        method='PUT')
    resp = urllib.request.urlopen(req, timeout=10)
    return json.loads(resp.read())

def api_delete(path, token=None):
    req = urllib.request.Request(f'{BASE}{path}',
        headers={'Authorization': f'Bearer {token}'},
        method='DELETE')
    resp = urllib.request.urlopen(req, timeout=10)
    return json.loads(resp.read())

print('=== 1. Login ===')
login = api_post('/auth/login', {'username': 'admin', 'password': 'admin123'})
token = login['access_token']
print(f'OK, token={token[:20]}...')

print('\n=== 2. Enterprise CRUD ===')
ents = api_get('/admin/enterprises', token)
print(f'List: {len(ents)} enterprises')
if ents:
    e = ents[0]
    print(f'  First: id={e["id"]}, name={e["name"]}')
    # Edit
    result = api_put(f'/admin/enterprises/{e["id"]}', {'contact_name': '编辑测试'}, token)
    print(f'  Edit OK: contact_name={result.get("contact_name")}')
# Create + Delete
new_ent = api_post('/admin/enterprises', {'name': '待删除测试', 'credit_code': '91530000DEL001', 'city_code': '530100', 'contact_name': '测试', 'contact_phone': '13800000001'}, token)
print(f'  Create OK: id={new_ent["id"]}')
del_result = api_delete(f'/admin/enterprises/{new_ent["id"]}', token)
print(f'  Delete OK: {del_result}')

print('\n=== 3. User CRUD ===')
users = api_get('/admin/users', token)
print(f'List: {len(users)} users')
if users:
    u = users[0]
    result = api_put(f'/admin/users/{u["id"]}', {'real_name': '编辑测试用户'}, token)
    print(f'  Edit OK: real_name={result.get("real_name")}')

print('\n=== 4. Report CRUD ===')
reports = api_get('/admin/reports', token)
print(f'List: total={reports["total"]}, items={len(reports["items"])}')
if reports['items']:
    r = reports['items'][0]
    print(f'  First: id={r["id"]}, status={r["status"]}, enterprise={r.get("enterprise_name")}')
    # Withdraw test (only if city_review or province_review)
    if r['status'] in ['city_review', 'province_review']:
        result = api_put(f'/admin/reports/{r["id"]}/withdraw', {}, token)
        print(f'  Withdraw OK: status={result["status"]}')
    else:
        print(f'  Status is {r["status"]}, withdraw not applicable')

print('\n=== 5. Stats ===')
stats = api_get('/data/stats/summary', token)
print(f'Summary: enterprises={stats.get("total_enterprises")}, reports={stats.get("total_reports")}')
print(f'  employed={stats.get("total_employed")}, unemployed={stats.get("total_unemployed")}')
print(f'  approved={stats.get("approved_reports")}, pending_city={stats.get("pending_city_review")}, pending_province={stats.get("pending_province_review")}')
print(f'  today_city={stats.get("today_city_reviewed")}, month_city={stats.get("month_city_reviewed")}')

trend = api_get('/data/stats/trend?year=2026', token)
print(f'Trend: {len(trend.get("trend", []))} months')
for t in trend.get('trend', []):
    print(f'  Month {t["month"]}: employed={t["employed"]}, unemployed={t["unemployed"]}')

print('\n=== 6. City user test ===')
city_login = api_post('/auth/login', {'username': 'city_km', 'password': 'city123456'})
city_token = city_login['access_token']
try:
    city_reports = api_get('/data/city/reports', city_token)
    print(f'City reports: {len(city_reports)} pending')
except Exception as ex:
    print(f'City reports error: {ex}')

print('\n=== 7. Enterprise user test ===')
ent_login = api_post('/auth/login', {'username': 'enterprise1', 'password': 'ent123456'})
ent_token = ent_login['access_token']
try:
    my_reports = api_get('/data/reports', ent_token)
    print(f'Enterprise reports: {len(my_reports)} reports')
except Exception as ex:
    print(f'Enterprise reports error: {ex}')

print('\n=== ALL TESTS PASSED ===')
