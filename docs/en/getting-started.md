# Install TestScript

TestScript is a Python interpreter for `.tscr` programs. You write TestScript, not Python; Python 3.12+ must be installed to run the interpreter.

!!! warning "Experimental language"
    Version 0.2.0 is published on [PyPI](https://pypi.org/project/testscript-lang/). Install `testscript-lang`; `testscript` on PyPI is an unrelated package. The language and its specification continue to evolve.

## Install from PyPI

Create and activate a virtual environment, then install:

```bash
python -m pip install testscript-lang
tscr --version
```

For Web automation, install `"testscript-lang[playwright]"` and run `python -m playwright install chromium`, or install `"testscript-lang[selenium]"` with Chrome available. API and core tests use only the base package.

The package installs the interpreter and CLI. Clone the repository separately for the examples below:

```bash
git clone https://github.com/angel-valdezzz/testscript.git
cd testscript
```

## Install the source

Clone the repository as shown above, or download and extract its archive. Open a terminal in the `testscript` directory.

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

    Install Chrome. Selenium Manager resolves the compatible driver and may need network access. Chrome, Edge and Firefox are supported; choose the browser in configuration.

Start the local demo server in another terminal **before** running the Web or API examples:

```bash
python examples/demo_server.py
```

Core/API use only the base package. Browser extras are optional. Browser downloads and drivers are not bundled into the Python wheel.

## Install a built wheel

```bash
python -m pip install /path/to/testscript_lang-0.2.0-py3-none-any.whl
```

Keep examples separately: the wheel installs the interpreter and CLI, not this repository's example directory.
