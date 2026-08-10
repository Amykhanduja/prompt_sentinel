import subprocess
import time
import os
from playwright.sync_api import sync_playwright

import sys

def run_tests():
    print("Starting backend...", flush=True)
    backend = subprocess.Popen(["venv/bin/uvicorn", "app:app", "--port", "8000"], stdout=sys.stdout, stderr=sys.stderr)
    
    import requests
    # Wait loop
    for _ in range(300):
        try:
            r = requests.get("http://127.0.0.1:8000/api/v1/health", timeout=2)
            if r.status_code == 200:
                print("Backend is up!", flush=True)
                break
        except Exception:
            time.sleep(1)
    else:
        print("Backend failed to start in time!")
        backend.terminate()
        return

    print("Starting frontend...", flush=True)
    frontend = subprocess.Popen(["npm", "run", "dev", "--", "--port", "5174"], cwd="dashboard", stdout=sys.stdout, stderr=sys.stderr)
    time.sleep(10)
    
    print("Creating test user in DB...")
    from sqlalchemy import text
    from database.connection import SessionLocal
    db = SessionLocal()
    db.execute(text("DELETE FROM users WHERE username = 'ui_ws_tester'"))
    db.commit()
    
    r = requests.post("http://127.0.0.1:8000/api/v1/auth/register", json={"username": "ui_ws_tester", "email": "ui_ws@example.com", "password": "password123"})
    print("Test user registration:", r.status_code)
    
    token = requests.post("http://127.0.0.1:8000/api/v1/auth/login", data={"username": "ui_ws_tester", "password": "password123"}).json()["access_token"]
    
    print("Starting Playwright tests...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            
            print("Logging in...")
            page.goto('http://localhost:5174/')
            page.wait_for_selector('text=Sign in to access')
            page.fill('input[name="username"]', 'ui_ws_tester')
            page.fill('input[name="password"]', 'password123')
            page.click('button[type="submit"]')
            page.wait_for_selector('text=Platform Overview', timeout=10000)
            print("Login succeeded. Dashboard rendered.")
            
            # Wait for data to load
            page.wait_for_selector('text=Total Scanned')
            time.sleep(2) # Give a moment for initial REST fetch to settle
            
            # Get initial count
            # Find the div containing "Total Scanned", and the number next to it.
            # We can get inner text of the parent
            total_scanned_element = page.locator("text=Total Scanned").locator("..").locator("p.text-2xl")
            initial_count_text = total_scanned_element.inner_text().strip()
            initial_count = int(initial_count_text.replace(',', ''))
            print("Initial Total Scanned:", initial_count)
            
            print("Triggering real scan via REST...")
            headers = {"Authorization": f"Bearer {token}"}
            scan_payload = {"prompt": "WebSocket UI integration test prompt."}
            r = requests.post("http://127.0.0.1:8000/api/v1/scan", json=scan_payload, headers=headers)
            print("REST Status:", r.status_code)
            
            print("Waiting for WebSocket UI update...")
            # Wait for the total to increment without refreshing
            expected_text = f"{initial_count + 1:,}"
            total_scanned_element.wait_for(state="visible", timeout=10000)
            
            # Since playwright wait_for doesn't easily wait for text content change, we'll poll
            for _ in range(10):
                new_text = total_scanned_element.inner_text().strip()
                if new_text == expected_text or new_text == str(initial_count + 1):
                    print("UI updated successfully via WebSocket!")
                    break
                time.sleep(1)
            else:
                print(f"FAILED: UI did not update. Expected {initial_count + 1}, got {new_text}")
                assert False, "UI did not update via WebSocket"
            
            browser.close()
            print("ALL WS UI TESTS PASSED!")
    finally:
        db.execute(text("DELETE FROM users WHERE username = 'ui_ws_tester'"))
        db.commit()
        db.close()
        backend.terminate()
        frontend.terminate()

if __name__ == "__main__":
    run_tests()
