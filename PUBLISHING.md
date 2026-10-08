# Publishing testscript-lang

Distribution: `testscript-lang`; Python import: `testscript`; CLI: `tscr`.

## Verified GitHub releases

A successful **push** verification on `main` triggers `release.yml`. It builds and validates the distributions, then creates the version's tag and experimental GitHub release with wheel/sdist assets. Existing releases are left unchanged. PR workflows never publish.

## PyPI publication

Version **0.2.0** is published on [PyPI](https://pypi.org/project/testscript-lang/0.2.0/). A clean installation from the public index, `tscr --version`, all four core example results and `pip check` were verified.

The project uses a Trusted Publisher with these values:

| Field | Value |
|---|---|
| PyPI project | `testscript-lang` |
| GitHub owner | `angel-valdezzz` |
| Repository | `testscript` |
| Workflow filename | `publish.yml` |
| Environment | `pypi` |

For each new version, wait for CI and the verified GitHub release, then run **Publish to PyPI** in GitHub Actions with that release's tag. The workflow builds and tests the tagged package, then publishes using PyPI's OIDC Trusted Publishing. No API token is stored in the repository. Published versions are immutable; do not replace existing artifacts or move their tags.

After publication, verify a clean installation of the exact new version and run the core example outside the source checkout. Update installation documentation only after verification succeeds. PyPI's project description comes from the README bundled with each release; subsequent README edits appear on PyPI with the next version.

Official setup: https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/
