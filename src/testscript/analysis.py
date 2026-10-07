"""Semantic diagnostics and optional style rules; no browser/network execution."""

import json
import re
from dataclasses import dataclass

from lark import Tree

from testscript.model import Builtin, Fixture, Function, RecordType, TypeSpec, type_spec
from testscript.parser import parse


@dataclass
class Diagnostic:
    severity: str
    message: str
    path: str
    line: int
    column: int

    def __str__(self):
        return f"{self.path}:{self.line}:{self.column}: {self.severity}: {self.message}"


def compatible(actual, expected):
    if "Any" in {actual.name, expected.name}:
        return True
    if actual.name == "Void":
        return expected.nullable or expected.name == "Void"
    if actual.nullable and not expected.nullable:
        return False
    if expected.name == "Number" and actual.name in {"Int", "Float"}:
        return True
    return actual.name == expected.name and (
        not expected.args
        or len(actual.args) == len(expected.args)
        and all(compatible(a, e) for a, e in zip(actual.args, expected.args))
    )


class Analyzer:
    def __init__(self, runtime, lint=False, flows_only=False):
        self.runtime, self.lint, self.flows_only = runtime, lint, flows_only
        self.diagnostics = []
        self.path, self.env = None, None
        self.pure, self.return_type = False, None
        self.in_test = False

    def diagnostic(self, node, message, severity="error"):
        self.diagnostics.append(
            Diagnostic(
                severity,
                message,
                str(self.path),
                getattr(node.meta, "line", 1),
                getattr(node.meta, "column", 1),
            )
        )

    def valid_type(self, typ, node):
        basic = {"Any", "String", "Int", "Float", "Number", "Bool", "Void", "Path", "Regex", "Locator"}
        if typ.name in {"List", "Map"}:
            count = 1 if typ.name == "List" else 2
            if len(typ.args) != count:
                self.diagnostic(node, f"{typ.name} requires {count} type parameter(s)")
        elif typ.args:
            self.diagnostic(node, f"{typ.name} does not accept type parameters")
        if typ.name not in basic | {"List", "Map"}:
            try:
                if not isinstance(self.env.get(typ.name), RecordType):
                    self.diagnostic(node, f"Unknown type '{typ.name}'")
            except NameError:
                self.diagnostic(node, f"Unknown type '{typ.name}'")
        for arg in typ.args:
            self.valid_type(arg, node)

    def symbol(self, name, scope, node):
        if name in scope:
            return scope[name]
        try:
            slot = self.env.slot(name)
            return slot.type, slot.constant
        except NameError:
            self.diagnostic(node, f"Unknown name '{name}'")
            return TypeSpec(), False

    def definition(self, name):
        try:
            return self.env.get(name)
        except NameError:
            return None

    def naming(self, name, node, pascal=False):
        if self.lint:
            pattern = r"[A-Z][A-Za-z0-9]*" if pascal else r"[a-z][A-Za-z0-9]*"
            if not re.fullmatch(pattern, name):
                self.diagnostic(
                    node, f"Use {'PascalCase' if pascal else 'camelCase'} for '{name}'", "warning"
                )

    def infer(self, node, scope):
        kind, children = node.data, node.children
        if kind == "string":
            for expr in re.findall(r"\$\{([^{}]+)\}", json.loads(str(children[0]))):
                self.infer(parse(f"const interpolation = {expr}").children[0].children[-1], scope)
            return TypeSpec("String")
        if kind == "number":
            return TypeSpec("Float" if "." in str(children[0]) else "Int")
        if kind in {"true", "false"}:
            return TypeSpec("Bool")
        if kind == "null":
            return TypeSpec("Void")
        if kind == "regex":
            try:
                re.compile(str(children[0])[2:-1])
            except re.error as exc:
                self.diagnostic(node, f"Invalid regex: {exc}")
            return TypeSpec("Regex")
        if kind == "variable":
            name = str(children[0])
            if name == "api" and name not in scope and self.definition(name) is None:
                self.diagnostic(node, "api.* was removed in 0.2; use GET/POST url { ... }")
            typ, _ = self.symbol(name, scope, node)
            if (
                self.pure
                and name not in scope
                and name in {"api", "env", "uuid", "load", "text", "value", "visible"}
            ):
                self.diagnostic(node, f"fn cannot access '{name}'")
            if (
                self.pure
                and name not in scope
                and isinstance(self.definition(name), Function)
                and self.definition(name).kind == "flow"
            ):
                self.diagnostic(node, "fn cannot call flow")
            return typ
        if kind == "list_expr":
            types = [self.infer(c, scope) for c in children]
            element = types[0] if types and all(t == types[0] for t in types) else TypeSpec()
            return TypeSpec("List", (element,))
        if kind == "http_request":
            if self.pure:
                self.diagnostic(node, "fn cannot send HTTP requests")
            if self.flows_only and self.in_test:
                self.diagnostic(node, "tests-use-flows-only: move HTTP actions to a flow", "warning")
            url_type = self.infer(children[1], scope)
            if url_type.name not in {"String", "Any"}:
                self.diagnostic(node, "HTTP URL must be String")
            seen = set()
            for option in children[2:]:
                key = str(option.data).removeprefix("http_")
                if key in seen:
                    self.diagnostic(option, f"Duplicate HTTP option '{key}'")
                seen.add(key)
                typ = self.infer(option.children[0], scope)
                if key in {"headers", "query"} and typ.name not in {"Map", "Any"}:
                    self.diagnostic(option, f"HTTP {key} must be Map")
            return TypeSpec("Map", (TypeSpec("String"), TypeSpec()))
        if kind == "map_expr":
            for pair in children:
                self.infer(pair.children[1], scope)
            return TypeSpec("Map", (TypeSpec("String"), TypeSpec()))
        if kind in {"or_expr", "and_expr", "comparison"}:
            for child in children:
                if isinstance(child, Tree):
                    self.infer(child, scope)
            return TypeSpec("Bool")
        if kind == "unary_expr":
            typ = self.infer(children[1], scope)
            return TypeSpec("Bool") if str(children[0]) == "not" else typ
        if kind in {"sum_expr", "product"}:
            types = [self.infer(c, scope) for c in children if isinstance(c, Tree)]
            if all(t.name == "String" for t in types) and all(str(o) == "+" for o in children[1::2]):
                return TypeSpec("String")
            if any(t.name not in {"Any", "Int", "Float", "Number"} for t in types):
                self.diagnostic(node, "Arithmetic operands must be numeric; + also accepts two Strings")
            if any(t.name == "Any" for t in types):
                return TypeSpec()
            if all(t.name in {"Int", "Float"} for t in types):
                return TypeSpec(
                    "Float"
                    if any(t.name == "Float" for t in types) or "/" in [str(c) for c in children[1::2]]
                    else "Int"
                )
            return TypeSpec("Number")
        if kind == "postfix":
            typ = self.infer(children[0], scope)
            name = str(children[0].children[0]) if children[0].data == "variable" else None
            value = self.definition(name) if name else None
            for part in children[1:]:
                if part.data == "member":
                    field = str(part.children[0])
                    record = self.definition(typ.name)
                    if isinstance(record, RecordType):
                        if field not in record.fields:
                            self.diagnostic(part, f"{typ.name} has no field '{field}'")
                        typ = record.fields.get(field, TypeSpec())
                    else:
                        typ = typ.args[1] if typ.name == "Map" and len(typ.args) == 2 else TypeSpec()
                    value = None
                    name = f"{name}.{field}" if name else None
                elif part.data == "index":
                    self.infer(part.children[0], scope)
                    typ = typ.args[-1] if typ.args else TypeSpec()
                    value = None
                elif part.data == "call":
                    args, kwargs = [], {}
                    for arg in part.children[0].children if part.children else []:
                        if arg.data == "named_argument":
                            key = str(arg.children[0])
                            if key in kwargs:
                                self.diagnostic(arg, f"Duplicate argument '{key}'")
                            kwargs[key] = self.infer(arg.children[1], scope)
                        else:
                            if kwargs:
                                self.diagnostic(arg, "Positional arguments must precede named arguments")
                            args.append(self.infer(arg.children[0], scope))
                    if isinstance(value, (Function, RecordType)):
                        params = value.params if isinstance(value, Function) else list(value.fields.items())
                        names = [p[0] for p in params]
                        if isinstance(value, RecordType) and args:
                            self.diagnostic(part, "Record constructors require named fields")
                        supplied = dict(zip(names, args))
                        if len(args) > len(names) or set(supplied) & set(kwargs):
                            self.diagnostic(part, "Too many or duplicated arguments")
                        supplied.update(kwargs)
                        if set(supplied) != set(names):
                            self.diagnostic(part, f"'{value.name}' requires: {', '.join(names)}")
                        for param, expected in params:
                            if param in supplied and not compatible(supplied[param], expected):
                                self.diagnostic(part, f"'{param}' expects {expected}, got {supplied[param]}")
                        typ = value.returns if isinstance(value, Function) else TypeSpec(value.name)
                    elif isinstance(value, Builtin) or name:
                        known = {
                            "len": "Int",
                            "str": "String",
                            "int": "Int",
                            "float": "Float",
                            "Path": "Path",
                            "css": "Locator",
                            "xpath": "Locator",
                            "text": "String",
                            "value": "String",
                            "visible": "Bool",
                            "uuid": "String",
                        }
                        typ = TypeSpec(known.get(name, "Any"))
                    value = None
            return typ
        return TypeSpec()

    def block(self, node, scope, shared=False):
        scope = scope if shared else dict(scope)
        declared = set()
        for child in node.children:
            kind, children = child.data, child.children
            if kind == "binding":
                name = str(children[1])
                if name in declared:
                    self.diagnostic(child, f"Duplicate declaration '{name}'")
                declared.add(name)
                self.naming(name, child)
                actual = self.infer(children[-1], scope)
                typ = type_spec(children[2]) if len(children) == 4 else actual
                self.valid_type(typ, child)
                if not compatible(actual, typ):
                    self.diagnostic(child, f"'{name}' expects {typ}, got {actual}")
                scope[name] = typ, str(children[0]) == "const"
            elif kind == "assignment":
                name = str(children[0])
                expected, const = self.symbol(name, scope, child)
                actual = self.infer(children[1], scope)
                if const:
                    self.diagnostic(child, f"Cannot assign to constant '{name}'")
                if not compatible(actual, expected):
                    self.diagnostic(child, f"'{name}' expects {expected}, got {actual}")
            elif kind == "if_stmt":
                self.infer(children[0], scope)
                for block in children[1:]:
                    self.block(block, scope)
            elif kind == "for_stmt":
                iterable = self.infer(children[1], scope)
                local = dict(scope)
                local[str(children[0])] = (iterable.args[0] if iterable.args else TypeSpec()), False
                self.block(children[2], local)
            elif kind == "return_stmt":
                actual = self.infer(children[0], scope)
                if self.return_type is None:
                    self.diagnostic(child, "return is only allowed inside fn or flow")
                elif not compatible(actual, self.return_type):
                    self.diagnostic(child, f"Return expects {self.return_type}, got {actual}")
            elif kind == "try_stmt":
                if len(children) == 1:
                    self.diagnostic(child, "try requires catch or finally")
                self.block(children[0], scope)
                for clause in children[1:]:
                    local = dict(scope)
                    if clause.data == "catch_clause":
                        local[str(clause.children[0])] = TypeSpec(), True
                    self.block(clause.children[-1], local)
            elif kind == "step_stmt":
                self.block(children[1], scope)
            else:
                for expr in children:
                    if isinstance(expr, Tree):
                        typ = self.infer(expr, scope)
                        if kind == "expect_stmt" and typ.name not in {"Bool", "Any"}:
                            self.diagnostic(child, "expect requires a Bool expression")
            if (
                self.pure
                and kind in {"expect_stmt", "step_stmt", "log_stmt", "skip_stmt"}
                or (self.pure and kind.startswith("web_"))
            ):
                self.diagnostic(child, f"fn cannot contain {kind.removesuffix('_stmt')}")
            if self.flows_only and self.in_test and kind.startswith("web_"):
                self.diagnostic(child, "tests-use-flows-only: move browser actions to a flow", "warning")

    def analyze(self):
        for path, (tree, env) in self.runtime.modules.items():
            self.path, self.env = path, env
            if self.lint and not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", path.stem):
                self.diagnostic(tree, "Use kebab-case for filenames", "warning")
            seen_tests = set()
            for node in tree.children:
                self.pure, self.return_type = False, None
                self.in_test = False
                if node.data == "record_decl":
                    self.naming(str(node.children[0]), node, pascal=True)
                    for field in node.children[1:]:
                        self.naming(str(field.children[0]), field)
                        self.valid_type(type_spec(field.children[1]), field)
                elif node.data == "function_decl":
                    fn = env.get(str(node.children[1]))
                    self.naming(fn.name, node)
                    self.pure, self.return_type = fn.kind == "fn", fn.returns
                    self.valid_type(fn.returns, node)
                    scope = {}
                    for name, typ in fn.params:
                        if name in scope:
                            self.diagnostic(node, f"Duplicate parameter '{name}'")
                        self.naming(name, node)
                        self.valid_type(typ, node)
                        scope[name] = typ, False
                    self.block(fn.body, scope)
                elif node.data == "fixture_decl":
                    fixture = env.get(str(node.children[0]))
                    self.naming(fixture.name, node)
                    scope = {}
                    self.block(fixture.setup, scope, shared=True)
                    if fixture.teardown:
                        self.block(fixture.teardown, scope, shared=True)
                elif node.data == "test_decl":
                    title = str(node.children[0])
                    if title in seen_tests:
                        self.diagnostic(node, "Duplicate test title in module")
                    seen_tests.add(title)
                    scope = {}
                    for child in node.children[1:-1]:
                        if child.data == "dataset":
                            self.infer(child.children[1], scope)
                            scope[str(child.children[0])] = TypeSpec(), False
                        elif child.data == "using" and child.children:
                            used = set()
                            for name in child.children[0].children:
                                if str(name) in used:
                                    self.diagnostic(child, f"Duplicate fixture '{name}'")
                                used.add(str(name))
                                fixture = self.definition(str(name))
                                if not isinstance(fixture, Fixture):
                                    self.diagnostic(child, f"Unknown fixture '{name}'")
                                else:
                                    original_env = self.env
                                    self.env = fixture.env
                                    self.block(fixture.setup, scope, shared=True)
                                    self.env = original_env
                    self.in_test = True
                    self.block(node.children[-1], scope)
                elif node.data == "binding":
                    self.naming(str(node.children[1]), node)
                    self.infer(node.children[-1], {})
                    if len(node.children) == 4:
                        self.valid_type(type_spec(node.children[2]), node)
                elif node.data == "data_decl":
                    self.naming(str(node.children[0]), node)
                    self.infer(node.children[1], {})
        return self.diagnostics
