# Language concepts

TestScript is a small, typed testing language. It describes test behavior and makes execution observable. It uses a Python interpreter, but its syntax and semantics belong to TestScript.

## test

A test is the runner's execution unit. Give it a human-readable title and optional tags. The runner discovers `.tscr` files, selects tests and records an independent result for each test or data row.

```tscr
test "A valid user" tags ["smoke"] {
    expect true
}
```

Tests can call flows and perform direct actions. Tests are not callable functions; fixtures and steps are not separately selected by the CLI.

## flow

A flow packages reusable behavior. It can interact with Web/API, perform assertions, call functions, compose other flows and return values.

```tscr
flow createUser(baseUrl: String, name: String) -> Map[String, Any] {
    var response = POST "${baseUrl}/users" { body json {name: name} }
    expect response.status == 201
    return response.json
}
```

Pass dependencies explicitly. A flow closes over its module's constants and imports, not the caller's local variables or fixture bindings.

## fn

A function computes or transforms data. It cannot access HTTP/browser actions, `load`, `env`, `uuid`, logs, steps or assertions, and it cannot call flows. Ordinary computation and calls to other pure functions are allowed.

```tscr
fn greeting(name: String) -> String {
    return "Hello, ${name}"
}
```

## fixture

A fixture has `setup` and optional `teardown`. It runs once per test or data row. Bindings created by setup are exposed to the test. Teardown retains the fixture's own environment and runs in reverse fixture order, including when setup failed after acquiring a resource.

```tscr
fixture session {
    setup { var baseUrl: String = "http://127.0.0.1:8765" }
    teardown { log "Cleanup completed" }
}
test "Session" using [session] { expect len(baseUrl) > 0 }
```

## record and data

A record defines named, typed fields; instances are constructed with named arguments. Fields can be read through dot or bracket access. Field mutation and classes are outside v0.2.

`data` declares module-level data, commonly loaded from CSV, JSON or YAML. A data-driven test creates one result per row. See [data and fixtures](data-fixtures.md).

## step and expect

A step names a group of statements. Nested steps form a path in the execution events. Variables declared inside a step stay inside that block.

An assertion records a passing/failing verification. A caught assertion still marks the case failed. See [errors and results](results.md).

## Naming

Use `camelCase` for variables, data, functions, flows and fixtures; `PascalCase` for record/type names; `kebab-case.tscr` for files. Test/step titles are descriptive strings. Naming rules are linter warnings, not execution errors.

## var / const and returns

Both variables and constants use `camelCase`. `var` can be reassigned; `const` fixes the binding (it does not deeply freeze a List/Map). Both can receive a flow/function return. `List[T]` and `Map[K, V]` name collection types; values still use names such as `userList` and `userById`.

```tscr
fn greeting(name: String) -> String { return "Hello, ${name}" }
flow verifiedName(name: String) -> String {
    expect len(name) > 0
    return greeting(name)
}
test "Returns" {
    var userName = verifiedName("Angel")
    const expectedName = greeting("Angel")
    expect userName == expectedName
}
```

`step` is optional grouping in the timeline, similar in purpose to Robot Framework GROUP. It has its own block scope; it is not callable. `flow` is reusable and can return a value.
