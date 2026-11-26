"""Keells: show the About, colour, UI kit and final-look boards whole (cutting
pieces out of them clipped their edges), flattened onto white so transparent
rounded corners never turn black; and paint the black device-frame corners
left on the Keells phone screens with the screen's own top or bottom colour.
Run from Portfolio/ (any time; it only touches Keells files)."""
from PIL import Image
import numpy as np, subprocess, glob
import os, tempfile

Image.MAX_IMAGE_PIXELS = None
TMP = os.path.join(tempfile.gettempdir(), 'portfolio-kf.png')

for f in sorted(glob.glob('site/img/apps/keells-[0-9][0-9].webp')):
    im = Image.open(f).convert('RGB'); a = np.asarray(im).copy(); h, w = a.shape[:2]
    cw, ch = int(w * 0.16), int(h * 0.08)
    top, bot = a[3, w // 2].copy(), a[h - 4, w // 2].copy()
    for (ys, xs, fill) in ((slice(0, ch), slice(0, cw), top), (slice(0, ch), slice(w - cw, w), top),
                           (slice(h - ch, h), slice(0, cw), bot), (slice(h - ch, h), slice(w - cw, w), bot)):
        region = a[ys, xs]
        dark = region.astype(int).sum(axis=2) < 120
        region[dark] = fill
    Image.fromarray(a).save(TMP)
    subprocess.run(['cwebp', '-quiet', '-q', '80', '-m', '6', TMP, '-o', f])
print('corners painted')
