"""Prepare real dataset frames for the static project page (Pillow + NumPy)."""
from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/assets'
OUT.mkdir(parents=True, exist_ok=True)
DESKTOP = Path.home() / 'Desktop'
scenes = [('louvre', 'Dataset_Louvre'), ('bryggen', 'Dataset_Bryggen'), ('maradona', 'Dataset_Maradona')]
contact = Image.new('RGB', (1000, 3*200), '#eee')
draw = ImageDraw.Draw(contact)
manifest = []
for row, (slug, folder) in enumerate(scenes):
    base = DESKTOP / folder
    for col, cam in enumerate([1, 3, 5, 7, 9]):
        src = base / f'camera_{cam}/rgb/rgb_camera_{cam}_0000.png'
        if not src.exists(): continue
        im = Image.open(src).convert('RGB'); im.thumbnail((200, 170))
        contact.paste(im, (col*200, row*200)); draw.text((col*200+5,row*200+175), f'{slug} cam {cam}', fill='black')
qa = ROOT / '.qa'
qa.mkdir(exist_ok=True)
contact.save(qa / 'contact.jpg')
print(qa / 'contact.jpg')

import shutil
source = Path.home() / 'urmat-page-assets'
for modality in ['rgb', 'depth', 'material', 'mesh']:
    im = Image.open(source / f'louvre_ds_{modality}.png').convert('RGB')
    im.save(OUT / f'louvre-{modality}.webp', lossless=True)
for modality, folder, prefix in [('rgb','rgb','rgb'), ('depth','depth_png','depth'), ('material','segmentation_material','segmat'), ('mesh','segmentation_mesh','seg')]:
    src = DESKTOP / f'Dataset_Bryggen/camera_5/{folder}/{prefix}_camera_5_0000.png'
    Image.open(src).convert('RGB').save(OUT / f'bryggen-{modality}.webp', lossless=True)
    manifest.append({'asset': f'bryggen-{modality}.webp', 'source': str(src.relative_to(DESKTOP)), 'sha256': hashlib.sha256(src.read_bytes()).hexdigest()})
# An exact registered RGB / material-mask wipe, not synthetic camera motion.
rgb = Image.open(OUT/'louvre-rgb.webp').convert('RGB')
mask = Image.open(OUT/'louvre-material.webp').convert('RGB')
frames=[]
for fraction in list(np.linspace(0,1,24))+list(np.linspace(1,0,24)):
    frame=rgb.copy(); x=int(frame.width*fraction)
    frame.paste(mask.crop((0,0,x,frame.height)),(0,0))
    ImageDraw.Draw(frame).line((x,0,x,frame.height),fill='white',width=2)
    frames.append(frame)
frames[0].save(OUT/'louvre-material-sweep.gif',save_all=True,append_images=frames[1:],duration=85,loop=0,optimize=True)
for name in ['paper-segmentation-a.png','paper-pipeline.jpeg']:
    if (source/name).exists():
        im=Image.open(source/name).convert('RGB'); im.thumbnail((1400,1400)); im.save(OUT/(Path(name).stem+'.webp'),quality=90)
# Reproducible counts for the three local exports, scoped separately from release stats.
audit=[]
for slug, folder in scenes:
    base=DESKTOP/folder
    cameras=sorted(base.glob('camera_*'))
    counts={key:sum(len(list((cam/sub).glob(pattern))) for cam in cameras) for key,sub,pattern in [('rgb','rgb','*.png'),('depth','depth_npy','*.npy'),('material','segmentation_material','*.npy'),('metadata','metadata','*.json')]}
    audit.append({'scene':slug,'folder':folder,'cameras':len(cameras),'counts':counts})
(OUT/'local-audit.json').write_text(json.dumps({'scope':'Local Desktop exports; counts are not a census of the Zenodo release.','method':'Count files in all camera_* directories; one modality-specific file per frame.','scenes':audit},indent=2))
(OUT/'provenance.json').write_text(json.dumps({'louvre':'Aligned example images from author thesis figs/ch3/louvre_ds_*.png; original 640x480 pixels.','animation':'48-frame wipe between the same Louvre RGB and material mask; not a camera trajectory.','bryggen':manifest,'paper':'ACM MM 2025, DOI 10.1145/3746027.3758314; figure 2 and pipeline figure.'},indent=2))
print(json.dumps(audit))
