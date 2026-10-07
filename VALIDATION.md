# Local validation — 2026-10-07

Validated on Linux / Python 3.12.14:

- **41 pytest checks passed**, including HTTP against a local service and real Playwright/Selenium browser workflows.
- **7 example cases passed with each provider**: two API, four core/data and one Web.
- Ruff checks passed for source, tests and scripts.
- **15 pages per documentation language**, 40 TestScript snippets parsed; both MkDocs builds passed strict mode.
- Desktop (1440 px) and mobile (390 px) reviewed; no horizontal page overflow; Web/API tabs, keyboard tab navigation, native syntax highlighting and JavaScript errors checked.
- Wheel and sdist built successfully.
- Wheel installed into a clean virtual environment, `pip check` passed, CLI version/check/run verified.

Browser verification used Chromium 153 and compatible ChromeDriver 153 in this environment. The normal Playwright browser download endpoint was unavailable here, so a compatible local binary was supplied through `TSCR_BROWSER_EXECUTABLE`; Selenium used `TSCR_DRIVER_EXECUTABLE`. Container-only verification supplied `TSCR_BROWSER_NO_SANDBOX=1`; it is not enabled by default.

CI configuration includes Python 3.12/3.13/3.14, separate provider integration jobs, documentation and distribution builds. **Remote CI has not run yet.** The public GitHub repository has been created. PyPI publication and GitHub Pages activation remain pending. Windows/macOS installation has not been tested here.

For a local documentation preview:

```bash
python scripts/build_docs.py
python scripts/serve_docs.py
```

The deliverable archive includes the prebuilt `site/` folder, a wheel and a Git history bundle. The bundle can be used with `git clone git-history.bundle restored-testscript`.
