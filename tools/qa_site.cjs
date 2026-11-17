const {chromium}=require('C:/Users/Debora/Desktop/twin-graph-demo/.qa-tools/node_modules/playwright');
const http=require('http'),fs=require('fs'),path=require('path'),assert=require('assert');
const root=path.resolve(__dirname,'../docs'),out=path.resolve(__dirname,'../.qa');fs.mkdirSync(out,{recursive:true});
const types={'.css':'text/css','.html':'text/html','.js':'application/javascript','.json':'application/json','.svg':'image/svg+xml','.webp':'image/webp','.gif':'image/gif','.glb':'model/gltf-binary'};
const server=http.createServer((req,res)=>{let relative=decodeURIComponent(req.url.split('?')[0]).replace(/^\/UR-MAT\/?/,'');let p=path.resolve(root,relative||'index.html');if(!p.startsWith(root+path.sep)&&p!==root){res.writeHead(403);return res.end();}if(fs.existsSync(p)&&fs.statSync(p).isDirectory())p=path.join(p,'index.html');if(!fs.existsSync(p)){res.writeHead(404);return res.end();}res.setHeader('Content-Type',types[path.extname(p)]||'application/octet-stream');fs.createReadStream(p).pipe(res);});
(async()=>{await new Promise(r=>server.listen(8779,'127.0.0.1',r));const browser=await chromium.launch({channel:'msedge',headless:true});let failed=false;try{
for(const [name,width,height] of [['desktop',1440,1000],['mobile',390,844]]){
 const page=await browser.newPage({viewport:{width,height},reducedMotion:'reduce'});const errors=[],bad=[];page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.url().includes('127.0.0.1')&&r.status()>=400)bad.push(r.url());});
 await page.goto('http://127.0.0.1:8779/UR-MAT/',{waitUntil:'networkidle'});await page.screenshot({path:path.join(out,name+'.png'),fullPage:true});
 assert.equal(await page.locator('#audit-body tr').count(),3);assert.equal(await page.locator('#geometry-stats strong').count(),3);
 await page.locator('#wipe').fill('75');assert((await page.locator('#compare').getAttribute('style')).includes('75%'));
 await page.locator('[data-scene=bryggen]').click();await page.locator('[data-mode=depth]').click();assert((await page.locator('#sample').getAttribute('src')).includes('bryggen-depth'));
 await page.locator('#animate').click();assert((await page.locator('#animation').getAttribute('src')).endsWith('.gif'));await page.locator('#animate').click();
 await page.locator('.citation summary').click();assert(await page.locator('#bibtex').isVisible());
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'Horizontal overflow');
 assert.equal(await page.evaluate(()=>[...document.images].filter(i=>!i.complete||!i.naturalWidth).length),0,'Broken images');
 await page.locator('#load-3d').click();await page.waitForFunction(()=>document.getElementById('viewer').dataset.loaded==='true',null,{timeout:60000});
 await page.locator('#viewer').screenshot({path:path.join(out,name+'-3d.png')});await page.locator('#reset-3d').click();
 assert.deepEqual(errors,[]);assert.deepEqual(bad,[]);console.log(name+': all interaction, geometry, asset and overflow checks passed');await page.close();
}
}catch(e){failed=true;console.error(e);}finally{await browser.close();await new Promise(r=>server.close(r));}if(failed)process.exitCode=1;})();
