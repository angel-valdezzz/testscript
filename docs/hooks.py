"""Share design assets between the two independently built language sites."""
import shutil
from pathlib import Path

from markdown import Markdown


def on_pre_build(config):
    source = Path(__file__).parent / 'assets'
    destination = Path(config['docs_dir']) / 'assets'
    shutil.copytree(source, destination, dirs_exist_ok=True)


def _heading_ids(source, config):
    """Use the same Markdown extensions to resolve translated section IDs."""
    if source.startswith("---\n"):
        source = source.split("---", 2)[-1]
    parser = Markdown(extensions=config.markdown_extensions,
                      extension_configs=config.mdx_configs)
    parser.convert(source)

    def flatten(tokens):
        for token in tokens:
            yield token["level"], token["id"]
            yield from flatten(token["children"])

    return list(flatten(parser.toc_tokens))


def on_page_context(context, page, config, nav):
    """Resolve both language destinations for this page, including its TOC."""
    root = config.extra["scope"]
    current = config.theme["language"]
    source = Path(config.docs_dir) / page.file.src_uri
    headings = _heading_ids(source.read_text(), config)
    alternates = []
    for alternate in config.extra["alternate"]:
        language = alternate["lang"]
        target = Path(config.docs_dir).parent / language / page.file.src_uri
        if not target.is_file():
            raise ValueError(f"Missing {language} translation: {page.file.src_uri}")
        translated = _heading_ids(target.read_text(), config)
        fragments = {}
        if [level for level, _ in headings] == [level for level, _ in translated]:
            fragments = {left[1]: right[1] for left, right in zip(headings, translated)}
        alternates.append({
            "name": alternate["name"], "lang": language,
            "link": root + ("es/" if language == "es" else "") + page.url,
            "fragments": fragments, "current": language == current,
        })
    # Material uses this list for both the header and hreflang metadata.
    config.extra["alternate"] = alternates
    return context
