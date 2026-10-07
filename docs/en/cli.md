# CLI and configuration

```bash
tscr --version
tscr check tests/
tscr lint tests/ --flows-only --strict
tscr list tests/ --tag smoke
tscr run tests/ --tag smoke --exclude-tag slow --name Login
```

Paths may be files or directories. Discovery is recursive for `.tscr` files, with stable lexical order; hidden directories, `node_modules`, `site`, `build` and `dist` are excluded. Default path: `tests/`. Imported modules are validated, but their tests only run when the module is also part of the selected entry paths.

## Commands

| Command | Behavior |
|---|---|
| `check` | Parse and validate all entry files/imports |
| `lint` | Check + naming warnings; optional flows-only rule |
| `list` | Show selected test declarations without executing bodies |
| `run` | Execute selected cases sequentially and write reports |

`check`/`list` do not open browsers or send HTTP requests. Module-level constants and data are loaded; file errors are diagnosed. A module may read an environment variable via a constant initializer.

## Filters

Repeated `--tag` flags select tests matching **any** included tag. Repeated `--exclude-tag` flags remove tests matching **any** excluded tag. `--name` uses case-sensitive substring matching. Tags are metadata on tests only; fixtures/flows do not inherit or propagate them. Boolean tag expressions are not supported in v0.2.

## Configuration

The CLI reads `testscript.toml` in the process working directory, or the file supplied with `--config`. It does not search parent directories. No file means defaults; a missing explicitly supplied file currently also uses defaults.

```toml
[testscript]
provider = "playwright"
browser = "chromium"
headless = true
incognito = true
viewport_width = 1440
viewport_height = 900
maximize = false
timeout = 10
base_url = "http://127.0.0.1:8765"
output = "testscript-results"
tests_use_flows_only = false
```

Unknown keys and invalid values are errors. `--provider` and `--output` override their corresponding values. Output paths are relative to the process working directory. Data/import paths are relative to their declaring module.

`tests_use_flows_only` emits warnings for direct browser/HTTP actions inside tests. `--flows-only` enables it for a lint invocation. `--strict` turns linter warnings into an unsuccessful check.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Successful check/list or no failed executed cases |
| 1 | One or more failed cases |
| 2 | Invalid program, input or configuration |
| 5 | No `.tscr` files or no tests selected |

Formatter, watch mode, parallel workers and editor/LSP integration are not implemented yet.

Browser flags and compatibility are documented in [Web automation](web.md). CLI overrides are applied before validation. Data-row results inherit all tags from their test; there are no per-row tags.
