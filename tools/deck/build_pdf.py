"""Render deck.html to Sasanka_Rasanjana_Portfolio.pdf at a sensible size.

Chrome embeds WebP/PNG images losslessly in a PDF, which made the deck
about 10 MB. This copies every opaque image to a JPEG (images with real
transparency, like the phone frame and logos, are left as they are),
points a temporary copy of the deck at those, and prints that.

Usage: python3 build_pdf.py
"""
import hashlib
import re
import subprocess
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
SRC = HERE / "deck.html"
TMP_HTML = HERE / ".deck-print.html"
IMG_DIR = HERE / ".print-img"
OUT = HERE / "Sasanka_Rasanjana_Portfolio.pdf"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
MAX_SIDE = 1800  # pixels; nothing in the deck is shown larger than ~1000px wide
REF = re.compile(r'(src="|url\()([^")]+\.(?:webp|png|jpe?g))')


def has_transparency(im):
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        return im.convert("RGBA").getchannel("A").getextrema()[0] < 255
    return False


def to_jpeg(rel):
    path = (HERE / rel).resolve()
    if not path.exists():
        return rel
    im = Image.open(path)
    if has_transparency(im):
        return rel
    im = im.convert("RGB")
    if max(im.size) > MAX_SIDE:
        r = MAX_SIDE / max(im.size)
        im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    name = hashlib.md5(str(path).encode()).hexdigest()[:10] + "-" + path.stem + ".jpg"
    im.save(IMG_DIR / name, quality=84, optimize=True)
    return f"{IMG_DIR.name}/{name}"


def main():
    IMG_DIR.mkdir(exist_ok=True)
    html = SRC.read_text()
    cache = {}

    def swap(m):
        rel = m.group(2)
        if rel not in cache:
            cache[rel] = to_jpeg(rel)
        return m.group(1) + cache[rel]

    TMP_HTML.write_text(REF.sub(swap, html))
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=8000", f"--print-to-pdf={OUT}",
                    TMP_HTML.as_uri()], check=True, stderr=subprocess.DEVNULL)
    swapped = sum(1 for k, v in cache.items() if k != v)
    print(f"{OUT.name}: {OUT.stat().st_size / 1e6:.1f} MB, {swapped} of {len(cache)} images as JPEG")


if __name__ == "__main__":
    main()
