"""Vendor pinned Three.js modules and license for offline-capable rendering."""
from pathlib import Path
from urllib.request import urlopen
root=Path(__file__).resolve().parents[1]/'docs/vendor'
root.mkdir(parents=True,exist_ok=True)
base='https://cdn.jsdelivr.net/npm/three@0.170.0/'
files={'build/three.module.js':'three.module.js','examples/jsm/loaders/GLTFLoader.js':'GLTFLoader.js','examples/jsm/controls/OrbitControls.js':'OrbitControls.js','examples/jsm/utils/BufferGeometryUtils.js':'utils/BufferGeometryUtils.js','LICENSE':'LICENSE-three.txt'}
for source,target in files.items():
    path=root/target;path.parent.mkdir(parents=True,exist_ok=True)
    with urlopen(base+source,timeout=40) as response:data=response.read()
    if target=='GLTFLoader.js':data=data.replace(b'../utils/BufferGeometryUtils.js',b'./utils/BufferGeometryUtils.js')
    path.write_bytes(data);print(target,len(data))
