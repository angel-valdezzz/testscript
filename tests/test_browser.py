"""Real provider integration, opt-in locally and enabled in CI."""

import importlib.util
import os
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from testscript.analysis import Analyzer
from testscript.runtime import Runtime

pytestmark = pytest.mark.skipif(
    os.getenv("TSCR_RUN_BROWSER_TESTS") != "1", reason="Set TSCR_RUN_BROWSER_TESTS=1"
)


@pytest.mark.parametrize("provider", ["playwright", "selenium"])
def test_real_browser_workflow(tmp_path, provider):
    requested = os.getenv("TSCR_TEST_PROVIDER")
    if requested and requested != provider:
        pytest.skip("Different CI provider")
    path = Path(__file__).resolve().parents[1] / "examples/demo_server.py"
    spec = importlib.util.spec_from_file_location("local_lab", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    server = ThreadingHTTPServer(("127.0.0.1", 0), module.Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        script = tmp_path / "browser.tscr"
        script.write_text(f"""flow login(username: String) {{
 open "http://127.0.0.1:{server.server_port}"
 type css("#username") with username
 select css("#role") option "tester"
 check css("#remember")
 click xpath("//button[@type='submit']")
}}
test "Browser workflow" {{
 login("Angel")
 expect visible(css("#welcome"))
 expect text(css("#welcome")) == "Welcome, Angel"
 expect value(css("#username")) == "Angel"
 expect value(css("#role")) == "tester"
 screenshot "browser.png"
}}""")
        runtime = Runtime({"provider": provider}, tmp_path / "results")
        runtime.load_module(script)
        assert not Analyzer(runtime).analyze()
        results = runtime.run()
        assert results[0].status == "passed", results[0].errors
        assert len(list((tmp_path / "results").glob("*.png"))) == 1
        assert runtime.browser is None
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
