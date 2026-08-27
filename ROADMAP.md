# Roadmap de ArbitraPDF

Este documento resume la evolución prevista del proyecto. Las prioridades pueden cambiar según pruebas reales y comentarios de usuarios.

## Fase 0 — Prototipos funcionales

Estado: **realizado / en validación**.

Objetivo: comprobar que los problemas principales pueden resolverse localmente.

Funciones ya exploradas en prototipos:

- unión masiva de archivos PDF;
- lectura de ZIP con carpetas ordenadas por fecha;
- normalización a A4 vertical;
- foliación ascendente y descendente;
- foliación con número, letras o número + letras;
- posición configurable de foliación;
- foliación correlativa entre varios expedientes;
- compresión;
- escala de grises;
- conversión de Word, Excel, PowerPoint, MSG y EML;
- procesamiento de Excel multipestaña;
- intercalado tipo zipper para certificación al reverso;
- empaquetado de aplicación Python como instalador de Windows.

## Fase 1 — Núcleo modular

Objetivo: separar la lógica del prototipo en módulos independientes y testeables.

Módulos previstos:

- `pdf_core`
- `merge`
- `page_ops`
- `normalize_a4`
- `compression`
- `grayscale`
- `foliation`
- `correlative_foliation`
- `zipper`
- `office_conversion`
- `email_conversion`
- `archive_reader`
- `annex_sorting`
- `path_normalization`
- `reporting`

Criterios:

- cada herramienta debe poder ejecutarse sin depender de la interfaz;
- cancelación segura;
- progreso observable;
- temporales controlados;
- errores recuperables;
- no modificar originales.

## Fase 2 — Interfaz ArbitraPDF

Objetivo: sustituir la ventana monolítica por una suite visual con tarjetas.

### Herramientas PDF

- Unir.
- Dividir / Extraer.
- Reordenar páginas.
- Girar / Eliminar páginas.
- Foliar.
- Comprimir.
- Escala de grises.
- Convertir a A4.
- Imágenes ↔ PDF.

### Herramientas para expedientes

- Procesar expediente.
- Foliación correlativa.
- Certificación al reverso.
- Escrito + Anexos.
- Correos + Adjuntos.
- Normalizar nombres y rutas.

Características de interfaz:

- drag & drop;
- previsualización;
- listas/tarjetas reordenables;
- progreso por archivo y página;
- cancelar de forma segura;
- reporte final;
- mensajes de error comprensibles.

## Fase 3 — Escrito + Anexos

Objetivo: automatizar uno de los flujos más manuales del trabajo con expedientes.

Debe aceptar:

- PDF de escrito;
- ZIP;
- RAR;
- carpetas;
- PDFs sueltos;
- Word/Excel/PPT;
- imágenes;
- MSG/EML.

Debe poder manejar secuencias como:

1. Escrito 1.
2. ZIP Anexos 1.
3. Escrito 2.
4. RAR Anexos 2.
5. PDF adicional.

El usuario podrá reordenar todos los bloques mediante drag & drop. Los archivos comprimidos se expandirán visualmente en su posición y sus elementos internos también podrán reordenarse.

## Herramienta planificada — Normalizar nombres y rutas

Objetivo: revisar carpetas completas antes de moverlas o sincronizarlas y evitar errores por nombres o rutas incompatibles.

Alcance previsto:

- análisis recursivo de archivos y subcarpetas;
- detección de nombres/rutas excesivamente largas;
- detección de símbolos incompatibles;
- nombres reservados de Windows;
- limpieza de caracteres invisibles, espacios repetidos y terminaciones problemáticas;
- detección y resolución segura de colisiones;
- conservación de extensiones;
- perfiles para Windows y OneDrive/SharePoint;
- vista previa antes de aplicar;
- CSV de cambios;
- opción de deshacer cuando sea técnicamente seguro;
- integración opcional con Procesar expediente y Escrito + Anexos.

La implementación deberá priorizar un análisis que no modifique nada hasta recibir confirmación explícita del usuario.

## Fase 4 — Beta instalable

Objetivo: producir una versión que usuarios no técnicos puedan instalar.

- Windows x64.
- No requiere Python instalado.
- Instalador `ArbitraPDF_Setup.exe`.
- Desinstalación normal desde Windows.
- Versionado semántico.
- Logs de errores locales.
- Sin telemetría invasiva.
- Pruebas en equipos sin entorno de desarrollo.

## Fase 5 — Web pública

Contenido mínimo:

- landing page;
- descripción;
- capturas;
- lista de herramientas;
- descarga para Windows;
- privacidad;
- seguridad;
- FAQ;
- changelog;
- reporte de errores;
- aportes voluntarios / donaciones.

Principio: los documentos no se procesan en la web.

## Fase 6 — Primera versión pública estable

Objetivos:

- instalador estable;
- manual;
- conjunto inicial de herramientas consolidado;
- actualizaciones;
- firma de código si el proyecto lo permite;
- canal de feedback.

## Fase 7 — Crecimiento

Posibles mejoras futuras:

- OCR opcional;
- marcas de agua;
- encabezados/pies;
- índices y separadores;
- detección de páginas en blanco;
- bookmarks/marcadores PDF;
- comparación de expedientes;
- búsqueda avanzada;
- perfiles de procesamiento reutilizables;
- versión portable;
- soporte para más sistemas operativos si es viable.
