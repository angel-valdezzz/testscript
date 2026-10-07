import json
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from testscript.analysis import Analyzer
from testscript.cli import main
from testscript.parser import ScriptError, parse
from testscript.reporting import write_reports
from testscript.runtime import Runtime


def program(tmp_path, source, **options):
    path = tmp_path / "case.tscr"
    path.write_text(source)
    runtime = Runtime(output=tmp_path / "results", **options)
    runtime.load_module(path)
    return runtime


def execute(tmp_path, source):
    runtime = program(tmp_path, source)
    errors = [str(d) for d in Analyzer(runtime).analyze() if d.severity == "error"]
    assert not errors, "\n".join(errors)
    return runtime.run()


def test_functions_flows_records_and_control(tmp_path):
    results = execute(
        tmp_path,
        """
record User { name: String age: Int? }
fn greet(name: String) -> String { return "Hello ${name}" }
flow verifyUser(user: User) { expect greet(user.name) == "Hello Angel" }
test "Composition" tags ["smoke"] {
    var user: User = User(name: "Angel", age: null)
    verifyUser(user)
    var count: Int = 0
    for each item in [1, 2, 3] { count = count + item }
    if count == 6 { expect true } else { expect false }
    expect user["name"] == "Angel"
    expect "Angel" matches r"^A.*l$"
}
""",
    )
    assert results[0].status == "passed"


def test_dataset_each_row_is_a_result(tmp_path):
    results = execute(
        tmp_path,
        """data users = [{name: "A"}, {name: "B"}]
test "User" tags ["data"] for each user in users { expect len(user.name) == 1 }""",
    )
    assert [r.name for r in results] == ["User [1]", "User [2]"]
    assert all(r.tags == ["data"] for r in results)


def test_assertion_catch_does_not_erase_failure(tmp_path):
    results = execute(
        tmp_path,
        """test "Catch" { try { expect false }
catch error { log error.message } finally { log "finished" } }""",
    )
    assert results[0].status == "failed"
    assert any(e["message"] == "finished" for e in results[0].events)


def test_operational_error_can_be_handled(tmp_path):
    results = execute(
        tmp_path,
        """test "Recovery" { try { var bad = 1 / 0 }
catch error { expect error.message contains "division" } }""",
    )
    assert results[0].status == "passed"


def test_rethrow(tmp_path):
    results = execute(
        tmp_path,
        """test "Rethrow" { try { var bad = 1 / 0 }
catch error { throw error } finally { log "finished" } }""",
    )
    assert results[0].status == "failed"
    assert "division" in results[0].errors[0]


def test_cleanup_when_setup_fails(tmp_path):
    results = execute(
        tmp_path,
        """fixture session { setup { var ready: Bool = true expect false }
teardown { log ready } } test "Setup" using [session] { expect true }""",
    )
    assert results[0].status == "failed"
    assert any(e["kind"] == "log" and e["message"] == "True" for e in results[0].events)


def test_cleanup_reverse_order_and_skip(tmp_path):
    results = execute(
        tmp_path,
        """fixture first { setup { log "first" } teardown { log "first-end" } }
fixture second { setup { log "second" } teardown { log "second-end" } }
test "Skip" using [first, second] { skip "Unavailable" }""",
    )
    assert results[0].status == "skipped"
    logs = [e["message"] for e in results[0].events if e["kind"] == "log"]
    assert logs == ["first", "second", "second-end", "first-end"]


@pytest.mark.parametrize(
    "source, message",
    [
        ('test "X" { var x: String = 1 }', "expects String"),
        ('test "X" { const x = 1 x = 2 }', "constant"),
        ('test "X" { expect unknown == 1 }', "Unknown name"),
        ('fn x() { open "https://example.com" }', "fn cannot"),
        ("flow x() { expect true } fn y() { x() }", "fn cannot call flow"),
        ('fn x() { GET "https://example.com" {} }', "fn cannot"),
        ('test "Legacy" { api.get("https://example.com") }', "removed in 0.2"),
        ('test "X" { return 1 }', "return is only"),
        ('test "X" { expect 1 }', "Bool"),
        ('test "X" { try { expect true } }', "try requires"),
        ('test "X" { var x: Unknown = null }', "Unknown type"),
        ('fn x(a: Int) -> Int { return a } test "X" { x("bad") }', "expects Int"),
        ('record User { name: String } test "X" { var u = User(name: "A") expect u.bad == 1 }', "no field"),
        ('test "X" using [missing] { expect true }', "Unknown fixture"),
    ],
)
def test_semantic_errors(tmp_path, source, message):
    runtime = program(tmp_path, source)
    assert any(message in str(d) for d in Analyzer(runtime).analyze())


def test_invalid_syntax_has_location():
    with pytest.raises(ScriptError, match="broken.tscr:2:"):
        parse('test "X" {\n expect ==\n}', "broken.tscr")


def test_imports_relative_to_module_not_cwd(tmp_path, monkeypatch):
    (tmp_path / "helpers.tscr").write_text('fn greet(name: String) -> String { return "Hi ${name}" }')
    monkeypatch.chdir("/")
    results = execute(
        tmp_path,
        """import { greet } from "helpers.tscr"
test "Imported" { expect greet("Angel") == "Hi Angel" }""",
    )
    assert results[0].status == "passed"


def test_import_cycle(tmp_path):
    (tmp_path / "a.tscr").write_text('import { x } from "b.tscr" const x = 1')
    (tmp_path / "b.tscr").write_text('import { x } from "a.tscr" const x = 2')
    with pytest.raises(ScriptError, match="Circular import"):
        Runtime().load_module(tmp_path / "a.tscr")


@pytest.mark.parametrize(
    "suffix, content",
    [
        ("csv", "name,age\nAngel,30\n"),
        ("json", '[{"name":"Angel","age":30}]'),
        ("yaml", "- name: Angel\n  age: 30\n"),
    ],
)
def test_data_files(tmp_path, suffix, content):
    (tmp_path / ("users." + suffix)).write_text(content)
    results = execute(
        tmp_path,
        f"""data users = load("users.{suffix}")
test "Data" for each user in users {{ expect user.name == "Angel" }}""",
    )
    assert results[0].status == "passed"


def test_filters_and_exit_codes(tmp_path):
    file = tmp_path / "tests.tscr"
    file.write_text(
        'test "Pass" tags ["smoke"] { expect true } test "Fail" tags ["negative"] { expect false }'
    )
    assert main(["run", str(file), "--tag", "smoke", "--output", str(tmp_path / "out")]) == 0
    assert main(["run", str(file), "--tag", "negative", "--output", str(tmp_path / "out")]) == 1
    assert main(["run", str(file), "--tag", "missing"]) == 5
    file.write_text('test "Bad" { expect unknown }')
    assert main(["run", str(file)]) == 2


def test_empty_dataset_is_not_false_success(tmp_path):
    file = tmp_path / "tests.tscr"
    file.write_text('data rows = [] test "Data" for each row in rows { expect true }')
    assert main(["run", str(file), "--output", str(tmp_path / "out")]) == 2


def test_formatterless_linter_optional_rule(tmp_path):
    runtime = program(tmp_path, 'flow Bad_name() { expect true } test "X" { open "https://example.com" }')
    messages = [str(d) for d in Analyzer(runtime, lint=True, flows_only=True).analyze()]
    assert any("camelCase" in m for m in messages)
    assert any("tests-use-flows-only" in m for m in messages)


def test_reports_escape_and_junit(tmp_path):
    results = execute(tmp_path, 'test "<script>alert(1)</script>" { log "<img src=x>" expect false }')
    write_reports(results, tmp_path / "out")
    html = (tmp_path / "out/report.html").read_text()
    assert "<script>alert" not in html
    assert "&lt;script&gt;" in html
    data = json.loads((tmp_path / "out/results.json").read_text())
    assert data["summary"]["failed"] == 1
    import xml.etree.ElementTree as ET

    root = ET.parse(tmp_path / "out/junit.xml").getroot()
    assert root.attrib["failures"] == "1"


class ApiHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        status = 404 if self.path.startswith("/missing") else 200
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"name": "Angel"}).encode())

    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({
            **json.loads(body), "path": self.path,
            "token": self.headers.get("Authorization"),
            "contentType": self.headers.get("Content-Type"),
        }).encode())

    def log_message(self, *_):
        pass


@pytest.fixture
def local_api():
    server = ThreadingHTTPServer(("127.0.0.1", 0), ApiHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    server.server_close()
    thread.join()


def test_real_http_response_and_negative_status(tmp_path, local_api):
    results = execute(
        tmp_path,
        f'''test "HTTP" {{
 var created = POST "{local_api}/users" {{ body json {{name: "Angel"}} }}
 expect created.status == 201
 expect created.json.name == "Angel"
 var missing = GET "{local_api}/missing" {{}}
 expect missing.status == 404
}}''',
    )
    assert results[0].status == "passed"
    assert [e["status"] for e in results[0].events if e["kind"] == "http"] == [201, 404]


def test_transport_error_is_catchable(tmp_path):
    results = execute(
        tmp_path,
        """test "Transport" { try { var response = GET "http://127.0.0.1:1" {} }
catch error { expect error.message contains "refused" } }""",
    )
    assert results[0].status == "passed"


def test_http_loaded_body_headers_query_and_flow_return(tmp_path, local_api):
    (tmp_path / "payload.json").write_text('{"name":"Angel"}')
    runtime = program(tmp_path, '''
flow createUser() -> Map[String, Any] {
    var payload = load("payload.json")
    return POST "/users" {
        headers { "Authorization": "Bearer secret" }
        query { notify: true }
        body json payload
    }
}
test "Declarative request" {
    const response = createUser()
    expect response.status == 201
    expect response.json.name == "Angel"
    expect response.json.token == "Bearer secret"
    expect response.json.path == "/users?notify=true"
    expect response.json.contentType == "application/json"
}
''', config={"base_url": local_api})
    assert not Analyzer(runtime).analyze()
    assert runtime.run()[0].status == "passed"


@pytest.mark.parametrize("method", ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"])
def test_http_method_dispatch(tmp_path, method):
    runtime = program(tmp_path, f'test "Request" {{ var r = {method} "https://example.com" {{}} expect r.status == 200 }}')
    calls = []
    runtime.http.request = lambda verb, url, **options: calls.append((verb, url, options)) or {"status": 200}
    assert not Analyzer(runtime).analyze()
    assert runtime.run()[0].status == "passed"
    assert calls == [(method, "https://example.com", {})]


@pytest.mark.parametrize("expression, message", [
    ('GET 42 {}', "HTTP URL must be String"),
    ('GET "https://example.com" { headers [] }', "HTTP headers must be Map"),
    ('GET "https://example.com" { query 42 }', "HTTP query must be Map"),
    ('GET "https://example.com" { query {} query {} }', "Duplicate HTTP option"),
])
def test_invalid_http_contract(tmp_path, expression, message):
    runtime = program(tmp_path, f'test "Request" {{ var r = {expression} }}')
    assert any(message in str(d) for d in Analyzer(runtime).analyze())


def test_http_is_not_executed_during_discovery(tmp_path):
    with pytest.raises(ScriptError, match="HTTP requests are only allowed"):
        program(tmp_path, 'const response = GET "https://example.com" {}')


def test_invalid_dynamic_headers_fail_before_network(tmp_path):
    results = execute(tmp_path, 'test "Invalid header" { var r = GET "http://127.0.0.1:1" { headers {token: 1} } }')
    assert results[0].status == "failed"
    assert "String values" in results[0].errors[0]


def test_maps_allow_optional_commas(tmp_path):
    results = execute(tmp_path, '''test "Map" {
        var body = { name: "Angel" role: "tester", preferences: {theme: "dark"}, }
        expect body.role == "tester"
        expect body.preferences.theme == "dark"
    }''')
    assert results[0].status == "passed"


class FakeBrowser:
    def __init__(self):
        self.calls = []
        self.closed = False

    def open(self, url):
        self.calls.append(("open", url))

    def type(self, locator, value):
        self.calls.append(("type", locator.value, value))

    def click(self, locator):
        self.calls.append(("click", locator.value))

    def text(self, locator):
        return "Welcome"

    def close(self):
        self.closed = True


def test_language_browser_contract_and_isolation(tmp_path):
    instances = []

    def factory():
        browser = FakeBrowser()
        instances.append(browser)
        return browser

    runtime = program(
        tmp_path,
        """flow login(name: String) { open "http://localhost"
 type css("#name") with name click xpath("//button") }
 test "First" { login("Angel") expect text(css("h1")) == "Welcome" }
 test "Second" { login("Other") expect false }""",
        browser_factory=factory,
    )
    assert not Analyzer(runtime).analyze()
    results = runtime.run()
    assert [r.status for r in results] == ["passed", "failed"]
    assert len(instances) == 2 and all(b.closed for b in instances)


def test_cli_python_module(tmp_path):
    path = tmp_path / "hello.tscr"
    path.write_text('test "Hello" { expect true }')
    result = subprocess.run(
        [sys.executable, "-m", "testscript", "check", str(path)], capture_output=True, text=True
    )
    assert result.returncode == 0


def test_parameters_can_share_builtin_names(tmp_path):
    results = execute(
        tmp_path,
        """fn increment(value: Int) -> Int { return value + 1 }
fn negate(notReady: Bool) -> Bool { return not notReady }
test "Parameters" { expect increment(2) == 3 expect negate(false) }""",
    )
    assert results[0].status == "passed"


def test_imported_fixture_preserves_module_paths_and_environment(tmp_path):
    folder = tmp_path / "shared"
    folder.mkdir()
    (folder / "config.json").write_text('{"name":"Angel"}')
    (folder / "fixtures.tscr").write_text("""const prefix: String = "Hi"
fixture session { setup { var config = load("config.json") }
teardown { log "${prefix} ${config.name}" } }""")
    results = execute(
        tmp_path,
        """import { session } from "shared/fixtures.tscr"
test "Fixture" using [session] { expect config.name == "Angel" }""",
    )
    assert results[0].status == "passed"
    assert any(e["message"] == "Hi Angel" for e in results[0].events)


def test_float_expression_return(tmp_path):
    results = execute(
        tmp_path,
        """fn half(value: Int) -> Float { return value / 2 }
test "Numeric types" { expect half(3) == 1.5 }""",
    )
    assert results[0].status == "passed"


def test_declared_return_enforced_at_runtime(tmp_path):
    results = execute(
        tmp_path,
        """fn missing() -> String { var value = "not returned" }
test "Missing return" { missing() }""",
    )
    assert results[0].status == "failed"
    assert "must return String" in results[0].errors[0]


def test_dynamic_data_type_boundary(tmp_path):
    (tmp_path / "bad.json").write_text('[{"age":"incorrect"}]')
    results = execute(
        tmp_path,
        """data rows = load("bad.json")
flow verifyAge(age: Int) { expect age > 0 }
test "Dynamic" for each row in rows { verifyAge(row.age) }""",
    )
    assert results[0].status == "failed"
    assert "expects Int" in results[0].errors[0]
