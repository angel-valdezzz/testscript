# Tu primera prueba

Guarda este programa como `hello.tscr`:

```tscr
flow verifyName(name: String) {
    step "Validate the name" {
        expect len(name) > 0
    }
}

test "A valid user" tags ["smoke"] {
    verifyName("Angel")
}
```

1. `test` declara un caso que descubre el runner.
2. `flow` agrupa comportamiento reutilizable.
3. `step` crea una sección legible en los eventos de ejecución.
4. `expect` exige una expresión booleana y falla cuando es falsa.
5. `tags` agrega metadatos para seleccionar casos.

```bash
tscr check hello.tscr
tscr list hello.tscr --tag smoke
tscr run hello.tscr --tag smoke
```

`check` revisa sintaxis, nombres, información disponible de tipos y restricciones de efectos. No abre navegadores ni envía requests. Lee los módulos importados y datos locales, y puede evaluar inicializadores puros.

## Observa un fallo

Cambia la llamada por `verifyName("")`. La assertion falla, el caso queda fallido, el proceso termina con código 1 y los resultados conservan la ubicación del error.

## Compón comportamientos

Un flow puede llamar otros flows. Las funciones `fn` calculan valores sin interactuar con el sistema bajo prueba. Usa flows para Web/API y funciones para transformar datos. Las acciones directas dentro de tests están permitidas; el linter opcional fomenta extraerlas a flows.

Continúa con los [conceptos](concepts.md), la [guía del lenguaje](language.md) y los [ejemplos completos](examples.md).
