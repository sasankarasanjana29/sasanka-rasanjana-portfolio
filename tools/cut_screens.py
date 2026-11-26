"""Finds every individual app screen on the Framer boards and saves each one
as its own WebP, so the case pages can lay screens out in code.
A screen is a large connected shape that differs from the board panel's grey.
Run from Portfolio/: python3 tools/cut_screens.py"""
from PIL import Image
import numpy as np, json, os, subprocess, glob
import os, tempfile
from collections import deque

Image.MAX_IMAGE_PIXELS = None
OUT = 'site/img/screens'
TMP = os.path.join(tempfile.gettempdir(), 'portfolio-scr.png')
S = 6  # work on a 1/6 grid

ocr = {}
cur = None
for line in open('raw/full/ocr.txt'):
    if line.startswith('## '):
        cur = line[3:].split(' h=')[0][:-4]; ocr[cur] = []
    else:
        p = line.rstrip('\n').split('\t')
        if len(p) == 3: ocr[cur].append((int(p[0]), int(p[1]), p[2]))


def components(mask):
    h, w = mask.shape
    seen = np.zeros_like(mask, bool); boxes = []
    for y in range(h):
        row = mask[y]
        for x in np.where(row & ~seen[y])[0]:
            if seen[y, x]: continue
            q = deque([(y, x)]); seen[y, x] = True
            y0 = y1 = y; x0 = x1 = x; n = 0
            while q:
                cy, cx = q.popleft(); n += 1
                y0, y1, x0, x1 = min(y0, cy), max(y1, cy), min(x0, cx), max(x1, cx)
                for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                    if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True; q.append((ny, nx))
            boxes.append((x0, y0, x1 + 1, y1 + 1, n))
    return boxes


for f in glob.glob(f'{OUT}/*.webp'): os.remove(f)
result = {}
for f in sorted(glob.glob('raw/full/*.png')):
    name = os.path.basename(f)[:-4]
    im = Image.open(f).convert('RGB'); W, H = im.size
    small = np.asarray(im.resize((W // S, H // S), Image.BOX)).astype(int)
    # the panel grey is the most common colour that is not the page white
    flat = small.reshape(-1, 3); flat = flat[flat.sum(axis=1) < 744]
    vals, counts = np.unique(flat // 2, axis=0, return_counts=True)
    bg = vals[counts.argmax()] * 2 + 1
    full = np.asarray(im).astype(int)
    # screen = pure white or real content; panel grey and soft shadows (226..252) = gap
    diff = (full.min(axis=2) >= 253) | (full.sum(axis=2) < 678)
    greyish = ~diff
    heads = sorted((y, t) for h, y, t in ocr.get(name, []) if h >= 55)
    shots = []
    # panel columns: mostly panel grey somewhere along the board
    colgrey = greyish.mean(axis=0)
    px = np.where(colgrey > 0.25)[0]
    if len(px) == 0: px = np.arange(W)
    X0, X1 = px.min() + 4, px.max() - 4
    d = diff[:, X0:X1]
    rowgap = d.mean(axis=1) < 0.004
    def runs(gap, minlen):
        out, i, n = [], 0, len(gap)
        while i < n:
            if gap[i]: i += 1; continue
            j = i
            while j < n and not gap[j]: j += 1
            if j - i >= minlen: out.append((i, j))
            i = j
        return out
    for ry0, ry1 in runs(rowgap, 300):
        colgap = d[ry0:ry1].mean(axis=0) < 0.01
        for cx0, cx1 in runs(colgap, int(W * 0.12)):
            box = (X0 + cx0, ry0, X0 + cx1, ry1)
            bw, bh = box[2] - box[0], box[3] - box[1]
            if bw > (X1 - X0) * 0.95 and bh > 2400: continue
            if 0.38 < bw / bh < 0.56:
                crop = im.crop(box)
            else:
                # wide pieces (banners, kits) come from the full-size original so they stay sharp
                o_ = Image.open(f'raw/cases/{name}.png').convert('RGBA'); orig = Image.new('RGB', o_.size, (255, 255, 255)); orig.paste(o_, mask=o_.split()[3]); k = orig.width / W
                crop = orig.crop(tuple(round(v * k) for v in box))
            cap = 900 if 0.38 < bw / bh < 0.56 else 1600
            if crop.width > cap: crop = crop.resize((cap, round(crop.height * cap / crop.width)), Image.LANCZOS)
            ab = [t for y, t in heads if y < box[1]]
            shots.append(dict(box=box, w=crop.width, h=crop.height, kind='phone' if 0.38 < bw / bh < 0.56 else 'wide', head=ab[-1] if ab else '', crop=crop))
    shots.sort(key=lambda s: (s['box'][1] // 200, s['box'][0]))
    out = []
    for k, s in enumerate(shots):
        s['crop'].save(TMP)
        o = f'{OUT}/{name}-{k + 1:02d}.webp'
        subprocess.run(['cwebp', '-quiet', '-q', '78', '-m', '6', TMP, '-o', o])
        out.append(dict(src=o[5:], w=s['w'], h=s['h'], kind=s['kind'], head=s['head']))
    for o_, sh in zip(out, shots): o_['box'] = [int(v) for v in sh['box']]
    result[name] = out  # boxes_dump
    print(name, len(out), sorted({s['head'][:40] for s in out}))
json.dump(result, open('raw/full/screens.json', 'w'), indent=1)
