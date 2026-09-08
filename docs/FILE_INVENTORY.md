# Mapear archivos

## Objetivo

`Mapear archivos` genera un inventario de solo lectura de una carpeta, ZIP o RAR. Recorre carpetas y subcarpetas de forma recursiva y muestra todos los archivos encontrados, independientemente de su extensión.

La herramienta no renombra, elimina ni modifica archivos originales. Cuando necesita inspeccionar un archivo comprimido, utiliza almacenamiento temporal local y lo elimina al finalizar.

## Entradas

- carpeta local;
- ZIP;
- RAR.

El usuario puede seleccionar la fuente mediante un selector o arrastrarla a la ventana.

## Información mostrada

La vista principal incluye:

- árbol completo de carpetas, subcarpetas y archivos;
- cantidad total de archivos;
- cantidad total de carpetas/subcarpetas;
- tamaño acumulado de los archivos;
- cantidad de extensiones distintas;
- resumen por extensión;
- buscador por nombre, extensión o ruta virtual.

El orden utilizado en el árbol es natural, por ejemplo `Anexo 2` antes de `Anexo 10` y `20230102` antes de `20230110`.

## Exportación

El inventario puede exportarse como:

- TXT: árbol legible;
- CSV: tabla con tipo, nombre, extensión, tamaño y ruta;
- JSON: estructura completa para procesos técnicos o futuras integraciones.

## RAR

La inspección de RAR reutiliza el adaptador local de archivos comprimidos de ArbitraDocs. Se intenta utilizar 7-Zip cuando está disponible y los mecanismos compatibles del sistema como respaldo. Si el entorno no puede abrir un RAR, la herramienta debe informar el problema sin modificar el archivo.

## Integraciones futuras

El inventario servirá como base para:

- enviar la estructura detectada a `Preparar PDFs`;
- revisar nombres problemáticos con `Normalizar nombres`;
- expandir visualmente ZIP/RAR y reordenar elementos antes de unir;
- generar alertas de rutas largas, duplicados, archivos sin extensión o formatos incompatibles.
