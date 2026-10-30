# ArbitraDocs Web — intro HyperFrames a pantalla completa (decisión V2)

**Decisión del propietario — 29/10/2026.** Esta especificación **sustituye** el planteamiento anterior de intro incrustada en la tarjeta derecha del hero en `docs/WEB_INTRO_AUTH_ADMIN_V1.md`. La animación ya implementada en local (composición 3,8 s, poster, player 0.8.214) debe **reutilizarse**, no reescribirse de cero.

## Experiencia visual obligatoria

1. Al entrar por primera vez en la sesión a la portada, aparece una **capa de bienvenida a pantalla completa**, ocupando todo el viewport (incluidas las esquinas, no solo el hero). Está **por encima del header, sidebar, tarjetas y footer**: no se debe ver el inicio ni una tarjeta a la derecha durante la presentación.
2. Fondo limpio y profesional (considerar tinta azul oscuro `#111C31` o el color brand acordado), hojas PDF que se agrupan y forman el icono original, aparición de `ArbitraDocs` y lema `Documentos, sin complicaciones.`. Composición centrada y fluida con tipografía/cromática de la marca, diseño responsive y espacio de seguridad para móviles/notch. No copiar animaciones de otras marcas.
3. Mantener la animación HyperFrames actual de aproximadamente 3,8 s o ajustarla para ritmo más ágil. Terminar con **transición de salida** de 250–450 ms que revela el home ya renderizado, sin parpadeo ni cambio brusco de scroll.
4. Control `Omitir presentación` visible desde el primer momento, accesible por teclado y pantalla táctil. No exigir esperar a descargar/importar el reproductor para omitir.
5. Solo reproducir una vez por sesión, cuando la visita comienza en Inicio; no volver a reproducir al navegar, usar herramientas, recargar o regresar a la portada. Si usuario tiene `prefers-reduced-motion: reduce`, mostrar la web inmediatamente con marca estática, sin overlay animado.
6. Si player/assets fallan, expiran o tardan demasiado, **el home debe mostrarse inmediatamente** sin bloquearse en pantalla oscura. Se debe poder pulsar Escape para omitir opcionalmente; limpiar timers, event listeners, animaciones y desmontar player.
7. Mientras se muestra la intro, evitar clics accidentales en contenido posterior y scroll del body, pero conservar acceso al botón de omitir. Tras salir, liberar scroll y devolver el foco a un elemento útil del contenido principal. No generar anuncios repetitivos para lector de pantalla. Nunca mostrar porcentajes falsos de carga.
8. La landing debe estar renderizada debajo del overlay, con carga de datos independiente; la intro es **presentación de marca, no una condición para que el servidor funcione ni una barra de progreso real**.
9. **Eliminar la dependencia visual del hero derecho con la animación**: tras terminar, no debe quedar el póster de HyperFrames como tarjeta permanente. Reemplazar esa superficie por una demostración estática/ligeramente interactiva de flujo PDF (archivo → herramienta → resultado) o rediseñar el hero equilibrado; no duplicar logo/título en la mitad derecha.
10. Para tablets y móviles: overlay `position: fixed; inset: 0; width: 100vw; height: 100dvh` (con fallback apropiado), contenido centrado, safe-area y controles accesibles. Evitar desbordamiento, barras oscuras y letras excesivamente pequeñas. Usar un root único y gestión explícita de `z-index` y foco.

## Implementación recomendada (según stack local real)

- Revisar primero `web/client/intro.js`, `web/client/index.html`, CSS, composición y pruebas Playwright **locales sin publicar**. Conservar toda la validación previa de 80 E2E / 14 backend.
- Reutilizar `@hyperframes/player` empaquetado localmente y la composición ya probada. Cambiar el contenedor de tarjeta por overlay global sin reinstalar ni rediseñar innecesariamente la composición.
- Usar `opacity`, `visibility` y `pointer-events` para la salida sin saltos de layout. `position: fixed` y overlay aislado del grid de inicio. Evitar conflictos `hidden` versus estilos CSS.
- Mantener un elemento logo/poster como fallback dentro del overlay mientras carga, no dejarlo en el hero final.
- Si la navegación o los permisos de automatización impiden el cambio, detallar bloqueos. No declarar realizado sin probarlo.

## Pruebas Playwright necesarias

- Primera navegación a Inicio en sesión limpia: captura inicial, frames intermedios y final; verificar overlay cubre **todo el viewport** en escritorio 1864×957 y 1440×900, tablet 768×1024 y móvil 390×844.
- Sin fugas del hero/header/sidebar detrás durante la bienvenida; salida con reveal suave y sin CLS sustancial.
- `Omitir` funciona mientras aún carga player; `prefers-reduced-motion` omite; reload/segunda navegación no repiten; foco/scroll restaurados; página disponible ante fallo intencional de asset.
- Verificar que la animación ocupa todo el área, centrado escalado, sin líneas negras ni recortes; comparar capturas y **abrirlas visualmente**.
- Regresión de operaciones PDF (unir, extraer, girar, subir, biblioteca y descargar), 14 backend y E2E previos; verificar adaptaciones de las pruebas que suponían intro en card.
- Registrar tiempos reales, estado de carga/primer render, errores de consola y límites. No publicar cambios ni hacer push/merge sin autorización.

**Nota:** `docs/WEB_INTRO_AUTH_ADMIN_V1.md` y `docs/WEB_VISUAL_REDESIGN_V2.md` definen el resto del producto. Para la ubicación de la animación, **esta decisión V2 tiene prioridad**.
