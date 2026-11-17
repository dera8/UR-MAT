import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/GLTFLoader.js';
import {OrbitControls} from 'three/addons/OrbitControls.js';
const palette={Limestone:'#ffff00',Slate:'#0000ff',Glass:'#00ffff',Steel:'#ffa500',Brick:'#b22222',Cobblestone:'#ff8c00',Plaster:'#ffd700',Concrete:'#800080',Gravel:'#4b0082',Tiles:'#8b0000',Wood:'#8b4513',Asphalt:'#171717',Plastic:'#ff1493',Unknown:'#808080'};
export async function startViewer(){
  const wrap=document.getElementById('canvas-wrap'),viewer=document.getElementById('viewer');
  const scene=new THREE.Scene();scene.background=new THREE.Color('#303c33');
  const camera=new THREE.PerspectiveCamera(40,wrap.clientWidth/wrap.clientHeight,.1,10000);
  const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.setSize(wrap.clientWidth,wrap.clientHeight);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;
  const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.maxPolarAngle=Math.PI*.49;
  scene.add(new THREE.HemisphereLight(0xffffff,0x727b5e,2.4));const sun=new THREE.DirectionalLight(0xfff4e4,3);sun.position.set(-100,350,200);scene.add(sun);
  let model;
  try{
    const compressed='DecompressionStream' in window;
    const response=await fetch(`assets/geometry/bryggen-ue-preview.glb${compressed?'.gz':''}`);
    if(!response.ok)throw new Error(`Scene download failed (${response.status})`);
    let buffer=await response.arrayBuffer();
    const signature=new Uint8Array(buffer,0,2);
    if(compressed&&signature[0]===31&&signature[1]===139)buffer=await new Response(new Blob([buffer]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();
    document.getElementById('viewer-status').textContent='Preparing UE textures and materials…';
    model=await new GLTFLoader().parseAsync(buffer,'assets/geometry/');
  }catch(e){renderer.dispose();controls.dispose();throw e;}
  const meshes=[],records=new Map(),semantic=new Map();
  model.scene.traverse(o=>{
    if(o.isLight)o.visible=false;
    if(!o.isMesh)return;
    const materials=Array.isArray(o.material)?o.material:[o.material];
    if(/sky/i.test(o.name)||materials.some(m=>/SkyDome/i.test(m.name))){o.visible=false;return;}
    o.userData.originalMaterials=o.material;meshes.push(o);
    for(const m of materials){const d=m.userData.urmat;if(d)records.set(d.metadata_material_name,d);}
  });
  scene.add(model.scene);model.scene.updateMatrixWorld(true);
  const box=new THREE.Box3();for(const mesh of meshes){mesh.geometry.computeBoundingBox();box.union(mesh.geometry.boundingBox.clone().applyMatrix4(mesh.matrixWorld));}
  const center=box.getCenter(new THREE.Vector3()),size=box.getSize(new THREE.Vector3()),extent=Math.max(size.x,size.y,size.z);
  controls.minDistance=extent*.08;controls.maxDistance=extent*4;camera.far=extent*20;camera.updateProjectionMatrix();
  function reset(){controls.target.copy(center);camera.position.copy(center).add(new THREE.Vector3(.78,.72,.94).multiplyScalar(extent));controls.update();}reset();
  function inspect(d){
    if(!d)return;const panel=document.getElementById('material-info');panel.replaceChildren();
    const title=document.createElement('strong');title.textContent=`${d.material_type} · ${d.metadata_material_name}`;
    const text=document.createElement('span'),p=d.physical_properties;
    text.textContent=`Source annotations — permittivity: ${p.permittivity}; attenuation: ${p.attenuation}; reflectance: ${p.reflectance}.`;
    const source=document.createElement('small');source.textContent=d.material_path;
    panel.append(title,text,source);document.getElementById('material-select').value=d.metadata_material_name;
  }
  const select=document.getElementById('material-select');select.replaceChildren();
  for(const [name,d] of [...records].sort((a,b)=>a[0].localeCompare(b[0]))){const option=document.createElement('option');option.value=name;option.textContent=`${d.material_type} — ${name}`;select.append(option);}
  select.disabled=false;select.addEventListener('change',()=>inspect(records.get(select.value)));inspect(records.get(select.value));
  function semanticMaterial(m){const cls=m.userData.urmat?.material_type||'Unknown';if(!semantic.has(cls))semantic.set(cls,new THREE.MeshBasicMaterial({color:palette[cls]||palette.Unknown,side:m.side}));return semantic.get(cls);}
  function setMode(mode){for(const mesh of meshes){const orig=mesh.userData.originalMaterials;mesh.material=mode==='appearance'?orig:Array.isArray(orig)?orig.map(semanticMaterial):semanticMaterial(orig);}viewer.dataset.mode=mode;for(const name of ['appearance','materials']){const b=document.getElementById(`view-${name}`);b.disabled=false;b.setAttribute('aria-pressed',String(name===mode));}}
  document.getElementById('view-appearance').addEventListener('click',()=>setMode('appearance'));document.getElementById('view-materials').addEventListener('click',()=>setMode('materials'));setMode('appearance');
  wrap.replaceChildren(renderer.domElement);renderer.domElement.setAttribute('aria-label','Material-aware Bryggen UE scene. Drag to orbit, scroll to zoom; click a surface to inspect its source material.');renderer.domElement.tabIndex=0;
  const resetButton=document.getElementById('reset-3d');resetButton.hidden=false;resetButton.addEventListener('click',reset);
  const ray=new THREE.Raycaster(),pointer=new THREE.Vector2();let down;
  renderer.domElement.addEventListener('pointerdown',e=>{down=[e.clientX,e.clientY];});
  renderer.domElement.addEventListener('pointerup',e=>{if(!down||Math.hypot(e.clientX-down[0],e.clientY-down[1])>5)return;const rect=renderer.domElement.getBoundingClientRect();pointer.set((e.clientX-rect.left)/rect.width*2-1,-(e.clientY-rect.top)/rect.height*2+1);ray.setFromCamera(pointer,camera);const hit=ray.intersectObjects(meshes,false)[0];if(hit){const originals=hit.object.userData.originalMaterials;const m=Array.isArray(originals)?originals[hit.face.materialIndex]:originals;inspect(m.userData.urmat);}});
  renderer.domElement.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','-'].includes(e.key)){e.preventDefault();const s=new THREE.Spherical().setFromVector3(camera.position.clone().sub(controls.target));if(e.key==='ArrowLeft')s.theta-=.1;if(e.key==='ArrowRight')s.theta+=.1;if(e.key==='ArrowUp')s.phi=Math.max(.1,s.phi-.1);if(e.key==='ArrowDown')s.phi=Math.min(1.5,s.phi+.1);if(e.key==='+')s.radius*=.9;if(e.key==='-')s.radius*=1.1;camera.position.copy(controls.target).add(new THREE.Vector3().setFromSpherical(s));controls.update();}});
  new ResizeObserver(()=>{camera.aspect=wrap.clientWidth/wrap.clientHeight;camera.updateProjectionMatrix();renderer.setSize(wrap.clientWidth,wrap.clientHeight);}).observe(wrap);
  let visible=true;new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;}).observe(wrap);
  renderer.setAnimationLoop(()=>{if(visible&&!document.hidden){controls.update();renderer.render(scene,camera);}});
  viewer.dataset.loaded='true';viewer.dataset.meshes=String(meshes.length);viewer.dataset.materials=String(records.size);
}
