# Complete examples

The repository includes a deterministic lab so verification does not rely on public demo sites. The lab uses loopback only, keeps users in memory and resets when restarted.

| File | Demonstrates | Requires |
|---|---|---|
| `examples/core.tscr` | Records, typed function/flow, fixture, data, control and errors | Base package |
| `examples/api.tscr` | Create/read user, HTTP 404 inspection | Local lab |
| `examples/web.tscr` | Imported login flow, UI checks and screenshot | Local lab + browser extra |
| `examples/login-flow.tscr` | Reusable Web behavior | Imported by Web example |
| `examples/data/users.*` | Equivalent CSV/JSON/YAML data | Used through `load()` |

## Core

```bash
tscr check examples/core.tscr
tscr run examples/core.tscr
```

Expected: four passing results, including two data rows.

## Web and API

Terminal one:

```bash
python examples/demo_server.py
```

Terminal two:

```bash
tscr run examples/api.tscr
tscr run examples/web.tscr --provider playwright
tscr run examples/web.tscr --provider selenium
```

Expected: two API cases and one Web case. The Web case types a name, selects a role, checks a checkbox, submits the form and verifies the greeting. Browser drivers/binaries must be installed first.

## All supported examples

```bash
tscr check examples/
tscr run examples/ --tag core
tscr run examples/ --tag api
tscr run examples/ --tag web
```

`login-flow.tscr` contributes no independent test. Automated CI is configured to verify core/API against a local service and exercise the Web example against both providers. ParaBank/Demo Users adaptations can be added later with explicit environment configuration; public availability is not a release criterion.
