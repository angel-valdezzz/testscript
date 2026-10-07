# Validation — 2026-10-07

Validated on Linux / Python 3.12.14:

- **41 pytest checks passed**, including HTTP against a local service and real Playwright/Selenium browser workflows.
- **7 example cases passed with each provider**: two API, four core/data and one Web.
- Ruff checks passed for source, tests and scripts.
- **15 pages per documentation language**, 40 TestScript snippets parsed; both MkDocs builds passed strict mode.
- Desktop (1440 px) and mobile (390 px) reviewed; no horizontal page overflow; Web/API tabs, keyboard tab navigation, native syntax highlighting and JavaScript errors checked.
- Wheel and sdist built successfully.
- Wheel installed into a clean virtual environment, `pip check` passed, CLI version/check/run verified.

Browser verification used Chromium 153 and compatible ChromeDriver 153 in this environment. The normal Playwright browser download endpoint was unavailable here, so a compatible local binary was supplied through `TSCR_BROWSER_EXECUTABLE`; Selenium used `TSCR_DRIVER_EXECUTABLE`. Container-only verification supplied `TSCR_BROWSER_NO_SANDBOX=1`; it is not enabled by default.

## Remote verification and publication

The public repository is live at https://github.com/angel-valdezzz/testscript.

All six GitHub Actions verification jobs passed for commit `23e75db7d9eaac529c2a565ad786fd804e05409b`: core on Python 3.12, 3.13 and 3.14, real Playwright and Selenium browser workflows, and documentation/distribution builds.

Verification run: https://github.com/angel-valdezzz/testscript/actions/runs/37693918326

The documentation build and deployment passed. English and Spanish pages are live at https://angel-valdezzz.github.io/testscript/ and https://angel-valdezzz.github.io/testscript/es/. The Spanish landing page was reviewed after publication.

Pages run: https://github.com/angel-valdezzz/testscript/actions/runs/37693918357

PyPI publication remains pending. Windows/macOS installation has not been tested here.

For a local documentation preview:

```bash
python scripts/build_docs.py
python scripts/serve_docs.py
```

The deliverable archive includes the prebuilt `site/` folder, a wheel and a Git history bundle. The bundle can be used with `git clone git-history.bundle restored-testscript`.
