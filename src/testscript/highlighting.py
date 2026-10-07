"""Native Pygments lexer for .tscr examples."""

from pygments.lexer import RegexLexer, words
from pygments.token import Comment, Keyword, Name, Number, Operator, Punctuation, String, Text


class TestScriptLexer(RegexLexer):
    name = "TestScript"
    aliases = ["tscr", "testscript"]
    filenames = ["*.tscr"]
    tokens = {
        "root": [
            (r"\s+", Text),
            (r"//[^\n]*", Comment.Single),
            (r"/\*[\s\S]*?\*/", Comment.Multiline),
            (r'r"(?:[^"\\]|\\.)*"', String.Regex),
            (r'"(?:[^"\\]|\\.)*"', String.Double),
            (
                words(
                    (
                        "test",
                        "flow",
                        "fn",
                        "fixture",
                        "setup",
                        "teardown",
                        "record",
                        "data",
                        "var",
                        "const",
                        "import",
                        "from",
                        "tags",
                        "using",
                        "step",
                        "expect",
                        "if",
                        "else",
                        "for",
                        "each",
                        "return",
                        "try",
                        "catch",
                        "finally",
                        "throw",
                        "log",
                        "skip",
                        "open",
                        "click",
                        "type",
                        "with",
                        "select",
                        "option",
                        "check",
                        "screenshot",
                    ),
                    suffix=r"\b",
                ),
                Keyword,
            ),
            (words(("true", "false", "null"), suffix=r"\b"), Keyword.Constant),
            (
                words(
                    (
                        "String",
                        "Int",
                        "Float",
                        "Number",
                        "Bool",
                        "Any",
                        "Void",
                        "Path",
                        "Regex",
                        "Locator",
                        "List",
                        "Map",
                    ),
                    suffix=r"\b",
                ),
                Keyword.Type,
            ),
            (words(("and", "or", "not", "in", "contains", "matches"), suffix=r"\b"), Operator.Word),
            (
                words(
                    (
                        "css",
                        "xpath",
                        "text",
                        "value",
                        "visible",
                        "load",
                        "env",
                        "uuid",
                        "len",
                        "str",
                        "int",
                        "float",
                        "abs",
                        "min",
                        "max",
                        "round",
                        "api",
                    ),
                    suffix=r"\b",
                ),
                Name.Builtin,
            ),
            (r"\d+(?:\.\d+)?", Number),
            (r"->|==|!=|>=|<=|[=+*/%<>?-]", Operator),
            (r"[{}\[\](),.:]", Punctuation),
            (r"[A-Z][A-Za-z0-9_]*", Name.Class),
            (r"[a-z_][A-Za-z0-9_]*", Name),
        ]
    }
