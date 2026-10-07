# API testing

HTTP requests are expressions: an uppercase method, a URL and one declarative block. A request returns a response value. HTTPX creates a client lazily and closes it after each test/data row.

## Send a request

```tscr
var token = "local-example"
var response = POST "http://127.0.0.1:8765/users" {
    headers { "Authorization": "Bearer ${token}" }
    query { notify: true }
    body json {
        name: "Angel"
        role: "tester"
    }
}
expect response.status == 201
expect response.json.name == "Angel"
```

Methods: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, `OPTIONS`. The block is required, even when empty. `headers`, `query` and `body json` are optional and can appear in any order, once each. Headers are a map of strings; query is a map; JSON accepts a serializable value. JSON bodies automatically receive `Content-Type: application/json` unless explicitly overridden. Property commas are optional in maps, including nested maps; list commas remain required.

## Reuse loaded payloads

```tscr
flow submitUser(baseUrl: String) -> Map[String, Any] {
    var payload = load("data/user.json")
    return POST "${baseUrl}/users" { body json payload }
}
test "Create user" {
    const response = submitUser("http://127.0.0.1:8765")
    expect response.status == 201
}
```

`load()` selects JSON, YAML or CSV from the filename extension. Paths resolve relative to the declaring module. Requests may run in tests, flows and fixtures; they are forbidden inside `fn` and module initializers. `check` and `list` never send a request.

## Response fields

| Field | Value |
|---|---|
| `status` | Integer HTTP status |
| `json` | Decoded JSON, or null for non-JSON/empty bodies |
| `text` | Response text |
| `headers` | Map with normalized lowercase header names |
| `url` | Final URL after redirects |

Responses are eager values. Redirects are followed; TLS verification stays enabled. Proxy environment variables are not implicitly used. Cookies last within a test and are cleared between tests.

## Negative HTTP responses

```tscr
var response = GET "http://127.0.0.1:8765/users/missing" {}
expect response.status == 404
expect response.json.error == "User not found"
```

HTTP 4xx/5xx are response values. Connection, timeout and TLS failures throw catchable execution errors. Assertions determine whether a response meets the test's expectation.

## Base URL and timeouts

```toml
[testscript]
base_url = "http://127.0.0.1:8765"
timeout = 10
```

`GET "/users/missing" {}` joins the configured base URL and path. Full URLs are used directly. Timeout is HTTPX's request timeout, not a whole-test deadline.

Start `python examples/demo_server.py`, then run `tscr run examples/api.tscr`. OAuth helpers, multipart uploads, retries, JSON Schema/OpenAPI assertions and streaming are future work. Use `env("TOKEN")` in tests/flows for credentials.

!!! warning "Migration from 0.1"
    `api.get(...)` and `api.post(...)` were removed in 0.2. Replace them with `GET url {}` and `POST url { body json payload }`. The response fields remain the same. See the [changelog](changelog.md).
