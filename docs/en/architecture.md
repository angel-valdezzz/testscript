# Architecture

TestScript separates language semantics from automation engines.

| Layer | Module | Responsibility |
|---|---|---|
| Syntax | `grammar.lark`, `parser.py` | Lark grammar, parse tree and source locations |
| Values | `model.py` | Types, records, callables and lexical environments |
| Validation | `analysis.py` | Names, type diagnostics, effects and linter rules |
| Execution | `runtime.py` | Modules, expressions, statements, fixtures and test lifecycle |
| Providers | `adapters/http.py`, `adapters/web.py` | HTTPX and optional browser engines |
| Reporting | `reporting.py` | Event model to HTML/JSON/JUnit |
| Interface | `cli.py` | Discovery, configuration, filters and exit codes |
| Documentation | `highlighting.py`, `docs/` | Native syntax highlighting and bilingual guides |

## Why Python + Lark?

Python provides packaging and access to mature automation libraries. Lark lets the language grammar be explicit instead of extracting statements with ad-hoc string matching. The interpreter executes a location-aware syntax tree directly. There is no transpilation or separate IR in v0.2; an intermediate representation can be introduced when there is a concrete optimization need.

## Provider boundary

Browser adapters share a protocol for navigation, actions, observations, screenshots and cleanup. The runtime holds a lazy provider instance per test. HTTP responses use language-native maps. Neither provider owns language scopes, type rules, tag filtering or test status.

## Event boundary

The runtime emits steps, flows, logs, assertion outcomes, HTTP status/URLs, fixture phases and screenshot references. Reports consume these events rather than re-running test logic. Future integrations with Evidence Reporter/Request Reporter should consume a stable event contract; they are not dependencies of this MVP.

## Verification

Tests cover syntax diagnostics, type/name checks, imports, data, exceptions, fixture failure cleanup, tag selection, CLI exit codes, report escaping and local HTTP. Provider contracts have unit coverage; browser integration tests use a controlled local form with Playwright and Selenium. CI builds both documentation languages and wheel/sdist artifacts.
