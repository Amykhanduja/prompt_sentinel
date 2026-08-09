const { chromium } = require('playwright');
const { exec, spawn } = require('child_process');

async function runTests() {
    console.log("Starting backend...");
    const backend = spawn("/mnt/c/Users/khand/prompt_sentinel/venv/bin/uvicorn", ["app:app", "--port", "8000"], { cwd: "/mnt/c/Users/khand/prompt_sentinel" });
    
    console.log("Starting frontend...");
    const frontend = spawn("npm", ["run", "dev", "--", "--port", "5174"], { cwd: "." });
    
    await new Promise(r => setTimeout(r, 20000));
    
    // Create test user via curl
    console.log("Creating test user in DB...");
    await new Promise((resolve) => {
        exec("curl -X POST http://127.0.0.1:8000/api/v1/auth/register -H 'Content-Type: application/json' -d '{\"username\": \"ui_tester\", \"email\": \"ui@example.com\", \"password\": \"password123\"}'", (err, stdout, stderr) => {
            console.log(stdout);
            resolve();
        });
    });

    console.log("Starting Playwright tests...");
    const browser = await chromium.launch();
    const page = await browser.newPage();
    
    try {
        console.log("A. Opening dashboard without auth...");
        await page.goto('http://localhost:5174/');
        await page.waitForSelector('text=Sign in to access');
        console.log("Redirected to login successfully.");
        
        console.log("B. Testing invalid login...");
        await page.fill('input[name="username"]', 'ui_tester');
        await page.fill('input[name="password"]', 'wrongpass');
        await page.click('button[type="submit"]');
        await page.waitForSelector('text=Invalid credentials');
        console.log("Invalid login rejected successfully.");
        
        console.log("C. Testing valid login...");
        await page.fill('input[name="password"]', 'password123');
        await page.click('button[type="submit"]');
        await page.waitForSelector('text=Total Scanned', { timeout: 15000 });
        console.log("Valid login succeeded. Dashboard rendered.");
        
        console.log("E. Testing Scan API call...");
        await page.click('text=Artifact Scanner');
        await page.fill('textarea[placeholder*="Paste the system prompt"]', 'Test prompt');
        await page.click('button:has-text("Scan Prompt")');
        await page.waitForSelector('text=Scan Complete', { timeout: 20000 });
        console.log("Scan succeeded.");
        
        console.log("G. Testing Logout...");
        await page.click('button[aria-label="User menu"]');
        await page.click('button:has-text("Logout")');
        await page.waitForSelector('text=Sign in to access');
        console.log("Logout succeeded.");
        
        console.log("H. Testing expired JWT...");
        await page.evaluate("localStorage.setItem('prompt_sentinel_token', 'invalid_token')");
        await page.goto('http://localhost:5174/');
        await page.waitForSelector('text=Sign in to access');
        console.log("Invalid token rejected successfully.");
        
        console.log("ALL UI TESTS PASSED!");
    } catch (e) {
        console.error("TEST FAILED:", e);
    } finally {
        await browser.close();
        backend.kill();
        frontend.kill();
    }
}

runTests();
