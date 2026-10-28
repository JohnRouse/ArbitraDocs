# ArbitraDocs Web — centro de actividad persistente y encadenamiento de herramientas

**Estado:** requerimiento de producto aprobado conceptualmente el 27/10/2026; diseño/especificación, NO implementación ni validación de backend. La rama remota puede no contener cambios locales recientes de Codex. No sobrescribir archivos locales.

## Objetivo

Que una conversión, compresión, OCR, foliación u otra herramienta pueda continuar mientras la persona navega a otra sección de ArbitraDocs. Al completarse, que pueda descargar, guardar o **usar el PDF resultante en otra herramienta sin cargarlo de nuevo**. Es una característica central del producto, no un simple toast o overlay.

## Experiencia de usuario — flujo principal

1. Subir/seleccionar PDF → abrir herramienta (p. ej. Comprimir) → configurar → «Comprimir PDF».
2. Al iniciarse el trabajo, la página presenta estado y ofrece «Seguir explorando». En navegación posterior aparece un **panel flotante no modal de actividad**, acoplado a la esquina inferior derecha en escritorio.
3. El panel compacto muestra icono de tarea, nombre truncado con tooltip/nombre accesible, estado real («En cola», «Procesando», «Terminado», «Error»), porcentaje **solo** si backend comunica medidas veraces, botón «Ver trabajo» y control «Minimizar».
4. Si existen varios trabajos, mostrar un resumen («2 en proceso · 1 listo») y permitir expandir la lista, sin apilar notificaciones invasivas.
5. Al completarse, el panel cambia a estado «Listo», permanece accesible (o se minimiza al centro de actividad), informa el resultado y ofrece **«Descargar»** y **«Usar en otra herramienta»**.
6. «Usar en otra herramienta» abre selector de herramientas compatibles, conservando el resultado **por ID de archivo en servidor**, sin segunda subida. Ejemplo: `Original.pdf → Comprimir → Proteger → Foliar → Descargar`. Cada etapa genera una nueva versión; original intacto.
7. Historial de trabajos y resultados en `/app/historial` y biblioteca, sujeto a política de retención. Permitir volver a abrir el resultado desde la herramienta y desde el panel flotante.
8. Si falla, mostrar explicación segura, sugerencia de reintento y salida para recuperar el original. Nunca cerrar automáticamente un estado de error significativo.
9. Móvil: en vez de panel flotante ancho que tape el contenido, usar pill discreta sobre navegación inferior, expandible como hoja/modal accesible. Considerar safe-area, tamaño táctil, teclado y «reduced motion».
10. El panel es **no modal**: no bloquea la web, no interrumpe scroll, enlaces ni formularios. Accesible por teclado, `aria-live` para cambios importantes sin anuncios excesivos.

## Arquitectura para que funcione de verdad

- Trabajos **persistentes del lado servidor**, no Promises dentro del componente frontend. `POST /api/jobs` devuelve `job_id` enseguida (respuesta 202), persistiendo dueño, entrada, herramienta, configuración validada y estado `queued`.
- Worker separado (Celery/RQ/Arq u otra cola adecuada) procesa en segundo plano. Base de datos almacena `Job` (ID, propietario, herramienta, input_file_ids, output_file_ids, estado, progreso real opcional, timestamps, error sanitizado, cancelable) y `FileAsset` (ID, owner, objeto privado, tipo, tamaño, páginas, expires_at, lineage).
- Actualización cliente vía SSE/WebSocket con reconexión, o polling con intervalos/backoff en primera fase. Recuperar todos los trabajos activos con `GET /api/jobs?status=active` tras navegar, recargar página o reabrir la pestaña.
- UI global montada en layout raíz (`ActivityDock`) y alimentada por estado compartido de tareas/consulta servidor, independiente de rutas de herramientas. Al terminar, actualizar resultado persistido en la API.
- El cambio de herramientas entrega **`file_id` del resultado**, sin retransmitir los bytes. Validar compatibilidad de tipo/firma y permisos en backend, incluso si el cliente cambia IDs.
- Entregar archivos mediante URLs autenticadas o firmadas y de vida corta, nunca rutas locales, objeto key visible o enlaces públicos permanentes.
- Aislar cada job por usuario, límites concurrentes, cuotas y tamaño, timeouts, cleanup de temporales, reintentos seguros e idempotencia para no duplicar procesamientos. «Cancelar» solo cuando el worker pueda respetarlo: cancelación cooperativa, sin prometer que puede interrumpirse cualquier proceso.
- Si el usuario cierra el navegador, el trabajo **debe seguir en el servidor** y reaparecer al iniciar sesión, siempre que la infraestructura de workers esté operativa; no afirmar esta capacidad en el actual prototipo local. Si se cae/reinicia el servidor, estado y cola deben sobrevivir con almacenamiento durable.
- Para uso sin login, considerar retención efímera y token de sesión seguro según el producto definitivo; no prometer continuidad entre dispositivos sin autenticación.
- Restringir acceso por `owner_id` en cada operación: job, asset, resultado, reuso, cancelación, borrado. Nunca mostrar otros usuarios o PDF internos en panel admin. Tratar documentos sensibles con cifrado, privacidad y políticas de retención.

## Estados y progreso

Máquina mínima: `queued → running → succeeded | failed | canceled` con etapas opcionales solo si se emiten desde backend. Los porcentajes de carga pueden derivarse de bytes de transferencia reales; el procesamiento puede ser indeterminado. No simular 20, 50 y 100 % por temporizador. Evitar ETA ficticia. Si no hay porcentaje, spinner/animación discreta y texto honesto. Estado `succeeded` únicamente tras verificar el resultado almacenado y descargable.

## Composición visual minimalista

- Desktop: ActivityDock abajo a la derecha (margen 24px); ancho ~320–360px. Tarjeta compacta y expandible, borde y sombra suaves, icono y nombre; movimiento fade/translate 6px ~180ms al cambiar estado.
- Ícono de campana/actividad en header con badge pequeño de tareas activas, y acceso a «Centro de actividad» y «Historial» para no depender solo del flotante.
- No usar modales bloqueantes salvo confirmación de acciones irreversibles. No acaparar foco al comenzar/terminar trabajo. Animación de éxito corta (200ms); accesibilidad y `prefers-reduced-motion`.
- El Dock nunca debe tapar una descarga, formulario, botón de acción o la barra de navegación; en resoluciones pequeñas se compacta.
- En carga/proceso largo, mantener indicador en la pantalla de la herramienta cuando se permanece allí; panel flotante se activa al navegar, sin crear dos elementos redundantes.
- «Usar en otra herramienta» es llamada de acción central y debe existir también en página de resultado e historial.

## Orden de implementación y dependencia técnica

1. Ahora: diseñar y prototipar `ActivityDock`, centro de actividad y UI de «Usar en otra herramienta» con datos ficticios **claramente etiquetados**; probar navegación responsive y estados con Playwright.
2. Antes de afirmar continuidad real: introducir API de trabajos, cola/worker, almacenamiento de archivos con IDs, persistencia y estados reales; conectar ActivityDock con backend.
3. Añadir reuso de resultados mediante referencias por ID, historial y biblioteca por propietario.
4. Solo después habilitarlo para otros usuarios con autenticación/aislamiento real y cuotas. Mantener los algoritmos PDF actuales y las exclusiones de herramientas en AGENTS.md.

## Pruebas obligatorias Codex + Playwright

- Iniciar un job lento sintético, navegar Inicio → Herramientas → Archivos, verificar que el Dock permanece y cambia de posición/forma correcta.
- Abrir/cerrar panel, navegar con teclado, `aria-live`, `prefers-reduced-motion`, 1440×900 / 768×1024 / 390×844; comprobar ausencia de overlays y scroll horizontal.
- Recargar página con trabajo activo y reconectar al mismo `job_id` (una vez construido backend).
- Completar job y usar output en una herramienta diferente **sin solicitud de segunda subida**; comprobar contenido del PDF generado y trazabilidad del original.
- Dos trabajos concurrentes; errores, reintentos, cancelación admisible, reconexión intermitente, expiración del archivo.
- Test de autorización: cuenta A no puede usar, descargar ni consultar el resultado/job de B, incluso manipulando IDs.
- Capturar y **abrir/inspeccionar** screenshots; documentar alcance y limitaciones reales. Sin push/merge salvo autorización.

Este diseño es distinto de la animación introductoria con HyperFrames, tratada en `docs/WEB_INTRO_AUTH_ADMIN_V1.md`: el progreso requiere datos reales y un sistema persistente de trabajos.
