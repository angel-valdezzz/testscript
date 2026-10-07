"""Tree interpreter, module loader and sequential test runner."""

import csv
import json
import operator
import os
import re
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter
from uuid import uuid4

import yaml
from lark import Tree

from testscript.adapters.http import HttpAdapter
from testscript.configuration import validate_config
from testscript.model import (
    Builtin,
    Env,
    Fixture,
    Function,
    Locator,
    Namespace,
    RecordType,
    RecordValue,
    ReturnSignal,
    SkipSignal,
    TestCase,
    TypeSpec,
    type_spec,
)
from testscript.parser import ScriptError, parse, parse_file


@dataclass
class Result:
    name: str
    path: str
    tags: list
    status: str = "passed"
    duration: float = 0
    errors: list = field(default_factory=list)
    events: list = field(default_factory=list)


class Runtime:
    def __init__(self, config=None, output=Path("testscript-results"), browser_factory=None):
        self.config = validate_config(dict(config or {}))
        self.output = Path(output)
        self.browser_factory = browser_factory
        self.browser = None
        self.modules, self.loading, self.tests = {}, set(), []
        self.path = Path("<script>")
        self.current = None
        self.pure_depth = 0
        self.initializing = False
        self.depth = 0
        self.fixture_mode = False
        self.steps = []
        self.root = Env()
        self.http = HttpAdapter(
            self.config.get("timeout", 10), self.config.get("base_url", ""), self.http_event
        )
        self.install_builtins()

    def install_builtins(self):
        pure = {
            "len": len,
            "str": str,
            "int": int,
            "float": float,
            "abs": abs,
            "min": min,
            "max": max,
            "round": round,
            "Path": lambda value: (self.path.parent / str(value)).resolve(),
            "css": lambda value: Locator("css", str(value)),
            "xpath": lambda value: Locator("xpath", str(value)),
        }
        effects = {
            "load": self.load_data,
            "env": lambda name: os.environ.get(name),
            "uuid": lambda: str(uuid4()),
            "text": lambda loc: self.web().text(loc),
            "value": lambda loc: self.web().value(loc),
            "visible": lambda loc: self.web().visible(loc),
        }
        for name, callback in pure.items():
            self.root.define(name, Builtin(name, callback), constant=True)
        for name, callback in effects.items():
            self.root.define(name, Builtin(name, callback, pure=False), constant=True)

    def event(self, kind, message, **extra):
        if self.current:
            self.current.events.append(
                {"kind": kind, "message": str(message), "steps": list(self.steps), **extra}
            )

    def http_event(self, method, url, status):
        self.event("http", f"{method} {url}", status=status)

    def error(self, node, message):
        return ScriptError(
            str(message), str(self.path), getattr(node.meta, "line", 1), getattr(node.meta, "column", 1)
        )

    def fail(self, exc):
        if self.current:
            message = str(exc)
            if message not in self.current.errors:
                self.current.errors.append(message)
                self.event("error", message)

    def load_data(self, value):
        path = value if isinstance(value, Path) else (self.path.parent / str(value)).resolve()
        if path.suffix.lower() == ".csv":
            with path.open(newline="", encoding="utf-8-sig") as handle:
                return list(csv.DictReader(handle))
        if path.suffix.lower() == ".json":
            return json.loads(path.read_text(encoding="utf-8"))
        if path.suffix.lower() in {".yaml", ".yml"}:
            return yaml.safe_load(path.read_text(encoding="utf-8"))
        raise ValueError("load() supports CSV, JSON and YAML")

    def web(self):
        if self.pure_depth or self.initializing:
            raise TypeError("Browser actions are not allowed in fn or module initializers")
        if self.browser is None:
            if self.browser_factory:
                self.browser = self.browser_factory()
            else:
                from testscript.adapters.web import PlaywrightAdapter, SeleniumAdapter

                provider = self.config.get("provider", "playwright")
                factory = {"playwright": PlaywrightAdapter, "selenium": SeleniumAdapter}.get(provider)
                if not factory:
                    raise ValueError(f"Unknown browser provider '{provider}'")
                self.browser = factory(
                    self.config.get("timeout", 10), self.config.get("headless", True),
                    browser=self.config.get("browser"),
                    incognito=self.config.get("incognito", True),
                    viewport_width=self.config.get("viewport_width", 1440),
                    viewport_height=self.config.get("viewport_height", 900),
                    maximize=self.config.get("maximize", False),
                )
        return self.browser

    def load_module(self, path):
        path = Path(path).resolve()
        if path in self.loading:
            raise ScriptError("Circular import", str(path))
        if path in self.modules:
            return self.modules[path][1]
        self.loading.add(path)
        previous = self.path
        self.path = path
        try:
            tree = parse_file(path)
            env = Env(self.root)
            for node in tree.children:
                if node.data == "import_decl":
                    source = json.loads(str(node.children[1]))
                    target = (path.parent / source).resolve()
                    if target.suffix != ".tscr":
                        raise self.error(node, "Imports must reference .tscr modules")
                    imported = self.load_module(target)
                    for name in node.children[0].children:
                        if str(name) not in imported.slots:
                            raise self.error(node, f"Module does not export '{name}'")
                        slot = imported.slots[str(name)]
                        env.define(str(name), slot.value, slot.type, constant=True)
            for node in tree.children:
                if node.data == "record_decl":
                    name = str(node.children[0])
                    fields = {}
                    for field_node in node.children[1:]:
                        key = str(field_node.children[0])
                        if key in fields:
                            raise self.error(field_node, f"Duplicate field '{key}'")
                        fields[key] = type_spec(field_node.children[1])
                    env.define(name, RecordType(name, fields), constant=True)
                elif node.data == "function_decl":
                    kind, name = map(str, node.children[:2])
                    params = next(
                        (c for c in node.children if isinstance(c, Tree) and c.data == "parameters"), None
                    )
                    params = (
                        [(str(p.children[0]), type_spec(p.children[1])) for p in params.children]
                        if params
                        else []
                    )
                    returns = next(
                        (type_spec(c) for c in node.children if isinstance(c, Tree) and c.data == "type"),
                        TypeSpec(),
                    )
                    env.define(
                        name,
                        Function(kind, name, params, returns, node.children[-1], env, path),
                        constant=True,
                    )
            self.initializing = True
            for node in tree.children:
                if node.data == "binding":
                    if str(node.children[0]) != "const":
                        raise self.error(node, "Module bindings must be const; use var inside blocks")
                    self.execute(node, env)
                elif node.data == "data_decl":
                    env.define(str(node.children[0]), self.evaluate(node.children[1], env), constant=True)
                elif node.data == "fixture_decl":
                    env.define(
                        str(node.children[0]),
                        Fixture(
                            str(node.children[0]),
                            node.children[1],
                            node.children[2] if len(node.children) > 2 else None,
                            env,
                            path,
                        ),
                        constant=True,
                    )
                elif node.data == "test_decl":
                    tags, fixtures, dataset = [], [], None
                    for child in node.children[1:-1]:
                        if child.data == "tags":
                            tags = self.evaluate(child.children[0], env)
                            if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
                                raise self.error(child, "Tags must be a list of strings")
                        elif child.data == "using":
                            fixtures = [str(n) for n in child.children[0].children] if child.children else []
                        elif child.data == "dataset":
                            dataset = child
                    self.tests.append(
                        TestCase(
                            json.loads(str(node.children[0])),
                            tags,
                            fixtures,
                            dataset,
                            node.children[-1],
                            env,
                            path,
                        )
                    )
            self.modules[path] = (tree, env)
            return env
        except ScriptError:
            raise
        except (TypeError, ValueError, NameError, OSError) as exc:
            raise ScriptError(str(exc), str(path)) from exc
        finally:
            self.initializing = False
            self.path = previous
            self.loading.remove(path)

    def evaluate(self, node, env):
        try:
            return self._evaluate(node, env)
        except ScriptError:
            raise
        except Exception as exc:
            raise self.error(node, exc) from exc

    def _evaluate(self, node, env):
        kind, children = node.data, node.children
        if kind == "string":
            value = json.loads(str(children[0]))

            def interpolate(match):
                parsed = parse(f"const interpolation = {match.group(1)}")
                return str(self.evaluate(parsed.children[0].children[-1], env))

            return re.sub(r"\$\{([^{}]+)\}", interpolate, value)
        if kind == "number":
            value = str(children[0])
            return float(value) if "." in value else int(value)
        if kind in {"true", "false", "null"}:
            return {"true": True, "false": False, "null": None}[kind]
        if kind == "regex":
            return re.compile(str(children[0])[2:-1])
        if kind == "variable":
            return env.get(str(children[0]))
        if kind == "http_request":
            if self.pure_depth or self.initializing:
                raise TypeError("HTTP requests are only allowed in tests, flows and fixtures")
            url = self.evaluate(children[1], env)
            if not isinstance(url, str):
                raise TypeError("HTTP URL must be String")
            options = {}
            for option in children[2:]:
                key = str(option.data).removeprefix("http_")
                if key in options:
                    raise TypeError(f"Duplicate HTTP option '{key}'")
                options[key] = self.evaluate(option.children[0], env)
            return self.http.request(str(children[0]), url, **options)
        if kind == "list_expr":
            return [self.evaluate(c, env) for c in children]
        if kind == "map_expr":
            result = {}
            for pair in children:
                raw = str(pair.children[0])
                key = json.loads(raw) if raw.startswith('"') else raw
                if key in result:
                    raise ValueError(f"Duplicate map key '{key}'")
                result[key] = self.evaluate(pair.children[1], env)
            return result
        if kind == "unary_expr":
            value = self.evaluate(children[1], env)
            return not value if str(children[0]) == "not" else -value
        if kind in {"or_expr", "and_expr"}:
            result = self.evaluate(children[0], env)
            for child in children[2::2]:
                if (kind == "or_expr" and result) or (kind == "and_expr" and not result):
                    return result
                result = self.evaluate(child, env)
            return result
        if kind in {"sum_expr", "product", "comparison"}:
            ops = {
                "+": operator.add,
                "-": operator.sub,
                "*": operator.mul,
                "/": operator.truediv,
                "%": operator.mod,
                "==": operator.eq,
                "!=": operator.ne,
                ">": operator.gt,
                "<": operator.lt,
                ">=": operator.ge,
                "<=": operator.le,
                "contains": lambda a, b: b in a,
                "in": lambda a, b: a in b,
                "matches": lambda a, b: bool((b if isinstance(b, re.Pattern) else re.compile(b)).search(a)),
            }
            result = self.evaluate(children[0], env)
            all_matches = True
            for op, right in zip(children[1::2], children[2::2]):
                value = self.evaluate(right, env)
                applied = ops[str(op)](result, value)
                if kind == "comparison":
                    all_matches = all_matches and applied
                    result = value
                else:
                    result = applied
            return all_matches if kind == "comparison" else result
        if kind == "postfix":
            value = self.evaluate(children[0], env)
            for part in children[1:]:
                if part.data == "member":
                    name = str(part.children[0])
                    if isinstance(value, Namespace):
                        value = value.members[name]
                    elif isinstance(value, RecordValue):
                        value = value.fields[name]
                    elif isinstance(value, dict):
                        value = value[name]
                    elif isinstance(value, ScriptError) and name in {"message", "path", "line", "column"}:
                        value = getattr(value, name)
                    else:
                        raise TypeError(f"Member '{name}' unavailable on {type(value).__name__}")
                elif part.data == "index":
                    key = self.evaluate(part.children[0], env)
                    value = value.fields[key] if isinstance(value, RecordValue) else value[key]
                elif part.data == "call":
                    args, kwargs = [], {}
                    for arg in part.children[0].children if part.children else []:
                        if arg.data == "named_argument":
                            key = str(arg.children[0])
                            if key in kwargs:
                                raise TypeError(f"Duplicate argument '{key}'")
                            kwargs[key] = self.evaluate(arg.children[1], env)
                        else:
                            if kwargs:
                                raise TypeError("Positional arguments must precede named arguments")
                            args.append(self.evaluate(arg.children[0], env))
                    value = self.call(value, args, kwargs)
            return value
        raise TypeError(f"Unsupported expression: {kind}")

    def call(self, value, args, kwargs):
        if isinstance(value, RecordType):
            return value.construct(args, kwargs)
        if isinstance(value, Builtin):
            if not value.pure and self.pure_depth:
                raise TypeError(f"fn cannot call '{value.name}'")
            if self.initializing and not value.pure and value.name not in {"load", "env"}:
                raise TypeError(f"Module initializer cannot call '{value.name}'")
            return value.callback(*args, **kwargs)
        if not isinstance(value, Function):
            raise TypeError("Only fn, flow, record constructors and builtins are callable")
        if self.pure_depth and value.kind == "flow":
            raise TypeError("fn cannot call flow")
        if self.initializing and value.kind == "flow":
            raise TypeError("Module initializer cannot call flow")
        if self.depth >= 100:
            raise RecursionError("Maximum TestScript call depth (100) exceeded")
        names = [p[0] for p in value.params]
        if len(args) > len(names) or set(kwargs) - set(names):
            raise TypeError(f"Invalid arguments for '{value.name}'")
        provided = dict(zip(names, args))
        if set(provided) & set(kwargs):
            raise TypeError("Argument supplied twice")
        provided.update(kwargs)
        if set(provided) != set(names):
            raise TypeError(f"'{value.name}' requires: {', '.join(names)}")
        local = Env(value.env)
        for name, typ in value.params:
            local.define(name, provided[name], typ)
        previous = self.path
        self.path = value.path
        self.depth += 1
        self.pure_depth += value.kind == "fn"
        self.event(value.kind, value.name)
        try:
            result = None
            try:
                self.block(value.body, local)
            except ReturnSignal as signal:
                result = signal.value
            if not value.returns.accepts(result):
                raise TypeError(f"'{value.name}' must return {value.returns}")
            return result
        finally:
            self.path = previous
            self.depth -= 1
            self.pure_depth -= value.kind == "fn"

    def block(self, node, env, scoped=True):
        local = Env(env) if scoped else env
        for statement in node.children:
            self.execute(statement, local)

    def execute(self, node, env):
        try:
            self._execute(node, env)
        except ScriptError:
            raise
        except Exception as exc:
            raise self.error(node, exc) from exc

    def _execute(self, node, env):
        kind, children = node.data, node.children
        if self.pure_depth and (
            kind.startswith("web_") or kind in {"expect_stmt", "log_stmt", "step_stmt", "skip_stmt"}
        ):
            raise TypeError(f"fn cannot contain {kind}")
        if kind == "binding":
            bind, name = map(str, children[:2])
            typ = type_spec(children[2]) if len(children) == 4 else TypeSpec()
            env.define(name, self.evaluate(children[-1], env), typ, constant=bind == "const")
        elif kind == "assignment":
            env.assign(str(children[0]), self.evaluate(children[1], env))
        elif kind == "expr_stmt":
            self.evaluate(children[0], env)
        elif kind == "if_stmt":
            if self.evaluate(children[0], env):
                self.block(children[1], env)
            elif len(children) > 2:
                self.block(children[2], env)
        elif kind == "for_stmt":
            values = self.evaluate(children[1], env)
            if not isinstance(values, (list, dict, str)):
                raise TypeError("for each requires List, Map or String")
            for value in values:
                local = Env(env)
                local.define(str(children[0]), value)
                self.block(children[2], local)
        elif kind == "return_stmt":
            raise ReturnSignal(self.evaluate(children[0], env))
        elif kind == "expect_stmt":
            actual = self.evaluate(children[0], env)
            if not isinstance(actual, bool):
                raise TypeError("expect requires a Bool expression")
            self.event("assertion", "expect", passed=actual, line=node.meta.line)
            if not actual:
                exc = self.error(node, "Assertion failed")
                self.fail(exc)
                raise exc
        elif kind == "try_stmt":
            catch = next((c for c in children[1:] if c.data == "catch_clause"), None)
            final = next((c for c in children[1:] if c.data == "finally_clause"), None)
            if catch is None and final is None:
                raise TypeError("try requires catch or finally")
            try:
                self.block(children[0], env)
            except ScriptError as exc:
                if catch is None:
                    raise
                local = Env(env)
                local.define(str(catch.children[0]), exc)
                self.event("caught", str(exc))
                self.block(catch.children[1], local)
            finally:
                if final:
                    self.block(final.children[0], env)
        elif kind == "throw_stmt":
            exc = self.evaluate(children[0], env)
            if not isinstance(exc, ScriptError):
                raise TypeError("throw only rethrows an existing catch error")
            raise exc
        elif kind == "step_stmt":
            title = self.evaluate(Tree("string", [children[0]], meta=node.meta), env)
            self.steps.append(title)
            self.event("step", title)
            try:
                self.block(children[1], env)
            finally:
                self.steps.pop()
        elif kind == "log_stmt":
            self.event("log", self.evaluate(children[0], env))
        elif kind == "skip_stmt":
            raise SkipSignal(str(self.evaluate(children[0], env)))
        elif kind.startswith("web_"):
            action = kind.removeprefix("web_")
            values = [self.evaluate(c, env) for c in children]
            if action == "screenshot":
                self.output.mkdir(parents=True, exist_ok=True)
                target = self.output / f"{uuid4().hex}-{Path(str(values[0])).name}"
                self.web().screenshot(target)
                self.event("screenshot", target.name)
            else:
                getattr(self.web(), action)(*values)
                self.event("web", action)
        else:
            raise TypeError(f"Unsupported statement: {kind}")

    def run(self, include=None, exclude=None, name=None):
        results = []
        for test in self.tests:
            if include and not set(include) & set(test.tags):
                continue
            if exclude and set(exclude) & set(test.tags):
                continue
            if name and name not in test.name:
                continue
            self.path = test.path
            cases = [(None, None)]
            if test.dataset:
                binding, expression = test.dataset.children
                rows = self.evaluate(expression, test.env)
                if not isinstance(rows, list) or not rows:
                    raise self.error(test.dataset, "Test dataset must be a non-empty List")
                cases = [(str(binding), row) for row in rows]
            for index, (binding, row) in enumerate(cases):
                result = Result(test.name + (f" [{index + 1}]" if binding else ""), str(test.path), test.tags)
                self.current = result
                self.path = test.path
                local = Env(test.env)
                if binding:
                    local.define(binding, deepcopy(row))
                started, active = perf_counter(), []
                try:
                    for fixture_name in test.fixtures:
                        fixture = test.env.get(fixture_name)
                        if not isinstance(fixture, Fixture):
                            raise self.error(test.body, f"'{fixture_name}' is not a fixture")
                        fixture_env = Env(fixture.env)
                        active.append((fixture, fixture_env))
                        self.event("fixture", fixture_name + ": setup")
                        self.path = fixture.path
                        self.block(fixture.setup, fixture_env, scoped=False)
                        for binding_name, slot in fixture_env.slots.items():
                            if binding_name in local.slots:
                                raise self.error(fixture.setup, f"Duplicate fixture binding '{binding_name}'")
                            local.slots[binding_name] = slot
                        self.path = test.path
                    self.block(test.body, local)
                except SkipSignal as signal:
                    result.status = "skipped"
                    self.event("skip", signal.reason)
                except ScriptError as exc:
                    self.fail(exc)
                finally:
                    for fixture, fixture_env in reversed(active):
                        if fixture.teardown:
                            self.event("fixture", fixture.name + ": teardown")
                            try:
                                self.path = fixture.path
                                self.block(fixture.teardown, fixture_env, scoped=False)
                            except (ScriptError, SkipSignal, ReturnSignal) as exc:
                                self.fail(exc)
                    try:
                        self.http.close()
                        if self.browser:
                            self.browser.close()
                    except Exception as exc:
                        self.fail(exc)
                    finally:
                        self.browser = None
                    if result.errors:
                        result.status = "failed"
                    result.duration = perf_counter() - started
                    results.append(result)
                    self.current = None
        return results
