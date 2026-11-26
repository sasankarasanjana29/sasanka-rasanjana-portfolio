# Build scripts

Copies of the scripts and sources that build this site, the CV and the portfolio PDF. They expect
the local Portfolio folder layout, so run them from `Portfolio/`:

- `python3 tools/build_cases.py`, then `python3 tools/add_srcset.py`: writes `site/work/*.html`
- `python3 deck/build_pdf.py`: renders `deck/deck.html` to `Sasanka_Rasanjana_Portfolio.pdf`.
  The deck's own images are in `deck/img/`; everything else it loads from `../site/`.
- CV: `cv/cv.html` is the source of `Sasanka_Rasanjana_CV.pdf`. From `Portfolio/cv/`, run
  `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf=Sasanka_Rasanjana_CV.pdf "file://$PWD/cv.html"`
  and check it is still 1 page, then copy the PDF into `site/`.

On a new machine, copy `tools/` to `Portfolio/tools/`, `tools/deck/` (deck.html, img/, build_pdf.py)
to `Portfolio/deck/`, and `tools/cv/cv.html` to `Portfolio/cv/`.

The site itself (this repo's root) goes in `Portfolio/site/`, since the deck and the
case-page scripts read from there.
