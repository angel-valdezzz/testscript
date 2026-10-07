# Conceptos del lenguaje

TestScript es un lenguaje pequeño y tipado para testing. Expresa comportamientos y hace visible su ejecución. El intérprete está construido en Python; la sintaxis y semántica pertenecen a TestScript.

## test

Es la unidad que ejecuta el runner. Tiene un título descriptivo y etiquetas opcionales. El runner descubre archivos `.tscr`, selecciona casos y registra un resultado independiente por test o fila de datos.

```tscr
test "A valid user" tags ["smoke"] { expect true }
```

Puede llamar flows y realizar acciones directas. Un test no es una función invocable. Fixtures y steps no se seleccionan individualmente desde la CLI.

## flow

Agrupa comportamiento reutilizable. Puede interactuar con Web/API, validar, llamar funciones, componer otros flows y devolver valores.

```tscr
flow createUser(baseUrl: String, name: String) -> Map[String, Any] {
    var response = POST "${baseUrl}/users" { body json {name: name} }
    expect response.status == 201
    return response.json
}
```

Recibe dependencias explícitas. Accede a constantes e imports de su módulo; no obtiene automáticamente variables locales o bindings de fixtures del llamador.

## fn

Calcula o transforma datos. No accede a HTTP/navegador, `load`, `env`, `uuid`, logs, steps o assertions; tampoco llama flows. Puede construir records y llamar funciones puras.

```tscr
fn greeting(name: String) -> String { return "Hello, ${name}" }
```

## fixture

Tiene `setup` y `teardown` opcional. Se ejecuta por test o fila. Los bindings exitosos de setup se exponen al test. Teardown conserva el entorno propio del fixture y se ejecuta en orden inverso, incluso si setup falló después de comenzar.

```tscr
fixture session {
    setup { var baseUrl: String = "http://127.0.0.1:8765" }
    teardown { log "Cleanup completed" }
}
test "Session" using [session] { expect len(baseUrl) > 0 }
```

## record and data

Un record define campos nombrados y tipados. Se construye con argumentos nombrados y permite acceso por punto o corchetes. La modificación de campos y las clases no están implementadas en v0.2.

`data` declara datos a nivel de módulo. Puede cargar CSV, JSON o YAML; una prueba parametrizada genera un resultado por fila. Consulta [datos y fixtures](data-fixtures.md).

## step and expect

Un step nombra un grupo de instrucciones. Los steps anidados forman una ruta en los eventos. Las variables declaradas dentro del step permanecen en ese bloque.

Una assertion registra una verificación exitosa o fallida. Si un catch captura su error, el caso sigue fallido. Consulta [errores y resultados](results.md).

## Convenciones

`camelCase` para variables, datos, funciones, flows y fixtures; `PascalCase` para records/tipos; `kebab-case.tscr` para archivos. Los títulos de tests/steps son textos descriptivos. Las convenciones generan avisos del linter.

## var / const y returns

Variables y constantes usan `camelCase`. `var` permite reasignar; `const` fija el binding (no congela profundamente una List/Map). Ambas reciben returns de flows o funciones. `List[T]` y `Map[K, V]` nombran tipos de colección; sus valores usan nombres como `userList` y `userById`.

```tscr
fn greeting(name: String) -> String { return "Hello, ${name}" }
flow verifiedName(name: String) -> String {
    expect len(name) > 0
    return greeting(name)
}
test "Returns" {
    var userName = verifiedName("Angel")
    const expectedName = greeting("Angel")
    expect userName == expectedName
}
```

`step` es una agrupación opcional en la línea de tiempo, similar en propósito a GROUP de Robot Framework. Tiene ámbito de bloque propio y no se puede llamar. `flow` es reutilizable y puede devolver un valor.
