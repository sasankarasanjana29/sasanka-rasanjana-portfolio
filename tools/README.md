# Build scripts

Copies of the scripts that build this site and the portfolio PDF. They expect
the local Portfolio folder layout, so run them from `Portfolio/`:

- `python3 tools/build_cases.py`, then `python3 tools/add_srcset.py`: writes `site/work/*.html`
- `python3 deck/build_pdf.py`: renders `deck/deck.html` to `Sasanka_Rasanjana_Portfolio.pdf`

On a new machine, copy `tools/` to `Portfolio/tools/` and `tools/deck/build_pdf.py`
to `Portfolio/deck/`.
