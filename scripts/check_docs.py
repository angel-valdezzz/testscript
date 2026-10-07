"""Check bilingual page parity and syntax of complete programs/code excerpts."""

import re
from pathlib import Path

from testscript.parser import ScriptError, parse

ROOT = Path(__file__).resolve().parents[1]
english = {p.name for p in (ROOT / "docs/en").glob("*.md")}
spanish = {p.name for p in (ROOT / "docs/es").glob("*.md")}
assert english == spanish, (english - spanish, spanish - english)
count = 0
for locale in ("en", "es"):
    for path in (ROOT / "docs" / locale).glob("*.md"):
        for match in re.finditer(r"```tscr\n(.*?)```", path.read_text(), re.S):
            source = match.group(1)
            try:
                parse(source, str(path))
            except ScriptError:
                parse('test "Documentation excerpt" {\n' + source + "\n}", str(path))
            count += 1
print(f"{len(english)} pages per language; {count} TestScript snippets parsed")
