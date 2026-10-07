# Ejemplos completos

El repositorio incluye un laboratorio determinista: la verificación no depende de servicios públicos. Se conecta a loopback, almacena usuarios en memoria y reinicia sus datos al reiniciar el proceso.

| Archivo | Demuestra | Requiere |
|---|---|---|
| `examples/core.tscr` | Records, fn/flow tipados, fixture, datos, control y errores | Paquete base |
| `examples/api.tscr` | Crear/consultar usuario e inspeccionar HTTP 404 | Laboratorio local |
| `examples/web.tscr` | Flow importado, validación UI y captura | Laboratorio + motor Web |
| `examples/login-flow.tscr` | Comportamiento Web reutilizable | Importado por el ejemplo Web |
| `examples/data/users.*` | Datos equivalentes CSV/JSON/YAML | `load()` |

## Core

```bash
tscr check examples/core.tscr
tscr run examples/core.tscr
```

Se esperan cuatro resultados exitosos, incluyendo dos filas parametrizadas.

## Web y API

Primera terminal:

```bash
python examples/demo_server.py
```

Segunda terminal:

```bash
tscr run examples/api.tscr
tscr run examples/web.tscr --provider playwright
tscr run examples/web.tscr --provider selenium
```

Se esperan dos casos API y uno Web. El caso UI escribe el nombre, selecciona rol, marca checkbox, envía formulario y comprueba el saludo. Instala primero navegadores/drivers.

## Selección de ejemplos

```bash
tscr check examples/
tscr run examples/ --tag core
tscr run examples/ --tag api
tscr run examples/ --tag web
```

`login-flow.tscr` no declara un test independiente. CI está configurado para verificar core/API con servicio local y el ejemplo Web con ambos motores. Se pueden agregar adaptaciones ParaBank/Demo Users con configuración explícita; la disponibilidad pública no será un criterio de release.
