<div align="center">

[**English**](https://github.com/angel-valdezzz/testscript/blob/main/README.md) · [Español](https://github.com/angel-valdezzz/testscript/blob/main/README.es.md)

<img src="https://raw.githubusercontent.com/angel-valdezzz/testscript/main/docs/assets/logo.svg" width="80" height="80" alt="TestScript" />

# TestScript


A typed testing language for Web and API automation. Python interpreter · Lark grammar · `.tscr` files · `tscr` CLI.

[User Guide](https://angel-valdezzz.github.io/testscript/) · [Language Reference](https://angel-valdezzz.github.io/testscript/language/) · [PyPI](https://pypi.org/project/testscript-lang/)

[![PyPI](https://img.shields.io/pypi/v/testscript-lang?color=c4f581)](https://pypi.org/project/testscript-lang/) [![CI](https://github.com/angel-valdezzz/testscript/actions/workflows/ci.yml/badge.svg)](https://github.com/angel-valdezzz/testscript/actions/workflows/ci.yml)

</div>

> **0.2.0 / experimental.** The implementation and language specification evolve together. Install the `testscript-lang` distribution; the PyPI name `testscript` belongs to an unrelated project.

## Install

Python 3.12+:

```bash
python -m pip install testscript-lang
tscr --version
```

```bash
git clone https://github.com/angel-valdezzz/testscript.git
cd testscript
tscr check examples/core.tscr
tscr run examples/core.tscr
```

For browser automation:

```bash
python -m pip install "testscript-lang[playwright]"
python -m playwright install chromium
```

Or `python -m pip install "testscript-lang[selenium]"` with Chrome available. API and core examples do not need a browser. Example files are available in the repository and are not installed by the package.

## A small language with a testing purpose

```text
flow verifyName(name: String) {
    step "Validate the name" {
        expect len(name) > 0
    }
}

test "A valid user" tags ["smoke"] {
    verifyName("Angel")
}
```

- `test`: discoverable execution unit.
- `flow`: reusable behavior; can compose flows and return values.
- `fn`: pure data computation; no browser/HTTP/observability effects.
- `fixture`: setup and teardown, including cleanup after setup failure.
- `record`: typed immutable fields.
- `data`: CSV/JSON/YAML parameterization; one result per row.
- `step`: a named section in the execution timeline.
- `expect`: assertions; catching an assertion does not erase its failure.

## Commands

| Command | Purpose |
|---|---|
| `tscr check tests/` | Syntax, names, types and effect checks |
| `tscr lint tests/ --flows-only` | Semantic checks + optional naming/architecture warnings |
| `tscr list tests/ --tag smoke` | Discover and filter tests |
| `tscr run tests/ --provider playwright` | Run with JSON, JUnit XML and standalone HTML results |

Repeat `--tag` for **OR** inclusion; repeat `--exclude-tag` to exclude any matching tag. `--name` is a case-sensitive title substring. Exit codes: 0 passed/skipped, 1 test failure, 2 invalid input/configuration, 5 no tests selected.

## Development

```bash
python -m pip install -e ".[dev,playwright,selenium]"
python -m pytest
python -m ruff check src tests
python scripts/check_docs.py
python scripts/build_docs.py
python -m build
```

See [specification](docs/en/specification.md), [architecture](docs/en/architecture.md), [roadmap](docs/en/roadmap.md) and [contributing](CONTRIBUTING.md).

## Credits

Built on Python, Lark, HTTPX, PyYAML, Playwright/Selenium and MkDocs Material. TestScript is an independent project; it is not affiliated with these projects or the existing PyPI package named `testscript`.

MIT · Angel Gerardo Molina Valdez
