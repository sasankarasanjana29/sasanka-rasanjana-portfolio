"""Screens cut from the Figma boards have their own Dynamic Island drawn in.
Inside the site's iPhone frame (which has its own island) that shows two, so
find the drawn island (a dark pill, centred, near the top) and paint it with
the colour beside it. Run from Portfolio/ after the cut scripts."""
from PIL import Image, ImageDraw
import numpy as np, glob, subprocess
import os, tempfile

TMP = os.path.join(tempfile.gettempdir(), 'portfolio-isl.png')
files = sorted(glob.glob('site/img/screens/*.webp')) + sorted(glob.glob('site/img/apps/keells-*.webp'))
fixed = 0
for f in files:
    im = Image.open(f).convert('RGB')
    w, h = im.size
    if not 0.42 <= w / h <= 0.5:
        continue  # only whole phone screens
    a = np.asarray(im).astype(int)
    top = int(h * 0.07)
    x0c, x1c = int(w * 0.25), int(w * 0.75)
    dark = a[:top, x0c:x1c].sum(axis=2) < 110
    rows = np.where(dark.sum(axis=1) > w * 0.12)[0]
    if len(rows) == 0:
        continue
    cols = np.where(dark[rows.min():rows.max() + 1].sum(axis=0) > 0)[0]
    bx0, bx1 = x0c + cols.min(), x0c + cols.max()
    by0, by1 = rows.min(), rows.max()
    bw, bh = bx1 - bx0, by1 - by0
    centred = abs((bx0 + bx1) / 2 - w / 2) < w * 0.06
    if not (w * 0.18 < bw < w * 0.42 and 4 < bh < h * 0.05 and centred):
        continue
    # the colour just left of the pill is the status bar behind it
    sample = tuple(int(v) for v in a[(by0 + by1) // 2, max(0, bx0 - 8)])
    ImageDraw.Draw(im).rounded_rectangle((bx0 - 3, by0 - 3, bx1 + 3, by1 + 3), radius=bh, fill=sample)
    im.save(TMP)
    subprocess.run(['cwebp', '-quiet', '-q', '80', '-m', '6', TMP, '-o', f])
    fixed += 1
print('islands removed:', fixed, 'of', len(files))
