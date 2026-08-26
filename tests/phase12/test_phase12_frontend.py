import subprocess
import time
import os
import signal
from playwright.sync_api import sync_playwright

def run_tests():
    print("Starting backend...")
    backend = subprocess.Popen(["venv/bin/uvicorn", "app:app", "--port", "8000"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(5)
    
    print("Starting frontend...")
    frontend = subprocess.Popen(["npm", "run", "dev", "--", "--port", "5174"], cwd="dashboard", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(10)
    
    print("Creating test user in DB...")
    from sqlalchemy import text
    from database.connection import SessionLocal
    db = SessionLocal()
    db.execute(text("DELETE FROM users WHERE username = 'ui_tester'"))
    db.commit()
    
    import requests
    r = requests.post("http://127.0.0.1:8000/api/v1/auth/register", json={"username": "ui_tester", "email": "ui@example.com", "password": "password123"})
    print("Test user registration:", r.status_code)
    
    print("Starting Playwright tests...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # A. Open dashboard without authentication -> redirected to login
        print("A. Opening dashboard without auth...")
        page.goto('http://localhost:5174/')
        page.wait_for_selector('text=Sign in to access')
        print("Redirected to login successfully.")
        
        # B. Login with invalid credentials -> rejected
        print("B. Testing invalid login...")
        page.fill('input[name="username"]', 'ui_tester')
        page.fill('input[name="password"]', 'wrongpass')
        page.click('button[type="submit"]')
        page.wait_for_selector('text=Invalid credentials')
        print("Invalid login rejected successfully.")
        
        # C. Login with valid credentials
        print("C. Testing valid login...")
        page.fill('input[name="password"]', 'password123')
        page.click('button[type="submit"]')
        page.wait_for_selector('text=Total Scanned', timeout=10000)
        print("Valid login succeeded. Dashboard rendered.")
        
        # D & E & F Dashboard API calls / Scan / File scan
        # E. Scan text
        print("E. Testing Scan API call...")
        page.click('text=Artifact Scanner')
        page.fill('textarea[placeholder*="Paste the system prompt"]', 'Test prompt')
        page.click('button:has-text("Scan Prompt")')
        page.wait_for_selector('text=Scan Complete', timeout=15000)
        print("Scan succeeded.")
        
        # G. Logout
        print("G. Testing Logout...")
        page.click('button[aria-label="User menu"]')
        page.click('button:has-text("Logout")')
        page.wait_for_selector('text=Sign in to access')
        print("Logout succeeded.")
        
        # H. Expired/invalid JWT
        print("H. Testing expired JWT...")
        page.evaluate("localStorage.setItem('prompt_sentinel_token', 'invalid_token')")
        page.goto('http://localhost:5174/')
        page.wait_for_selector('text=Sign in to access')
        print("Invalid token rejected successfully.")
        
        # I. /api/v1/health
        print("I. Testing public health route...")
        health = requests.get("http://127.0.0.1:8000/api/v1/health")
        assert health.status_code == 200
        print("Health route accessible.")
        
        browser.close()

    db.execute(text("DELETE FROM users WHERE username = 'ui_tester'"))
    db.commit()
    db.close()
    print("ALL UI TESTS PASSED!")
    
    backend.terminate()
    frontend.terminate()

if __name__ == "__main__":
    run_tests()
