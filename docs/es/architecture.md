# Arquitectura

TestScript separa semántica del lenguaje y motores de automatización.

| Capa | Módulo | Responsabilidad |
|---|---|---|
| Sintaxis | `grammar.lark`, `parser.py` | Gramática, árbol y ubicaciones de origen |
| Valores | `model.py` | Tipos, records, callables y entornos léxicos |
| Validación | `analysis.py` | Nombres, diagnósticos, efectos y linter |
| Ejecución | `runtime.py` | Módulos, instrucciones, fixtures y ciclo de tests |
| Providers | `adapters/http.py`, `adapters/web.py` | HTTPX y motores Web opcionales |
| Resultados | `reporting.py` | Eventos a HTML/JSON/JUnit |
| Interfaz | `cli.py` | Descubrimiento, configuración, filtros y salida |
| Documentación | `highlighting.py`, `docs/` | Resaltado nativo y guías bilingües |

## Python + Lark

Python aporta empaquetado y acceso a librerías maduras. Lark permite una gramática explícita. El intérprete ejecuta directamente un árbol con ubicaciones. No hay transpilación ni IR separado en v0.2; se evaluará un IR cuando exista una necesidad concreta.

## Contrato de providers

Los adaptadores Web comparten navegación, acciones, observaciones, capturas y cierre. El runtime crea una instancia lazy por caso. HTTP devuelve maps nativos. Los providers no administran ámbitos, tipos, etiquetas o estado de tests.

## Eventos

El runtime emite steps, flows, logs, assertions, URL/status HTTP, fases de fixtures y capturas. Los reportes consumen eventos. Integraciones con Evidence Reporter/Request Reporter deberán usar un contrato estable; no son dependencias de este MVP.

## Verificación

Pruebas de sintaxis, tipos/nombres, imports, datos, excepciones, cleanup, etiquetas, CLI, escaping HTML y HTTP local. Contratos Web con pruebas unitarias; integración real contra formulario controlado mediante Playwright/Selenium. CI compila ambos idiomas y wheel/sdist.
