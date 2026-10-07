# { } TestScript

**Pruebas legibles. Flows reutilizables. Una historia de ejecución.**

Lenguaje tipado para testing Web/API: intérprete Python + Lark, archivos `.tscr` y comando `tscr`.

**0.1.0 experimental.** Todavía no publicado en PyPI. `testscript` en PyPI pertenece a otro proyecto; nuestra distribución es `testscript-lang`.

Desde la carpeta del código fuente:

```bash
python -m pip install .
tscr --version
tscr check examples/core.tscr
tscr run examples/core.tscr
```

Para Web: `python -m pip install ".[playwright]"` y `python -m playwright install chromium`, o `python -m pip install ".[selenium]"` con Chrome instalado.

```tscr
flow verifyName(name: String) {
    step "Validate the name" { expect len(name) > 0 }
}
test "A valid user" tags ["smoke"] { verifyName("Angel") }
```

`test` ejecuta, `flow` reutiliza comportamiento, `fn` transforma datos sin efectos, `fixture` prepara/limpia, `record` define campos tipados, `data` parametriza y `step` explica la ejecución. `expect` valida; capturar una assertion fallida no elimina el fallo.

[Guía](docs/es/getting-started.md) · [Conceptos](docs/es/concepts.md) · [Lenguaje](docs/es/language.md) · [Ejemplos](examples/) · [English](README.md)

Comandos: `tscr check`, `tscr lint`, `tscr list`, `tscr run`. Etiquetas `--tag` con inclusión OR; `--exclude-tag` excluye coincidencias. Salidas HTML/JSON/JUnit. Códigos: 0 éxito/skip, 1 fallo de test, 2 entrada inválida, 5 sin tests seleccionados.

Inicia `python examples/demo_server.py` antes de los ejemplos Web/API. Lee [alcance y límites](docs/es/specification.md) y [roadmap](docs/es/roadmap.md).

Construido sobre Python, Lark, HTTPX, PyYAML, Playwright/Selenium y MkDocs Material. Proyecto independiente de estas herramientas y del paquete existente `testscript`.

MIT · Angel Gerardo Molina Valdez
