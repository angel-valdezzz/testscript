"""Lark parser with source locations retained in the syntax tree."""

from pathlib import Path

from lark import Lark, Tree
from lark.exceptions import UnexpectedInput


class ScriptError(Exception):
    def __init__(self, message: str, path: str = "<script>", line: int = 1, column: int = 1):
        self.message, self.path, self.line, self.column = message, path, line, column
        super().__init__(f"{path}:{line}:{column}: {message}")


_PARSER = Lark(
    Path(__file__).with_name("grammar.lark").read_text(),
    parser="lalr",
    propagate_positions=True,
    maybe_placeholders=False,
)


def parse(source: str, path: str = "<script>") -> Tree:
    try:
        return _PARSER.parse(source)
    except UnexpectedInput as exc:
        context = exc.get_context(source, span=35).strip()
        raise ScriptError(f"Invalid syntax\n{context}", path, exc.line, exc.column) from exc


def parse_file(path: Path) -> Tree:
    try:
        return parse(path.read_text(encoding="utf-8"), str(path))
    except OSError as exc:
        raise ScriptError(str(exc), str(path)) from exc
