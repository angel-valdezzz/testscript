# TestScript v0.2 specification

**Status:** experimental implementation contract. The executable grammar is `src/testscript/grammar.lark`. This document describes the supported behavior; proposals belong in the roadmap.

## Program structure

A module is a UTF-8 `.tscr` file containing imports, records, functions, flows, fixtures, tests, data declarations and constant bindings. Arbitrary top-level actions are invalid. Imports and declarations are resolved before test execution. Initializers run in source order; reading a later constant is invalid. Import cycles are rejected.

Tests are the only discoverable execution units. Data rows expand one declaration into independent cases. Execution is sequential with no language-level async/await. Tests do not call other tests. Flows can call flows/functions; functions cannot call flows or effectful builtins.

## Grammar and lexical rules

Identifiers: `[A-Za-z_][A-Za-z0-9_]*`. Case matters. Strings are double quoted with JSON escapes; regex literals use `r"..."`. Comments: `//` and `/* ... */`. Braces delimit blocks and map literals. No semicolons. Generic type syntax: `List[String]`, `Map[String, Any]`; nullable syntax: `String?`.

```tscr
record User { name: String }
fn greeting(name: String) -> String { return "Hello ${name}" }
flow verify(user: User) { expect len(user.name) > 0 }
fixture session { setup { log "ready" } teardown { log "closed" } }
data users = [{name: "Angel"}]
test "User" tags ["smoke"] using [session] for each user in users {
    verify(User(name: user.name))
}
```

## Types and scopes

Primitive/container/record contracts are described in the [language guide](language.md). Module bindings are constant. Mutable local bindings use lexical scope. Blocks do not export their variables, except fixture setup exports its successfully initialized bindings to the test. Record fields are immutable from the language.

Static analysis is deliberately limited: it resolves names, signatures, explicit types, known record fields and basic expression types. Dynamic data/map access and many builtin calls remain `Any`. Runtime checks cover typed bindings, assignments, fields, parameters and returns. The implementation does not claim complete static type soundness.

## Effects and call contracts

`fn` may compute, construct records and call pure functions/builtins. `flow` may perform Web/API operations, observe/log and assert. The checker and runtime reject effectful operations in `fn`. Native Python attributes, callbacks and user-defined classes are not exposed.

Function parameters are typed; no defaults/variadics. Named arguments follow positional arguments and must be unique. Optional return annotation defaults to `Any`. Non-nullable declared returns cannot silently return null. The interpreter limits nested function calls to 100.

## Fixtures, failures and cleanup

Fixture scope is per-case. Setup order follows `using`; teardown reverses it. A fixture is registered for teardown before setup starts. Fixture environments are independent and module-relative. Successful bindings are shared with the test; duplicate exported names fail.

Failed assertions taint the case immediately, even if caught. Caught operational errors may be handled successfully. Unhandled errors or cleanup failures fail the case. Skips run cleanup, but do not overwrite earlier failures. Adapter cleanup follows fixture teardown.

## Web and HTTP

Web supports Chromium/Chrome/Edge/Firefox/WebKit through the provider/browser combinations described in the Web guide with CSS/XPath locators. Actions wait through adapter-specific behavior; assertions are single evaluations. HTTP supports JSON requests, headers/query maps, redirects and response inspection. Non-2xx statuses are response values. Transport failures are execution errors.

## Discovery, metadata and reporting

Tags apply to test declarations only, with OR include/exclude semantics. One result per test/row. Statuses: passed/failed/skipped. Outputs: HTML, JSON and JUnit XML. Exit codes: 0/1/2/5. See [CLI reference](cli.md).

## Explicit exclusions

Mobile, classes/interfaces/inheritance, custom exceptions, task/page blocks, callbacks, map/filter/reduce, parallel execution, async/await, formatter, LSP, wildcard imports, fixture suite scopes, automatic assertion retries, automatic screenshots and reporter-library integrations are not implemented in 0.2.

Changes to this contract require updating the grammar/interpreter, regression tests, examples and both documentation languages together.

HTTP syntax is `METHOD url { headers map query map body json expression }`; each optional section is unique. Map property commas are optional, while list and argument commas remain required.
