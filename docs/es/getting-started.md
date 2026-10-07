# Instala TestScript

TestScript es un intérprete de Python para programas `.tscr`. Escribes TestScript; necesitas Python 3.12+ instalado para ejecutar el intérprete.

!!! warning "Estado de distribución"
    La versión 0.1.0 es experimental y todavía no está publicada en PyPI. `testscript` en PyPI es otro proyecto. Nuestra distribución se llama `testscript-lang`; el nombre no queda reservado hasta publicarlo. Usa el código fuente o el wheel.

## Desde el código fuente

Descarga el archivo del proyecto, extráelo y abre una terminal dentro de `testscript`. Una vez publicado el repositorio remoto, también podrás clonarlo desde `https://github.com/angel-valdezzz/testscript.git`.

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

    Instala Chrome. Selenium Manager resuelve el driver compatible y puede necesitar red. El MVP utiliza Chrome/Chromium.

Antes de ejecutar los ejemplos Web/API, inicia el laboratorio en otra terminal:

```bash
python examples/demo_server.py
```

El paquete base cubre core/API. Los motores Web son dependencias opcionales; sus navegadores y drivers no vienen dentro del wheel.

## Desde un wheel

```bash
python -m pip install /ruta/testscript_lang-0.1.0-py3-none-any.whl
```

El wheel instala intérprete y CLI; conserva los ejemplos por separado. Las instrucciones de PyPI se agregarán después de publicar realmente el paquete.
