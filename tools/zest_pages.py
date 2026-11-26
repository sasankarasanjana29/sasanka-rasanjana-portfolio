"""SUPERSEDED: Portfolio/covers/zestbowls holds clean exports from the designer; use those.
ZestBowls web pages, cut from raw/cases/zest-03.png. That board is a
256-colour image, so its soft shadows came out as flat blotches. Here the
light, colourless areas (where the shadows live) are smoothed with a blur
that only mixes light pixels, so text and coloured UI keep their edges and
no grey halo forms around them. Run from Portfolio/."""
from PIL import Image, ImageFilter
import numpy as np, subprocess
import os, tempfile

Image.MAX_IMAGE_PIXELS = None
TMP = os.path.join(tempfile.gettempdir(), 'portfolio-zp.png')
PAGES = {'zest-landing': (264, 732, 2594, 5724), 'zest-cart': (264, 6048, 2594, 7958)}
RADIUS = 9


def smooth_light(im):
    a = np.asarray(im).astype(np.float32)
    mx, mn = a.max(axis=2), a.min(axis=2)
    light = (mn >= 222) & (mx - mn <= 10)          # white, greys and shadow tones only
    m = light.astype(np.float32)
    w = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(RADIUS))).astype(np.float32) / 255
    out = a.copy()
    for c in range(3):
        ch = Image.fromarray(np.clip(a[:, :, c] * m, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(RADIUS))
        blur = np.asarray(ch).astype(np.float32) / np.maximum(w, 1e-3)
        out[:, :, c] = np.where(light & (w > 0.6), blur, a[:, :, c])
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


src = Image.open('raw/cases/zest-03.png').convert('RGB')
for name, box in PAGES.items():
    c = smooth_light(src.crop(box))
    c = c.resize((1600, round(c.height * 1600 / c.width)), Image.LANCZOS)
    c.save(TMP)
    subprocess.run(['cwebp', '-quiet', '-q', '82', '-m', '6', TMP, '-o', f'site/img/screens/{name}.webp'])
    print(name, c.size)
