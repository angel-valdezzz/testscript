# Datos y fixtures

## Parametriza pruebas

```tscr
data users = load("data/users.json")
test "A named user" tags ["data"] for each user in users {
    expect len(user.name) > 0
}
```

Cada fila genera un resultado como `A named user [1]`. La limpieza y el aislamiento Web se aplican por fila. El dataset debe ser una lista con al menos un elemento; datos vacíos o inválidos son errores de entrada.

`load()` resuelve rutas relativas al módulo actual, independientemente de la carpeta de la terminal. También acepta `Path()`.

=== "JSON"

    ```json
    [{"name": "Angel", "active": true}]
    ```

=== "CSV"

    ```csv
    name,active
    Angel,true
    ```

=== "YAML"

    ```yaml
    - name: Angel
      active: true
    ```

CSV conserva valores como strings. JSON/YAML conservan tipos escalares soportados. Convierte CSV explícitamente con `int()`/`float()` o compara strings. YAML se carga sin construcción arbitraria de objetos.

## Ciclo de vida

```tscr
fixture session {
    setup {
        var baseUrl: String = "http://127.0.0.1:8765"
        log "Session ready"
    }
    teardown { log "Session closed" }
}
test "Session" using [session] { expect baseUrl contains "127.0.0.1" }
```

1. Setup de fixtures de izquierda a derecha.
2. Exposición de bindings inicializados correctamente al test.
3. Ejecución del cuerpo de la prueba.
4. Teardown de fixtures iniciados de derecha a izquierda.
5. Cierre del cliente HTTP y navegador del caso.

Un fixture iniciado se limpia aunque setup falle. Teardown accede a bindings creados antes del fallo: su código debe considerar recursos incompletos. Un error de limpieza falla el caso y conserva fallos anteriores. `skip` también dispara limpieza.

Los fixtures mantienen entornos de módulo independientes y no dependen implícitamente de bindings de otros fixtures. Exportar nombres duplicados es un error. Scopes suite/session, inyección de dependencias y resolución lazy de fixtures son trabajo futuro.

El navegador se crea cuando hace falta; un test exclusivamente API no lo inicia. Cada test/fila obtiene un navegador nuevo. Pasa valores de fixtures a los flows mediante parámetros.
