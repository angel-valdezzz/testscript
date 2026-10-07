# Errores y resultados

## Excepciones

```tscr
test "Handle an operational error" {
    try { var response = api.get("http://127.0.0.1:1") }
    catch error { log error.message }
    finally { log "Finished" }
}
```

`try` requiere `catch`, `finally` o ambos. El error capturado expone `message`, `path`, `line` y `column`. `throw error` propaga ese error existente. Tipos de errores personalizados y lanzar strings no están soportados.

Un error operativo capturado puede manejarse y permitir un resultado exitoso. Una assertion fallida queda registrada inmediatamente: capturarla no borra el fallo. La limpieza se realiza mediante `finally`, teardown y cierre automático de adaptadores.

## Estados

| Estado | Significado |
|---|---|
| `passed` | Sin assertions fallidas ni errores pendientes/de limpieza |
| `failed` | Assertion fallida, error sin manejar o error de limpieza |
| `skipped` | `skip "motivo"` terminó el caso sin un fallo anterior |

Un test sin assertions puede pasar. Una selección con todos los casos skipped termina con 0 en v0.1. Ningún caso seleccionado termina con 5.

## Archivos generados

- `report.html`: reporte independiente con eventos, steps, duración y enlaces a capturas.
- `results.json`: resumen y eventos estructurados.
- `junit.xml`: resultados compatibles con CI.
- Capturas solicitadas explícitamente por el script.

```bash
tscr run examples/core.tscr --output artifacts/core
```

Se registran logs, flows, assertions, método/URL/status HTTP y fases de fixtures. Los cuerpos HTTP no se capturan automáticamente. Los textos HTML se escapan antes de renderizar. Si tú registras un secreto mediante `log`, aparecerá en el resultado.

## Diagnósticos

Errores de sintaxis/semántica incluyen ubicación de origen. El checker valida nombres, firmas explícitas y tipos inferibles. Datos externos pueden conservar tipo `Any`; los contratos tipados se aplican en ejecución. Consulta los límites en la [especificación](specification.md).
