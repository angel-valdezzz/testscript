# Pruebas de API

`api` es un namespace HTTP basado en HTTPX. Su cliente se crea cuando hace falta y se cierra después de cada test/fila.

## Envía un request

```tscr
var response = api.post(
    "http://127.0.0.1:8765/users",
    body: {name: "Angel"},
    headers: {"Content-Type": "application/json"}
)
expect response.status == 201
expect response.json.name == "Angel"
```

Métodos: `get`, `post`, `put`, `patch`, `delete`, `head`, `options`. Aceptan `url` y opcionalmente `body` JSON, `headers` y `query`. Los parámetros query se proporcionan como map. La respuesta se carga completa; no es un stream.

| Campo | Valor |
|---|---|
| `status` | Código HTTP entero |
| `json` | JSON decodificado, o null si el contenido no es JSON |
| `text` | Texto de respuesta |
| `headers` | Map con nombres de encabezados en minúsculas |
| `url` | URL final tras redirects |

Se siguen redirects y se mantiene verificación TLS. Las variables de proxy del entorno no se aplican implícitamente. Las cookies se conservan durante el test y se descartan al cerrar el cliente.

## Respuestas negativas

```tscr
var response = api.get("http://127.0.0.1:8765/users/missing")
expect response.status == 404
expect response.json.error == "User not found"
```

Los códigos HTTP 4xx/5xx son valores inspeccionables. Conexión, timeout o TLS producen errores capturables. Las assertions determinan si la respuesta cumple lo esperado.

## URL base y timeouts

```toml
[testscript]
base_url = "http://127.0.0.1:8765"
timeout = 10
```

`api.get("/users/missing")` concatena URL base y path. Una URL completa se utiliza directamente. El timeout se pasa a HTTPX; no es un límite para el tiempo total del test.

Inicia el servidor local y ejecuta `tscr run examples/api.tscr`. Se crea/consulta un usuario y se valida un 404. El laboratorio guarda datos en memoria y sirve para verificación local.

Helpers OAuth, multipart, retries, validaciones JSON Schema/OpenAPI e integraciones con otros reporters permanecen en el roadmap. Usa `env("TOKEN")` en tests/flows para leer secretos del entorno y evita guardarlos en ejemplos versionados.
