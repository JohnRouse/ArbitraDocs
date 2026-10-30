# ArbitraDocs Web — bienvenida animada, acceso y paneles por rol

**Estado:** especificación funcional y visual para Codex CLI. No supone que autenticación, almacenamiento multiusuario ni administración estén implementados. Conservar el prototipo local y las herramientas PDF operativas.

## 1. Visión

Tres espacios con identidad visual coherente y responsabilidades distintas:

1. **Sitio público:** bienvenida visual, explorador de herramientas PDF, páginas de herramientas, ayuda y acceso a la cuenta. Proponer acceso anónimo a las herramientas sencillas (sin biblioteca persistente) como decisión de producto pendiente de aprobación.
2. **Espacio personal del usuario:** cuenta, biblioteca privada, resultados, historial, almacenamiento y configuración.
3. **Administración (solo rol admin):** usuarios, estado de trabajos, uso de recursos, almacenamiento agregado, disponibilidad/configuración de herramientas, métricas y auditoría.

No incluir análisis automático de expedientes, búsqueda de anexos, inventario documental ni detección de contratos/pagos descartados en AGENTS.md.

## 2. Animación inicial: HyperFrames

### Concepto: «Los documentos toman forma»

- 0.0–0.6 s: tres trazos/hojas de documento entran desde direcciones suaves.
- 0.6–1.4 s: las hojas se alinean y componen el símbolo original de ArbitraDocs.
- 1.4–2.1 s: aparece «ArbitraDocs» y el lema «Tus documentos, sin complicaciones».
- 2.1–2.5 s: transición de opacidad hacia el hero y su buscador de herramientas.

**Decisión V2 (29/10/2026):** El propietario confirmó que la animación debe ocupar **toda la pantalla como presentación inicial**, NO un cuadro del hero. Reutilizar la composición existente mediante un overlay global, con opción visible «Omitir», salida fluida y respeto a movimiento reducido. No bloquear indefinidamente ni retrasar la carga funcional de la web. Ver `docs/WEB_FULLSCREEN_INTRO_V2.md`, que prevalece sobre la anterior preferencia.

HyperFrames admite crear composiciones HTML y renderizarlas a MP4/WebM; también ofrece `@hyperframes/player` para embeber composiciones. Codex debe investigar ambas alternativas, probar rendimiento y elegir la más ligera y compatible. Composición original; no usar plantillas visuales idénticas a competidores. Referencia: https://hyperframes.app/docs/5-packages/player y https://hyperframes.app/docs/3-guides/4-rendering.

Reglas:
- Primera visita en una sesión como máximo; navegación interna nunca debe reiniciar la presentación.
- Sin audio automático. No descargar video grande antes de mostrar contenido principal.
- `prefers-reduced-motion: reduce` → logo estático e inmediato.
- Si faltan recursos, mostrar logo estático sin pantalla negra, salto de contenido o bloqueo.
- Probar interacción y rendimiento en móvil/tableta/escritorio; verificar impacto en LCP/INP.
- El estado «cargando» del archivo/proceso PDF no debe confundirse con la intro de marca.

## 3. Arquitectura de navegación propuesta

### Público
`/`: landing + animación; `/herramientas`: catálogo; `/herramientas/<slug>`: operación individual; `/acceder`: inicio de sesión; `/registro`: crear cuenta; `/recuperar-acceso`: restablecer; `/privacidad`, `/ayuda`.

### Usuario autenticado
`/app`: resumen personalizado; `/app/archivos`: biblioteca propia; `/app/historial`: trabajos y resultados; `/app/cuenta`: configuración/seguridad; `/app/almacenamiento`: uso y cuota.

### Administrador
`/admin`: indicadores generales (usuarios, tareas, errores, carga, capacidad);
`/admin/usuarios`: búsqueda, roles y estado;
`/admin/trabajos`: cola y errores técnicos;
`/admin/herramientas`: estado/flags/activación;
`/admin/almacenamiento`: indicadores agregados, políticas y limpieza;
`/admin/auditoria`: actividades administrativas relevantes;
`/admin/configuracion`: límites, avisos y ajustes permitidos.

No mostrar administrador en navegación de usuarios corrientes. **Ocultar enlaces no constituye seguridad**: aplicar autorización de servidor en cada ruta, acción y archivo.

## 4. Identidad y permisos

Proponer roles iniciales:
- `visitor`: páginas públicas; PDF anónimo únicamente si se decide habilitarlo.
- `user`: solo sus propios documentos, procesos, resultados y datos de perfil.
- `admin`: administración de plataforma sin lectura por defecto de contenidos privados de otros usuarios.

Provisionar la cuenta admin mediante configuración segura del servidor, **nunca** mediante registro público, variable JS del cliente, credenciales fijas o cambio de rol manipulable. MFA obligatorio para administrador; sesiones protegidas (cookies Secure/HttpOnly/SameSite y CSRF, según arquitectura). Denegar por defecto y comprobar permisos en cada operación de API, almacenamiento y trabajos. Documentos cifrados, buckets privados y descargas temporales. Logs con metadatos mínimos; no registrar contenido PDF ni datos confidenciales de expedientes.

Antes de exponer la web en Internet, implementar usuarios reales, almacenamiento multiusuario segregado, cuotas y límites de carga, validación/antivirus, workers aislados, rate limiting, retención y eliminación, auditoría y tests de escalada de privilegios. El prototipo local **no** tiene estas defensas completas: no desplegarlo públicamente.

## 5. Diseño de los paneles

### Login y registro
Composición limpia en dos columnas desktop, una columna móvil; marca y fondo discreto, formulario central, mostrar/ocultar contraseña, estado de carga/error, restablecer, textos de privacidad claros. No hacer obligatorio login para ver catálogo público.

### Usuario
Espacio cálido y organizado, sin saturación de gráficas: sección «Tus archivos», trabajos recientes, acciones rápidas, cuota y búsqueda, miniaturas opcionales y vista previa real. Visibles solo datos del usuario.

### Administrador
Superficie algo más densa, pero del mismo sistema de diseño. Estadísticas con números reales, filtros y paginación en usuarios/trabajos, estados de carga/vacío/error, confirmación de acciones sensibles, eventos auditados. No presentar métricas ficticias como reales; mocks solo en desarrollo etiquetados.

## 6. Orden de implementación

1. **Primero:** rediseño de landing y prototipo HyperFrames para intro; Playwright + capturas, métricas y prueba de movimiento reducido.
2. **Después:** maquetas navegables de acceder/registro, usuario y admin **claramente marcadas como demo**, sin iniciar sesión ficticia que dé apariencia de seguridad.
3. **Antes de usuarios reales:** elegir proveedor y modelo de autenticación y almacenamiento; construir aislamiento y pruebas de acceso, invitación inicial del admin y MFA.
4. **Luego:** panel de usuario real, biblioteca individual y trabajos.
5. **Por último:** administración efectiva con auditoría/roles, indicadores reales y controles protegidos.

## 7. Verificación Codex/Playwright

- Capturas en 1440×900, 768×1024 y 390×844; introducción y hero final, login, biblioteca y panel admin.
- Comprobar intro solo primera navegación, opción omitir si aplica, no reproducción para `prefers-reduced-motion`, sin sonido, caída elegante si falta media.
- Probar accesibilidad de formularios, error y validación, foco visible y navegación con teclado.
- Cuando exista auth real: usuario A no debe obtener PDF de usuario B aunque conozca ID; usuario corriente no puede ejecutar rutas admin por API directa; sesión caducada no accede. Los E2E visuales **no sustituyen** estos tests backend.
- Informar tiempos de carga, assets de intro y resultados verdaderos; no prometer éxito sin pruebas ejecutadas.
- No borrar trabajo local de Codex ni hacer push/merge sin aprobación.

Referencia de seguridad: https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html y https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html.
