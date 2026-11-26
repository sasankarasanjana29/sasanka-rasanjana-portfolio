"""Phone screens show anywhere from ~90px to ~260px wide. One big file shrunk
7x by the browser smears the text, so every phone screen gets 300px and
540px copies and each <img> lists them in srcset; the browser then picks the
closest size for the screen it is on.
Run from Portfolio/ after build_cases.py (it rewrites site/index.html and
site/work/*.html in place, and is safe to run twice)."""
from PIL import Image
import glob, os, re, subprocess
import os, tempfile

ROOT = 'site'
TMP = os.path.join(tempfile.gettempdir(), 'portfolio-ss.png')
SIZES = '(max-width: 640px) 34vw, (max-width: 900px) 160px, 240px'


def variants(rel):
    """rel like img/screens/x.webp -> list of (path, width), smallest first."""
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p) or re.search(r'-(300|540)\.webp$', rel):
        return None
    w, h = Image.open(p).size
    if not 0.42 <= w / h <= 0.5:
        return None
    out = []
    for vw in (300, 540):
        if vw >= w:
            continue
        vrel = rel[:-5] + f'-{vw}.webp'
        vp = os.path.join(ROOT, vrel)
        if not os.path.exists(vp) or os.path.getmtime(vp) < os.path.getmtime(p):
            Image.open(p).convert('RGB').resize((vw, round(h * vw / w)), Image.LANCZOS).save(TMP)
            subprocess.run(['cwebp', '-quiet', '-q', '80', '-m', '6', TMP, '-o', vp])
        out.append((vrel, vw))
    out.append((rel, w))
    return out


def rewrite(html, prefix):
    def fix(m):
        tag = m.group(0)
        if 'srcset=' in tag or 'data-full' in tag:  # web pages stay full size
            return tag
        sm = re.search(r'\b(data-src|src)="(\.\./)?(img/[^"]+\.webp)"', tag)
        if not sm:
            return tag
        v = variants(sm.group(3))
        if not v:
            return tag
        pre = sm.group(2) or ''
        attr = 'data-srcset' if sm.group(1) == 'data-src' else 'srcset'
        ss = ', '.join(f'{pre}{r} {w}w' for r, w in v)
        return tag[:-1].rstrip('/').rstrip() + f' {attr}="{ss}" sizes="{SIZES}">'
    return re.sub(r'<img\b[^>]*>', fix, html)


for f in [os.path.join(ROOT, 'index.html')] + sorted(glob.glob(os.path.join(ROOT, 'work', '*.html'))):
    s = open(f).read()
    n = rewrite(s, '')
    open(f, 'w').write(n)
    print(f, n.count('srcset=') + n.count('data-srcset='))
