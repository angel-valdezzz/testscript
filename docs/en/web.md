# Web automation

The MVP includes two optional adapters: Playwright and Selenium. Both target Chrome/Chromium through the same TestScript action/locator contract. Switching providers does not change `.tscr` syntax, though underlying engine behavior can differ.

## Locators and actions

```tscr
flow login(baseUrl: String, username: String) {
    open baseUrl
    type css("#username") with username
    select css("#role") option "tester"
    check css("#remember")
    click css("button[type=submit]")
}
```

| Action | Meaning |
|---|---|
| `open url` | Navigate to a URL |
| `click locator` | Click an actionable element |
| `type locator with value` | Replace the input value |
| `select locator option value` | Select an option by value |
| `check locator` | Check a checkbox if necessary |
| `screenshot "name.png"` | Save uniquely named evidence in the output directory |

Locators support `css("selector")` and `xpath("expression")`. Role/text locators, frames, multiple windows, downloads, uploads and mobile are outside v0.1. Choose locators that uniquely identify the intended element.

## Observations and waiting

```tscr
expect visible(css("#welcome"))
expect text(css("#welcome")) == "Welcome, Angel"
expect value(css("#username")) == "Angel"
```

Actions use the adapter's waiting behavior. Playwright uses its built-in actionability checks. Selenium uses explicit visibility/clickability waits. `visible()` waits for visibility. The configured `timeout` is in seconds.

!!! note "Assertions in v0.1"
    `expect` evaluates once; it does not repeatedly rerun an expression until it becomes true. Element lookup/action waiting is separate from assertion retrying. Automatic assertion retries are future work.

## Engine selection

```toml
[testscript]
provider = "playwright"
headless = true
timeout = 10
```

```bash
tscr run examples/web.tscr --provider selenium
```

`--provider` overrides configuration. `TSCR_BROWSER_EXECUTABLE` optionally supplies a Chrome/Chromium executable for controlled environments. Install browser extras first. See [installation](getting-started.md).

Run `python examples/demo_server.py`, then execute `examples/web.tscr`. Browser resources are closed after fixtures, including on test failure. Screenshots are explicit in this version; automatic failure screenshots are future work.

`TSCR_DRIVER_EXECUTABLE` optionally supplies an existing compatible ChromeDriver for Selenium. The driver must match your Chrome/Chromium version.
