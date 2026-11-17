"""UE preview: exact geometry, UVs, normals, transforms and PBR assignments.
Only texture resolution changes (256px colour, 128px other maps).
"""
from pathlib import Path
import struct, json, hashlib, io, re, copy, gzip
from collections import Counter
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]/'docs/assets/geometry'
SOURCE=Path.home()/'Desktop/glb/Bryggen_ue.glb'
META=Path.home()/'Desktop/scene_physical_metadata_bryggen.json'
ROOT.mkdir(parents=True,exist_ok=True)
raw=SOURCE.read_bytes();n,kind=struct.unpack_from('<II',raw,12)
original=json.loads(raw[20:20+n]);doc=copy.deepcopy(original);binary=memoryview(raw)[20+n+8:]
metadata=json.loads(META.read_text());lookup={}
for sections in metadata.values():
    for entry in sections.values():
        key=entry['material_path'].split('.')[-1]
        if key in lookup:assert lookup[key]==entry, f'Conflicting source metadata: {key}'
        lookup[key]=entry
material_index=[]
for idx,mat in enumerate(doc['materials']):
    name=mat['name'];key=re.sub(r'_bergen_norway_node_\d+$','',name);key=re.sub(r'_SurfaceArea_w-\d+$','',key)
    assert key in lookup, f'No exact base material metadata: {name}'
    entry=lookup[key]
    details={'source_material_index':idx,'source_material_name':name,'metadata_material_name':key,'material_type':entry['material_type'],'physical_properties':entry['physical_properties'],'material_path':entry['material_path']}
    mat.setdefault('extras',{})['urmat']=details;material_index.append(details)
color_images=set()
for mat in doc['materials']:
    pbr=mat.get('pbrMetallicRoughness',{})
    for tex in [pbr.get('baseColorTexture'),mat.get('emissiveTexture')]:
        if tex:color_images.add(doc['textures'][tex['index']]['source'])
image_views={i['bufferView'] for i in doc['images']}
chunks=bytearray();newviews=[];mapping={};dedup={}
def add(payload,template=None):
    while len(chunks)%4:chunks.append(0)
    view=dict(template or {});view.update(buffer=0,byteOffset=len(chunks),byteLength=len(payload))
    chunks.extend(payload);newviews.append(view);return len(newviews)-1
for i,view in enumerate(original['bufferViews']):
    if i in image_views:continue
    start=view.get('byteOffset',0);mapping[i]=add(binary[start:start+view['byteLength']],view)
for a in doc['accessors']:
    if 'bufferView' in a:a['bufferView']=mapping[a['bufferView']]
    if 'sparse' in a:
        for key in ['indices','values']:a['sparse'][key]['bufferView']=mapping[a['sparse'][key]['bufferView']]
for i,img in enumerate(doc['images']):
    v=original['bufferViews'][img['bufferView']];start=v.get('byteOffset',0)
    im=Image.open(io.BytesIO(binary[start:start+v['byteLength']])).convert('RGBA')
    limit=256 if i in color_images else 128;im.thumbnail((limit,limit),Image.Resampling.LANCZOS)
    if im.getextrema()[3]==(255,255):im=im.convert('RGB')
    b=io.BytesIO()
    im.save(b,format='WEBP',lossless=i not in color_images,quality=85,method=4)
    payload=b.getvalue();digest=hashlib.sha256(payload).hexdigest()
    if digest not in dedup:dedup[digest]=add(payload)
    img['bufferView']=dedup[digest];img['mimeType']='image/webp'
    if i%400==0:print(f'Textures {i}/{len(doc["images"])}',flush=True)
doc['bufferViews']=newviews
for texture in doc['textures']:
    texture.setdefault('extensions',{})['EXT_texture_webp']={'source':texture.pop('source')}
for old,new in zip(original['textures'],doc['textures']):
    assert old['source']==new['extensions']['EXT_texture_webp']['source']
doc.setdefault('extensionsUsed',[]).append('EXT_texture_webp')
doc.setdefault('extensionsRequired',[]).append('EXT_texture_webp')
while len(chunks)%4:chunks.append(0)
doc['buffers']=[{'byteLength':len(chunks)}];doc['asset']['generator']='UR-MAT UE web preview: exact geometry and assignments, reduced texture resolution'
js=json.dumps(doc,separators=(',',':')).encode();js+=b' '*((-len(js))%4)
out=struct.pack('<III',0x46546c67,2,28+len(js)+len(chunks))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(chunks),0x004e4942)+chunks
assert len(out)<95_000_000, f'Preview exceeds web size budget: {len(out)}'
assert doc['meshes']==original['meshes'] and doc['nodes']==original['nodes']
for old,new in zip(original['accessors'],doc['accessors']):
    a=dict(old);b=dict(new);a.pop('bufferView',None);b.pop('bufferView',None);assert a==b
    if 'bufferView' in old:
        ov=original['bufferViews'][old['bufferView']];nv=newviews[new['bufferView']]
        assert binary[ov.get('byteOffset',0):ov.get('byteOffset',0)+ov['byteLength']]==chunks[nv['byteOffset']:nv['byteOffset']+nv['byteLength']]
for a,b in zip(original['materials'],doc['materials']):
    b=dict(b);b.pop('extras');assert a==b
triangles=sum(original['accessors'][p['indices']]['count']//3 if 'indices' in p else original['accessors'][p['attributes']['POSITION']]['count']//3 for m in original['meshes'] for p in m['primitives'])
vertices=sum(original['accessors'][p['attributes']['POSITION']]['count'] for m in original['meshes'] for p in m['primitives'])
metrics={'scene':'Bryggen','source_file':SOURCE.name,'source_sha256':hashlib.sha256(raw).hexdigest(),'source_bytes':len(raw),'metadata_source':META.name,'metadata_sha256':hashlib.sha256(META.read_bytes()).hexdigest(),'mesh_definitions':len(doc['meshes']),'mesh_instances':sum('mesh' in x for x in doc['nodes']),'material_definitions':len(doc['materials']),'vertex_entries':vertices,'triangle_count':triangles,'preview_triangle_count':triangles,'preview_bytes':len(out),'preview_file':'bryggen-ue-preview.glb','source_images':len(doc['images']),'unique_preview_image_payloads':len(dedup),'max_color_texture_px':256,'max_other_texture_px':128,'metadata_matched_materials':len(material_index),'material_classes':dict(Counter(m['material_type'] for m in material_index)),'validation':{'geometry_accessor_bytes_identical':True,'nodes_and_transforms_identical':True,'primitive_material_assignments_identical':True,'pbr_material_parameters_identical':True},'preview_method':'UE export retained without decimation or mesh merging. All geometry buffers, normals, UVs, transforms, material indices and PBR parameters preserved. PNG colour textures reduced to at most 256px; other maps to 128px; identical resized images share storage. Runtime hides the sky sphere and exported scene lights for framing. Material classes and physical values copied from source metadata; only exporter suffixes removed for matching.','physical_properties_note':'Values are source annotations, not measured or frequency-calibrated properties. Unknown labels are preserved.'}
(ROOT/'bryggen-ue-preview.glb').write_bytes(out)
compressed=gzip.compress(out,compresslevel=9,mtime=0)
(ROOT/'bryggen-ue-preview.glb.gz').write_bytes(compressed)
metrics['download_bytes']=len(compressed)
metrics['preview_method']=metrics['preview_method'].replace('PNG colour textures','WebP colour textures (quality 85)').replace('other maps to 128px','other maps to 128px (lossless WebP after resizing)')+' Gzip transport is lossless; browsers decompress before loading.'
(ROOT/'metrics.json').write_text(json.dumps(metrics,indent=2))
(ROOT/'material-index.json').write_text(json.dumps({'source':META.name,'matching':'Exact material basename after removing _bergen_norway_node_N or _SurfaceArea_w-N exporter suffix.','materials':material_index},indent=2))
print(json.dumps(metrics,indent=2))
