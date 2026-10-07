# Pruebas de API

Las peticiones HTTP son expresiones: método en mayúsculas, URL y un bloque declarativo. Devuelven una respuesta como valor. HTTPX crea el cliente al necesitarlo y lo cierra después de cada test/fila.

## Enviar una petición

```tscr
var token = "ejemplo-local"
var response = POST "http://127.0.0.1:8765/users" {
    headers { "Authorization": "Bearer ${token}" }
    query { notify: true }
    body json {
        name: "Angel"
        role: "tester"
    }
}
expect response.status == 201
expect response.json.name == "Angel"
```

Métodos: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, `OPTIONS`. El bloque es obligatorio, aunque esté vacío. `headers`, `query` y `body json` son opcionales, pueden ir en cualquier orden y aparecer una vez cada uno. Headers es un mapa de strings; query es un mapa; JSON acepta un valor serializable. El cuerpo JSON añade `Content-Type: application/json` salvo que lo reemplaces. Las comas entre propiedades son opcionales en mapas, también anidados; en listas siguen siendo obligatorias.

## Reutilizar un payload cargado

```tscr
flow submitUser(baseUrl: String) -> Map[String, Any] {
    var payload = load("data/user.json")
    return POST "${baseUrl}/users" { body json payload }
}
test "Crear usuario" {
    const response = submitUser("http://127.0.0.1:8765")
    expect response.status == 201
}
```

`load()` elige JSON, YAML o CSV por la extensión. Las rutas se resuelven desde el módulo que declara la carga. Puedes enviar peticiones en tests, flows y fixtures; están prohibidas dentro de `fn` e inicializadores del módulo. `check` y `list` nunca envían peticiones.

## Campos de la respuesta

| Campo | Valor |
|---|---|
| `status` | Código HTTP entero |
| `json` | JSON decodificado, o null si el cuerpo está vacío/no es JSON |
| `text` | Texto de la respuesta |
| `headers` | Mapa con nombres de headers en minúsculas |
| `url` | URL final después de redirects |

Las respuestas se cargan completas. Se siguen redirects y se verifica TLS. No se usan implícitamente proxies del entorno. Las cookies duran dentro del test y se eliminan entre tests.

## Respuestas negativas

```tscr
var response = GET "http://127.0.0.1:8765/users/missing" {}
expect response.status == 404
expect response.json.error == "User not found"
```

HTTP 4xx/5xx son valores de respuesta. Fallos de conexión, timeout y TLS lanzan errores capturables. Los asserts determinan si la respuesta cumple lo esperado.

## URL base y timeout

```toml
[testscript]
base_url = "http://127.0.0.1:8765"
timeout = 10
```

`GET "/users/missing" {}` une la URL base y el path. Una URL completa se utiliza directamente. El timeout se aplica a HTTPX, no al tiempo total del test.

Inicia `python examples/demo_server.py` y ejecuta `tscr run examples/api.tscr`. OAuth, multipart, retries, validación JSON Schema/OpenAPI y streaming quedan para futuras versiones. Usa `env("TOKEN")` en tests/flows para las credenciales.

!!! warning "Migración desde 0.1"
    `api.get(...)` y `api.post(...)` se retiraron en 0.2. Sustitúyelos por `GET url {}` y `POST url { body json payload }`. Los campos de respuesta se conservan. Consulta el [changelog](changelog.md).
