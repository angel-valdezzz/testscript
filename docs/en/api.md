# API testing

`api` is a built-in HTTP namespace backed by HTTPX. It creates a client lazily and closes it after each test/data row.

## Send a request

```tscr
var response = api.post(
    "http://127.0.0.1:8765/users",
    body: {name: "Angel"},
    headers: {"Content-Type": "application/json"}
)
expect response.status == 201
expect response.json.name == "Angel"
```

Methods: `get`, `post`, `put`, `patch`, `delete`, `head`, `options`. Every method accepts `url`, optional JSON `body`, `headers` and `query`. Query parameters are supplied as a map. Responses are eager values, not streaming objects.

| Field | Value |
|---|---|
| `status` | Integer HTTP status |
| `json` | Decoded JSON, or null for non-JSON bodies |
| `text` | Response text |
| `headers` | Map with normalized lowercase header names |
| `url` | Final URL after redirects |

Redirects are followed. TLS verification remains enabled. Proxy environment variables are not implicitly used by this MVP. Cookies are retained within a test and cleared through client teardown between tests.

## Negative HTTP responses

```tscr
var response = api.get("http://127.0.0.1:8765/users/missing")
expect response.status == 404
expect response.json.error == "User not found"
```

HTTP 4xx/5xx are normal response values. Transport errors (connection, timeout, TLS) throw catchable execution errors. An assertion determines whether an inspected response meets the test's expectation.

## Base URL and timeouts

```toml
[testscript]
base_url = "http://127.0.0.1:8765"
timeout = 10
```

With a base URL, `api.get("/users/missing")` concatenates the configured base and path. Full URLs are used directly. `timeout` is passed to HTTPX's timeout configuration; it is not a whole-test deadline.

Run the local server and `tscr run examples/api.tscr`. The example creates and retrieves a user and checks a missing user. The demo stores data in memory and is only for local verification.

OAuth helpers, multipart uploads, retries, JSON Schema/OpenAPI assertions and direct integrations with other reporters are roadmap items. Never put secrets into committed example files; `env("TOKEN")` is available in tests/flows.
