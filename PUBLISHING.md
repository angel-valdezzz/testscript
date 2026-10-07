# Publishing testscript-lang

Distribution: `testscript-lang`; Python import: `testscript`; CLI: `tscr`.

## Verified GitHub releases

A successful **push** verification on `main` triggers `release.yml`. It builds and validates the distributions, then creates the version's tag and experimental GitHub release with wheel/sdist assets. Existing releases are left unchanged. PR workflows never publish.

## First PyPI publication

PyPI publication remains pending; `pip install testscript-lang` is not yet the installation route.

Configure a pending Trusted Publisher on your PyPI account's publishing page using:

| Field | Value |
|---|---|
| PyPI project | `testscript-lang` |
| GitHub owner | `angel-valdezzz` |
| Repository | `testscript` |
| Workflow filename | `publish.yml` |
| Environment | `pypi` |

Then run **Publish to PyPI** in GitHub Actions with verified tag `v0.2.0`. The workflow builds and tests the package, then publishes using PyPI's OIDC Trusted Publishing. No API token is stored in the repository.

After the package appears on PyPI, verify a clean `python -m pip install testscript-lang==0.2.0`, update the README/installation page with the PyPI version badge and installation command, and remove the pending-publication notice. Do not advertise PyPI installation until this succeeds.

Official setup: https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/
