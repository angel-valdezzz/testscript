# Errors and execution results

## Exceptions

```tscr
test "Handle an operational error" {
    try {
        var response = GET "http://127.0.0.1:1" {}
    } catch error {
        log error.message
    } finally {
        log "Finished"
    }
}
```

`try` requires `catch`, `finally` or both. `catch error` exposes `message`, `path`, `line` and `column`. `throw error` rethrows that existing error. Creating custom error types or throwing arbitrary strings is outside v0.2.

A caught operational error can be handled and allow the test to pass. An assertion failure is recorded immediately and remains a failure even when caught. Cleanup runs through `finally`, fixture teardown and automatic adapter shutdown.

## Statuses

| Status | Meaning |
|---|---|
| `passed` | No recorded assertions or unhandled/cleanup errors failed |
| `failed` | Failed assertion, unhandled execution error or cleanup error |
| `skipped` | `skip "reason"` ended the case without an earlier failure |

A test with no assertions can pass; the runner does not invent validations. All-skipped selections exit with 0 in v0.2. No selected tests exits with 5.

## Output files

`tscr run` writes:

- `report.html`: standalone report with per-case events, steps, durations and screenshot links.
- `results.json`: summary and structured test events.
- `junit.xml`: interoperable CI results.
- Screenshot files explicitly requested by the script.

```bash
tscr run examples/core.tscr --output artifacts/core
```

A `step` adds grouping; logs, flows, assertions, HTTP status/URLs and fixture lifecycle events form the timeline. Reports do not capture HTTP bodies automatically. HTML text is escaped before rendering. If you log sensitive values yourself, they appear in the results.

## Diagnostics

Syntax/semantic errors include source location. The checker validates names, explicit signatures and types it can infer. External JSON/data can remain `Any`, with runtime contracts applied at typed boundaries. See the [specification](specification.md) for current limitations.
