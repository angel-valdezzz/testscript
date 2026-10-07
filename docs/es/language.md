# Guía del lenguaje

## Sintaxis y comentarios

Usa llaves para bloques, `=` para asignaciones y ningún punto y coma. Los espacios y saltos de línea permiten separar código legible; un operador puede continuar una expresión en otra línea. Los identificadores usan letras ASCII, números y guion bajo; no comienzan con un número.

```tscr
// Comentario de línea
/* Comentario de bloque */
const baseUrl: String = "http://127.0.0.1:8765"
```

Los strings usan comillas dobles y escapes JSON. `${expresión}` interpola una expresión; las llaves anidadas dentro de interpolación no están soportadas. Regex: `r"patrón"`, con sintaxis compatible con Python.

## Variables y tipos

```tscr
var count: Int = 0
count = count + 1
const label: String = "smoke"
var optionalName: String? = null
var names: List[String] = ["Angel", "Denis"]
var metadata: Map[String, Any] = {owner: "QA", attempts: 2}
```

Tipos disponibles: `String`, `Bool`, `Int`, `Float`, `Number`, `Any`, `Void`, `Path`, `Regex`, `Locator`, `List[T]`, `Map[K, V]` y records declarados. `?` permite null. `List` requiere un parámetro y `Map` dos. `Number` acepta enteros/decimales, no booleanos.

Las anotaciones de variables son opcionales. El checker infiere la información disponible; valores `Any` se validan al asignarlos a campos, parámetros o bindings tipados. JSON/CSV externos requieren validación en ejecución. Los bindings de módulo deben usar `const`; los `var` mutables pertenecen a bloques.

`const` impide reasignar el nombre. No hay asignación a elementos de listas/maps/records. El ámbito es léxico; una asignación actualiza el binding mutable visible más cercano.

## Records

```tscr
record User { name: String age: Int? }
test "Read user fields" {
    var user: User = User(name: "Angel", age: null)
    expect user.name == "Angel"
    expect user["age"] == null
}
```

Proporciona todos los campos, incluso los nullable. Campos faltantes, desconocidos o con tipos incorrectos generan diagnósticos o errores de ejecución.

## Funciones y flows

```tscr
fn increment(value: Int) -> Int { return value + 1 }
flow verifyCount(value: Int) { expect increment(value) > value }
```

Los parámetros requieren tipo. El retorno anotado es opcional (`Any` por defecto) y se comprueba en ejecución. Puedes usar argumentos posicionales y nombrados; los posicionales van primero. No hay parámetros por defecto o variádicos. `return expresión` se permite solamente dentro de `fn`/`flow`.

## Condiciones e iteración

```tscr
var total: Int = 0
for each item in [1, 2, 3] { total = total + item }
if total == 6 { expect true } else { expect false }
```

`for each` recorre listas, claves de maps y caracteres de strings. Crea un binding por iteración. `while`, `break`, `continue` y el atajo `else if` no están implementados; puedes anidar `if` dentro de `else`.

## Expresiones

Aritmética: `+ - * / %`. Comparación: `== != < <= > >=`. Pertenencia: `in`, `contains`. Regex: `matches`. Lógica: `not`, `and`, `or`, con cortocircuito. Precedencia: postfix → unarios → multiplicación/división → suma/resta → comparación → and → or. Las comparaciones encadenadas comparan valores adyacentes.

```tscr
expect "Angel" matches r"^A.*l$"
expect "tester" in ["tester", "developer"]
expect "TestScript" contains "Script"
```

## Imports

```tscr
import { login } from "login-flow.tscr"
```

Son explícitos, nombrados y relativos al archivo importador. Solo se importan módulos `.tscr`. Se pueden importar records, funciones, flows, fixtures, constantes y datos. Los ciclos y declaraciones duplicadas son errores. Las dependencias del módulo original permanecen disponibles para sus funciones/fixtures. Imports Python, comodines y aliases no están soportados.

## Builtins

| Nombre | Uso |
|---|---|
| `len`, `str`, `int`, `float` | Longitud y conversiones |
| `abs`, `min`, `max`, `round` | Operaciones numéricas |
| `Path("ruta")` | Ruta relativa al módulo que la declara |
| `css`, `xpath` | Locators Web |
| `load` | Carga local CSV/JSON/YAML |
| `env` | Variable de entorno: String o null |
| `uuid` | Genera UUID String |
| `text`, `value`, `visible` | Observaciones Web |
| `api` | Namespace de métodos HTTP |

El lenguaje no expone atributos arbitrarios de Python ni ejecuta código Python.
