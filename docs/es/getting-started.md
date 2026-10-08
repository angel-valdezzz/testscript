# Instala TestScript

TestScript es un intérprete de Python para programas `.tscr`. Escribes TestScript; necesitas Python 3.12+ instalado para ejecutar el intérprete.

!!! warning "Lenguaje experimental"
    La versión 0.2.0 está publicada en [PyPI](https://pypi.org/project/testscript-lang/). Instala `testscript-lang`; `testscript` en PyPI pertenece a otro proyecto. El lenguaje y su especificación continúan evolucionando.

## Desde PyPI

Crea y activa un entorno virtual; después instala:

```bash
python -m pip install testscript-lang
tscr --version
```

Para Web, instala `"testscript-lang[playwright]"` y ejecuta `python -m playwright install chromium`, o instala `"testscript-lang[selenium]"` con Chrome disponible. El paquete base cubre API y core.

El paquete instala el intérprete y CLI. Descarga los ejemplos por separado:

```bash
git clone https://github.com/angel-valdezzz/testscript.git
cd testscript
```

## Desde el código fuente

Clona el repositorio como se indica arriba o descarga y extrae su archivo. Abre una terminal dentro de `testscript`.

```bash
python -m venv .venv
```

Activa `.venv` con el comando correspondiente a tu sistema operativo y ejecuta:

```bash
python -m pip install .
tscr --version
tscr check examples/core.tscr
tscr run examples/core.tscr
```

Se esperan cuatro resultados exitosos. Abre `testscript-results/report.html`; encontrarás JSON y JUnit XML en la misma carpeta.

## Elige el motor Web

=== "Playwright"

    ```bash
    python -m pip install ".[playwright]"
    python -m playwright install chromium
    tscr run examples/web.tscr --provider playwright
    ```

=== "Selenium"

    ```bash
    python -m pip install ".[selenium]"
    tscr run examples/web.tscr --provider selenium
    ```

    Instala Chrome. Selenium Manager resuelve el driver compatible y puede necesitar red. Se admiten Chrome, Edge y Firefox; elige el navegador en configuración.

Antes de ejecutar los ejemplos Web/API, inicia el laboratorio en otra terminal:

```bash
python examples/demo_server.py
```

El paquete base cubre core/API. Los motores Web son dependencias opcionales; sus navegadores y drivers no vienen dentro del wheel.

## Desde un wheel

```bash
python -m pip install /ruta/testscript_lang-0.2.0-py3-none-any.whl
```

El wheel instala intérprete y CLI; conserva los ejemplos por separado.
