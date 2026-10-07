# Changelog

## 0.2.0 — 2026-10-07

- **Breaking:** replace `api.*` calls with declarative HTTP expressions: `POST url { headers {...} query {...} body json payload }`. Empty requests use `GET url {}`; response fields are unchanged.
- Optional commas between map properties, including JSON request bodies.
- Browser selection, private/normal temporary profiles, viewport dimensions and headed maximization with configuration validation.
- More API/naming/return examples, bilingual reference, unified logo, version/CI badges and light/dark palettes.
- The new landing direction is under visual review; it is not included in this release.


## 0.1.0 — 2026-10-07

Initial experimental implementation of TestScript: `.tscr` grammar, Python/Lark interpreter, CLI, typed records and function boundaries, reusable flows, per-case fixtures, parameterized data, tags, basic exceptions, optional Playwright/Selenium adapters, HTTPX API operations, HTML/JSON/JUnit results and English/Spanish documentation.

Distribution publication is pending. See the [roadmap](roadmap.md) and [specification](specification.md) for the current contract and exclusions.
