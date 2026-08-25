import subprocess
import time
import requests
import json
import asyncio
import websockets
from sqlalchemy import text
from database.connection import SessionLocal
import httpx

async def test_websocket():
    db = SessionLocal()
    db.execute(text("DELETE FROM users WHERE username = 'ws_tester'"))
    db.commit()
    r = requests.post("http://127.0.0.1:8000/api/v1/auth/register", json={"username": "ws_tester", "email": "ws@example.com", "password": "password123"})
    
    r = requests.post("http://127.0.0.1:8000/api/v1/auth/login", data={"username": "ws_tester", "password": "password123"})
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    print("Test 1 & 2: Backend and APIs running")
    r = requests.get("http://127.0.0.1:8000/api/v1/health")
    assert r.status_code == 200

    print("Test 3: Connect WebSocket")
    ws1 = await websockets.connect("ws://127.0.0.1:8000/ws/dashboard")
    print("WS1 Connected")

    print("Test 4: Disconnect WS1")
    await ws1.close()
    await asyncio.sleep(1)
    r = requests.get("http://127.0.0.1:8000/api/v1/health")
    assert r.status_code == 200
    print("Backend still running")

    print("Test 5: Multiple clients")
    ws2 = await websockets.connect("ws://127.0.0.1:8000/ws/dashboard")
    ws3 = await websockets.connect("ws://127.0.0.1:8000/ws/dashboard")
    print("WS2 and WS3 connected")

    print("Test 6: Trigger broadcast")
    async with httpx.AsyncClient() as client:
        resp = await client.post("http://127.0.0.1:8000/api/v1/test-broadcast", headers=headers)
        assert resp.status_code == 200
    
    msg2 = await asyncio.wait_for(ws2.recv(), timeout=5.0)
    msg3 = await asyncio.wait_for(ws3.recv(), timeout=5.0)
    print("Broadcast received:", msg2, msg3)
    assert json.loads(msg2)["event"] == "test"
    assert json.loads(msg3)["event"] == "test"

    print("Test 7: Disconnect one, check other")
    await ws2.close()
    await asyncio.sleep(1)
    
    async with httpx.AsyncClient() as client:
        resp = await client.post("http://127.0.0.1:8000/api/v1/test-broadcast", headers=headers)
        assert resp.status_code == 200
    
    msg3_new = await asyncio.wait_for(ws3.recv(), timeout=5.0)
    print("WS3 still receiving:", msg3_new)
    
    await ws3.close()
    
    db.execute(text("DELETE FROM users WHERE username = 'ws_tester'"))
    db.commit()
    db.close()
    print("All tests passed.")

import pytest
import sys

@pytest.fixture(scope="module", autouse=True)
def run_backend():
    print("Starting backend for tests...")
    backend = subprocess.Popen(["venv/bin/uvicorn", "app:app", "--port", "8000"], stdout=sys.stdout, stderr=sys.stderr)
    
    # Wait loop
    for _ in range(120):
        try:
            r = requests.get("http://127.0.0.1:8000/api/v1/health")
            if r.status_code == 200:
                print("Backend is up!")
                break
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    else:
        print("Backend failed to start in time!")
        backend.terminate()
        raise Exception("Backend failed to start")

    yield

    backend.terminate()
    backend.wait()

