# Roadmap and current scope

Roadmap entries are intentions, not implemented capabilities or delivery dates.

## 0.1.0 — first vertical slice

Implemented: grammar/parser, interpreter, typed boundaries, records, fn/flow, test/fixture/data/step, basic exceptions, tags, module imports, local CSV/JSON/YAML, CLI diagnostics, optional browser adapters, HTTP responses, HTML/JSON/JUnit and bilingual MkDocs.

## Next iterations

1. Harden grammar, diagnostics, type inference and return-path validation using real suites.
2. Add assertion retries with explicit safe semantics, automatic failure evidence and richer result events.
3. Extend Web locators/frames/windows and HTTP/schema validation as real examples require them.
4. Add formatting and VS Code syntax/editor support, followed by an LSP if warranted.
5. Introduce controlled parallel execution and richer fixture scopes without breaking isolation.
6. Evaluate Mobile adapters and stable reporter integrations.

## Before a stable 1.0

Freeze the public language syntax and event/provider contracts, document compatibility policy, validate installations across supported OS/Python versions and demonstrate maintainable real-world Web/API suites. Version 0.1 is not a claim of production maturity.

## Publication

The distribution name is `testscript-lang`, subject to registration. `.tscr` and `tscr` remain stable product identifiers. PyPI publication, GitHub remote creation and Pages activation require actual successful publication steps; documentation must not describe them as completed until then.
