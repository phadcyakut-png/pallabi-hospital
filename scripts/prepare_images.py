from PIL import Image, ImageDraw
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'source-images'
DEST=ROOT/'site/assets/images'
ORIG=ROOT/'source-images'
DEST.mkdir(parents=True,exist_ok=True)
ORIG.mkdir(parents=True,exist_ok=True)
for i in range(1,16):
    file=SRC/f'Hospital Images ({i}).jpeg'
    img=Image.open(file).convert('RGB')
    if img.width>1300: img.thumbnail((1300,1300),Image.Resampling.LANCZOS)
    img.save(DEST/f'hospital-{i:02d}.webp','WEBP',quality=82,method=6)
for key,name in [('chairman','Chairman.jpeg')]:
    file=SRC/name
    img=Image.open(file).convert('RGB')
    img.thumbnail((1000,1400),Image.Resampling.LANCZOS)
    img.save(DEST/f'{key}.webp','WEBP',quality=85,method=6)
# Remove portraits that are no longer published.
for stale in ('ceo.webp', 'managing-director.webp', 'director.webp'):
    (DEST/stale).unlink(missing_ok=True)
logo=Image.open(SRC/'Logo.jpeg').convert('RGBA')
# Keep the official circular emblem while removing the checkerboard background around it.
w,h=logo.size
bbox=(round(w*.045),round(h*.045),round(w*.955),round(h*.955))
logo=logo.crop(bbox)
S=logo.width
mask=Image.new('L',(S,S),0)
draw=ImageDraw.Draw(mask)
draw.ellipse((1,1,S-2,S-2),fill=255)
logo.putalpha(mask)
logo.thumbnail((520,520),Image.Resampling.LANCZOS)
logo.save(DEST/'logo.png',optimize=True)
logo.resize((64,64),Image.Resampling.LANCZOS).save(ROOT/'site/favicon.png',optimize=True)
# Generate gallery photocards and smaller thumbnails from approved originals.
from PIL import ImageOps
import json
cards=json.loads((ROOT/'content/photocards.json').read_text(encoding='utf-8'))
for card in cards:
    source=SRC/'photocards'/card['file']
    if not source.is_file():
        raise FileNotFoundError(f'Missing gallery source image: {source}')
    original=ImageOps.exif_transpose(Image.open(source)).convert('RGB')
    large=original.copy()
    large.thumbnail((1600,2000),Image.Resampling.LANCZOS)
    stem=Path(card['file']).stem
    large.save(DEST/f'{stem}.webp','WEBP',quality=87,method=6)
    preview=original.copy()
    preview.thumbnail((760,980),Image.Resampling.LANCZOS)
    preview.save(DEST/f'{stem}-preview.webp','WEBP',quality=76,method=6)
print(f'Prepared {len(cards)} photo-card originals and thumbnails')
print('Prepared 17 images and favicon')
