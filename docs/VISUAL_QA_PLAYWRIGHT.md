# Validación visual y funcional con Codex CLI + Playwright

ArbitraDocs Web se desarrolla en Visual Studio Code. Codex CLI debe usar Playwright para **abrir la aplicación real** en un navegador, comprobar su funcionamiento y revisar las capturas; no basta con editar JSX/HTML/CSS y afirmar que se ve bien.

## Ciclo obligatorio tras cualquier cambio en la interfaz

1. Inspeccionar el proyecto existente, instalar dependencias declaradas y arrancar **solo en localhost**. La versión actual de arranque usa `http://127.0.0.1:8000`; si se migra a Next.js, documentar el nuevo puerto, comandos y el proceso webServer para Playwright.
2. Usar Playwright con Chromium y al menos tres tamaños representativos: escritorio 1440 × 900, tableta 768 × 1024 y móvil 390 × 844. Probar tanto una página inicial como la herramienta modificada.
3. Guardar capturas de **pantalla completa** (por ejemplo en `web/test-results/visual/`) y **abrir/inspeccionar sus píxeles** mediante la capacidad visual realmente disponible para Codex. Si Codex no puede verlas, explicar el límite y mostrar/entregar las capturas; no afirmar que las inspeccionó.
4. Verificar que no hay texto recortado, columnas desbordadas, scroll horizontal inesperado, botones superpuestos, elementos fuera de pantalla, contrastes deficientes ni errores en la consola. Asegurar estados inicial, hover/focus, carga, error, vacío y finalizado donde apliquen.
5. Probar funciones mediante interacción real: elegir una herramienta, subir PDFs sintéticos de prueba, reordenar si existe UI, ejecutar proceso, comprobar el resultado descargable. No usar expedientes de clientes. Las herramientas todavía no operativas deben figurar como próximas, sin botones engañosos.
6. Si se detecta un defecto, corregirlo y **volver a ejecutar** Playwright. Repetir hasta quedar sin defectos conocidos o informar bloqueos concretos. No cambiar el motor de procesamiento solo para corregir estilos.
7. Ejecutar las pruebas backend relevantes (actualmente `python -m pytest tests -q` dentro de `web/`) y pruebas E2E antes de proponer commit. Reportar comandos y resultados reales.
8. No actualizar automáticamente líneas base de pruebas visuales: primero comparar, entender cambios y aprobar diferencias deliberadas. Las pruebas de captura por sí solas no garantizan calidad estética.

## Criterios de diseño

Identidad **original** de ArbitraDocs: moderna, clara, usable, profesional y consistente. Smallpdf, iLovePDF o PDF Candy son referencias de flujo de tareas, **no** de copiar colores, gráficos, composición exacta, logotipos o textos.

Mantener componentes reutilizables, tokens de colores/espaciado/tipografía, navegación accesible por teclado, etiquetas para entradas, feedback de carga/errores y diseño adaptativo. Dar prioridad a la experiencia de subir → configurar → procesar → previsualizar → descargar/guardar.

## Preparación de Playwright

Codex debe detectar primero si ya existe Playwright en `web/`. Si no lo hay, configurar un proyecto de pruebas E2E apropiado (por ejemplo, `@playwright/test` con `playwright.config.ts`) y registrar los comandos en `web/README.md`. En CI, usar servidor de pruebas local con `webServer` y puertos aislados.

Playwright automatiza el navegador, pero **no** sustituye análisis visual de capturas, pruebas de usabilidad, accesibilidad ni verificación del PDF generado. Usar aserciones de DOM y estados + inspección visual + pruebas del documento de salida.

## Seguridad y alcance

- Nunca exponer en Internet el prototipo sin autenticación, aislamiento de archivos y controles de seguridad.
- No subir PDFs reales, tokens, credenciales, capturas con datos personales ni archivos de `.local-data` al repositorio.
- No incorporar funciones que el usuario descartó en `AGENTS.md`.
- No publicar cambios ni fusionar ramas sin aprobación explícita.
