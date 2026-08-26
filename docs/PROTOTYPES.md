# Prototipos y validaciones realizadas

Este documento registra capacidades que ya fueron probadas en versiones internas antes de la construcción de la primera versión pública de ArbitraPDF.

## Unión masiva de expedientes

Se ha probado la unión de ZIP con decenas y cientos de PDFs, incluyendo expedientes con cientos y miles de páginas.

Casos validados:

- orden de carpetas de fecha de menor a mayor;
- conservación del orden interno;
- archivos repetidos;
- omisión explícita de carpetas cuando el usuario lo solicita;
- generación de un PDF consolidado.

## Normalización A4

Se ha implementado un prototipo capaz de llevar las páginas a A4 vertical mediante ajuste proporcional sin recortar.

## Foliación

Se ha probado:

- ascendente;
- descendente;
- número;
- letras;
- número + letras;
- posición superior/inferior;
- alineación derecha/izquierda/centro;
- número arriba + letras debajo con alineación derecha común.

## Foliación correlativa

Existe un prototipo que permite ordenar varios expedientes y continuar la numeración de uno al siguiente manteniendo PDFs de salida separados o unificados.

## Excel

El prototipo contempla:

- pestañas visibles en orden;
- 1 página de ancho;
- toda la hoja en 1 página;
- conversión mediante Microsoft Excel cuando está disponible.

Debe seguir validándose con libros complejos reales antes de considerarse estable.

## MSG / EML

Existe soporte experimental para:

- correo principal;
- cabeceras principales;
- cuerpo;
- adjuntos compatibles;
- omisión de adjuntos no compatibles.

Debe validarse con mayor variedad de correos reales.

## Color y compresión

Se han implementado opciones experimentales de:

- color original;
- escala de grises;
- salida original;
- salida comprimida con nivel de calidad.

## Certificación al reverso / Zipper

Se creó una herramienta independiente que intercala una misma página de certificación después de cada página del PDF principal sin alterar la foliación original.

Ejemplo validado:

`P1, C, P2, C, P3, C...`

## Instalador Windows

Se validó el empaquetado del prototipo Python mediante PyInstaller y la creación de un instalador de Windows mediante Inno Setup.

El ejecutable instalado puede funcionar sin Python instalado en la computadora del usuario final.

## Pendiente de validación extensa

- Word complejo;
- PowerPoint complejo;
- Excel con configuraciones de impresión atípicas;
- MSG/EML de múltiples clientes;
- RAR;
- archivos dañados;
- grandes expedientes con mezcla completa de formatos;
- drag & drop de la futura interfaz;
- Escrito + Anexos avanzado.
