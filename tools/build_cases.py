"""Builds site/work/*.html. Words are written here; images are the single
screens cut by tools/cut_screens.py (site/img/screens) plus a few board
pieces for colour, type and UI kits.
Run from Portfolio/: python3 tools/build_cases.py"""
import json, html, os
from PIL import Image

ROOT = os.path.join(os.path.dirname(__file__), '..', 'site')
e = html.escape
ARROW_L = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 12H5M11 6l-6 6 6 6"/></svg>'
ARROW_R = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
ARROW_OUT = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg>'


def size(src):
    w, h = Image.open(os.path.join(ROOT, src)).size
    return w, h


def scr(name):
    return f'img/screens/{name}.webp'


def img(src, alt, cls=''):
    w, h = size(src)
    c = f' class="{cls}"' if cls else ''
    return f'<img{c} src="../{src}" alt="{e(alt)}" width="{w}" height="{h}" loading="lazy" decoding="async">'


def rail(title, bullets, shots, alt, wide=False):
    shots = [x if x.startswith('img/') else f'img/{x}.webp' for x in shots]
    fc = ' class="wide"' if wide else ''
    figs = ''.join(f'<figure{fc}>{img(s, f"{alt}, screen {i + 1}")}</figure>' for i, s in enumerate(shots))
    lis = ''.join(f'<li>{e(b)}</li>' for b in bullets)
    return f'''<div class="group" data-reveal>
      <div class="group-head"><h3>{e(title)}</h3><ul>{lis}</ul>
        <div class="rail-btns"><button aria-label="Previous screens">{ARROW_L}</button><button aria-label="Next screens">{ARROW_R}</button></div></div>
      <div class="rail" tabindex="0" aria-label="{e(title)} screens">{figs}</div>
    </div>'''


def whole(n):
    if not os.path.exists(os.path.join(ROOT, f'img/{n}.webp')):
        return False
    w, h = size(f'img/{n}.webp')
    return 0.43 <= w / h <= 0.48


def phones(title, bullets, names, alt):
    names = [n if '/' in n else f'apps/{n}' for n in names]
    names = [n for n in names if whole(n)]
    figs = ''.join(f'<figure><div class="phone"><div class="screen"><img src="../img/{n}.webp" alt="{e(alt)}, screen {i + 1}" loading="lazy" decoding="async"></div></div></figure>' for i, n in enumerate(names))
    lis = ''.join(f'<li>{e(b)}</li>' for b in bullets)
    return f'''<div class="group" data-reveal>
      <div class="group-head"><h3>{e(title)}</h3><ul>{lis}</ul></div>
      <div class="rail phones">{figs}</div>
    </div>'''


def proto(url, poster, label):
    ph = ''.join(f'<div class="phone"><div class="screen"><img src="../img/{n}.webp" alt="" loading="lazy"></div></div>' for n in poster)
    return f'''<div class="proto" data-reveal data-src="{e(url)}">
        <div class="proto-text"><h2>Try the live prototype</h2><p>The real clickable prototype from Figma. Tap through it like the app.</p>
          <button class="btn btn-dark proto-load">Open the prototype {ARROW_R}</button></div>
        <div class="proto-media sc-phones">{ph}</div>
      </div>'''


def demo(name, title, steps):
    """A real recording in the phone frame, with story-style chapter bars under it
    that fill as the clip plays. Tap a chapter to replay just that part.
    steps = [(start_seconds, label, text)]."""
    if not os.path.exists(os.path.join(ROOT, f'video/{name}.mp4')):
        return ''
    li = ''.join(f'<li data-at="{t}"><button type="button"><span class="bar"><i></i></span><span class="k">{label}</span><span class="d">{e(text)}</span></button></li>' for t, label, text in steps)
    return f'''<div class="demo story" data-reveal>
      <div class="demo-copy"><h2>{e(title)}</h2><p class="sub">A real screen recording from the iPhone simulator. Tap a chapter to replay it.</p></div>
      <div class="demo-phone"><div class="phone"><div class="screen"><video src="../video/{name}.mp4" poster="../video/{name}-poster.webp" muted loop playsinline preload="none" aria-label="{e(title)}"></video></div></div></div>
      <div class="demo-ctl"><ol class="demo-steps">{li}</ol><p class="demo-caption" aria-live="polite">{e(steps[0][2])}</p></div>
    </div>'''


def web(title, bullets, shot, alt, full=False):
    """A web page as a flow card: notes on the left, the page in a browser
    window on the right at a readable size. A long page is cut to its top
    with a fade, and opens whole in the lightbox."""
    lis = ''.join(f'<li>{e(b)}</li>' for b in bullets)
    more = '<button type="button" class="web-more">See the full page</button>' if full else ''
    cls = 'frame web-frame is-capped' if full else 'frame web-frame'
    return f'''<div class="group webcard" data-reveal>
      <div class="group-head"><h3>{e(title)}</h3><ul>{lis}</ul></div>
      <div class="{cls}"><div class="frame-bar"><i></i><i></i><i></i><span>zestbowls.lk</span></div><div class="frame-body">{img(shot, alt).replace("<img ", "<img data-full ", 1)}</div>{more}</div>
    </div>'''


def plain(title, bullets, shots, alt):
    pics = ''.join(img(s, f'{alt}, part {i + 1}', 'plain') for i, s in enumerate(shots))
    lis = ''.join(f'<li>{e(b)}</li>' for b in bullets)
    return f'''<div class="group" data-reveal>
      <div class="group-head"><h3>{e(title)}</h3><ul>{lis}</ul></div>
      <div class="shots">{pics}</div>
    </div>'''


def tiles(items, numbered=False, cols=3):
    out = []
    for n, (t, b) in enumerate(items):
        body = '<ul>' + ''.join(f'<li>{e(x)}</li>' for x in b) + '</ul>' if isinstance(b, list) else f'<p>{e(b)}</p>'
        k = f'<span class="k">{n + 1:02d}</span>' if numbered else ''
        out.append(f'<div class="tile" data-reveal>{k}<h3>{e(t)}</h3>{body}</div>')
    return f'<div class="grid{cols}">' + ''.join(out) + '</div>'


def stats(items):
    return '<div class="stat-row" data-reveal>' + ''.join(f'<div><b>{e(a)}</b><span>{e(b)}</span></div>' for a, b in items) + '</div>'


def callout(t, p):
    return f'<div class="callout" data-reveal><h3>{e(t)}</h3><p>{e(p)}</p></div>'


def bars(title, base, rows, note=None):
    """A small bar chart. Bars start at zero and share one scale, so their lengths compare honestly."""
    top = max(v for _, v in rows) / 0.92
    li = ''.join(f'<li><span class="bl">{e(l)}</span><b>{v}%</b><span class="bt"><i style="--w:{v / top * 100:.1f}%"></i></span></li>' for l, v in rows)
    n = f'<p class="bars-note">{e(note)}</p>' if note else ''
    return f'<figure class="bars" data-reveal><figcaption><h3>{e(title)}</h3><p>{e(base)}</p></figcaption><ol>{li}</ol>{n}</figure>'


def cuts(intro, items):
    """What I tried and took out, and what replaced it. Each item: (title, tried, why, instead). Shown as compact rows."""
    return f'<h2>What I cut and why</h2><p class="sub">{e(intro)}</p>' + rows([(t, why, inst) for t, tried, why, inst in items], keys=('Cut', 'Now'))


def annotated(title, intro, screens):
    """Screens with notes that point at the part they explain, and a switch to hide them.
    screens: [(image, [(y as a share of the screenshot height, 'l' or 'r', title, text)])]"""
    figs = []
    for name, notes in screens:
        lis = ''.join(f'<li class="{side}" style="--y:{2.5 + y * 95:.1f}%"><b>{e(t)}</b><span>{e(d)}</span></li>' for y, side, t, d in notes)
        figs.append(f'<figure class="ann-fig"><div class="phone"><div class="screen"><img src="../img/apps/{name}.webp" alt="{e(title)}" loading="lazy"></div></div><ol class="ann-notes">{lis}</ol></figure>')
    return (f'<div class="ann-head" data-reveal><div><h2>{e(title)}</h2><p class="sub">{e(intro)}</p></div>'
            f'<button class="ann-toggle" type="button" aria-pressed="true">Hide notes</button></div>'
            f'<div class="ann">' + ''.join(figs) + '</div>')


def viewer(tabs, app='Pouch'):
    """Many screen groups in one block: tabs above, flat phones with a short caption under each.
    It moves to the next tab by itself until someone picks one. More than three screens become a
    sideways row. tabs: [(label, captions, images)]; images without a folder are read from img/apps."""
    btns, panels = [], []
    for i, (label, lines, names) in enumerate(tabs):
        on = ' is-on' if i == 0 else ''
        btns.append(f'<button type="button" class="vw-tab{on}" role="tab" aria-selected="{str(i == 0).lower()}">{e(label)}</button>')
        figs = ''
        for k, n in enumerate(names):
            src = n if '/' in n else f'apps/{n}'
            cap = lines[k] if k < len(lines) else ''
            alt = f'{app}, {cap or label}'
            figs += f'<figure><div class="phone"><div class="screen"><img src="../img/{src}.webp" alt="{e(alt)}" loading="lazy" decoding="async"></div></div>' + (f'<figcaption><span class="n">{k + 1}</span>{e(cap)}</figcaption>' if cap else '') + '</figure>'
        rail = ' is-rail' if len(names) > 3 else ''
        panels.append(f'<div class="vw-panel{on}" role="tabpanel"><div class="vw-row{rail}">{figs}</div></div>')
    return f'<div class="viewer" data-reveal><div class="vw-tabs" role="tablist">{"".join(btns)}</div>{"".join(panels)}<div class="vw-clock"><i></i></div></div>'


ICON = {
    # simple line icons drawn for this site, 24px grid, stroke follows the text colour
    'target': '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r="0.6"/>',
    'alert': '<path d="M12 4 21 19H3z"/><path d="M12 10v4M12 16.5v.5"/>',
    'nobank': '<path d="M4 9 12 4l8 5M5 9v8M9 9v8M15 9v8M19 9v8M3 20h18"/><path d="M3 3l18 18"/>',
    'gift': '<rect x="4" y="9" width="16" height="11" rx="2"/><path d="M12 9v11M4 13h16M12 9c-2-4-6-3-5-1s5 1 5 1 4 1 5-1-3-3-5 1"/>',
    'shield': '<path d="M12 3l7 3v5c0 5-3 8-7 10-4-2-7-5-7-10V6z"/><path d="m9 12 2 2 4-4"/>',
    'globe': '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c3 3.5 3 13.5 0 17M12 3.5c-3 3.5-3 13.5 0 17"/>',
    'bug': '<rect x="8" y="7" width="8" height="12" rx="4"/><path d="M12 7V4M8 11H4M8 15H4M16 11h4M16 15h4M9 5l1.5 2M15 5l-1.5 2"/>',
    'tangle': '<path d="M4 8h10l-3-3M20 16H10l3 3"/><path d="M14 8c3 0 3 8 6 8M10 16c-3 0-3-8-6-8"/>',
    'clock': '<circle cx="12" cy="12" r="8.5"/><path d="M12 7v5l3 2"/>',
    'palette': '<path d="M12 3a9 9 0 1 0 0 18c1.5 0 2-1 1.5-2s0-2 1.5-2H18a3 3 0 0 0 3-3c0-6-4-11-9-11z"/><circle cx="7.5" cy="11" r="1"/><circle cx="11" cy="7" r="1"/><circle cx="15.5" cy="8.5" r="1"/>',
    'code': '<path d="m8 8-4 4 4 4M16 8l4 4-4 4M14 5l-4 14"/>',
    'search': '<circle cx="11" cy="11" r="6.5"/><path d="m16 16 4 4"/>',
    'store': '<path d="M5 8h14l-1 12H6z"/><path d="M9 8a3 3 0 0 1 6 0"/>',
    'calendar': '<rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 10h16M9 3v4M15 3v4"/>',
    'repeat': '<path d="M17 3l3 3-3 3M20 6H8a4 4 0 0 0-4 4v1M7 21l-3-3 3-3M4 18h12a4 4 0 0 0 4-4v-1"/>',
    'heart': '<path d="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.5A4 4 0 0 1 19 10c0 5.5-7 10-7 10z"/>',
    'user': '<circle cx="12" cy="8" r="3.5"/><path d="M5 20c1-4 4-6 7-6s6 2 7 6"/>',
    'arrow': '<path d="M5 12h14M13 6l6 6-6 6"/>',
}


def icon(name):
    return f'<svg class="ico" viewBox="0 0 24 24" aria-hidden="true">{ICON[name]}</svg>'


def iconcards(items, cls=''):
    """Cards led by an icon: (icon, title, one short line)."""
    return f'<div class="iconcards {cls}" data-reveal>' + ''.join(f'<div class="ic"><span class="ic-badge">{icon(i)}</span><b>{e(t)}</b><span>{e(d)}</span></div>' for i, t, d in items) + '</div>'


def statcards(items):
    """Big value, small label, icon in the corner: (icon, value, label)."""
    return '<div class="statcards" data-reveal>' + ''.join(f'<div class="sc"><span class="ic-badge">{icon(i)}</span><b>{e(v)}</b><span>{e(l)}</span></div>' for i, v, l in items) + '</div>'


def beforeafter(intro, items):
    """Cuts as a tiny before and after of the same screen part: (title, before_html, after_html, why)."""
    rows = ''.join(f'<div class="ba"><div class="ba-top"><b>{e(t)}</b><span>{e(w)}</span></div><div class="ba-pair"><div class="ba-side is-before"><small>Before</small>{b}</div><div class="ba-side is-now"><small>Now</small>{a}</div></div></div>' for t, b, a, w in items)
    return f'<h2>What I cut and why</h2><p class="sub">{e(intro)}</p><div class="bas" data-reveal>{rows}</div>'


def specrow(items):
    """Short label and value pairs in one row, in place of a paragraph."""
    return '<dl class="spec-row" data-reveal>' + ''.join(f'<div><dt>{e(a)}</dt><dd>{e(b)}</dd></div>' for a, b in items) + '</dl>'


def bigwords(items):
    """A row of big words, one short line under each."""
    return '<div class="bigwords" data-reveal>' + ''.join(f'<div><b>{e(a)}</b><span>{e(b)}</span></div>' for a, b in items) + '</div>'


def rows(items, keys=None):
    """Compact rows: a title, then one or two short lines. items: [(title, line)] or [(title, line, line)] with keys."""
    out = []
    for it in items:
        t, rest = it[0], it[1:]
        cells = ''.join(f'<span>{f"<i>{e(keys[k])}</i>" if keys else ""}{e(x)}</span>' for k, x in enumerate(rest))
        out.append(f'<div class="crow"><b>{e(t)}</b>{cells}</div>')
    return '<div class="crows" data-reveal>' + ''.join(out) + '</div>'


def pair(a, b):
    """Two cards side by side: the business goal and the user problem."""
    return '<div class="grid2 goal-pair" data-reveal>' + ''.join(f'<div class="tile"><h3>{e(t)}</h3><p>{e(d)}</p></div>' for t, d in (a, b)) + '</div>'


def duo(items, heading='Pouch in action'):
    """Two recordings side by side, each with small chapter chips and one caption line.
    items: [(video name, title, [(start_seconds, label, text)])]"""
    out = []
    for name, title, steps in items:
        if not os.path.exists(os.path.join(ROOT, f'video/{name}.mp4')):
            continue
        li = ''.join(f'<li data-at="{t}"><button type="button"><span class="bar"><i></i></span><span class="k">{label}</span><span class="d">{e(text)}</span></button></li>' for t, label, text in steps)
        out.append(f'''<div class="demo compact">
        <div class="demo-phone"><div class="phone"><div class="screen"><video src="../video/{name}.mp4" poster="../video/{name}-poster.webp" muted loop playsinline preload="none" aria-label="{e(title)}"></video></div></div></div>
        <div class="demo-ctl"><h3>{e(title)}</h3><ol class="demo-steps">{li}</ol><p class="demo-caption" aria-live="polite">{e(steps[0][2])}</p></div>
      </div>''')
    one = ' one' if len(out) == 1 else ''
    return f'<h2>{e(heading)}</h2><p class="sub">A real screen recording from the iPhone simulator. Tap a step to replay it.</p><div class="duo{one}" data-reveal>' + ''.join(out) + '</div>'


def hotspots(title, intro, screens):
    """Numbered dots on the screen, with the same numbers in a short list beside it.
    Hover or tap a line to light up its dot. screens: [(image, [(x, y, title, text)])], x and y as shares of the screenshot."""
    figs = []
    n = 0
    for name, spots in screens:
        dots, lis = '', ''
        for x, y, t, d in spots:
            n += 1
            dots += f'<span class="hs-dot" data-n="{n}" style="left:{5.333 + x * 89.333:.1f}%;top:{2.5 + y * 95:.1f}%">{n}</span>'
            lis += f'<li data-n="{n}"><span class="hs-n">{n}</span><div><b>{e(t)}</b><span>{e(d)}</span></div></li>'
        figs.append(f'<figure class="hs"><div class="phone"><div class="screen"><img src="../img/apps/{name}.webp" alt="{e(title)}" loading="lazy"></div>{dots}</div><ol class="hs-list">{lis}</ol></figure>')
    return f'<h2>{e(title)}</h2><p class="sub">{e(intro)}</p><div class="hss" data-reveal>' + ''.join(figs) + '</div>'


def compare(head, rows):
    """A two-column comparison: what other apps do, what this app does. rows: [(topic, others, ours)]"""
    tr = ''.join(f'<div class="cmp-row"><span class="cmp-topic">{e(t)}</span><span class="cmp-them">{e(a)}</span><span class="cmp-us">{e(b)}</span></div>' for t, a, b in rows)
    ours = f'<img src="../img/pouch-icon.webp" alt="" width="28" height="28">{e(head[1])}' if head[1] == 'Pouch' else e(head[1])
    return f'<div class="cmp" data-reveal><div class="cmp-row cmp-head"><span></span><span>{e(head[0])}</span><span class="cmp-us">{ours}</span></div>{tr}</div>'


def learned(items, last_next=True):
    """Numbered cards. With last_next, the last one is filled and called Next. items: [(title, line)]"""
    n = len(items)
    out = ''.join(f'<div class="ln{" is-next" if last_next and k == n - 1 else ""}"><span class="ln-k">{"Next" if last_next and k == n - 1 else f"0{k + 1}"}</span><b>{e(t)}</b><span>{e(d)}</span></div>' for k, (t, d) in enumerate(items))
    return f'<div class="lns{" four" if n == 4 else ""}" data-reveal>{out}</div>'


def tracevis(rows):
    """Research number, then the screen it shaped, then what the pilot changed.
    rows: [(title, stat, finding, screen, designed, pilot)]"""
    out = ''
    for t, stat, f, img, d, pl in rows:
        out += (f'<div class="tv"><div class="tv-find"><small>{e(t)}</small><b>{e(stat)}</b><span>{e(f)}</span></div>'
                f'<div class="tv-screen"><div class="phone"><div class="screen"><img src="../img/{img}.webp" alt="TrustBank, {e(d)}" loading="lazy"></div></div></div>'
                f'<div class="tv-out"><p><i>Designed</i>{e(d)}</p><p><i>Pilot</i>{e(pl)}</p></div></div>')
    return f'<h3 style="margin:40px 0 4px">From finding to design</h3><div class="tvs" data-reveal>{out}</div>'


def measures():
    """Pouch's three planned measures, each a big target with a small drawing of it."""
    week = ''.join(f'<i class="{"on" if k < 4 else ""}">{d}</i>' for k, d in enumerate('MTWTFSS'))
    weeks = ''.join(f'<i class="on" style="height:{40 + k * 14}%">W{k}</i>' for k in range(1, 5))
    return ('<div class="meas" data-reveal>'
            f'<div class="m"><span class="m-k">Habit</span><b class="m-big">4 of 7</b><span class="m-l">days logged each week</span><div class="m-vis m-week">{week}</div></div>'
            '<div class="m"><span class="m-k">Speed</span><b class="m-big">&lt; 10 s</b><span class="m-l">from open to saved</span><div class="m-vis m-time"><span class="m-track"><i style="width:62%"></i><b>target</b></span><span class="m-scale"><em>0 s</em><em>10 s</em></span></div></div>'
            f'<div class="m"><span class="m-k">Staying</span><b class="m-big">Week 4</b><span class="m-l">still logging, counted in weeks</span><div class="m-vis m-weeks">{weeks}</div></div>'
            '</div>')


MADE = {
    'cloudia': 'I came up with the idea and directed the product: the flows, the screens and the design system, which I drew in Figma. The code was written with Claude Code, an AI coding tool, working from my direction, and I tested every build on the simulator and my own iPhone. I have not run formal user testing yet, and Cloudia is not on the App Store yet.',
    'pouch': 'I directed the product and designed the experience, shaping the screens directly in the working app on the simulator and my own iPhone. The code was written with Claude Code, an AI coding tool, working from my direction. The research is desk research: public App Store reviews, read and grouped by theme, not interviews or user testing. The website is live, and the app is not on the App Store yet.',
    'fretbelly': 'I directed the product and designed the experience, shaping the screens directly in the working app on the simulator and my own iPhone. The code was written with Claude Code, an AI coding tool, working from my direction. The research is desk research: public App Store reviews and app screens from my Mobbin library, not interviews or user testing. Fretbelly is not on the App Store yet.',
}


def made(slug):
    """How an app was made, said plainly: what was mine, what the AI coding tool did, what the research was."""
    return callout('How I made this', MADE[slug])


THESIS = ('From our team thesis at Uva Wellassa University (2025): three students, supervised by Ms. C.S.D. Ellepola, comparing how Gen X, '
          'Millennials and Gen Z in Sri Lanka use banking and shopping apps. Mixed methods, with ethics approval and consent from every participant.')


def thesis_stats():
    return stats([('~300', 'survey responses: 113 Gen Z, 107 Millennials and 80 Gen X'), ('9', 'expert interviews with banking and e-commerce designers, 4 to 10 years in the field'), ('60', 'people in a moderated pilot on our Figma prototypes, 20 per generation')])


def thesis_methods(apps):
    return '<div style="margin-top:14px"></div>' + tiles([
        ('Survey', 'An online questionnaire for people aged 18 to 56 who already use banking or shopping apps, shared online and through campus and community networks.'),
        ('Interviews', 'Semi-structured, 45 to 60 minutes each, online and in person, on generational pain points and the balance of security and ease.'),
        ('Pilot', 'Moderated tasks on the prototypes, like signing in with a fingerprint or one-time code, paying, and checking out. Field notes only, used to fix the design.'),
        ('Existing apps', f'A heuristic review of widely used Sri Lankan {apps} apps against Nielsen Norman Group\'s ten usability heuristics.'),
    ], cols=2)


def trace(rows):
    """Research finding -> what I designed -> what the pilot did with it. Sources: thesis PDF pages 19 (pilot), 26-28 (Gen X), 29-33 (Millennials), 47 (e-commerce pilot), 53-55 (design guidelines)."""
    out = []
    for n, (t, f, d, pl) in enumerate(rows):
        steps = ''.join(f'<li><b>{k}</b> {e(v)}</li>' for k, v in (('Found', f), ('Designed', d), ('Pilot', pl)))
        out.append(f'<div class="tile" data-reveal><span class="k">{n + 1:02d}</span><h3>{e(t)}</h3><ul>{steps}</ul></div>')
    return '<h3 style="margin:36px 0 4px">From finding to design</h3><div class="grid3">' + ''.join(out) + '</div>'


def not_tested():
    return callout('What is not tested yet', 'The pilot shaped the design, but the finished screens have not been tested with users. The thesis plans that next: a quarter of each generation trying the prototype, then follow-up interviews.')


TRUST = dict(
    slug='trustbank', theme='t-trust', title='TrustBank', meta='Research case study · Fintech',
    lede='A concept mobile banking app from our team research thesis, designed so people of every generation can log in, send money and find proof of payment without second-guessing.',
    facts=[('Role', 'UX/UI designer'), ('Type', 'Research case study'), ('Platform', 'Mobile app'), ('Context', 'Team thesis of three, Uva Wellassa University')],
    cover=('PHONES', ['screens/trust-08-01', 'screens/trust-08-home-1', 'screens/trust-08-pay-2']),
    sections=[
        ('overview', 'Overview', pair(('Goal', 'Fast, clear everyday banking for every generation.'), ('Problem', 'People get lost at sign in, sending money and finding proof.'))
            + specrow([('Role', 'Flows, UI, visual system, prototype'), ('Team', 'Thesis of three, research together'), ('Screens', '20+ in Figma'), ('Tested', 'Pilot of 60, final screens not yet')])),
        ('research', 'Research', '<h2>Research</h2><p class="sub">' + e(THESIS) + '</p>' + specrow([('Survey', '~300 people, aged 18 to 56'), ('Interviews', '9 designers, 45 to 60 min each'), ('Pilot', '60 people, 20 per generation'), ('App review', 'Local banking apps vs 10 usability heuristics')])
            + rail('Apps people use today', ['Dense home screens, small tap targets and features buried in menus.', 'Transfers with no clear review step, and receipts that are hard to find.'], [f'screens/trust-02-{i:02d}' for i in range(1, 7)], 'An existing Sri Lankan banking app')
            + '<div class="grid2" style="margin-top:28px">'
            + bars('Most people wanted a calm design', 'Share of each generation who preferred a minimal design', [('Gen X', 56), ('Millennials', 61), ('Gen Z', 53)])
            + bars('What each generation put first', 'Top answer in each generation', [('Gen X: face or fingerprint sign-in', 50), ('Millennials: fast payment', 37), ('Gen Z: fast payment', 27)])
            + '</div>'
            + callout('Safe, not exhausting', 'The experts asked for security that does not wear people out: biometrics by default, with a simple fallback for anyone who struggles with codes.')
            + tracevis([
                ('Sign-in', '50%', 'of Gen X put face or fingerprint sign-in first.', 'screens/trust-08-06', 'Face ID by default, a code as the fallback.', 'Codes and errors rewritten in plainer words.'),
                ('Paying', '37%', 'of Millennials put fast payment first.', 'screens/trust-08-review-2', 'One review screen, then Face ID approves.', 'Steps that repeated themselves removed.'),
                ('Proof', '31%', 'of Gen X ranked transaction history next.', 'screens/trust-09-proof-1', 'A reference and a PDF receipt every time.', 'Larger tap targets and stronger contrast.'),
            ])
            + callout('What the pilot changed', 'Clearer one-time code and error messages, larger tap targets, stronger contrast, more visible trust cues, and fewer steps.')
            + not_tested()),
        ('problem', 'Problem', '<h2>The problem</h2><p class="sub">Banking is high stakes: unsure people slow down, make mistakes or stop trusting the app.</p>' + rows([
            ('Basics are hard to find', 'Balances and history take too many taps.'),
            ('Transfers feel risky', 'No easy review before confirming.'),
            ('No real proof', 'People fall back on screenshots.'),
            ('Unclear alerts', 'They say what happened, not what to do.'),
            ('Different generations', 'It has to work at 20 and at 60.'),
        ])),
        ('screens', 'Screens', '<h2>Final screens</h2><p class="sub">Pick a flow.</p>' + viewer([
            ('Sign in', ['Pick a language.', 'Verify your phone.', 'Enter the 6-digit code.', 'Create a device passcode.', 'Sign in with Face or Touch ID.', 'Or use the app passcode.', 'Enable Face or Touch ID.', 'Your view, your way.'], [f'screens/trust-08-{i:02d}' for i in range(2, 10)]),
            ('Home', ['Every account and balance.', 'Quick actions and recent spending.', 'One account, with filters and export.'], ['screens/trust-08-home-1', 'screens/trust-08-home-2', 'screens/trust-08-home-3']),
            ('Pay', ['Pick who to pay.', 'Add a new bank recipient.', 'Choose the recipient type.', 'Saved recipients up top.', 'Payment details and the fee.', 'Enter the amount.'], ['screens/trust-08-11', 'screens/trust-08-12', 'screens/trust-08-13', 'screens/trust-08-pay-1', 'screens/trust-08-pay-2', 'screens/trust-08-pay-3']),
            ('Review and proof', ['Payment details, once more.', 'Review and confirm.', 'Face ID approves it.', 'Done, with a PDF receipt.'], ['screens/trust-08-review-1', 'screens/trust-08-review-2', 'screens/trust-08-review-3', 'screens/trust-09-proof-1']),
            ('History', ['Recent transactions.', 'Search and filter.', 'Export transactions.', 'Pick a date range.', 'Export as PDF.', 'Details and reference.'], ['screens/trust-09-tx-1', 'screens/trust-09-tx-2', 'screens/trust-09-tx-3', 'screens/trust-09-export-1', 'screens/trust-09-export-2', 'screens/trust-09-export-3']),
            ('Alerts', ['Every alert in one inbox.', 'New sign-in: Approve or Report.'], ['screens/trust-09-alert-1', 'screens/trust-09-alert-2']),
        ], app='TrustBank')),
        ('prototype', 'Prototype', proto('https://embed.figma.com/proto/NT0B473eA8D6CawCK4EsbQ/Bank-App-Prototype?node-id=387-7584&scaling=scale-down&content-scaling=fixed&page-id=0%3A1&starting-point-node-id=34%3A3225&embed-host=share', ['screens/trust-08-01', 'screens/trust-08-home-1', 'screens/trust-08-pay-2'], 'TrustBank')),
        ('design', 'Design', '<h2>Look and feel</h2>' + plain('A warm, confident yellow', ['A friendly yellow brand with plenty of white space, SF Pro type and large, readable amounts.'], [scr('trust-10-01')], 'TrustBank brand')),
    ],
    next=('vela', 'VELA', ['screens/vela-04-01', 'screens/vela-04-home-1', 'screens/vela-04-09'], '#e5f7f3'),
)

VELA = dict(
    slug='vela', theme='t-vela', title='VELA', meta='Research case study · E-commerce',
    lede='A shopping app prototype from our team research thesis, made so Gen Z, Millennial and Gen X shoppers in Sri Lanka can search, decide and check out faster.',
    facts=[('Role', 'UX/UI designer'), ('Type', 'Research case study'), ('Platform', 'Mobile app'), ('Context', 'Team thesis of three, Uva Wellassa University')],
    cover=('PHONES', ['screens/vela-04-01', 'screens/vela-04-home-1', 'screens/vela-04-09']),
    sections=[
        ('overview', 'Overview', pair(('Goal', 'Faster searching, deciding and paying, for every generation.'), ('Problem', 'Shoppers slow down at search, product pages and checkout.'))
            + specrow([('Role', 'Flows, visual system, prototype'), ('Team', 'Thesis of three, research together'), ('Modes', 'Light and dark'), ('Tested', 'Pilot of 60, final screens not yet')])),
        ('research', 'Research', '<h2>Research</h2><p class="sub">' + e(THESIS) + '</p>' + specrow([('Survey', '~300 people, aged 18 to 56'), ('Interviews', '9 designers, 45 to 60 min each'), ('Pilot', '60 people, 20 per generation'), ('App review', 'Local shopping apps vs 10 usability heuristics')])
            + '<div class="grid2" style="margin-top:28px">'
            + bars('Clean wins', 'Share of each generation who preferred a minimal, uncluttered design', [('Gen X', 56), ('Millennials', 61), ('Gen Z', 53)])
            + bars('Different priorities', 'What mattered most to each generation', [('Gen X: fast checkout', 44), ('Millennials: easy search', 28), ('Millennials: product reviews', 23)])
            + '</div>'
            + callout('So', 'Discovery and checkout had to be the strongest parts of the app. The pilot shaped labels, step count, tap targets, contrast and trust cues.')
            + trace([
                ('Checkout', 'Gen X put a fast checkout first (44%), and pilot sessions found cluttered checkout screens.', 'Four predictable steps, cart, address, delivery and payment, with the total always on screen.', 'We cut checkout steps that added nothing, without weakening the safeguards.'),
                ('Search', 'Millennials cared most about easy search (28%) and product reviews (23%).', 'Recent and top searches, light filters that are easy to undo, and price and rating first on the product page.', 'Search is not in our pilot notes, so this part is still untested.'),
                ('Trust', 'In the pilot, security steps were easy to miss or hard to understand.', 'Plain-language security copy and familiar icons at checkout, and a failed payment that offers retry or another method.', 'This change came from the pilot itself.'),
            ])
            + not_tested()
            + rail('Apps people use today', ['Busy home screens, hidden filters and checkout totals that appear late.'], [f'screens/vela-02-{i:02d}' for i in range(1, 7)], 'An existing Sri Lankan shopping app')
            + '<div class="group" data-reveal><div class="group-head"><h3>What shoppers wrote in reviews</h3><ul><li>Real store reviews: missing prices in search, slow refunds and orders marked delivered that never arrived.</li></ul></div><div class="reviews">'
            + ''.join(img(f'img/cases/trust-0{i}-1.webp', 'An app store review') for i in range(3, 7)) + '</div></div>'),
        ('problem', 'Problem', '<h2>The problem</h2><p class="sub">Shopping is a repeat habit, so small friction adds up to drop-offs.</p>' + rows([
            ('Slow discovery', 'Search and filters are hard to find.'),
            ('Low confidence', 'Ratings, delivery and returns are hidden.'),
            ('Checkout friction', 'Too many steps, totals unclear until the end.'),
            ('Dead-end payments', 'A failed payment has no way forward.'),
        ])),
        ('screens', 'Screens', '<h2>Final screens</h2><p class="sub">Pick a flow.</p>' + viewer([
            ('Sign in', ['Welcome, or continue as a guest.', 'Language comes first.', 'Create an account, with password help.'], [f'screens/vela-04-{i:02d}' for i in range(1, 4)]),
            ('Discover and search', ['Home: categories and trending.', 'Recent and top searches.', 'No match? Similar picks.', 'Results at a glance.', 'Light filters, easy to reset.', 'Search with a photo.', 'Items found from the photo.', 'Product details.'], ['screens/vela-04-home-1', 'screens/vela-04-home-2', 'screens/vela-04-home-3', 'screens/vela-04-search-1', 'screens/vela-04-search-2', 'screens/vela-04-search-3', 'screens/vela-04-04', 'screens/vela-04-05']),
            ('Product page', ['Specs and reviews.', 'Pick a size.', 'Price, rating, Add to cart.'], [f'screens/vela-04-{i:02d}' for i in range(6, 9)]),
            ('Cart', ['Swipe to remove.', 'Removed, total updated.', 'Undo brings it back.'], [f'screens/vela-04-{i:02d}' for i in range(9, 12)]),
            ('Checkout', ['Add a card.', 'Quick Pay or saved cards.', 'Review and pay.', 'Verify your card.', 'Order placed.', 'Failed: retry or change method.'], [f'screens/vela-04-{i:02d}' for i in range(12, 18)]),
        ], app='VELA')),
        ('prototype', 'Prototype', proto('https://embed.figma.com/proto/Nm8tZVvYDXHVjoPphuYHkA/Ecommerce-App-prototype?node-id=7-170&scaling=scale-down&content-scaling=fixed&page-id=0%3A1&starting-point-node-id=1%3A4&embed-host=share', ['screens/vela-04-01', 'screens/vela-04-home-1', 'screens/vela-04-09'], 'VELA')),
        ('design', 'Design', '<h2>Look and feel</h2>'
            + plain('Light and dark mode', ['Every screen designed in both modes.'], [scr('vela-05-01')], 'VELA dark mode')
            + plain('Style', ['A fresh teal, Rubik type and a small UI kit.'], [scr('vela-05-02')], 'VELA style guide')),
    ],
    next=('keells', 'Keells redesign', ['apps/keells-05', 'apps/keells-06', 'apps/keells-14'], '#e8f6ea'),
)

KEELLS = dict(
    slug='keells', theme='t-keells', title='Keells redesign', meta='Redesign concept · Retail',
    note='An unofficial concept I designed on my own. It is not affiliated with or endorsed by John Keells Holdings or Keells.',
    lede='A concept redesign of the Keells supermarket app: a fresher look, simpler navigation and a smoother path from basket to checkout. Shared on LinkedIn, it earned over 100,000 impressions.',
    facts=[('Role', 'UX/UI designer'), ('Type', 'Redesign concept'), ('Platform', 'Mobile app'), ('Reach', '100k+ impressions, 2k+ reactions')],
    cover=('PHONES', ['apps/keells-05', 'apps/keells-06', 'apps/keells-14']),
    sections=[
        ('overview', 'Overview', pair(('Goal', 'A modern grocery app people would rather order from than queue.'), ('Problem', 'Dull colours, a cluttered layout and little reason to browse.'))
            + specrow([('Role', 'UX/UI, end to end'), ('Type', 'Unofficial concept'), ('LinkedIn reach', '100k+ impressions'), ('Reactions', '2k+')])),
        ('flow', 'Flow', '<h2>User flow</h2>' + plain('From opening the app to paying', ['I mapped the journey first: onboarding, browsing, the basket and checkout.'], [scr('keells-02-board')], 'Keells user flow')),
        ('screens', 'Screens', '<h2>Screens</h2><p class="sub">Pick a part of the app.</p>' + viewer([
            ('Onboarding', ['A green splash.', 'Shop groceries from home.', 'Pay online with saved cards.', 'Sign in, or browse as a guest.'], ['keells-01', 'keells-02', 'keells-03', 'keells-05']),
            ('Home and browsing', ['Address, offer and categories.', 'Favourites with steppers.', 'Price per kilo, one-tap add.', 'A light filter.'], ['keells-06', 'keells-07', 'keells-10', 'keells-09']),
            ('Basket', ['A mini basket with a total.', 'Change quantities in place.', 'Suggestions above checkout.'], ['keells-13', 'keells-14', 'keells-15']),
            ('Checkout', ['Delivery and payment on one screen.', 'Confirm and Pay.', 'A clear success.', 'Order status and charges.'], ['keells-16', 'keells-17', 'keells-18', 'keells-19']),
        ], app='Keells redesign')),
        ('design', 'Design', '<h2>Look and feel</h2>'
            + plain('Colour and type', ['Keells green, made brighter, with Inter and Poppins.'], [scr('keells-03-board')], 'Keells colours and type')
            + plain('UI kit and prototype', ['Reusable components and a clickable prototype.'], [scr('keells-05-board')], 'Keells UI kit')
            + plain('Final look', [], [scr('keells-06-board')], 'Keells final look')),
    ],
    next=('zestbowls', 'ZestBowls', 'img/zest-hero.webp', '#eef7e6'),
)

ZEST = dict(
    slug='zestbowls', theme='t-zest', title='ZestBowls', meta='Product concept · Web',
    lede='A web app for discovering and ordering healthy meals, including calorie deficit plans, with clear information and easy navigation.',
    facts=[('Role', 'Product designer'), ('Type', 'Product concept'), ('Platform', 'Web app'), ('Industry', 'Food and beverage')],
    cover=('img/zest-hero.webp', True),
    sections=[
        ('overview', 'Overview', pair(('Goal', 'Find fresh meals that fit your diet, and order in seconds.'), ('Focus', 'Appetising visuals, simple navigation, clear nutrition.'))
            + specrow([('Role', 'Brand, UI kit and every page'), ('Type', 'Product concept'), ('Platform', 'Web app'), ('Industry', 'Food and beverage')])),
        ('screens', 'Screens', '<h2>Screens</h2>'
            + web('Landing page', [
                'A bold promise up top, Discover your path to healthier eating, with Order Now beside it.',
                'Popular meal plans as cards with a rating, the price and Add to cart.',
                'A weekend flash deal banner that slides between offers.',
                'Featured meals, then three reasons to choose ZestBowls: offers, fresh as home, nutritious.',
                'Meal plans filtered by type: nutritious, veggie, beef, chicken and noodle bowls.',
                'A footer with quick links, legal pages and a newsletter sign-up.',
            ], scr('zest-landing'), 'ZestBowls landing page', full=True)
            + web('Meal and cart', [
                'A breadcrumb shows where the meal sits: popular meals, bowl type, then the meal.',
                'Calories, carbs, protein and fat sit under the photo of every meal.',
                'What is included, a quantity stepper, the price and Add to cart, side by side.',
                'The cart stays open on the right, with the delivery address and each item.',
                'The order summary adds delivery and shows the total before Place Order.',
                'Similar meals below keep people browsing.',
            ], scr('zest-cart'), 'ZestBowls meal and cart')),
        ('design', 'Design', '<h2>Look and feel</h2>'
            + plain('Colour and type', ['A fresh green palette with Poppins in four weights.'], [scr('zest-colours')], 'ZestBowls colours and type')
            + plain('UI kit', ['Navigation, buttons and icons built as one small kit.'], [scr('zest-kit')], 'ZestBowls UI kit')
            + plain('Final look', [], [scr('zest-04-board')], 'ZestBowls final look')),
    ],
    next=('pouch', 'Pouch', ['apps/pouch-budget', 'apps/pouch-today', 'apps/pouch-overview'], '#efeaff'),
)

CLOUDIA = dict(
    slug='cloudia', theme='t-cloudia', title='Cloudia', meta='My app · iOS · Designed by me, coded with AI',
    site=('Visit the website', 'https://sasankarasanjana29.github.io/cloudia-site/'),
    lede='A calm iOS app for the loose ends in your head: what you promised, and what someone owes you.',
    facts=[('Role', 'Product and design, AI-assisted build'), ('Platform', 'iOS, React Native and Expo'), ('Status', 'Website live, in development'), ('Year', '2026')],
    cover=('PHONES', ['apps/cloudia-voice', 'apps/cloudia-today', 'apps/cloudia-seal']),
    sections=[
        ('overview', 'Overview', pair(('Goal', 'One calm place for what you owe and what you are owed.'), ('Problem', 'Small promises live in heads, notes and screenshots, then slip.'))
            + specrow([('Design', 'Figma components and tokens'), ('Code', 'Claude Code, from my direction'), ('Testing', 'My iPhone, no formal user tests yet'), ('Status', 'Not on the App Store yet')])
            + '<h2 style="margin-top:56px">Principles</h2>' + learned([
                ('Never nags', 'Reminders help, they never guilt.'),
                ('Private by default', 'No ads, no tracking, no account needed.'),
                ('Honest', 'It never claims a feature it does not have.'),
            ], last_next=False)),
        ('demo', 'In action', duo([('cloudia', 'Closing a loop', [
            (0, 'Today', 'The few loops that need you, on a week strip.'),
            (4.7, 'Done', 'Mark a late bill done and the seal stamps it.'),
            (12.4, 'Waiting', 'What others owe you, then days in the clear.'),
        ])], heading='Cloudia in action')),
        ('cuts', 'Cuts', cuts('Things I built or planned, then took out, and what replaced them.', [
            ('Money mode', 'A Money switch with a settle-up page for shared costs.', 'It turned an app for small promises into a budget app.', 'An amount is an optional detail on a loop.'),
            ('A login streak', 'Counting the days you open the app.', 'It would make the app nag you to protect a number.', 'Days in the clear: days that end with nothing overdue.'),
            ('A sun for the streak', 'A sun as the streak mark.', 'In an app made of sky and clouds it read as a weather forecast.', 'A simple check mark.'),
        ])),
        ('screens', 'Screens', '<h2>Screens</h2><p class="sub">Pick a part of the app.</p>' + viewer([
            ('The seal', ['Marking done plays the wax seal.', 'The closed loop keeps its stamp.', 'The first seal gets its own moment.'], ['cloudia-seal', 'cloudia-sealed', 'cloudia-first-seal']),
            ('Voice', ['Say one sentence.', 'One card per fact.', 'Amounts stay optional.'], ['cloudia-voice', 'cloudia-add', 'cloudia-amount']),
            ('Today', ['A week strip and what needs you.', 'The same in dark mode.', 'Search every loop.'], ['cloudia-today', 'cloudia-today-dark', 'cloudia-search']),
            ('Loops', ['My turn: what you owe.', 'Waiting: what you are owed.', 'Late says how late, calmly.'], ['cloudia-my-turn', 'cloudia-loop-waiting', 'cloudia-loop-late']),
            ('Nudges', ['Nudges you choose.', 'Reminders that never guilt.', 'Your people in one place.'], ['cloudia-nudge', 'cloudia-reminders', 'cloudia-people']),
            ('Getting started', ['A friendly welcome.', 'A promise you sign yourself.', '50 illustrated categories.'], ['cloudia-welcome', 'cloudia-promise', 'cloudia-categories']),
            ('Streak', ['Days in the clear, not logins.', 'Profile keeps it with your data.'], ['cloudia-streak', 'cloudia-profile']),
        ], app='Cloudia')),
    ],
    next=('fretbelly', 'Fretbelly', ['apps/fret-write', 'apps/fret-home', 'apps/fret-insights'], '#ece9fb'),
)

POUCH = dict(
    slug='pouch', theme='t-pouch', title='Pouch', meta='My app · iOS · Designed by me, coded with AI',
    site=('Visit the website', 'https://sasankarasanjana29.github.io/hedge-site/'),
    lede='A free, private budgeting app for iPhone, shaped by what 1,751 App Store reviews of a popular budgeting app asked for, with Hedge the hedgehog as a guide.',
    facts=[('Role', 'Product and design, AI-assisted build'), ('Platform', 'iOS, React Native and Expo'), ('Status', 'Website live, in development'), ('Quality', '280 automated tests on the money maths')],
    cover=('PHONES', ['apps/pouch-celebrate-week', 'apps/pouch-today', 'apps/pouch-wardrobe']),
    sections=[
        ('research', 'Research', pair(('Goal', 'Get people logging money every day, with no bank link.'), ('Problem', 'Bank sync breaks, prices hide until setup, money gets confusing.'))
            + '<h2 style="margin-top:56px">What the reviews said</h2><p class="sub">1,751 public App Store reviews of a popular budgeting app, from 12 countries, grouped by complaint.</p>'
            + bars('What people complained about', 'Share of all 1,751 reviews that raised each problem', [('Bank sync breaks, or my bank is not supported', 24), ('Paying, or seeing the price only after setup', 23), ('The app crashes or will not open', 8)], '54% of one star reviews mention bank sync or the price.')
            + specrow([('Design', 'Me, in the working app'), ('Code', 'Claude Code, from my direction'), ('Research', 'Public reviews, desk research'), ('Status', 'Not on the App Store yet')])),
        ('answer', 'Answer', '<h2>What Pouch does instead</h2>' + compare(('Most budgeting apps', 'Pouch'), [
            ('Getting your spends in', 'Link your bank, and hope sync works', 'Three taps, or paste the bank text'),
            ('Price', 'Shown after setup', 'Free, no paywall'),
            ('Your data', 'On their servers', 'Stays on your phone'),
            ('Language', 'English first', '13 languages, Sinhala and Tamil too'),
        ])),
        ('demo', 'In action', duo([
            ('pouch-setup', 'Setting up', [(0, 'Opens', 'Hedge climbs the Pouch wall.'), (7.0, 'Asks', 'He asks when you get paid.'), (16.0, 'Plans', 'Split your pay guesses every category.')]),
            ('pouch', 'Logging a spend', [(0, 'Today', 'Today opens on what is safe to spend.'), (1.4, 'Log', 'Rs 450, Groceries, saved.'), (11.8, 'Budget', 'Budget by family, then weeks tracked.')]),
            ('pouch-trip', "Hedge's trip", [(0, 'Today', 'Tap Hedge on Today.'), (1.4, 'Opens', 'His trip opens on the forest trail.'), (4.9, 'Closes', 'Close it and he lands back on Today.')]),
        ])),
        ('notes', 'Notes', hotspots('Why each part is there', 'Tap or hover a note to find it on the screen.', [
            ('pouch-today', [
                (0.04, 0.215, 'One number first', 'Safe to spend, worked out for you.'),
                (0.96, 0.31, 'Never red', 'Past the plan it says extra, in grey.'),
                (0.04, 0.45, 'Savings in one tap', 'The pouch fills as you save.'),
                (0.70, 0.84, 'In thumb reach', 'Add sits bottom right.'),
            ]),
            ('pouch-paste-filled', [
                (0.96, 0.19, 'Hedge reacts', 'He says how the spend fits today.'),
                (0.04, 0.29, "Today's range", 'See where it lands before saving.'),
                (0.96, 0.43, 'Filled from the bank text', 'Shop and card come from the SMS.'),
                (0.04, 0.78, 'A keypad of its own', 'Never hidden by the keyboard.'),
            ]),
        ])),
        ('cuts', 'Cuts', beforeafter('Two things I built, then took out.', [
            ('Red when you overspend', '<em class="mini-l">Groceries</em><span class="mini"><i style="width:100%"></i></span><em class="mini-t">Rs 520 over</em>', '<em class="mini-l">Groceries</em><span class="mini"><i style="width:100%"></i></span><em class="mini-t">Rs 520 extra</em>', 'Guilt stops people logging.'),
            ('A minus balance', '<em class="mini-l">Safe to spend today</em><em class="mini-big">-Rs 1,200</em>', '<em class="mini-l">Safe to spend today</em><em class="mini-big">Rs 0</em>', 'A minus reads as failure.'),
        ])),
        ('screens', 'Screens', '<h2>Screens</h2><p class="sub">Pick a part of the app.</p>' + viewer([
            ('Setup', ['The welcome: Hedge climbs the Pouch wall.', 'Split your pay until All planned.', 'Today shows what is safe to spend.'], ['pouch-welcome', 'pouch-split', 'pouch-today']),
            ('Log a spend', ['Copy a bank text and Paste appears.', 'One tap fills in the amount and shop.', 'Siri payments wait on Today.'], ['pouch-paste-row', 'pouch-paste-filled', 'pouch-add-these']),
            ('Budget', ['Categories in families, with what is left.', 'Each has its own colour and icon.', 'See where the month went.'], ['pouch-budget', 'pouch-pot-edit', 'pouch-overview']),
            ('Wallets and big buys', ['Every wallet in one list.', 'Big buys paid off in parts.', 'Every entry by day.'], ['pouch-wallets', 'pouch-bigbuy-tiles', 'pouch-entries']),
            ('Any currency', ['Income has its own categories.', "Paid from abroad? Today's rate.", '13 languages, Sinhala and Tamil too.'], ['pouch-income', 'pouch-paid-in', 'pouch-today-si']),
            ('Hedge', ['Tap him for his trip through the woods.', 'Weeks, not days, so quiet days count.', 'Gems buy outfits from a wardrobe of 51.'], ['pouch-trip', 'pouch-streak', 'pouch-wardrobe']),
            ('Dark mode', ['Today in dark mode.', 'A new entry, every colour checked for contrast.', 'Budget in dark mode.'], ['pouch-dark-today', 'pouch-dark-new', 'pouch-dark-budget']),
        ])),
        ('duo', 'Duo', '<h2>Ready for iPhone Duo</h2><p class="sub">Open, the big screen shows a list and what you tapped side by side, split on the fold. Closed, it is the phone app. Built and tested on the Duo simulator.</p>'
            '<figure class="duo-shot" data-reveal><img src="../img/apps/pouch-duo.webp?v=3" srcset="../img/apps/pouch-duo-800.webp?v=3 800w, ../img/apps/pouch-duo.webp?v=3 1600w" sizes="(max-width: 900px) 92vw, 880px" '
            'alt="Pouch on an open iPhone Duo: Budget categories on the left, Rent paid on the right with Log into Rent and its entry" width="1600" height="1162" loading="lazy" decoding="async">'
            '<figcaption>Budget, Entries and Wallets each keep the list on the left and the chosen item on the right.</figcaption></figure>'),
        ('next', 'Next', '<h2>What I learned and what is next</h2>' + learned([
            ('Kind beats strict', 'Friendly words keep people logging.'),
            ('I use it daily', 'Most fixes came from my own logging.'),
            ('Outside testers, then the App Store', 'Then watch days logged a week and time to log a spend.'),
        ])),
    ],
    next=('cloudia', 'Cloudia', ['apps/cloudia-today-dark', 'apps/cloudia-today', 'apps/cloudia-loop-late'], '#e6f1ff'),
)

FRET = dict(
    slug='fretbelly', theme='t-fret', title='Fretbelly', meta='My app · iOS · Designed by me, coded with AI',
    lede='A small creature that eats your worries, and shows you how few of them ever come true.',
    facts=[('Role', 'Product and design, AI-assisted build'), ('Platform', 'iOS, React Native and Expo'), ('Status', 'On iPhone, in development'), ('Privacy', 'No account, no tracking')],
    cover=('PHONES', ['apps/fret-toss', 'apps/fret-home', 'apps/fret-lantern']),
    sections=[
        ('research', 'Research', specrow([('Reviews read', '30k+, popular personal apps'), ('Screens studied', '300, from my Mobbin library'), ('Real reality check', '0 of the apps studied'), ('Status', 'Not on the App Store yet')])
            + '<h2 style="margin-top:56px">What other worry apps miss</h2>' + compare(('Other worry apps', 'Fretbelly'), [
                ('A character to hand worries to', 'Only comfort apps and worry games', 'A small creature that eats them'),
                ('Checks what really happened', 'None of the apps I studied', 'Asks: did it happen?'),
                ('What makes it grow', 'Streaks, or nothing', 'Your answers, never streaks'),
            ])),
        ('idea', 'Idea', '<h2>How it works</h2>' + learned([
            ('Put it down', 'Write it, crumple it, toss it in.'),
            ('Worry later', 'One worry time a day. The jar stays sealed.'),
            ('Check reality', 'Did it happen? If not, a lantern.'),
            ('See the truth', 'Like 17 eaten, 2 came true.'),
        ], last_next=False)),
        ('demo', 'In action', duo([('fretbelly', 'Feeding a worry', [
            (0, 'Home', 'Home counts every worry it has eaten.'),
            (5.9, 'Feed', 'Write, rate, crumple, flick it in.'),
            (18.5, 'Check', 'Did it happen? If not, a lantern.'),
            (26.7, 'Truth', 'How little came true, over time.'),
        ])], heading='Fretbelly in action')),
        ('cuts', 'Cuts', cuts('Things I planned, then took out, and what replaced them.', [
            ('The name Worry Eater', 'Worry Eater, the working name.', 'A brand already owns WORRY EATERS as a trademark.', 'Fretbelly.'),
            ('Streaks', 'Growing the creature for every day you open the app.', 'It rewards opening the app, not checking what really happened.', 'It grows from answers to Did it happen?'),
            ('Rereading any time', 'Worries you could open and reread whenever you liked.', 'Rereading a worry feeds it.', 'The jar stays sealed until your worry time.'),
        ])),
        ('screens', 'Screens', '<h2>Screens</h2><p class="sub">Pick a part of the app.</p>' + viewer([
            ('Feed it', ['Write it down.', 'Rate how likely it feels.', 'Crumple and toss it in.'], ['fret-write', 'fret-likely', 'fret-toss']),
            ('Did it happen?', ['The worry unfolds.', 'Did it happen?', 'If not, a lantern.'], ['fret-unfold', 'fret-check', 'fret-lantern']),
            ('The truth', ['Home keeps the count.', 'A share card, no worries on it.', "Each month's sky of lanterns."], ['fret-home', 'fret-truth', 'fret-month-sky']),
            ('Meet it', ['Hold to wake it.', 'One tap a day at worry time.', 'Pick one of ten colours.', 'Name it, it says hello.'], ['fret-wake', 'fret-worrytime-ask', 'fret-colours', 'fret-creature']),
            ('Worry time', ['Pick one time a day.', 'The jar opens with the proof.', 'Outside it, the jar stays sealed.'], ['fret-worrytime', 'fret-jar2', 'fret-later']),
            ('Hard days', ['Proof the night before.', '5 things you can see.', 'One slow minute of breathing.', 'Is it in my control?'], ['fret-hardday2', 'fret-ground', 'fret-breathe', 'fret-control']),
        ], app='Fretbelly')),
    ],
    next=('trustbank', 'TrustBank', ['screens/trust-08-01', 'screens/trust-08-home-1', 'screens/trust-08-pay-2'], '#fff6d9'),
)


NEXT_LINE = {
    'trustbank': 'Mobile banking that feels faster and safer for every generation.',
    'vela': 'A shopping app that is easy to search and quick to check out.',
    'keells': 'A fresh grocery app redesign with 100,000+ LinkedIn impressions.',
    'zestbowls': 'A healthy meal ordering web app, designed end to end.',
    'cloudia': 'My iOS app for the small promises too small for a calendar.',
    'pouch': 'My budgeting app that never asks for your bank login.',
    'fretbelly': 'My app with a small creature that eats your worries.',
}


# Search: a title and description per case (titles under 60 characters, descriptions under 160),
# and the structured data that tells search engines this is Sasanka's portfolio work.
SITE = 'https://sasankarasanjana29.github.io/sasanka-rasanjana-portfolio/'
SEO = {
    'trustbank': ('TrustBank: Mobile Banking UX Case Study', 'A mobile banking app concept from our team thesis research in Sri Lanka: safer transfers, clear receipts and security alerts that say what to do next.'),
    'vela': ('VELA: E-commerce App UX Case Study', None),
    'keells': ('Keells Grocery App Redesign Concept', 'An unofficial redesign concept of a Sri Lankan grocery app: a cleaner home, clear categories and a smoother basket to checkout.'),
    'zestbowls': ('ZestBowls: Meal Ordering Web App Design', None),
    'cloudia': ('Cloudia: iOS App I Designed and Built', 'A calm iOS app for the loose ends in your head: what you promised, and what someone owes you. Designed by me and coded with AI.'),
    'pouch': ('Pouch: Budgeting App for iPhone', None),
    'fretbelly': ('Fretbelly: Worry App for iPhone', 'A small creature that eats your worries, and shows you how few of them ever come true. An iOS app I designed and coded with AI.'),
}


def seo_for(c):
    title, desc = SEO[c['slug']]
    desc = desc or c['lede']
    assert len(title) + len(' | Sasanka Rasanjana') <= 60 and len(desc) <= 160, c['slug']
    return title, desc


def jsonld(c, title, desc):
    url = f"{SITE}work/{c['slug']}.html"
    data = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'CreativeWork', '@id': url + '#work', 'name': c['title'], 'headline': title, 'description': desc, 'url': url,
         'image': SITE + 'og.jpg', 'inLanguage': 'en', 'genre': c['meta'].replace(' · ', ', '),
         'author': {'@id': SITE + '#person'}, 'creator': {'@id': SITE + '#person'}, 'isPartOf': {'@id': SITE + '#website'}},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Sasanka Rasanjana', 'item': SITE},
            {'@type': 'ListItem', 'position': 2, 'name': c['title'], 'item': url}]},
    ]}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + '</script>'


def page(c):
    facts = ''.join(f'<div><dt>{e(a)}</dt><dd>{e(b)}</dd></div>' for a, b in c['facts'])
    # The app's own website, when it has one: a button under the facts in the top card
    site_html = ''
    if c.get('site'):
        label, url = c['site']
        site_html = f'\n      <a class="btn btn-dark cs-site" href="{url}" target="_blank" rel="noopener">{e(label)} {ARROW_OUT}</a>'
    cover, wide = c['cover']
    if cover == 'PHONES':
        ph = ''.join(f'<div class="phone"><div class="screen"><img src="../img/{n}.webp" alt="{e(c["title"])} screen"></div></div>' for n in wide)
        cover_html = f'<div class="cs-cover cs-phones sc-phones" data-rise style="--d:150ms">{ph}</div>'
    else:
        cover_html = f'<div class="cs-cover{" is-wide" if wide else ""}" data-rise style="--d:150ms"><img src="../{cover}" alt="{e(c["title"])} screens" width="{size(cover)[0]}" height="{size(cover)[1]}"></div>'
    pills = ''.join(f'<a href="#{sid}">{e(label)}</a>' for sid, label, _ in c['sections'])
    secs = ''.join(f'<section class="cs-sec" id="{sid}">{body}</section>' for sid, _, body in c['sections'])
    nslug, ntitle, nimg, nsoft = c['next']
    if isinstance(nimg, list):
        media = '<div class="sc-phones">' + ''.join(f'<div class="phone"><div class="screen"><img src="../img/{n}.webp" alt="" loading="lazy"></div></div>' for n in nimg) + '</div>'
    else:
        media = f'<img src="../{nimg}" alt="" loading="lazy">'
    stitle, sdesc = seo_for(c)
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(stitle)} | Sasanka Rasanjana</title>
  <meta name="description" content="{e(sdesc)}">
  <meta name="author" content="Sasanka Rasanjana">
  <meta name="theme-color" content="#ffffff">
  <link rel="icon" href="../favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="../apple-touch-icon.png">
  <link rel="canonical" href="https://sasankarasanjana29.github.io/sasanka-rasanjana-portfolio/work/{c['slug']}.html">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{e(stitle)} | Sasanka Rasanjana">
  <meta property="og:description" content="{e(sdesc)}">
  <meta property="og:url" content="{SITE}work/{c['slug']}.html">
  <meta property="og:site_name" content="Sasanka Rasanjana">
  <meta property="og:image" content="https://sasankarasanjana29.github.io/sasanka-rasanjana-portfolio/og.jpg?v=2">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="preload" as="image" href="../img/phone-frame.webp" fetchpriority="high">
  <link rel="preload" href="../fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="../fonts/inter-tight-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="../styles.css?v=20261128b">
  <script>document.documentElement.classList.add('js')</script>
  {jsonld(c, stitle, sdesc)}
</head>
<body class="{c['theme']}">
<header class="nav" id="nav">
  <a class="nav-me" href="../index.html"><img src="../img/me-nav.webp" alt="" width="32" height="32"><span>Sasanka</span></a>
  <nav class="nav-links" aria-label="Site"><a href="../index.html#work">Work</a><a href="../index.html#apps">Apps</a><a href="../index.html#about">About</a><a href="../index.html#contact">Contact</a></nav>
  <a class="btn btn-sm btn-dark" href="../Sasanka_Rasanjana_CV.pdf" target="_blank" rel="noopener">Resume</a>
</header>
<main class="cs">
  <header class="cs-hero">
    <div class="cs-intro" data-rise>
      <a class="back" href="../index.html#work">{ARROW_L}All work</a>
      <p class="case-meta" style="margin-top:28px">{e(c['meta'])}</p>
      <h1>{e(c['title'])}</h1>
      <p class="cs-lede">{e(c['lede'])}</p>{f'<p class="cs-note">{e(c["note"])}</p>' if c.get('note') else ''}
      <dl class="facts">{facts}</dl>{site_html}
    </div>
    {cover_html}
  </header>
  <nav class="cs-nav" aria-label="On this page">{pills}</nav>
  {secs}
  <nav class="next" id="next-case" aria-label="Next case study">
    <a href="{nslug}.html" style="--n-soft:{nsoft}">
      <div class="next-text"><small>Next case study</small><b>{e(ntitle)}</b><p>{e(NEXT_LINE[nslug])}</p><span class="case-cta">Read next {ARROW_R}</span></div>
      <div class="next-media">{media}</div>
    </a>
  </nav>
  <p class="footer-note" style="padding:40px 0">Designed and built by Sasanka, with Claude Code. 2026.</p>
</main>
<script src="../vendor-lenis.min.js" defer></script>
<script src="../main.js?v=20261126a" defer></script>
<script data-goatcounter="https://sasanka.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
</body>
</html>
'''


os.makedirs(os.path.join(ROOT, 'work'), exist_ok=True)
for c in (TRUST, VELA, KEELLS, ZEST, POUCH, CLOUDIA, FRET):
    open(os.path.join(ROOT, 'work', c['slug'] + '.html'), 'w').write(page(c))
    print('wrote', c['slug'])
