# ArbitraDocs Web — rediseño profesional minimalista (brief de implementación)

**Estado:** especificación de diseño basada en 4 capturas enviadas por el propietario el 27/10/2026. No es un cambio de la UI ejecutable. La UI local contiene cambios aún no publicados; **inspeccionar los archivos locales antes de editar**, no sobrescribir ni asumir que la rama remota contiene el último código.

## Diagnóstico de capturas

1. **Inicio:** la ilustración y el hero tienen buena dirección, pero se ven contenidos dentro de un dashboard; demasiadas herramientas y biblioteca en una sola página producen scroll muy largo. El buscador de herramientas debería protagonizar la home. El texto en 1864px resulta pequeño.
2. **Herramientas:** muchas tarjetas idénticas, algunos iconos de estilos distintos, exceso de estados «Próximamente» y poca jerarquía; las funciones útiles no destacan lo suficiente. Chips de filtrado pequeños.
3. **Mis archivos:** zona de carga bien localizada pero con escaso protagonismo; estados de selección / procesamiento / resultado poco claros. Acciones de fila diminutas, iconos sin suficientes etiquetas y nombre largo de archivo con truncamiento potencial. La carga debería tener feedback visual y de estado real.
4. **Expedientes:** demasiado espacio vacío (solo cuatro tarjetas) y nomenclatura incoherente con el nuevo enfoque de herramientas PDF generales. Cambiar la etiqueta de navegación a **Herramientas avanzadas** o **Especializadas** y eliminar referencias a análisis de expedientes/anexos descartados. Mantener Foliar, Certificar, Mapear archivos y Normalizar nombres.
5. **Sistema común:** barra lateral fija domina la experiencia; fuente pequeña, baja densidad informativa en algunos lugares y alta en otros; demasiadas superficies/bordes y varios colores sin función semántica. El marcador «Prototipo» se mantiene solo en desarrollo.

## Principios

- Suite PDF general comparable en **facilidad de uso** con Smallpdf/iLovePDF/PDF Candy, sin copiar diseño, textos, gráficos o marca.
- Una acción principal por pantalla. Navegación clara y moderna; jerarquía tipográfica editorial; gran espacio respirable, pero evitar vacío sin propósito.
- Diseño sencillo, premium, calmado. NO glassmorphism intenso, gradientes arcoíris, confeti, partículas, animaciones invasivas o elementos decorativos sin función.
- UI responsive, teclado accesible, foco visible, etiquetas semánticas, contraste AA.
- Priorizar las tres herramientas funcionales (Unir, Extraer páginas, Girar) y dejar el resto visiblemente «En desarrollo» sin interacción engañosa.

## Tokens y componentes propuestos

Usar CSS variables y componentes reutilizables adaptados al stack local existente. No migrar a React por el simple deseo de animar.

- `--ink: #17243A`; `--muted: #637189`; `--brand: #325BEA`; `--brand-hover: #2249D1`.
- `--canvas: #F7F9FC`; `--surface: #FFFFFF`; `--border: #E4EAF2`; `--soft-brand: #EDF2FF`.
- Exito `#147D61`, error `#B83246`, advertencia `#966311`; colores de estado solo para feedback real.
- Fuente: **Manrope** en títulos y **Inter** en contenido, o una sola familia variable si el rendimiento pesa. Tamaño base 15–16 px; texto secundario ≥14 px; títulos de página 30–36 px desktop / 26–30 móvil; hero 42–52 desktop.
- Spacing: escala 4/8/12/16/24/32/48/64; área de lectura max-width 1200–1280 px; cards radius 14–16 px; botones radius 10–12 px; bordes finos y sombras discretas.
- Iconos: una sola familia SVG (p.ej. Lucide), trazos coherentes de 1.75–2; no mezclar emojis ni glifos tipográficos.
- Botón primario azul sólido y secundario blanco/borde; estados hover, active, focus-visible, disabled y loading.
- Preferir microtextos muy concretos y útiles; no subtítulos redundantes ni navegación «Expedientes» como sección principal.

## Estructura

### Inicio

- Cabecera liviana: logo, Herramientas, Mis archivos, Ayuda; botón «Subir PDF» visible. Sidebar compacta solo en la zona de trabajo; no convertir la landing en dashboard corporativo.
- Hero con titular humano: **Tus PDF, resueltos en pocos clics.** Subtítulo de una frase y CTA «Seleccionar archivos» + secundario «Explorar herramientas». Sostener el foco en el dropzone.
- Buscador de herramientas visible arriba, categoría/chips refinados.
- Primera fila de 3–6 herramientas disponibles y populares. Sección separada «Próximamente» discreta o catálogo completo con bloqueo visual claro.
- Sección breve de beneficios (sin sobrecarga), y «Tus archivos recientes» SOLO cuando existan y el usuario esté en espacio de trabajo. No duplicar una biblioteca íntegra en home.
- Ilustración de papeles sutil y opcional; no hacerla competir con el CTA.

### Catálogo de herramientas

- Título «Herramientas PDF», campo de búsqueda, filtros dinámicos; grid responsive 3 desktop, 2 tableta, 1 móvil. No cards excesivamente altas.
- «Disponibles» primero, «En desarrollo» después; estado de herramienta evidente sin contaminar con una etiqueta en TODAS las cards.
- Cada card: icono consistente 40 px, título 16–17 px, descripción una línea o dos, affordance para abrir solo si funciona.
- Reemplazar sección «Expedientes» por «Herramientas avanzadas» con las 4 permitidas.

### Biblioteca y página de operación

- Dropzone protagónico con icono y texto: «Arrastra tus PDF o selecciónalos»; indicar restricciones y privacidad *real* (local/dev o cloud según despliegue).
- Al añadir archivos, transición a lista visual de documentos con nombre legible, tamaño, páginas, miniatura de primera hoja cuando sea viable, eliminar/reordenar con etiquetas.
- Cada herramienta debe tener flujo separado y cohesivo: **Seleccionar → Configurar → Procesar → Resultado**. Permitir cambiar de fase y recuperar el estado de trabajo cuando sea razonable.
- Mostrar estado vacío, error de validación, carga, procesamiento, éxito y cancelación; evitar acciones grises ambiguas. Cuando haya un único archivo, no ofrecer «Unir» como acción principal si requiere 2.
- Resultados: icono claro de éxito, nombre, páginas/tamaño reales, CTA «Descargar PDF», CTA secundario «Guardar en mis archivos» solo si funciona.
- En móvil, ocultar sidebar o convertir a navegación accesible compacta, evitar toolbar horizontal y scroll lateral.

## Animación y transición (funcional, no decorativa)

**Primera elección para el stack actual FastAPI + HTML/CSS/JS:** CSS transitions, keyframes y Web Animations API. Si el frontend migra en otro proyecto a React, evaluar Motion for React; GSAP solo si las secuencias requieren más control. **HyperFrames está orientado a composiciones de video HTML→MP4; no usar como motor runtime de interacción.**

- Hover card: `translateY(-3px)`, borde y sombra apenas más perceptibles, 160–200 ms.
- Focus: anillo visible estático, nunca depender solo del hover.
- Navegación y cambio entre pestañas: fade + desplazamiento Y 4–8 px, 160–240 ms; transiciones no deben ocultar botones ni demorar interacción.
- Drag enter: borde brand, fondo azul muy pálido y ligero scale 1.005, 150–200 ms. Drag leave vuelve suavemente.
- Selección de archivo: tarjeta aparece con fade+slide 6px, nombre, metadatos y estado. Miniatura real o icono; jamás animar miniaturas falsas.
- Subida: barra con **progreso real** basado en bytes enviados si la API puede medirlos. Si no, barra indeterminada claramente etiquetada «Subiendo…», sin porcentajes inventados.
- Procesamiento PDF: componente de etapas con indicadores válidos: «Preparando», «Procesando» y «Finalizando» solo cuando el backend puede reportar etapas reales. Si no, indicador indeterminado con estado «Procesando documento…». Evitar progreso porcentual simulado y ETA inventada.
- Éxito: transición breve de 220–300 ms a un panel de resultado, icono check con trazo progresivo **opcional**, CTA de descarga prominente.
- Error: mensaje estable y contextual, sin sacudidas; «Reintentar» si es técnicamente seguro.
- Skeleton solo para recursos que realmente cargarán. No mostrar pantallas falsas durante tareas instantáneas.
- `prefers-reduced-motion: reduce`: desactivar transformaciones, loops y animaciones no esenciales; conservar feedback mediante texto y cambios de opacidad. No loops infinitos decorativos, flashing, parallax o efectos pesados.

## QA obligatorio Playwright y Codex

1. Comenzar leyendo implementación local y tests existentes. No modificar motor documental ni flujo de API salvo necesidad funcional y con pruebas.
2. Capturar e INSPECCIONAR screenshots **antes** del rediseño y **después**, en 1440×900, 768×1024, 390×844 y 1864×957.
3. Capturar estados: home, grid de herramientas, dropzone vacío, dragover, archivo cargado, procesando (demorar mock/control de prueba), éxito, error, sidebar/tableta/móvil, focus teclado.
4. Medir `scrollWidth <= clientWidth`, targets táctiles, ausencia de elementos cortados, texto legible, contraste AA y consola sin errores. Verificar que animaciones no creen scroll horizontal ni transiciones de layout erráticas.
5. Probar `prefers-reduced-motion` con Playwright; durante screenshot usar animaciones desactivadas para diffs reproducibles, aparte de probar transiciones activas.
6. Usar exclusivamente PDFs sintéticos, probar download y contenido del resultado; backend pytest + E2E. No declarar visual QA completado si capturas no fueron abiertas e inspeccionadas.
7. Reportar cambios, capturas, pruebas y limitaciones; mantener todo local y no hacer git push/merge sin aprobación del propietario.
