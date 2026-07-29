import { JSDOM, VirtualConsole } from 'jsdom';

const virtualConsole = new VirtualConsole();
virtualConsole.on("error", (err, ...rest) => {
  console.log("JSDOM CONSOLE ERROR:", err, rest);
});
virtualConsole.on("log", (log) => {
  console.log("JSDOM CONSOLE LOG:", log);
});

JSDOM.fromURL('http://localhost:5174/', {
  runScripts: 'dangerously',
  resources: 'usable',
  virtualConsole
}).then(dom => {
  setTimeout(() => {
    console.log('ROOT HTML:', dom.window.document.getElementById('root').innerHTML.substring(0, 200));
    process.exit(0);
  }, 2000);
}).catch(e => {
  console.log('JSDOM FETCH ERROR:', e.message);
});
