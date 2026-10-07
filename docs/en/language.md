# Language guide

## Syntax and comments

Use braces for blocks, `=` for assignment and no semicolons. Whitespace and newlines separate readable code; operators can continue expressions across lines. Identifiers use ASCII letters, digits and underscores and cannot start with a digit.

```tscr
// A line comment
/* A block comment */
const baseUrl: String = "http://127.0.0.1:8765"
```

Strings use double quotes and JSON escapes. `${expression}` interpolates an expression; nested braces inside interpolation are outside v0.2. Regex literals use `r"pattern"` and Python-compatible regex syntax.

## Variables and types

```tscr
var count: Int = 0
count = count + 1
const label: String = "smoke"
var optionalName: String? = null
var names: List[String] = ["Angel", "Denis"]
var metadata: Map[String, Any] = {owner: "QA", attempts: 2}
```

Types: `String`, `Bool`, `Int`, `Float`, `Number`, `Any`, `Void`, `Path`, `Regex`, `Locator`, `List[T]`, `Map[K, V]` and declared records. `?` permits null. `List` requires one parameter; `Map` requires two. `Number` accepts integers/floats, not booleans.

Annotations on variables are optional. The checker infers what it can; `Any` values are validated when assigned to typed parameters, fields or bindings. Runtime contracts remain necessary for external JSON/CSV data. Top-level variable bindings must be `const`; mutable `var` bindings belong inside blocks.

`const` prevents rebinding. List/map/record element assignment is not implemented. Blocks have lexical scope. Assigning a name updates its nearest visible mutable binding.

## Records

```tscr
record User { name: String age: Int? }
test "Read user fields" {
    var user: User = User(name: "Angel", age: null)
    expect user.name == "Angel"
    expect user["age"] == null
}
```

Supply every field, including nullable fields. Missing, unknown or incorrectly typed fields produce diagnostics or runtime errors.

## Functions and flows

```tscr
fn increment(value: Int) -> Int { return value + 1 }
flow verifyCount(value: Int) { expect increment(value) > value }
```

Parameters require types. Return annotations are optional (`Any` by default); declared returns are checked at runtime. Arguments can be positional or named; positional arguments precede named ones. There are no default/variadic parameters. Return values with `return expression`. `return` is allowed only in `fn`/`flow`.

## Conditions and iteration

```tscr
var total: Int = 0
for each item in [1, 2, 3] { total = total + item }
if total == 6 { expect true } else { expect false }
```

`for each` supports lists, map keys and string characters. It creates a per-iteration binding. `while`, `break`, `continue` and `else if` shorthand are outside v0.2; use a nested `if` inside `else`.

## Expressions

Arithmetic: `+ - * / %`. Comparisons: `== != < <= > >=`. Membership: `in`, `contains`. Regex: `matches`. Logic: `not`, `and`, `or`, with short-circuit evaluation. Precedence: postfix → unary → multiply/divide → add/subtract → comparisons → and → or. Chained comparisons compare adjacent values.

```tscr
expect "Angel" matches r"^A.*l$"
expect "tester" in ["tester", "developer"]
expect "TestScript" contains "Script"
```

## Imports

```tscr
import { login } from "login-flow.tscr"
```

Imports are explicit, named and relative to the importing file. Only `.tscr` modules are supported. Records, functions, flows, fixtures, constants and data may be imported. Circular imports and duplicate declarations are errors. Module-local dependencies remain available to imported functions/fixtures. Native Python imports, wildcard imports and aliases are outside v0.2.

## Builtins

| Name | Purpose |
|---|---|
| `len`, `str`, `int`, `float` | Length and conversion |
| `abs`, `min`, `max`, `round` | Numeric helpers |
| `Path("relative/path")` | Path resolved relative to the declaring module |
| `css`, `xpath` | Browser locators |
| `load` | Read local CSV/JSON/YAML |
| `env` | Read an environment variable (String or null) |
| `uuid` | Generate a UUID String |
| `text`, `value`, `visible` | Browser observations |
| `api` | HTTP method namespace |

TestScript does not expose arbitrary Python attributes or execute Python code.
