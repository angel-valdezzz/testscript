"""Check the built bilingual landing's routes, language map and sample-free surface."""

import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


class Landing(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.assets = []
        self.tags = []
        self.ids = []
        self.concepts = 0
        self.accent = False
        self.pause = False
        self.current_language = []
        self.alternates = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append(tag)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "a":
            self.links.append(attrs.get("href", ""))
            if attrs.get("aria-current") == "page":
                self.current_language.append(attrs.get("lang"))
            if "data-ts-language" in attrs:
                self.alternates[attrs["lang"]] = (
                    attrs["href"], json.loads(attrs["data-ts-fragments"])
                )
        if tag in ("img", "script") and "src" in attrs:
            self.assets.append(attrs["src"])
        if tag == "link" and attrs.get("rel") in ("stylesheet", "preload"):
            self.assets.append(attrs.get("href", ""))
        self.concepts += "ts-concept" in attrs.get("class", "").split()
        self.accent |= "ts-green" in attrs.get("class", "").split()
        self.pause |= tag == "button" and attrs.get("id") == "ts-pause"


def local_target(href, page):
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    path = unquote(parsed.path)
    if path.startswith("/testscript/"):
        target = SITE / path.removeprefix("/testscript/")
    elif path.startswith("/"):
        target = SITE / path.removeprefix("/")
    else:
        target = page.parent / path
    if target.is_dir():
        target /= "index.html"
    return target


def main():
    for language in ("en", "es"):
        page = SITE / ("es/index.html" if language == "es" else "index.html")
        source = page.read_text()
        landing = Landing()
        landing.feed(source)
        expected = "Menos ruido." if language == "es" else "Less noise."
        assert expected in source, f"{language}: missing heading"
        assert landing.accent and landing.pause and landing.concepts == 4
        assert "ts-language-section" in landing.ids
        assert len(landing.ids) == len(set(landing.ids)), f"{language}: duplicate HTML IDs"
        assert landing.current_language == [language], f"{language}: active locale"
        assert not {"pre", "code", "table"}.intersection(landing.tags), f"{language}: sample in landing"
        for href in landing.links + landing.assets:
            target = local_target(href, page)
            assert target is None or target.is_file(), f"{language}: missing route or asset: {href}"
        for asset in ("landing.css", "product.js", "Inter-Bold.woff2"):
            assert any(asset in url for url in landing.assets), f"{language}: missing {asset}"
    for name in ("README.md", "README.es.md"):
        lines = (ROOT / name).read_text().splitlines()
        languages = next(line for line in lines if "README.md)" in line and "README.es.md)" in line)
        docs = next(line for line in lines if "pypi.org/project/testscript-lang/)" in line and "language/)" in line)
        assert languages != docs and lines.index(languages) < lines.index(docs), name
        label = "Guía de usuario" if name == "README.es.md" else "User Guide"
        root = "https://angel-valdezzz.github.io/testscript/" + ("es/" if name == "README.es.md" else "")
        assert f"[{label}]({root})" in docs, name
        assert "[Home]" not in docs and "[Inicio]" not in docs, name
    pages = list(SITE.glob("**/index.html"))
    for page in pages:
        source = page.read_text()
        parsed = Landing()
        parsed.feed(source)
        relative = page.relative_to(SITE).as_posix().removesuffix("index.html")
        route = relative.removeprefix("es/")
        assert set(parsed.alternates) == {"en", "es"}, page
        assert '__md_scope=new URL("/testscript/",location)' in source, page
        for locale, (href, fragments) in parsed.alternates.items():
            expected = "/testscript/" + ("es/" if locale == "es" else "") + route
            assert href == expected, f"{page}: language link loses current page: {href}"
            target = local_target(href, page)
            translated = Landing()
            translated.feed(target.read_text())
            assert set(fragments).issubset(parsed.ids), page
            assert set(fragments.values()).issubset(translated.ids), page
    print(f"Bilingual landing and README navigation passed; {len(pages)} pages preserve language routes, sections and theme scope")


if __name__ == "__main__":
    main()
