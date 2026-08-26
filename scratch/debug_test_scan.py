import requests

def get_token():
    requests.post("http://127.0.0.1:8000/api/v1/auth/register", json={
        "username": "wsuser",
        "email": "wsuser@example.com",
        "password": "Password123!"
    })
    r = requests.post("http://127.0.0.1:8000/api/v1/auth/login", data={
        "username": "wsuser",
        "password": "Password123!"
    })
    return r.json()["access_token"]

if __name__ == "__main__":
    token = get_token()
    print("Token:", token)
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post("http://127.0.0.1:8000/api/v1/scan", json={"prompt": "This is a test prompt to check if scanning works."}, headers=headers)
    print("REST Status:", r.status_code)
    print("Response:", r.text)
