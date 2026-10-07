# Automatización Web

Dos adaptadores opcionales: Playwright y Selenium. Ambos exponen el mismo contrato de acciones/locators. La sintaxis `.tscr` se conserva al cambiar motor; el comportamiento interno puede diferir.

## Locators y acciones

```tscr
flow login(baseUrl: String, username: String) {
    open baseUrl
    type css("#username") with username
    select css("#role") option "tester"
    check css("#remember")
    click css("button[type=submit]")
}
```

| Acción | Significado |
|---|---|
| `open url` | Navega a una URL |
| `click locator` | Hace clic en un elemento accionable |
| `type locator with value` | Reemplaza el valor de un input |
| `select locator option value` | Selecciona una opción por value |
| `check locator` | Marca un checkbox si hace falta |
| `screenshot "name.png"` | Guarda evidencia con nombre único en la salida |

Locators: `css("selector")` y `xpath("expresión")`. Locators por rol/texto, frames, ventanas múltiples, descargas, uploads y mobile no están implementados. Elige locators que identifiquen un solo elemento.

## Observaciones y esperas

```tscr
expect visible(css("#welcome"))
expect text(css("#welcome")) == "Welcome, Angel"
expect value(css("#username")) == "Angel"
```

Playwright aplica sus verificaciones nativas de actionability. Selenium usa esperas explícitas de visibilidad/clickability. `visible()` espera visibilidad. El `timeout` se configura en segundos.

!!! note "Assertions en v0.2"
    `expect` evalúa una vez. No repite la expresión hasta que sea verdadera. Las esperas de elementos/acciones son independientes del retry de assertions; este último permanece en el roadmap.

## Proveedor, navegador y ventana

El proveedor elige el motor de automatización; browser elige su navegador. La sintaxis de los scripts se conserva.

| Proveedor | Valores de browser | Por defecto |
|---|---|---|
| Playwright | `chromium`, `chrome`, `edge`, `firefox`, `webkit` | `chromium` |
| Selenium | `chrome`, `edge`, `firefox` | `chrome` |

Firefox/WebKit de Playwright son sus builds administrados. WebKit no es la aplicación Safari. Chrome/Edge utilizan canales estables instalados. Selenium usa el navegador instalado y un driver compatible mediante Selenium Manager.

```toml
[testscript]
provider = "playwright"
browser = "firefox"
headless = true
incognito = true
viewport_width = 1440
viewport_height = 900
timeout = 10
```

```bash
python -m playwright install firefox
tscr run examples/web.tscr --provider playwright --browser firefox
tscr run examples/web.tscr --provider selenium --browser chrome --headed --no-incognito
tscr run examples/web.tscr --viewport-width 1024 --viewport-height 768
```

`incognito = true` crea un contexto/perfil privado. `false` crea un perfil normal **temporal** por test. Ninguno reutiliza tu perfil personal ni conserva cookies entre tests. Playwright usa un contexto persistente temporal para el modo normal. Width/height indican el viewport de la página, no el marco de la ventana. Selenium compensa el tamaño del marco; el gestor de ventanas puede limitar el tamaño alcanzable.

Para maximizar una ventana visible:

```toml
[testscript]
provider = "selenium"
browser = "chrome"
headless = false
maximize = true
```

Maximizar es incompatible con dimensiones explícitas y con headless. En Playwright solo se admite Chromium/Chrome/Edge, con el comportamiento nativo de inicio; la resolución y el gestor de ventanas determinan el tamaño final.

La CLI reemplaza TOML. Disponibles: `--headless`/`--headed`, `--incognito`/`--no-incognito`, `--maximize`/`--no-maximize`. Instala primero el navegador elegido; consulta [instalación](getting-started.md).

`TSCR_BROWSER_EXECUTABLE` y `TSCR_DRIVER_EXECUTABLE` permiten indicar un navegador y driver Selenium compatibles para entornos controlados. Sin ejecutable propio, Playwright utiliza su motor administrado.

Inicia `python examples/demo_server.py` y ejecuta `examples/web.tscr`. Los recursos se cierran después del teardown, también si falla el test. Las capturas son explícitas; capturas automáticas al fallar quedan para futuras versiones.
