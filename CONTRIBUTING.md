# Contributing

Python 3.12+ is required. Install with `python -m pip install -e ".[dev,playwright,selenium]"`.

A language change must update the grammar, interpreter/analyzer, regression tests, runnable examples, specification and both documentation languages in the same change. Do not advertise a roadmap feature as implemented.

Run:

```bash
python -m ruff check src tests scripts
python -m pytest -q
python -m testscript check examples
python scripts/check_docs.py
python scripts/build_docs.py
python -m build
```

For real browser tests, install Chromium and Chrome/driver, then set `TSCR_RUN_BROWSER_TESTS=1`. Optionally set `TSCR_TEST_PROVIDER=playwright` or `selenium` to choose one. CI enables these integration tests separately from core tests.

Keep the language independent from browser engines. New providers must satisfy the action/locator protocol and demonstrate cleanup/isolation against a controlled service. Tests must not rely on public demos as their only evidence.

## Initial publication

Create the `angel-valdezzz/testscript` remote, push `main`, and enable GitHub Pages with GitHub Actions as the source. The included Pages workflow builds English first and Spanish at `/es/`.

The distribution is **not published** to PyPI yet. Register the chosen distribution and configure Trusted Publishing before adding a PyPI release workflow. The existing `testscript` package is unrelated; never publish to or claim ownership of it.
