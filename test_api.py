import urllib.request, json

# Login
req = urllib.request.Request(
    'http://127.0.0.1:8000/api/v1/auth/login',
    data=json.dumps({'username': 'admin', 'password': 'admin123'}).encode(),
    headers={'Content-Type': 'application/json'}
)
resp = json.loads(urllib.request.urlopen(req).read())
token = resp.get('access_token', '')
print('Token:', token[:20] + '...' if token else 'NONE')

# Get reports with token
req2 = urllib.request.Request(
    'http://127.0.0.1:8000/api/v1/admin/reports',
    headers={'Authorization': f'Bearer {token}'}
)
try:
    resp2 = json.loads(urllib.request.urlopen(req2).read())
    print('Reports:', str(resp2)[:300])
except Exception as e:
    print('Error:', e)
