# ArbitraDocs — reglas de Codex

- Dirección actual: construir ArbitraDocs Web como suite web de herramientas PDF y documentales; conservar el proyecto WinUI 3 existente sin eliminar su código.
- `web/` es un prototipo local mientras no existan autenticación, autorización, cifrado, límites de recursos, retención y seguridad. No desplegar públicamente.
- No subir PDFs reales, credenciales, tokens, datos de clientes, bases de datos o temporales a GitHub.
- Documentar cada nueva herramienta. «Disponible» solo si existe un endpoint funcional probado.
- Pruebas de regresión obligatorias para PDF con rotaciones 90/180/270, normalización A4, folios, orden de ZIP/RAR y seguridad de rutas al incorporar esas funciones.
- Mantener endpoints API estables al mejorar diseño; usar navegador y Playwright con servidor local.
- Ejecutar pytest antes de commits; evitar cambios del motor documental innecesarios al rediseñar UI.
- No fusionar a main ni publicar una nueva versión sin aprobación explícita.

## Decisiones de alcance — NO construir en la web

No volver a agregar al catálogo, roadmap ni interfaz: Analizar expediente; Detectar anexos desde el escrito; Preparar escrito + anexos automáticamente; Ordenar anexos por nomenclatura; Inventario documental independiente; Ubicación de contratos, cláusulas y comprobantes. Siguen en alcance el mapeo visual de archivos/carpetas, ZIP/RAR para unión, foliación, certificación y normalizar nombres. No borrar código legado WinUI por esta instrucción.

## Flujo de desarrollo visual obligatorio

Todos los cambios de diseño en ArbitraDocs Web deben pasar por un ciclo local Codex CLI + Playwright: levantar web en localhost, probar en escritorio/tableta/móvil, generar capturas reales, **inspeccionarlas visualmente**, corregir defectos y repetir la prueba. También revisar consola, flujos de carga/proceso/descarga y backend. No afirmar que se inspeccionaron capturas si el entorno no permite verlas. Usar únicamente PDFs de prueba sintéticos. Mantener diseño original, no copiar sitios competidores. Leer `docs/VISUAL_QA_PLAYWRIGHT.md` antes de modificar frontend. Los resultados de Playwright y `.local-data` no se suben al repositorio.

## Rediseño visual actual (octubre de 2026)

Antes de cambios visuales de la web, leer `docs/WEB_VISUAL_REDESIGN_V2.md` y `docs/VISUAL_QA_PLAYWRIGHT.md`. Aplicar experiencia minimalista premium, microinteracciones útiles y estados reales de subida/procesamiento/resultado. No añadir HyperFrames como motor runtime (sirve para composición de video, no interacción de web). **El código web funcional más reciente está localmente y puede no existir todavía en la rama remota; inspeccionar cambios locales y respaldarlos antes de editar.** No hacer push ni merge sin aprobación.

## Intro de marca y portales por rol

Aplicar las decisiones de `docs/WEB_INTRO_AUTH_ADMIN_V1.md`: posible animación inicial con HyperFrames (sin bloquear la web, opción reducida/estática), tres áreas públicas/de usuario/admin; los prototipos de cuenta/panel no son autenticación real. Antes de producción exigir roles autorizados server-side, biblioteca por propietario, MFA para admin, seguridad y auditoría. Preservar y respetar cambios locales no publicados.

## Centro de actividad global y cadena de herramientas

Aplicar `docs/WEB_ACTIVITY_DOCK_AND_PIPELINE_V1.md`: mientras un PDF se procesa, mantener job persistente en servidor; al navegar mostrar ActivityDock no modal en esquina inferior derecha o compactado en móvil, con estado real y acceso a resultados. Ofrecer `Usar en otra herramienta` reutilizando `file_id` del PDF resultante sin subir de nuevo. No simular porcentajes ni continuidad backend que el prototipo actual no implementa. Prototipar UI y probar con Playwright; no bloquear navegación. Respetar permisos de usuario y retención de archivos.
