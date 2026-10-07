# CLI y configuración

```bash
tscr --version
tscr check tests/
tscr lint tests/ --flows-only --strict
tscr list tests/ --tag smoke
tscr run tests/ --tag smoke --exclude-tag slow --name Login
```

Acepta archivos/directorios. Descubrimiento recursivo de `.tscr` con orden léxico; excluye carpetas ocultas, `node_modules`, `site`, `build` y `dist`. Ruta por defecto: `tests/`. Se validan imports, pero sus tests solo se ejecutan si el módulo también está incluido entre las rutas de entrada.

## Comandos

| Comando | Comportamiento |
|---|---|
| `check` | Sintaxis y semántica de entradas/imports |
| `lint` | Check + convenciones y regla opcional de flows |
| `list` | Lista declaraciones seleccionadas sin ejecutar cuerpos |
| `run` | Ejecuta secuencialmente y genera resultados |

Check/list no abren navegadores ni envían HTTP. Cargan constantes/datos de módulo; se diagnostican errores de archivos. Un inicializador de constante puede leer una variable de entorno.

## Filtros

Varios `--tag` incluyen tests con **cualquiera** de esas etiquetas. Varios `--exclude-tag` excluyen tests con **cualquiera** de ellas. `--name` busca un fragmento del título y distingue mayúsculas. Las etiquetas pertenecen al test; flows/fixtures no las heredan. Expresiones booleanas de etiquetas no están soportadas.

## Configuración

Se lee `testscript.toml` de la carpeta de la terminal o el archivo indicado con `--config`. No se buscan carpetas superiores. Sin archivo se utilizan defaults; por ahora, una ruta explícita inexistente también utiliza defaults.

```toml
[testscript]
provider = "playwright"
headless = true
timeout = 10
base_url = "http://127.0.0.1:8765"
output = "testscript-results"
tests_use_flows_only = false
```

Claves desconocidas/valores inválidos generan errores. `--provider` y `--output` sobreescriben sus valores. La salida es relativa a la terminal; datos/imports son relativos a su módulo.

`tests_use_flows_only` avisa sobre acciones Web/HTTP directas en tests. `--flows-only` lo activa en una ejecución del linter. `--strict` convierte avisos en un check fallido.

## Códigos de salida

| Código | Significado |
|---|---|
| 0 | Check/list correcto o ejecución sin casos fallidos |
| 1 | Uno o más casos fallidos |
| 2 | Programa, entrada o configuración inválida |
| 5 | Sin archivos `.tscr` o sin tests seleccionados |

Formatter, watch, workers paralelos y LSP/editor no están implementados.
