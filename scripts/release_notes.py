"""Extract current-version release notes from the maintained English changelog."""
import tomllib
from pathlib import Path

root = Path(__file__).resolve().parents[1]
version = tomllib.loads((root / 'pyproject.toml').read_text())['project']['version']
changelog = (root / 'docs/en/changelog.md').read_text()
section = changelog.split(f'## {version} — ', 1)[1].split('\n## ', 1)[0]
print(section.split('\n', 1)[1].strip())
print('\nPython 3.12+. Install the attached wheel with `python -m pip install testscript_lang-' + version + '-py3-none-any.whl`.')
print('\nPyPI publication is pending account setup. Documentation: https://angel-valdezzz.github.io/testscript/')
