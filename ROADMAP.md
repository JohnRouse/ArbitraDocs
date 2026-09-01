# Roadmap de ArbitraDocs

Este documento organiza la evolución prevista de **ArbitraDocs**, una suite gratuita de herramientas documentales.

## Fase 0 — Base técnica y cambio de identidad

Estado: **en desarrollo**.

Objetivos:

- consolidar el nombre ArbitraDocs;
- reutilizar el núcleo ya iniciado de unión, A4 y foliación;
- separar cada herramienta en módulos independientes;
- mantener pruebas automatizadas;
- preparar una arquitectura común para toda la suite.

Principios:

- procesamiento local;
- no modificar originales por defecto;
- interfaz consistente;
- usuario final sin necesidad de Python;
- soporte de archivos grandes;
- cancelación segura.

## Fase 1 — Núcleo PDF básico

Implementar y estabilizar:

- Unir PDF.
- Dividir PDF.
- Girar PDF.
- Recortar PDF.
- Comprimir PDF.
- Aplanar PDF.
- Marca de agua en PDF.
- JPG/PNG/WEBP a PDF.
- PDF a JPG/PNG/WEBP.

Esta fase establecerá los componentes comunes de selección, drag & drop, previsualización, progreso, guardado y manejo de errores.

## Fase 2 — Seguridad y firma

Implementar:

- Proteger PDF.
- Desbloquear PDF con contraseña válida.
- Firmar PDF visualmente.

Evaluar posteriormente firma digital criptográfica con certificado como modalidad adicional.

## Fase 3 — OCR

Implementar **OCR en PDF** con un motor local.

Objetivos:

- PDF buscable;
- conservar apariencia original;
- idioma configurable;
- opción de exportar texto;
- pruebas con documentos escaneados reales.

Tecnologías candidatas: Tesseract y OCRmyPDF.

## Fase 4 — Conversión hacia PDF

Implementar:

- Word a PDF.
- Excel a PDF.
- PowerPoint a PDF.

Para Office:

- priorizar Microsoft Office local cuando esté disponible;
- utilizar LibreOffice como alternativa;
- no depender de servicios web externos para convertir documentos.

Excel conservará los modos ya diseñados:

- respetar configuración;
- 1 página de ancho;
- toda la hoja en 1 página.

## Fase 5 — Conversión desde PDF

Implementar y validar:

- PDF a Word.
- PDF a Excel.
- PDF a PowerPoint.

Estas conversiones requieren una fase de investigación específica porque la editabilidad y fidelidad dependen mucho de la estructura del PDF.

El producto deberá distinguir claramente entre:

- conversión de alta fidelidad visual;
- conversión editable;
- PDF digital;
- PDF escaneado que requiere OCR.

## Fase 6 — Herramientas especiales ArbitraDocs

### Foliar PDF

- ascendente/descendente;
- número/letras/ambos;
- posiciones configurables;
- foliación correlativa;
- preservar páginas A4 existentes al 100 %.

### Certificar PDF

- certificación al reverso / zipper;
- insertar antes o después de cada página;
- mantener foliación original;
- previsualizar total de páginas.

### Normalizar nombres

- análisis recursivo de carpetas;
- nombres/rutas largas;
- caracteres problemáticos;
- nombres reservados;
- colisiones;
- perfiles Windows/OneDrive/SharePoint;
- vista previa;
- CSV de cambios;
- deshacer cuando sea seguro.

## Fase 7 — Interfaz unificada

Construir la pantalla principal de ArbitraDocs como suite de tarjetas.

Categorías previstas:

- PDF.
- Convertir a PDF.
- Convertir desde PDF.
- Imágenes.
- Seguridad y firma.
- Herramientas especiales.

Características:

- búsqueda de herramientas;
- favoritos/recientes en una fase posterior;
- drag & drop;
- previsualización;
- configuración consistente;
- barra de progreso;
- cancelación;
- notificaciones de finalización.

## Fase 8 — Beta instalable

- Windows x64.
- `ArbitraDocs_Setup.exe`.
- sin Python para el usuario;
- instalación/desinstalación normal;
- logs locales;
- sin telemetría documental;
- pruebas en PCs sin entorno de desarrollo;
- firma de código cuando sea viable.

## Fase 9 — Web pública

La web será el punto público del proyecto.

Contenido:

- presentación;
- catálogo completo de herramientas;
- descargas;
- documentación;
- tutoriales;
- privacidad y seguridad;
- changelog;
- reporte de errores;
- donaciones/aportes voluntarios.

Principio: la aplicación de escritorio procesa los documentos localmente; la web no debe ser obligatoria para utilizar las herramientas.

## Fase 10 — Primera versión estable

Objetivos:

- conjunto inicial de herramientas consolidado;
- instalador estable;
- documentación completa;
- sistema de actualizaciones;
- pruebas de regresión;
- canal de feedback.

## Crecimiento futuro

Posibles herramientas adicionales:

- eliminar páginas;
- reordenar páginas visualmente;
- encabezados y pies;
- números de página convencionales;
- detectar/eliminar páginas en blanco;
- reparar PDF;
- extraer imágenes;
- extraer texto;
- comparar PDFs;
- bookmarks/marcadores;
- metadatos;
- perfiles de procesamiento;
- versión portable;
- soporte para otros sistemas operativos si es viable.
