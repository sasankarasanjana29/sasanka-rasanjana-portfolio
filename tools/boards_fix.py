"""Whole-board images for the case pages (Keells and ZestBowls boards, the
TrustBank banner): flattened onto white, then trimmed just inside the board's
own rounded panel so no rim, dark corner or patch shows. The page rounds the
corners itself. Run from Portfolio/ after cut_screens.py (it rewrites
trust-10-01 in place and writes *-board.webp)."""
from PIL import Image
import subprocess
import os, tempfile

Image.MAX_IMAGE_PIXELS = None
TMP = os.path.join(tempfile.gettempdir(), 'portfolio-bf.png')
INSET = 0.004  # shave the anti-aliased edge; the page rounds the corners


def flat(path):
    src = Image.open(path).convert('RGBA')
    im = Image.new('RGB', src.size, (255, 255, 255)); im.paste(src, mask=src.split()[3])
    return im


def save(im, out, inset=INSET):
    w, h = im.size; d = round(min(w, h) * inset)
    im = im.crop((d, d, w - d, h - d))
    if im.width > 1600:
        im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
    im.save(TMP)
    subprocess.run(['cwebp', '-quiet', '-q', '80', '-m', '6', TMP, '-o', out])
    print(out, im.size)


for name in ('keells-02', 'keells-03', 'keells-05', 'keells-06', 'zest-02', 'zest-03', 'zest-04'):
    save(flat(f'raw/cases/{name}.png'), f'site/img/screens/{name}-board.webp')

# the TrustBank banner: cut from its board with the rim, so trim the rim off
src = 'site/img/screens/trust-10-01.webp'
if Image.open(src).width == 1600:  # a fresh cut (trimmed ones are narrower)
    save(Image.open(src).convert('RGB'), src, 0.03)
