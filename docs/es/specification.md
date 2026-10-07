# Especificación TestScript v0.2

**Estado:** contrato experimental de implementación. La gramática ejecutable está en `src/testscript/grammar.lark`. Esta referencia describe lo soportado; las propuestas se mantienen en el roadmap.

## Estructura

Un módulo es un `.tscr` UTF-8 con imports, records, funciones, flows, fixtures, tests, datos y constantes. Las acciones arbitrarias en la raíz son inválidas. Imports y declaraciones se resuelven antes de ejecutar tests. Los inicializadores se evalúan en orden: leer una constante posterior es inválido. Se rechazan ciclos de imports.

Tests son las únicas unidades descubiertas. Cada fila de datos expande un caso independiente. La ejecución es secuencial y no hay async/await. Tests no llaman tests; flows llaman flows/funciones; funciones no llaman flows ni builtins con efectos.

## Gramática

Identificadores: `[A-Za-z_][A-Za-z0-9_]*`, sensibles a mayúsculas. Strings con comillas dobles/escapes JSON; regex `r"..."`. Comentarios `//` y `/* ... */`. Llaves para bloques/maps. Sin punto y coma. Contenedores: `List[String]`, `Map[String, Any]`; nullable: `String?`.

```tscr
record User { name: String }
fn greeting(name: String) -> String { return "Hello ${name}" }
flow verify(user: User) { expect len(user.name) > 0 }
fixture session { setup { log "ready" } teardown { log "closed" } }
data users = [{name: "Angel"}]
test "User" tags ["smoke"] using [session] for each user in users {
    verify(User(name: user.name))
}
```

## Tipos y ámbitos

Los tipos/contratos se detallan en la [guía](language.md). Bindings de módulo constantes; bindings locales mutables con ámbito léxico. Los bloques no exportan variables, excepto setup: sus bindings exitosos se exponen al test. Los campos de records son inmutables desde el lenguaje.

El análisis estático tiene límites: resuelve nombres, firmas, tipos explícitos, campos conocidos y tipos básicos de expresiones. Datos dinámicos/maps y muchos builtins permanecen `Any`. Los contratos en ejecución cubren bindings, reasignaciones, campos, parámetros y retornos. Esta versión no promete verificación estática completa.

## Efectos y llamadas

`fn` calcula, construye records y llama funciones/builtins puros. `flow` interactúa con Web/API, observa, registra y valida. Checker/runtime rechazan efectos dentro de funciones. No se exponen atributos arbitrarios Python, callbacks o clases de usuario.

Parámetros tipados, sin defaults/variádicos. Argumentos nombrados únicos después de posicionales. Retorno opcional `Any`; un retorno anotado no-nullable no acepta null implícito. Se limitan las llamadas anidadas a 100.

## Fixtures y fallos

Scope por caso; setup según `using` y teardown inverso. Un fixture se registra para limpieza antes de iniciar setup. Entornos independientes con rutas relativas al módulo. Se comparten bindings exitosos; nombres exportados duplicados fallan.

Assertions fallidas marcan el caso incluso si se capturan. Errores operativos capturados pueden manejarse; errores pendientes/de limpieza fallan el caso. Skip conserva fallos previos y ejecuta limpieza. Adaptadores se cierran al terminar teardown.

## Web y HTTP

Combinaciones proveedor/navegador de la guía Web con CSS/XPath. Las acciones esperan según el adaptador; las assertions evalúan una vez. HTTP soporta cuerpos JSON, maps headers/query, redirects e inspección. Status no-2xx son respuestas; fallos de transporte son errores.

## Selección y resultados

Tags solo en tests; inclusión/exclusión OR. Un resultado por test/fila. Estados passed/failed/skipped. HTML/JSON/JUnit. Códigos 0/1/2/5. Consulta la [CLI](cli.md).

## Exclusiones explícitas

Mobile, clases/interfaces/herencia, errores personalizados, task/page, callbacks, map/filter/reduce, paralelismo, async/await, formatter, LSP, imports comodín, scope suite de fixtures, retry automático de assertions, capturas automáticas e integraciones con librerías reporter no están implementados.

Cada cambio de contrato debe actualizar gramática/intérprete, regresiones, ejemplos y ambos idiomas.

La sintaxis HTTP es `METHOD url { headers map query map body json expression }`; cada sección opcional aparece una vez. Las comas de propiedades de mapas son opcionales; las de listas y argumentos siguen siendo obligatorias.
