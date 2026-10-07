# Validation — 0.2.0 / 2026-10-07

Local Linux / Python 3.12.14:

- 75 automated language/configuration checks passed. Browser integration tests are opt-in and skipped in this local core run.
- HTTP tests use a real local server for JSON payloads, headers, query parameters, 404 inspection and loaded bodies. Seven methods have dispatch coverage.
- Configuration rejects unsupported provider/browser pairs, invalid dimensions and incompatible maximization settings. CLI override precedence is covered.
- Ruff checks passed for source, tests and scripts.
- 15 pages per documentation language, 44 TestScript excerpts parsed; both MkDocs builds passed strict mode.
- Wheel and sdist built successfully; clean-environment wheel installation, `pip check`, CLI version and four core/data cases passed.

The CI browser matrix covers Playwright Chromium, Firefox, WebKit, Chrome and Edge, and Selenium Chrome, Firefox and Edge. Each job exercises both private and normal temporary profiles, viewport dimensions, browser actions, screenshots and cookie isolation across tests.

Maximization is validated as configuration; native headed maximization depends on the display/window manager and has not been tested in this headless environment. Windows/macOS installation has not been tested.

The new landing direction is pending visual selection. Current-layout theme tokens and documentation palettes are updated; this release does not claim the final landing redesign.

PyPI publication is pending account/Trusted Publisher configuration. See [publishing](PUBLISHING.md).
