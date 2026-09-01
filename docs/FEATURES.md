# Especificación funcional de ArbitraDocs

Este documento define el comportamiento previsto de las herramientas principales de la suite.

## 1. Unir PDF

Permitir seleccionar múltiples PDFs, reordenarlos mediante drag & drop y generar un único archivo respetando exactamente el orden visual.

Requisitos:

- no alterar innecesariamente el tamaño de páginas existentes;
- preservar páginas A4 al 100 % cuando no se solicite normalización;
- mostrar cantidad total de archivos y páginas;
- permitir quitar/reordenar elementos antes de procesar;
- soportar archivos de gran volumen sin cargar todo el expediente en memoria cuando sea posible.

## 2. Comprimir PDF

Reducir el tamaño del archivo priorizando legibilidad.

Opciones previstas:

- compresión suave;
- compresión equilibrada;
- compresión alta;
- calidad personalizada.

Mostrar:

- tamaño original;
- tamaño final;
- porcentaje real de reducción.

Evitar rasterizar contenido vectorial/texto cuando exista una alternativa más eficiente.

## 3. OCR en PDF

Reconocer texto en PDFs escaneados y producir un PDF buscable.

Objetivo:

- conservar visualmente la página original;
- añadir una capa de texto reconocida;
- permitir selección de idioma cuando sea necesario;
- exportar opcionalmente el texto reconocido.

Tecnología candidata: Tesseract/OCRmyPDF u otra solución local y libre compatible.

## 4. PDF a JPG / PNG / WEBP

Convertir cada página del PDF a una imagen independiente.

Opciones:

- formato de salida;
- resolución/DPI;
- calidad para JPG/WEBP;
- rango de páginas;
- carpeta o ZIP de salida cuando existan muchas páginas.

## 5. Word a PDF

Convertir DOC/DOCX/RTF/ODT a PDF.

Prioridad de motores locales:

1. Microsoft Word, si está disponible;
2. LibreOffice como alternativa.

El archivo original nunca debe modificarse.

## 6. Excel a PDF

Convertir XLS/XLSX/XLSM/XLSB/ODS a PDF.

Modos previstos:

- respetar configuración existente;
- 1 página de ancho;
- toda la hoja en 1 página.

Procesar pestañas visibles en orden y respetar área de impresión cuando exista.

## 7. PowerPoint a PDF

Convertir PPT/PPTX/ODP a PDF preservando el orden de diapositivas.

Prioridad:

1. Microsoft PowerPoint local;
2. LibreOffice como alternativa.

## 8. PDF a Word

Convertir PDF a un documento Word editable cuando sea técnicamente posible.

Debe distinguir entre:

- PDF con texto digital;
- PDF escaneado que requiere OCR.

La fidelidad dependerá de la complejidad del diseño original.

## 9. PDF a Excel

Extraer tablas y contenido estructurado desde PDF hacia Excel.

La herramienta debe advertir que PDFs con estructuras complejas, tablas irregulares o escaneos pueden requerir OCR y revisión manual.

## 10. PDF a PowerPoint

Convertir páginas de PDF a una presentación.

Modos potenciales:

- cada página como imagen/diapositiva de alta fidelidad;
- conversión editable cuando exista una tecnología local suficientemente fiable.

## 11. JPG / PNG / WEBP a PDF

Aceptar una o múltiples imágenes, permitir reordenarlas y generar un PDF.

Opciones:

- tamaño de página;
- ajustar imagen manteniendo proporción;
- orientación;
- márgenes;
- calidad.

## 12. Proteger PDF

Aplicar protección mediante contraseña y, cuando la biblioteca utilizada lo permita, permisos de uso.

Opciones potenciales:

- contraseña de apertura;
- contraseña de propietario;
- restricciones de impresión/copia/modificación.

No almacenar contraseñas utilizadas.

## 13. Desbloquear PDF

Eliminar la protección de un PDF cuando el usuario disponga de la contraseña válida o el archivo sea legítimamente accesible.

La herramienta **no estará diseñada para romper, adivinar o atacar contraseñas**.

Salida: una nueva copia sin contraseña, conservando intacto el archivo original.

## 14. Dividir PDF

Permitir:

- extraer páginas específicas;
- dividir por rangos;
- separar cada página;
- dividir cada N páginas;
- eliminar páginas no deseadas antes de exportar.

## 15. Girar PDF

Girar páginas seleccionadas 90°, 180° o 270°.

Opciones:

- todas las páginas;
- páginas pares/impares;
- rango personalizado;
- páginas seleccionadas visualmente.

## 16. Aplanar PDF

Crear una copia consolidada para reducir problemas con elementos editables/interactivos.

Según la implementación, puede aplanar:

- anotaciones;
- comentarios;
- campos de formulario;
- capas visuales compatibles.

Debe advertirse cuando el proceso pueda eliminar editabilidad.

## 17. Firmar PDF

Permitir colocar una firma sobre el documento.

Primera modalidad prevista:

- firma visual mediante imagen/PNG;
- posición y tamaño configurables;
- selección de páginas.

La firma digital criptográfica con certificado podrá implementarse como una modalidad separada si se valida una biblioteca y flujo adecuados.

## 18. Marca de agua en PDF

Añadir texto o imagen como marca de agua.

Opciones:

- texto/imagen;
- opacidad;
- tamaño;
- rotación;
- posición;
- páginas seleccionadas;
- aplicar a todas las páginas.

## 19. Recortar PDF

Permitir definir nuevos límites visibles de página.

Opciones:

- recorte manual;
- mismo recorte para todas las páginas;
- páginas seleccionadas;
- previsualización antes de aplicar.

## 20. Foliar PDF — herramienta especial

Herramienta propia de ArbitraDocs para numerar documentos y expedientes.

Modos:

- número;
- letras;
- número + letras.

Sentido:

- ascendente;
- descendente.

Configuración:

- número inicial;
- posición;
- tamaño de fuente;
- márgenes;
- alineación.

Regla para número + letras:

- número arriba;
- texto en letras debajo;
- cuando la posición es derecha, ambos terminan exactamente en el mismo borde derecho.

Debe incluir foliación correlativa entre varios PDFs, conservando salidas separadas o permitiendo unirlas al final.

## 21. Certificar PDF — herramienta especial

Nombre de interfaz para la función de **certificación al reverso / zipper** desarrollada en los prototipos.

Entrada:

- PDF principal;
- PDF/página de certificación.

Salida conceptual:

`P1, Certificación, P2, Certificación, P3, Certificación...`

Opciones:

- insertar certificación después de cada página;
- insertar antes de cada página;
- seleccionar qué página usar si el PDF de certificación contiene varias;
- mantener intacta la foliación del documento principal;
- mostrar páginas finales esperadas antes de procesar.

Esta herramienta es distinta de **Firmar PDF**.

## 22. Normalizar nombres — herramienta especial

Analizar una carpeta raíz y recorrer recursivamente archivos y subcarpetas para detectar nombres/rutas que puedan ocasionar problemas en Windows, OneDrive, SharePoint u otros sistemas.

Aunque la herramienta aparezca en la suite junto a las utilidades PDF, su alcance puede incluir **cualquier tipo de archivo**, no solo PDF.

Flujo:

1. seleccionar carpeta;
2. analizar sin modificar;
3. mostrar problemas;
4. proponer nombres/rutas;
5. permitir correcciones manuales;
6. aplicar únicamente después de confirmación;
7. generar registro CSV.

Detectar:

- nombres demasiado largos;
- rutas completas demasiado largas;
- caracteres incompatibles;
- caracteres invisibles;
- espacios/puntos finales;
- nombres reservados de Windows;
- colisiones después de normalizar.

Reglas:

- conservar extensiones;
- nunca sobrescribir archivos;
- resolver duplicados de forma segura;
- preservar nombres legibles;
- permitir perfiles de normalización;
- ofrecer deshacer cuando sea técnicamente seguro.

## Criterios comunes de todas las herramientas

- procesamiento local siempre que sea viable;
- no modificar originales por defecto;
- barra de progreso y cancelación segura;
- drag & drop en herramientas donde simplifique el flujo;
- resultados y errores comprensibles;
- temporales controlados y eliminados al finalizar;
- capacidad de trabajar con archivos grandes;
- interfaz consistente en toda la suite.
