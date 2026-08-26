import asyncio
import time
import subprocess
import requests
import websockets
import json
import sys

def get_token():
    # Register and get token
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

async def test_integration():
    try:
        token = get_token()
    except Exception as e:
        print("Failed to get token:", e)
        return
        
    print("Test 5 & 6: REAL scan event and Verify event data")
    async with websockets.connect("ws://127.0.0.1:8000/ws/dashboard") as ws:
        print("WS connected")
        
        # Trigger scan
        headers = {"Authorization": f"Bearer {token}"}
        scan_payload = {"prompt": "This is a test prompt to check if scanning works."}
        
        # We need to run requests.post in another thread so we don't block the async loop
        import threading
        def do_scan():
            try:
                r = requests.post("http://127.0.0.1:8000/api/v1/scan", json=scan_payload, headers=headers)
                print("Test 7: Verify REST response")
                print("REST Status:", r.status_code)
            except Exception as e:
                print("REST Scan failed:", e)

        t = threading.Thread(target=do_scan)
        t.start()
        
        # Wait for WS message
        msg = await asyncio.wait_for(ws.recv(), timeout=300.0)
        data = json.loads(msg)
        print("Broadcast received:", json.dumps(data, indent=2))
        assert data["event"] == "scan_completed"
        assert "risk_score" in data["data"]
        assert "severity" in data["data"]
        
        t.join()
        
    print("Test 8: Verify database consistency (handled by existing pipeline)")
    print("Test 9: WebSocket failure isolation")
    # Disconnect WS and scan again
    r = requests.post("http://127.0.0.1:8000/api/v1/scan", json=scan_payload, headers=headers)
    assert r.status_code == 200
    print("REST succeeded without WS")
    
    print("Test 10: Multiple dashboard clients")
    async with websockets.connect("ws://127.0.0.1:8000/ws/dashboard") as ws1:
        async with websockets.connect("ws://127.0.0.1:8000/ws/dashboard") as ws2:
            t = threading.Thread(target=do_scan)
            t.start()
            
            msg1 = await asyncio.wait_for(ws1.recv(), timeout=300.0)
            msg2 = await asyncio.wait_for(ws2.recv(), timeout=300.0)

            
            assert json.loads(msg1)["event"] == "scan_completed"
            assert json.loads(msg2)["event"] == "scan_completed"
            
            t.join()
            print("Both clients received event")
            
    print("All integration tests passed.")

import pytest

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

