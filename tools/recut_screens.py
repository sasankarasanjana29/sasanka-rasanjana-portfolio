"""Re-cuts every whole phone screen from the full-size Figma boards
(raw/cases/*.png), so screens are sharp and never lose an edge.

Each rough box (2000px-board space) comes from raw/full/screens.json or the
hand list in tools/fix_trust_screens.py. On the full-size board the screen's
edge is where the soft drop shadow (getting darker towards the screen) meets
the screen itself: a sudden jump in colour. The left and right edges are read
along the status-bar rows, the top edge down the middle column, and the
height follows from the iPhone proportions.
Run from Portfolio/, then tools/strip_island.py, then tools/build_cases.py."""
from PIL import Image
import numpy as np, json, subprocess, re, sys
import os, tempfile

Image.MAX_IMAGE_PIXELS = None
TMP = os.path.join(tempfile.gettempdir(), 'portfolio-recut.png')
OUT_W = 720
RATIO = 852 / 393  # iPhone screen height / width


def screenish(px):
    """True where a pixel belongs to a screen: anything but the board's
    colourless light grey (panel and drop shadow, 236-251)."""
    px = px.astype(int)
    mx, mn = px.max(axis=-1), px.min(axis=-1)
    board = (mx - mn < 12) & (px.mean(axis=-1) >= 236) & (px.mean(axis=-1) <= 253.5)
    return ~board


def edge_in(col):
    """Index where a run of drop shadow (colourless, 236-251) jumps sharply
    into the screen: the screen's outer edge, seen from outside."""
    c = col.astype(int)
    mean = c.mean(axis=-1); flat = (c.max(axis=-1) - c.min(axis=-1)) < 12
    shadow = flat & (mean >= 226) & (mean <= 251.5)
    jump = np.abs(np.diff(c, axis=0)).sum(axis=-1) >= 15
    for i in range(1, len(c)):
        if shadow[i - 1] and jump[i - 1] and not shadow[i]:
            return i
        # a dimmed screen (dark overlay) or coloured header after a shadow run
        if shadow[i - 1] and not shadow[i] and abs(mean[i] - mean[i - 1]) >= 25:
            return i
    return None


def refine(a, x0, y0, x1, y1, k):
    pad = round(40 * k)
    w = x1 - x0
    # top: down a column a third of the way in (clear of the drawn island)
    cx = x0 + w // 3
    col = screenish(a[max(0, y0 - pad):y0 + pad, cx])
    hits = np.where(col)[0]
    top = max(0, y0 - pad) + int(hits[0]) if len(hits) else y0
    # sides: a band just under the status bar, where the screen's own
    # background runs edge to edge; keep the run that holds the centre
    lefts, rights = [], []
    for f in (0.038, 0.042, 0.046, 0.05):
        y = top + round(f * w * RATIO)
        xs = max(0, x0 - pad)
        row = screenish(a[y, xs:x1 + pad])
        c = (x0 + x1) // 2 - xs
        if not row[c]:
            continue
        l = c
        gap = 0
        while l > 0 and gap <= 3:
            l -= 1; gap = 0 if row[l] else gap + 1
        r = c
        gap = 0
        while r < len(row) - 1 and gap <= 3:
            r += 1; gap = 0 if row[r] else gap + 1
        lefts.append(xs + l + 4); rights.append(xs + r - 4)
    if lefts:
        left, right = int(np.median(lefts)), int(np.median(rights))
    else:
        left, right = x0, x1
    if not 0.85 * w < right - left < 1.08 * w:
        left, right = x0, x1
    return left, top, right, top + round((right - left) * RATIO)


def boxes():
    out = {}
    for board, items in json.load(open('raw/full/screens.json')).items():
        for it in items:
            x0, y0, x1, y1 = it['box']
            if 0.42 <= (x1 - x0) / (y1 - y0) <= 0.5:
                out[it['src']] = (board, (x0, y0, x1, y1))
    src = open('tools/fix_trust_screens.py').read()
    ns = {}
    exec(src[:src.index('def snap')], ns)  # COLS and BOXES only
    for board, items in ns['BOXES'].items():
        for name, box in items.items():
            out[f'img/screens/{board}-{name}.webp'] = (board, box)
    return out


def columns(a, items, k):
    """Exact screen columns for one board: where the band under the status
    bar is screen (not board grey) for most of the board's screens."""
    votes = np.zeros(a.shape[1]); n = 0
    for x0, y0, x1, y1 in items:
        h = y1 - y0
        band = a[y0 + int(0.04 * h):y0 + int(0.07 * h):max(1, int(0.004 * h))]
        votes += screenish(band).mean(axis=0); n += 1
    v = votes / max(n, 1)
    on = v > 0.6
    runs, x = [], 0
    while x < len(on):
        if on[x]:
            s0 = x
            while x < len(on) and on[x]: x += 1
            if x - s0 > 200: runs.append((s0, x))
        x += 1
    return runs


only = sys.argv[1:]
allb = boxes()
by_board = {}
for dst, (board, box) in allb.items():
    by_board.setdefault(board, []).append((dst, box))
cache = {}
for board in sorted(by_board):
    todo = [(d, b) for d, b in by_board[board] if not only or any(o in d for o in only)]
    if not todo:
        continue
    src_im = Image.open(f'raw/cases/{board}.png').convert('RGBA')
    im = Image.new('RGB', src_im.size, (255, 255, 255)); im.paste(src_im, mask=src_im.split()[3]); del src_im
    a = np.asarray(im).astype(np.int16); k = im.width / 2000
    full = [tuple(round(v * k) for v in b) for _, b in by_board[board]]
    plan = []
    for dst, box in sorted(todo):
        x0, y0, x1, y1 = [round(v * k) for v in box]
        cx = (x0 + x1) // 2
        same_row = [b for b in full if abs(b[1] - y0) < 0.1 * (y1 - y0)]
        cols = columns(a, same_row, k)
        col = [c for c in cols if c[0] <= cx < c[1]]
        left, right = col[0] if col else (x0, x1)
        if not 0.8 * (x1 - x0) < right - left < 1.15 * (x1 - x0):
            left, right = x0, x1
        # top and bottom: where the drop shadow jumps into the screen, read down
        # (and up) a column a third of the way in, clear of island and home bar
        pad = round(60 * k)
        cx3 = left + (right - left) // 3
        t = edge_in(a[max(0, y0 - pad):y0 + pad, cx3])
        top = max(0, y0 - pad) + t if t is not None else y0
        up = a[min(a.shape[0] - 1, y1 + pad):max(0, y1 - pad):-1, cx3]
        bb = edge_in(up)
        bottom = min(a.shape[0] - 1, y1 + pad) - bb + 1 if bb is not None else y1
        # sides: the shadow-to-screen jump along rows just under the rounded
        # corners (status bar and header, solid white or brand colour there);
        # the middle value of those rows
        h = bottom - top
        ps = round(30 * k)
        ls, rs = [], []
        for f in (0.035, 0.045, 0.055, 0.065, 0.075):
            y = top + int(f * h)
            l = edge_in(a[y, max(0, left - ps):left + 2 * ps])
            if l is not None: ls.append(max(0, left - ps) + l)
            seg = a[y, max(0, right - 2 * ps):min(a.shape[1], right + ps)][::-1]
            r = edge_in(seg)
            if r is not None: rs.append(min(a.shape[1], right + ps) - r)
        if len(ls) >= 2: left = int(np.median(ls))
        if len(rs) >= 2: right = int(np.median(rs))
        plan.append((dst, left, top, right, bottom))
    # every screen on a board is the same width; an outlier picked up board margin
    for dst, left, top, right, bottom in plan:
        row = [p_ for p_ in plan if abs(p_[2] - top) < 0.3 * (bottom - top)]
        med = float(np.median([r - l for _, l, _, r, _ in row]))
        medh = float(np.median([b - t for _, _, t, _, b in row]))
        if len(row) >= 3 and abs((right - left) - med) > 0.015 * med:
            right = left + round(med)
        if len(row) >= 3 and abs((bottom - top) - medh) > 0.015 * medh:
            bottom = top + round(medh)
        b = (left, top, right, bottom)
        crop = im.crop(b)
        crop = crop.resize((OUT_W, round(crop.height * OUT_W / crop.width)), Image.LANCZOS) if crop.width > OUT_W else crop
        crop.save(TMP)
        subprocess.run(['cwebp', '-quiet', '-q', '82', '-m', '6', TMP, '-o', 'site/' + dst])
        print(' ', dst.split('/')[-1], b)
