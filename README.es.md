# TestScript

<img src="docs/assets/logo.svg" width="80" height="80" alt="TestScript" />


Lenguaje tipado para testing Web/API: intérprete Python + Lark, archivos `.tscr` y comando `tscr`.

**0.2.0 experimental.** Instala nuestra distribución `testscript-lang`; `testscript` en PyPI pertenece a otro proyecto.

[![PyPI](https://img.shields.io/pypi/v/testscript-lang?color=c4f581)](https://pypi.org/project/testscript-lang/) [![CI](https://github.com/angel-valdezzz/testscript/actions/workflows/ci.yml/badge.svg)](https://github.com/angel-valdezzz/testscript/actions/workflows/ci.yml)

Con Python 3.12+:

```bash
python -m pip install testscript-lang
tscr --version
```

Los ejemplos se descargan por separado del repositorio:

```bash
git clone https://github.com/angel-valdezzz/testscript.git
cd testscript
tscr check examples/core.tscr
tscr run examples/core.tscr
```

Para Web: `python -m pip install "testscript-lang[playwright]"` y `python -m playwright install chromium`, o `python -m pip install "testscript-lang[selenium]"` con Chrome instalado.

```tscr
flow verifyName(name: String) {
    step "Validate the name" { expect len(name) > 0 }
}
test "A valid user" tags ["smoke"] { verifyName("Angel") }
```

`test` ejecuta, `flow` reutiliza comportamiento, `fn` transforma datos sin efectos, `fixture` prepara/limpia, `record` define campos tipados, `data` parametriza y `step` explica la ejecución. `expect` valida; capturar una assertion fallida no elimina el fallo.

[Guía de usuario](https://angel-valdezzz.github.io/testscript/es/) · [Referencia del lenguaje](https://angel-valdezzz.github.io/testscript/es/language/) · [PyPI](https://pypi.org/project/testscript-lang/) · [English](README.md)

Comandos: `tscr check`, `tscr lint`, `tscr list`, `tscr run`. Etiquetas `--tag` con inclusión OR; `--exclude-tag` excluye coincidencias. Salidas HTML/JSON/JUnit. Códigos: 0 éxito/skip, 1 fallo de test, 2 entrada inválida, 5 sin tests seleccionados.

Inicia `python examples/demo_server.py` antes de los ejemplos Web/API. Lee [alcance y límites](docs/es/specification.md) y [roadmap](docs/es/roadmap.md).

Construido sobre Python, Lark, HTTPX, PyYAML, Playwright/Selenium y MkDocs Material. Proyecto independiente de estas herramientas y del paquete existente `testscript`.

MIT · Angel Gerardo Molina Valdez
