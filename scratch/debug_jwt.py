import requests
requests.post("http://127.0.0.1:8000/api/v1/auth/register", json={
    "username": "wsuser_test",
    "email": "wsuser_test@example.com",
    "password": "Password123!"
})
r = requests.post("http://127.0.0.1:8000/api/v1/auth/login", data={
    "username": "wsuser_test",
    "password": "Password123!"
})
print(r.json())
token = r.json().get("access_token")
if token:
    r2 = requests.post("http://127.0.0.1:8000/api/v1/scan", json={"prompt": "test"}, headers={"Authorization": f"Bearer {token}"})
    print(r2.status_code, r2.json())
