"""Cuts the strips of app screens out of each Framer board, leaving out the
board's own paragraphs (those are rewritten as real text on the case pages).
Board text is >= 38px tall in the 2000px-wide boards; UI text inside screens
is smaller, so OCR line height separates the two.
Run from Portfolio/: python3 tools/cut_bands.py"""
from PIL import Image
import numpy as np, json, os, subprocess, glob
import os, tempfile

Image.MAX_IMAGE_PIXELS = None
OUT = 'site/img/screens'
os.makedirs(OUT, exist_ok=True)
TMP = os.path.join(tempfile.gettempdir(), 'portfolio-band.png')

ocr = {}
cur = None
for line in open('raw/full/ocr.txt'):
    if line.startswith('## '):
        cur = line[3:].split(' h=')[0][:-4]; ocr[cur] = []
    else:
        p = line.rstrip('\n').split('\t')
        if len(p) == 3:
            ocr[cur].append((int(p[0]), int(p[1]), p[2]))

result = {}
import sys
for f in sorted(glob.glob('raw/full/*.png')):
    if len(sys.argv) > 1 and os.path.basename(f)[:-4] not in sys.argv[1:]: continue
    name = os.path.basename(f)[:-4]
    im = Image.open(f).convert('RGB'); a = np.asarray(im).astype(int)
    H, W = a.shape[:2]
    diff = (255 * 3 - a.sum(axis=2))
    ink = diff > 30          # content
    faint = diff > 8         # content plus soft shadows
    rows = ink.sum(axis=1) > 3
    text = np.zeros(H, bool)
    heads = []
    for h, y, t in ocr.get(name, []):
        if h >= 38:
            text[max(0, y - 12):min(H, y + h + 12)] = True
            heads.append((y, h, t))
    lab = np.where(text, 'T', np.where(rows, 'C', 'B'))
    bands, y = [], 0
    while y < H:
        if lab[y] != 'C':
            y += 1; continue
        y0 = y; last = y
        while y < H and lab[y] != 'T':
            if lab[y] == 'C': last = y
            elif y - last > 70: break
            y += 1
        if last - y0 > 220: bands.append((y0, last))
        y = max(y, last + 1)
    out = []
    for k, (y0, y1) in enumerate(bands):
        t0 = y0; t1 = y1
        while t0 > 0 and y0 - t0 < 36 and lab[t0 - 1] != 'T': t0 -= 1
        while t1 < H - 1 and t1 - y1 < 36 and lab[t1 + 1] != 'T': t1 += 1
        cols = np.where(faint[t0:t1 + 1].sum(axis=0) > 2)[0]
        x0 = max(0, cols.min() - 36); x1 = min(W, cols.max() + 37)
        crop = im.crop((x0, t0, x1, t1 + 1))
        if crop.width > 1600: crop = crop.resize((1600, round(crop.height * 1600 / crop.width)), Image.LANCZOS)
        crop.save(TMP)
        o = f'{OUT}/{name}-{k + 1}.webp'
        subprocess.run(['cwebp', '-quiet', '-q', '76', '-m', '6', TMP, '-o', o])
        above = [t for (hy, hh, t) in heads if hy < y0 and y0 - hy < 700]
        out.append(dict(src=o[5:], w=crop.width, h=crop.height, above=above[-3:]))
    result[name] = out
json.dump(result, open('raw/full/bands.json', 'w'), indent=1)
for n, v in result.items():
    print(n, len(v), [(b['w'], b['h'], ' / '.join(b['above'])[:70]) for b in v])
