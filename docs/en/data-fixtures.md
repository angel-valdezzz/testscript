# Data and fixtures

## Parameterize tests

```tscr
data users = load("data/users.json")
test "A named user" tags ["data"] for each user in users {
    expect len(user.name) > 0
}
```

Each row yields a result such as `A named user [1]`. Fixtures and browser isolation apply per row. The dataset must be a non-empty list; empty or malformed data is an input error, not a passing test.

`load()` resolves relative paths from the current module, independent of the process working directory. `Path()` can be passed to `load()`.

=== "JSON"

    ```json
    [{"name": "Angel", "active": true}]
    ```

=== "CSV"

    ```csv
    name,active
    Angel,true
    ```

=== "YAML"

    ```yaml
    - name: Angel
      active: true
    ```

CSV values are strings. JSON/YAML preserve supported scalar types. Convert CSV explicitly with `int()`/`float()` or compare strings. YAML is loaded safely without arbitrary object construction.

## Fixtures and lifecycle

```tscr
fixture session {
    setup {
        var baseUrl: String = "http://127.0.0.1:8765"
        log "Session ready"
    }
    teardown {
        log "Session closed"
    }
}

test "Session" using [session] {
    expect baseUrl contains "127.0.0.1"
}
```

1. Set up listed fixtures from left to right.
2. Expose successful setup bindings to the test.
3. Run the test body.
4. Tear down started fixtures from right to left.
5. Close the test's HTTP client and browser.

Started fixtures are cleaned up even if their setup failed. Teardown can access bindings created before that failure; cleanup must account for resources not fully initialized. A teardown failure marks the case failed and preserves earlier reported failures. Skipping a test also triggers cleanup.

Fixtures have independent module environments. They do not implicitly depend on another fixture's bindings. Duplicate exported bindings are errors. Suite/session scopes, fixture dependency injection and lazy fixture resolution are future work.

Browser creation is lazy: API-only tests never launch one. Each test or row gets a fresh browser instance. Flows receive fixture values explicitly as parameters.
