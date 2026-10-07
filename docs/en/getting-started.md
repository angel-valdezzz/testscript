# Install TestScript

TestScript is a Python interpreter for `.tscr` programs. You write TestScript, not Python; Python 3.12+ must be installed to run the interpreter.

!!! warning "Distribution status"
    Version 0.1.0 is experimental and has not been published to PyPI. `testscript` on PyPI is an unrelated package. Our distribution is named `testscript-lang`; its name is not reserved until publication. Use the source or wheel installation below.

## Install the source

Download the project archive, extract it and open a terminal in its `testscript` directory. After the remote repository is published, you can also clone `https://github.com/angel-valdezzz/testscript.git`.

```bash
python -m venv .venv
```

Activate `.venv` using the command for your OS, then:

```bash
python -m pip install .
tscr --version
tscr check examples/core.tscr
tscr run examples/core.tscr
```

You should see four passing results. Open `testscript-results/report.html`; JSON and JUnit XML are written alongside it.

## Choose a browser engine

=== "Playwright"

    ```bash
    python -m pip install ".[playwright]"
    python -m playwright install chromium
    tscr run examples/web.tscr --provider playwright
    ```

=== "Selenium"

    ```bash
    python -m pip install ".[selenium]"
    tscr run examples/web.tscr --provider selenium
    ```

    Install Chrome. Selenium Manager resolves the compatible driver and may need network access. The MVP targets Chrome/Chromium.

Start the local demo server in another terminal **before** running the Web or API examples:

```bash
python examples/demo_server.py
```

Core/API use only the base package. Browser extras are optional. Browser downloads and drivers are not bundled into the Python wheel.

## Install a built wheel

```bash
python -m pip install /path/to/testscript_lang-0.1.0-py3-none-any.whl
```

Keep examples separately: the wheel installs the interpreter and CLI, not this repository's example directory. Future PyPI instructions will replace source commands only after publication.
