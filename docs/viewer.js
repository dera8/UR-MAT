import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/GLTFLoader.js';
import {OrbitControls} from 'three/addons/OrbitControls.js';
export async function startViewer(){
  const wrap=document.getElementById('canvas-wrap');
  const scene=new THREE.Scene();scene.background=new THREE.Color('#303c33');
  const camera=new THREE.PerspectiveCamera(40,wrap.clientWidth/wrap.clientHeight,1,5000);
  const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setSize(wrap.clientWidth,wrap.clientHeight);renderer.outputColorSpace=THREE.SRGBColorSpace;
  const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.maxPolarAngle=Math.PI*.49;controls.minDistance=90;controls.maxDistance=1800;
  scene.add(new THREE.HemisphereLight(0xffffff,0x727b5e,2));const sun=new THREE.DirectionalLight(0xfff4d6,2.4);sun.position.set(-100,350,200);scene.add(sun);
  let model;
  try{model=await new GLTFLoader().loadAsync('assets/geometry/bryggen-preview.glb');}catch(e){renderer.dispose();controls.dispose();throw e;}
  model.scene.traverse(o=>{if(o.isMesh){const materials=Array.isArray(o.material)?o.material:[o.material];materials.forEach(m=>{m.flatShading=true;m.side=THREE.DoubleSide;m.needsUpdate=true;});}});scene.add(model.scene);
  const box=new THREE.Box3().setFromObject(model.scene);const center=box.getCenter(new THREE.Vector3());
  function reset(){controls.target.copy(center);camera.position.copy(center).add(new THREE.Vector3(440,410,530));controls.update();}reset();
  wrap.replaceChildren(renderer.domElement);renderer.domElement.setAttribute('aria-label','Interactive 3D geometry of Bryggen. Drag to orbit; scroll to zoom.');renderer.domElement.tabIndex=0;
  const resetButton=document.getElementById('reset-3d');resetButton.hidden=false;resetButton.addEventListener('click',reset);
  renderer.domElement.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','-'].includes(e.key)){e.preventDefault();const offset=camera.position.clone().sub(controls.target);const s=new THREE.Spherical().setFromVector3(offset);if(e.key==='ArrowLeft')s.theta-=.1;if(e.key==='ArrowRight')s.theta+=.1;if(e.key==='ArrowUp')s.phi=Math.max(.1,s.phi-.1);if(e.key==='ArrowDown')s.phi=Math.min(1.5,s.phi+.1);if(e.key==='+')s.radius*=.9;if(e.key==='-')s.radius*=1.1;camera.position.copy(controls.target).add(new THREE.Vector3().setFromSpherical(s));controls.update();}});
  const resize=new ResizeObserver(()=>{camera.aspect=wrap.clientWidth/wrap.clientHeight;camera.updateProjectionMatrix();renderer.setSize(wrap.clientWidth,wrap.clientHeight);});resize.observe(wrap);
  let visible=true;new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;}).observe(wrap);
  renderer.setAnimationLoop(()=>{if(visible&&!document.hidden){controls.update();renderer.render(scene,camera);}});
  document.getElementById('viewer').dataset.loaded='true';
}
