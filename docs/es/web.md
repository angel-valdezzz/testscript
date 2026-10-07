# Automatización Web

Dos adaptadores opcionales: Playwright y Selenium. Ambos utilizan Chrome/Chromium con el mismo contrato de acciones/locators. La sintaxis `.tscr` se conserva al cambiar motor; el comportamiento interno puede diferir.

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

!!! note "Assertions en v0.1"
    `expect` evalúa una vez. No repite la expresión hasta que sea verdadera. Las esperas de elementos/acciones son independientes del retry de assertions; este último permanece en el roadmap.

## Configuración

```toml
[testscript]
provider = "playwright"
headless = true
timeout = 10
```

```bash
tscr run examples/web.tscr --provider selenium
```

`--provider` sobreescribe configuración. `TSCR_BROWSER_EXECUTABLE` puede indicar un ejecutable de Chrome/Chromium en entornos controlados. Instala primero las dependencias Web; consulta [instalación](getting-started.md).

Inicia `python examples/demo_server.py` y ejecuta `examples/web.tscr`. El navegador se cierra después de los fixtures, también en fallos. Las capturas son explícitas; capturas automáticas al fallar son trabajo futuro.

`TSCR_DRIVER_EXECUTABLE` permite indicar un ChromeDriver existente para Selenium. El driver debe ser compatible con tu versión de Chrome/Chromium.
