const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ channel: 'chrome' }); // Use system Chrome
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
  
  await page.goto('http://localhost:5174/');
  await page.waitForTimeout(2000);
  
  const root = await page.$eval('#root', el => el.innerHTML);
  console.log('ROOT LENGTH:', root.length);
  
  await browser.close();
})();
