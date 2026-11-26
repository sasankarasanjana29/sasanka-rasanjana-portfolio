"""TrustBank's boards mix text and screens, and a few screens have grey app
backgrounds that the gap cutter mistakes for gaps. Here each screen gets an
approximate box (read off the 2000px board), then the box snaps to the
screen's real edges against the panel grey (249). Writes whole screens only.
Run from Portfolio/ after tools/cut_screens.py."""
from PIL import Image
import numpy as np, subprocess
import os, tempfile

Image.MAX_IMAGE_PIXELS = None
TMP = os.path.join(tempfile.gettempdir(), 'portfolio-fix.png')
COLS = [(182, 710), (732, 1262), (1283, 1820)]

BOXES = {
    'vela-04': {
        # home, search and results, then filters and the visual scan: missed by the gap cutter
        'home-1': (180, 2636, 715, 3805), 'home-2': (732, 2636, 1266, 3805), 'home-3': (1284, 2636, 1818, 3805),
        'search-1': (180, 3870, 715, 5039), 'search-2': (732, 3870, 1266, 5039), 'search-3': (1284, 3870, 1818, 5039),
    },
    'trust-08': {
        # home, accounts and quick actions
        'home-1': (*COLS[0][:1], 4864, COLS[0][1], 6037), 'home-2': (COLS[1][0], 4864, COLS[1][1], 6037), 'home-3': (COLS[2][0], 4864, COLS[2][1], 6037),
        # recipients, payment details, keypad: their tops were cut
        'pay-1': (COLS[0][0], 7878, COLS[0][1], 9047), 'pay-2': (COLS[1][0], 7878, COLS[1][1], 9047), 'pay-3': (COLS[2][0], 7878, COLS[2][1], 9047),
        # payment details, review and confirm
        'review-1': (COLS[0][0], 9732, COLS[0][1], 10901), 'review-2': (COLS[1][0], 9732, COLS[1][1], 10901), 'review-3': (COLS[2][0], 9732, COLS[2][1], 10901),
    },
    'trust-09': {
        'proof-1': (460, 525, 985, 1690), 'proof-2': (1005, 525, 1545, 1690),
        'tx-1': (175, 2240, 710, 3410), 'tx-2': (730, 2240, 1265, 3410), 'tx-3': (1285, 2240, 1820, 3410),
        'export-1': (175, 3510, 710, 4675), 'export-2': (730, 3510, 1265, 4675), 'export-3': (1285, 3510, 1820, 4675),
        'alert-1': (455, 5250, 985, 6415), 'alert-2': (1005, 5250, 1545, 6415),
    },
}


def snap(a, box, W=537, H=1169, reach=34):
    """Every screen on these boards is the same size, so slide a window of
    exactly that size around the rough box and keep the spot holding the most
    screen pixels (pure white or real content; grey and shadow count as none)."""
    m = ((a.min(axis=2) >= 253) | (a.sum(axis=2) < 678)).astype(np.int32)
    ii = np.pad(m.cumsum(0).cumsum(1), ((1, 0), (1, 0)))
    cx, cy = (box[0] + box[2]) // 2 - W // 2, (box[1] + box[3]) // 2 - H // 2
    best, at = -1, (cx, cy)
    for dy in range(-reach, reach + 1, 2):
        for dx in range(-reach, reach + 1, 2):
            x, y = cx + dx, cy + dy
            if x < 0 or y < 0 or x + W > a.shape[1] or y + H > a.shape[0]:
                continue
            v = ii[y + H, x + W] - ii[y, x + W] - ii[y + H, x] + ii[y, x]
            if v > best or (v == best and abs(dx) + abs(dy) < abs(at[0] - cx) + abs(at[1] - cy)):
                best, at = v, (x, y)
    return (at[0], at[1], at[0] + W, at[1] + H)


for board, boxes in BOXES.items():
    im = Image.open(f'raw/full/{board}.png').convert('RGB')
    a = np.asarray(im).astype(int)
    for name, box in boxes.items():
        b = snap(a, box)
        # trim strips of panel grey or shadow: a real screen edge always has some
        # white (status bar, tab bar) or real content somewhere along it
        x0, y0, x1, y1 = b
        sub = a[y0:y1, x0:x1]
        scr = (sub.min(axis=2) >= 253) | ((sub.max(axis=2) - sub.min(axis=2)) > 30) | (sub.mean(axis=2) < 200)
        cf, rf = scr.mean(axis=0), scr.mean(axis=1)
        l, r, t, btm = 0, len(cf) - 1, 0, len(rf) - 1
        # the window height already matches the screen, so only the sides get trimmed
        while l < 25 and cf[l] < 0.08: l += 1
        while r > len(cf) - 26 and cf[r] < 0.08: r -= 1
        b = (x0 + l, y0 + t, x0 + r + 1, y0 + btm + 1)
        crop = im.crop(b)
        if crop.width > 540:
            crop = crop.resize((540, round(crop.height * 540 / crop.width)), Image.LANCZOS)
        crop.save(TMP)
        out = f'site/img/screens/{board}-{name}.webp'
        subprocess.run(['cwebp', '-quiet', '-q', '78', '-m', '6', TMP, '-o', out])
        print(out, b, 'ratio', round((b[2] - b[0]) / (b[3] - b[1]), 3))
