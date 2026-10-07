# Your first test

Save this as `hello.tscr`:

```tscr
flow verifyName(name: String) {
    step "Validate the name" {
        expect len(name) > 0
    }
}

test "A valid user" tags ["smoke"] {
    verifyName("Angel")
}
```

1. `test` gives the runner a discoverable case.
2. `flow` gives that case a reusable behavior.
3. `step` adds a readable section to the execution events.
4. `expect` requires a Boolean expression and fails when it is false.
5. `tags` attach metadata used for selection.

```bash
tscr check hello.tscr
tscr list hello.tscr --tag smoke
tscr run hello.tscr --tag smoke
```

`check` validates syntax, names, available type information and effect restrictions. It does not open a browser or send requests. It reads imported modules and local data files and can evaluate pure module initializers.

## See a failure

Change the flow call to `verifyName("")`. The assertion fails, the case is marked failed, the process exits with code 1 and the reports retain the failing source location.

## Compose behavior

Flows can call other flows. Functions declared with `fn` compute values without accessing the system under test. Put browser/API behavior in flows and data transformations in functions. Direct actions in tests are permitted; the optional flows-only linter encourages extracting them.

Continue with [concepts](concepts.md), [the language](language.md) or [complete examples](examples.md).
