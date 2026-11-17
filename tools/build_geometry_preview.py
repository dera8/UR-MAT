"""Compact a real UR-MAT scene without deleting or moving any triangle."""
from pathlib import Path
import struct, json, hashlib, io
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1] / 'docs/assets/geometry'
ROOT.mkdir(parents=True, exist_ok=True)
SOURCE = Path.home() / 'Desktop/glb/bryggen_osm2world.glb'
raw = SOURCE.read_bytes()
n, _ = struct.unpack_from('<II', raw, 12)
src = json.loads(raw[20:20+n])
bin_start = 20+n+8
binary = memoryview(raw)[bin_start:]
assert not any(set(node) & {'matrix','translation','rotation','scale'} for node in src['nodes'])

def array(i):
    a = src['accessors'][i]; v = src['bufferViews'][a['bufferView']]
    dtype = {5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']]
    dim = {'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
    off = v.get('byteOffset',0)+a.get('byteOffset',0)
    stride = v.get('byteStride',np.dtype(dtype).itemsize*dim)
    return np.ndarray((a['count'],dim), dtype=dtype, buffer=binary, offset=off, strides=(stride,np.dtype(dtype).itemsize)).copy()

out = {'asset':{'version':'2.0','generator':'UR-MAT lossless-position web preview'},'scene':0,'scenes':[{'nodes':[0]}], 'nodes':[{'mesh':0,'name':'Bryggen — original geometry, averaged texture colors'}], 'meshes':[{'primitives':[]}], 'materials':[], 'bufferViews':[], 'accessors':[], 'buffers':[]}
chunks = bytearray()
def add(a, typ, target):
    while len(chunks)%4: chunks.append(0)
    idx = len(out['bufferViews']); offset=len(chunks); chunks.extend(a.tobytes())
    out['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':a.nbytes,'target':target})
    d={'bufferView':idx,'componentType':5126 if a.dtype.kind=='f' else (5123 if a.dtype.itemsize==2 else 5125),'count':len(a),'type':typ}
    if typ=='VEC3': d.update(min=a.min(axis=0).tolist(),max=a.max(axis=0).tolist())
    out['accessors'].append(d); return len(out['accessors'])-1

groups={}; original_vertices=0; original_triangles=0
for mesh in src['meshes']:
    for p in mesh['primitives']:
        assert p.get('mode',4)==4
        v=array(p['attributes']['POSITION']); original_vertices += len(v)
        triangles=v[array(p['indices']).ravel()] if 'indices' in p else v
        assert len(triangles)%3==0
        original_triangles += len(triangles)//3
        groups.setdefault(p.get('material',0),[]).append(triangles)

allmins=[]; allmaxs=[]; preview_vertices=0
for material, parts in groups.items():
    vertices=np.concatenate(parts)
    unique, indices=np.unique(vertices,axis=0,return_inverse=True)
    unique=unique.astype('<f4'); indices=indices.astype('<u4')
    preview_vertices+=len(unique); allmins.append(unique.min(axis=0)); allmaxs.append(unique.max(axis=0))
    sm=src['materials'][material]; pbr=sm.get('pbrMetallicRoughness',{})
    color=pbr.get('baseColorFactor',[0.65,0.65,0.65,1])
    if 'baseColorTexture' in pbr:
        tex=src['textures'][pbr['baseColorTexture']['index']]; im=src['images'][tex['source']]
        bv=src['bufferViews'][im['bufferView']]; start=bv.get('byteOffset',0)
        img=Image.open(io.BytesIO(bytes(binary[start:start+bv['byteLength']]))).convert('RGB')
        # Display texture average in linear color space, as required for glTF factors.
        rgb=np.array(img.resize((32,32)),dtype=float).mean(axis=(0,1))/255
        rgb=np.where(rgb<=0.04045,rgb/12.92,((rgb+0.055)/1.055)**2.4)
        color=[*rgb.tolist(),1.0]
    mat={'name':sm.get('name',f'Material {material}'),'doubleSided':True,'pbrMetallicRoughness':{'baseColorFactor':color,'metallicFactor':0,'roughnessFactor':0.9}}
    out['materials'].append(mat)
    # Partition only the index stream; every original triangle is retained.
    # Each batch fits uint16 indices, supported without compression extensions.
    for start in range(0,len(vertices),60000):
        batch=vertices[start:start+60000]
        bv,bi=np.unique(batch,axis=0,return_inverse=True)
        out['meshes'][0]['primitives'].append({'attributes':{'POSITION':add(bv.astype('<f4'),'VEC3',34962)},'indices':add(bi.astype('<u2'),'SCALAR',34963),'material':len(out['materials'])-1,'mode':4})

while len(chunks)%4:chunks.append(0)
out['buffers']=[{'byteLength':len(chunks)}]
js=json.dumps(out,separators=(',',':'),ensure_ascii=True).encode()
js+=b' '*((-len(js))%4)
glb=struct.pack('<III',0x46546C67,2,12+8+len(js)+8+len(chunks))+struct.pack('<II',len(js),0x4E4F534A)+js+struct.pack('<II',len(chunks),0x004E4942)+chunks
(ROOT/'bryggen-preview.glb').write_bytes(glb)
preview_vertices=sum(out['accessors'][p['attributes']['POSITION']]['count'] for p in out['meshes'][0]['primitives'])
lo=np.min(allmins,axis=0); hi=np.max(allmaxs,axis=0)
metrics={'scene':'Bryggen','source_file':SOURCE.name,'source_sha256':hashlib.sha256(raw).hexdigest(),'source_bytes':len(raw),'mesh_definitions':len(src['meshes']),'mesh_instances':sum('mesh' in n for n in src['nodes']),'material_definitions':len(src['materials']),'vertex_entries':original_vertices,'triangle_count':original_triangles,'bounds_min':lo.tolist(),'bounds_max':hi.tolist(),'extent_scene_units':(hi-lo).tolist(),'preview_bytes':len(glb),'preview_vertices':preview_vertices,'preview_triangle_count':original_triangles,'preview_method':'All original triangles and exact float32 positions retained. Vertices deduplicated by material; textures replaced with average texture colors; UVs and normals omitted; materials grouped to reduce draw calls. Geometry metrics are measured from this local source GLB, not a dataset-wide benchmark.','axis':'glTF Y-up','units_note':'Extents are reported in source scene units; no external survey validation was performed.'}
(ROOT/'metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
print(json.dumps(metrics,indent=2))
