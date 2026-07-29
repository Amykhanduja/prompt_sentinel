import { readFileSync } from 'fs';
import { JSDOM } from 'jsdom';

const html = readFileSync('./dist/index.html', 'utf8');
const dom = new JSDOM(html, { runScripts: 'dangerously', resources: 'usable' });

dom.window.addEventListener('error', (e) => {
  console.log('JSDOM ERROR:', e.message);
});

setTimeout(() => {
  console.log('ROOT HTML:', dom.window.document.getElementById('root').innerHTML.substring(0, 200));
  process.exit(0);
}, 2000);
