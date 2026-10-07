# Web automation

The MVP includes two optional adapters: Playwright and Selenium. Both expose the same TestScript action/locator contract. Switching providers does not change `.tscr` syntax, though underlying engine behavior can differ.

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

Locators support `css("selector")` and `xpath("expression")`. Role/text locators, frames, multiple windows, downloads, uploads and mobile are outside v0.2. Choose locators that uniquely identify the intended element.

## Observations and waiting

```tscr
expect visible(css("#welcome"))
expect text(css("#welcome")) == "Welcome, Angel"
expect value(css("#username")) == "Angel"
```

Actions use the adapter's waiting behavior. Playwright uses its built-in actionability checks. Selenium uses explicit visibility/clickability waits. `visible()` waits for visibility. The configured `timeout` is in seconds.

!!! note "Assertions in v0.2"
    `expect` evaluates once; it does not repeatedly rerun an expression until it becomes true. Element lookup/action waiting is separate from assertion retrying. Automatic assertion retries are future work.

## Provider, browser and window

The provider chooses the automation engine; browser chooses its target. Scripts keep the same syntax.

| Provider | Browser values | Default |
|---|---|---|
| Playwright | `chromium`, `chrome`, `edge`, `firefox`, `webkit` | `chromium` |
| Selenium | `chrome`, `edge`, `firefox` | `chrome` |

Playwright's Firefox/WebKit are its managed builds. WebKit is not the Safari application. Chrome/Edge use installed stable channels. Selenium uses the installed browser and a compatible driver through Selenium Manager.

```toml
[testscript]
provider = "playwright"
browser = "firefox"
headless = true
incognito = true
viewport_width = 1440
viewport_height = 900
timeout = 10
```

```bash
python -m playwright install firefox
tscr run examples/web.tscr --provider playwright --browser firefox
tscr run examples/web.tscr --provider selenium --browser chrome --headed --no-incognito
tscr run examples/web.tscr --viewport-width 1024 --viewport-height 768
```

`incognito = true` creates a private context/profile. `false` creates a normal **temporary** profile per test. Neither reuses your personal profile or carries cookies between tests. Playwright uses a temporary persistent context for normal mode. Width/height target the page's viewport, not the surrounding window frame. Selenium compensates for browser chrome; platform window managers may limit the achievable size.

For a maximized visible window:

```toml
[testscript]
provider = "selenium"
browser = "chrome"
headless = false
maximize = true
```

Maximize is incompatible with explicit viewport dimensions and headless mode. Playwright supports it only with Chromium/Chrome/Edge, using the browser's native launch behavior; screen resolution and window manager control the resulting size.

CLI values override TOML. `--headless`/`--headed`, `--incognito`/`--no-incognito`, `--maximize`/`--no-maximize` are available. Install the selected browser first; see [installation](getting-started.md).

`TSCR_BROWSER_EXECUTABLE` and `TSCR_DRIVER_EXECUTABLE` optionally point to a matching browser and Selenium driver in controlled environments. Playwright uses its managed engine when no custom executable is supplied.

Start `python examples/demo_server.py`, then run `examples/web.tscr`. Browser resources close after teardown, including on failure. Screenshots are explicit; automatic failure screenshots are future work.
