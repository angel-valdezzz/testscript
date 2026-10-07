"""Language values, lexical scopes and runtime type contracts."""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from lark import Tree


@dataclass(frozen=True)
class TypeSpec:
    name: str = "Any"
    args: tuple = ()
    nullable: bool = False

    def __str__(self):
        suffix = "[" + ", ".join(map(str, self.args)) + "]" if self.args else ""
        return self.name + suffix + ("?" if self.nullable else "")

    def accepts(self, value):
        if self.name == "Any":
            return True
        if value is None:
            return self.nullable or self.name == "Void"
        primitives = {
            "String": str,
            "Bool": bool,
            "Int": int,
            "Float": float,
            "Number": (int, float),
            "Path": Path,
            "Regex": re.Pattern,
        }
        if self.name in primitives:
            return isinstance(value, primitives[self.name]) and not (
                self.name in {"Int", "Float", "Number"} and isinstance(value, bool)
            )
        if self.name == "Locator":
            return isinstance(value, Locator)
        if self.name == "List":
            return (
                len(self.args) == 1
                and isinstance(value, list)
                and all(self.args[0].accepts(v) for v in value)
            )
        if self.name == "Map":
            return (
                len(self.args) == 2
                and isinstance(value, dict)
                and all(self.args[0].accepts(k) and self.args[1].accepts(v) for k, v in value.items())
            )
        return isinstance(value, RecordValue) and value.type_name == self.name


def type_spec(node: Tree) -> TypeSpec:
    return TypeSpec(
        str(node.children[0]),
        tuple(type_spec(c) for c in node.children[1:] if isinstance(c, Tree)),
        any(str(c) == "?" for c in node.children),
    )


@dataclass
class Slot:
    value: Any
    type: TypeSpec = field(default_factory=TypeSpec)
    constant: bool = False


class Env:
    def __init__(self, parent=None):
        self.parent, self.slots = parent, {}

    def define(self, name, value, typ=None, constant=False):
        if name in self.slots:
            raise ValueError(f"Duplicate declaration '{name}'")
        typ = typ or TypeSpec()
        if not typ.accepts(value):
            raise TypeError(f"'{name}' expects {typ}, got {type(value).__name__}")
        self.slots[name] = Slot(value, typ, constant)

    def slot(self, name):
        if name in self.slots:
            return self.slots[name]
        if self.parent:
            return self.parent.slot(name)
        raise NameError(f"Unknown name '{name}'")

    def get(self, name):
        return self.slot(name).value

    def assign(self, name, value):
        slot = self.slot(name)
        if slot.constant:
            raise TypeError(f"Cannot assign to constant '{name}'")
        if not slot.type.accepts(value):
            raise TypeError(f"'{name}' expects {slot.type}, got {type(value).__name__}")
        slot.value = value


@dataclass(frozen=True)
class RecordValue:
    type_name: str
    fields: dict


@dataclass
class RecordType:
    name: str
    fields: dict

    def construct(self, args, kwargs):
        if args:
            raise TypeError(f"{self.name} requires named fields")
        if set(kwargs) != set(self.fields):
            raise TypeError(f"{self.name} requires fields: {', '.join(self.fields)}")
        for name, typ in self.fields.items():
            if not typ.accepts(kwargs[name]):
                raise TypeError(f"{self.name}.{name} expects {typ}")
        return RecordValue(self.name, dict(kwargs))


@dataclass
class Function:
    kind: str
    name: str
    params: list
    returns: TypeSpec
    body: Tree
    env: Env
    path: Path


@dataclass
class Fixture:
    name: str
    setup: Tree
    teardown: Tree | None
    env: Env
    path: Path


@dataclass
class TestCase:
    name: str
    tags: list
    fixtures: list
    dataset: Tree | None
    body: Tree
    env: Env
    path: Path


@dataclass
class Builtin:
    name: str
    callback: Any
    pure: bool = True


@dataclass
class Namespace:
    members: dict


@dataclass(frozen=True)
class Locator:
    strategy: str
    value: str


class ReturnSignal(BaseException):
    def __init__(self, value):
        self.value = value


class SkipSignal(BaseException):
    def __init__(self, reason):
        self.reason = reason
