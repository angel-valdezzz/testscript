# Historial de cambios

## 0.2.0 — 2026-10-07

- **Incompatible:** sustituye `api.*` por HTTP declarativo: `POST url { headers {...} query {...} body json payload }`. Sin opciones usa `GET url {}`; se conservan los campos de respuesta.
- Comas opcionales entre propiedades de mapas, incluyendo el cuerpo JSON.
- Selección de navegador, perfiles privados/normales temporales, viewport y maximización visible con validación de configuración.
- Más ejemplos de API/naming/returns, referencia bilingüe, logo unificado, badges de versión/CI y paletas clara/oscura.
- La nueva dirección visual de landing está en revisión; no forma parte de esta versión.


## 0.1.0 — 2026-10-07

Implementación experimental inicial: gramática `.tscr`, intérprete Python/Lark, CLI, records y contratos tipados, flows reutilizables, fixtures por caso, datos parametrizados, tags, excepciones básicas, Playwright/Selenium opcionales, API HTTPX, resultados HTML/JSON/JUnit y documentación EN/ES.

Publicación de la distribución pendiente. Consulta [roadmap](roadmap.md) y [especificación](specification.md).
