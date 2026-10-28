// Small interactions only. CSS owns all motion; this says when.

const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const fine = matchMedia('(hover: hover) and (pointer: fine)').matches;

// Scroll reveal: fade up once, with a short stagger for siblings in a grid.
const reveal = document.querySelectorAll('[data-reveal]');
document.querySelectorAll('.cases, .about, .grid2, .grid3, .stat-row').forEach((grid) => {
  [...grid.querySelectorAll('[data-reveal]')].forEach((el, i) => el.style.setProperty('--stagger', `${(i % 2) * 90}ms`));
});
if ('IntersectionObserver' in window) {
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (!e.isIntersecting) continue;
      e.target.classList.add('is-in');
      io.unobserve(e.target);
    }
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0 });
  reveal.forEach((el) => io.observe(el));
} else {
  reveal.forEach((el) => el.classList.add('is-in'));
}
// Safety net: if a browser pauses the observer, a plain scroll check still reveals what is on screen.
let ticking = false;
const sweep = () => {
  ticking = false;
  reveal.forEach((el) => { if (!el.classList.contains('is-in') && el.getBoundingClientRect().top < innerHeight * 0.95) el.classList.add('is-in'); });
};
addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(sweep); } }, { passive: true });
setTimeout(sweep, 1200);

// Smooth, weighted wheel scrolling (Lenis, vendored). Mouse and trackpad on a
// desktop only: touch keeps the platform's own scrolling, and reduced motion
// keeps native scrolling. In-page links glide and land under the nav.
if (window.Lenis && fine && !reduce) {
  const lenis = new Lenis({ lerp: 0.1, smoothWheel: true, anchors: { offset: -96 } });
  window.__lenis = lenis;
  const raf = (t) => { lenis.raf(t); requestAnimationFrame(raf); };
  requestAnimationFrame(raf);
}

// Stagger: children of groups that arrive together get their index.
document.querySelectorAll('.journey, .tools, .stat-row').forEach((g) => {
  [...g.children].forEach((c, i) => c.style.setProperty('--i', Math.min(i, 8)));
});

// Lazy images fade in when they arrive (already-loaded ones show at once).
document.querySelectorAll('img[loading="lazy"]').forEach((img) => {
  if (img.complete && img.naturalWidth) return;
  img.classList.add('fade');
  const done = () => img.classList.add('is-loaded');
  img.addEventListener('load', done, { once: true });
  img.addEventListener('error', done, { once: true });
});

// Nav frosts once the page moves.
const nav = document.getElementById('nav');
const onScroll = () => nav.classList.toggle('is-scrolled', scrollY > 24);
addEventListener('scroll', onScroll, { passive: true });
onScroll();

// Hero reel: a second copy of the screens makes the loop seamless.
const reel = document.querySelector('.reel-track');
if (reel) reel.append(...[...reel.children].map((n) => n.cloneNode(true)));

// Experience: the line fills and each dot lights as you scroll past it.
const line = document.querySelector('.timeline');
if (line) {
  const items = line.querySelectorAll('li');
  const fill = () => {
    const r = line.getBoundingClientRect();
    const p = Math.min(1, Math.max(0, (innerHeight * 0.6 - r.top) / r.height));
    line.style.setProperty('--fill', p.toFixed(3));
    items.forEach((li) => li.classList.toggle('is-lit', li.getBoundingClientRect().top < innerHeight * 0.6));
  };
  addEventListener('scroll', fill, { passive: true });
  fill();
}

// FAQ: one open at a time.
const qs = document.querySelectorAll('.faq-q');
qs.forEach((q) => q.addEventListener('click', () => {
  const open = q.getAttribute('aria-expanded') !== 'true';
  qs.forEach((o) => o.setAttribute('aria-expanded', 'false'));
  q.setAttribute('aria-expanded', String(open));
}));

// Copy email, with the label sliding to "Copied".
const live = document.getElementById('live');
document.querySelectorAll('.copy').forEach((btn) => btn.addEventListener('click', async () => {
  const email = btn.dataset.email;
  try {
    await navigator.clipboard.writeText(email);
    btn.classList.add('is-done');
    if (live) live.textContent = 'Email copied';
    setTimeout(() => btn.classList.remove('is-done'), 1800);
  } catch {
    location.href = `mailto:${email}`;
  }
}));

// Case pages: the contents list follows the section you are reading.
const toc = document.querySelectorAll('.cs-nav a');
if (toc.length) {
  const byId = new Map([...toc].map((a) => [a.hash.slice(1), a]));
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (!e.isIntersecting) continue;
      toc.forEach((a) => a.classList.remove('is-on'));
      const a = byId.get(e.target.id);
      a?.classList.add('is-on');
      if (a) { const bar = a.parentElement; bar.scrollTo({ left: a.offsetLeft - (bar.clientWidth - a.offsetWidth) / 2, behavior: reduce ? 'auto' : 'smooth' }); }
    }
  }, { rootMargin: '-30% 0px -60% 0px' });
  byId.forEach((_, id) => { const s = document.getElementById(id); if (s) io.observe(s); });
}

// Case pages: tap a board to read it full width.
const zoomable = document.querySelectorAll('.rail img, .frame img, .shots img, .reviews img');
if (zoomable.length) {
  const box = document.createElement('div');
  box.className = 'lightbox';
  box.setAttribute('role', 'dialog');
  box.setAttribute('data-lenis-prevent', '');
  box.setAttribute('aria-label', 'Enlarged image');
  box.innerHTML = '<button aria-label="Close"><svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6 6 18"/></svg></button><img alt="">';
  document.body.append(box);
  const big = box.querySelector('img');
  const close = () => { box.classList.remove('is-open'); document.body.style.overflow = ''; window.__lenis?.start(); };
  zoomable.forEach((img) => img.addEventListener('click', () => {
    big.removeAttribute('srcset');
    big.src = img.getAttribute('src').startsWith('..') ? new URL(img.getAttribute('src'), location.href).href : img.src;
    big.alt = img.alt;
    box.scrollTop = 0;
    box.classList.add('is-open');
    document.body.style.overflow = 'hidden';
    window.__lenis?.stop();
    box.querySelector('button').focus();
  }));
  box.addEventListener('click', close);
  addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });
}

// Screen rails: arrow buttons move one screen at a time.
document.querySelectorAll('.group').forEach((g) => {
  const rail = g.querySelector('.rail');
  const [prev, next] = g.querySelectorAll('.rail-btns button');
  if (!rail || !prev) return;
  const step = () => (rail.querySelector('figure')?.offsetWidth || 240) + 14;
  const sync = () => {
    prev.disabled = rail.scrollLeft < 4;
    next.disabled = rail.scrollLeft + rail.clientWidth > rail.scrollWidth - 4;
  };
  prev.addEventListener('click', () => rail.scrollBy({ left: -step(), behavior: 'smooth' }));
  next.addEventListener('click', () => rail.scrollBy({ left: step(), behavior: 'smooth' }));
  rail.addEventListener('scroll', sync, { passive: true });
  addEventListener('resize', sync);
  sync();
});

// Name: pointing at it sends one wave through the letters (no colour change).
const name = document.querySelector('.hero-name');
if (name) setTimeout(() => name.classList.add('is-ready'), 1400);
if (name && fine && !reduce) {
  name.addEventListener('pointerenter', () => {
    if (!name.classList.contains('is-ready') || name.classList.contains('is-waving')) return;
    name.classList.add('is-waving');
    setTimeout(() => name.classList.remove('is-waving'), 1300);
  });
}

// Work cards and the contact card: a soft light follows the cursor.
if (fine && !reduce) {
  document.querySelectorAll('.case, .showcase, .contact-card').forEach((el) => {
    el.addEventListener('pointermove', (e) => {
      const r = el.getBoundingClientRect();
      el.style.setProperty('--mx', `${e.clientX - r.left}px`);
      el.style.setProperty('--my', `${e.clientY - r.top}px`);
    }, { passive: true });
  });
}

// Live prototype: swap the poster for the Figma embed on tap.
document.querySelectorAll('.proto').forEach((box) => {
  box.querySelector('.proto-load')?.addEventListener('click', () => {
    const f = document.createElement('iframe');
    f.src = box.dataset.src;
    f.title = 'Live Figma prototype';
    f.allowFullscreen = true;
    box.classList.add('is-open');
    box.replaceChildren(f);
  });
});

// Hero: five apps side by side, all on the same kind of screen (home, welcome,
// key action, success, insights); the five flip together. Only the first set
// loads with the page; each next set loads just before its turn.
const spot = document.querySelector('.spot');
if (spot) {
  const phones = [...spot.querySelectorAll('.phone')].map((p) => [...p.querySelectorAll('.screen img')]);
  const dots = spot.querySelectorAll('.spot-dots i');
  const [prev, next] = spot.querySelectorAll('.spot-pager button');
  const count = phones[0].length;
  let at = 0;
  let timer;
  const load = (n) => phones.forEach((imgs) => {
    const img = imgs[n];
    if (img.dataset.srcset) { img.srcset = img.dataset.srcset; delete img.dataset.srcset; }
    if (img.dataset.src) { img.src = img.dataset.src; delete img.dataset.src; }
  });
  const show = (n) => {
    n = (n + count) % count;
    load(n);
    phones.forEach((imgs) => { imgs[at].classList.remove('is-on'); imgs[n].classList.add('is-on'); });
    dots[at].classList.remove('is-on'); dots[n].classList.add('is-on');
    at = n;
    load((n + 1) % count);
  };
  const auto = () => { clearInterval(timer); if (!reduce) timer = setInterval(() => { if (!document.hidden) show(at + 1); }, 3400); };
  prev.addEventListener('click', () => { show(at - 1); auto(); });
  next.addEventListener('click', () => { show(at + 1); auto(); });
  setTimeout(() => load(1), 1500);
  auto();
}

// Phone and tablet menu: a button in the nav pill opens a small panel with the
// same links. Built here so every page gets it from the same markup.
const navEl = document.getElementById('nav');
const navLinks = navEl?.querySelector('.nav-links');
if (navEl && navLinks) {
  const btn = document.createElement('button');
  btn.className = 'nav-menu-btn';
  btn.setAttribute('aria-label', 'Menu');
  btn.setAttribute('aria-expanded', 'false');
  btn.setAttribute('aria-controls', 'nav-panel');
  btn.innerHTML = '<span></span><span></span>';
  const panel = document.createElement('div');
  panel.className = 'nav-panel';
  panel.id = 'nav-panel';
  panel.innerHTML = [...navLinks.querySelectorAll('a')].map((a) => `<a href="${a.getAttribute('href')}">${a.textContent}</a>`).join('');
  navEl.append(panel);
  navEl.querySelector('.btn').after(btn);
  const set = (open) => {
    btn.setAttribute('aria-expanded', String(open));
    navEl.classList.toggle('is-open', open);
  };
  btn.addEventListener('click', (e) => { e.stopPropagation(); set(btn.getAttribute('aria-expanded') !== 'true'); });
  panel.addEventListener('click', (e) => { if (e.target.closest('a')) set(false); });
  document.addEventListener('click', (e) => { if (!e.target.closest('#nav')) set(false); });
  addEventListener('keydown', (e) => { if (e.key === 'Escape') set(false); });
}
