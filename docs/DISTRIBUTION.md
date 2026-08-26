# Distribución e instalación

## Objetivo

El usuario común debe poder descargar e instalar ArbitraPDF como cualquier programa de Windows.

## Requisito clave

**El usuario final no necesita tener Python instalado.**

Python y las dependencias necesarias se empaquetarán dentro de la aplicación.

## Estrategia validada en prototipo

- PyInstaller para empaquetar la aplicación.
- Modo `onedir` por estabilidad con PyMuPDF, pywin32, extract-msg y Pillow.
- Inno Setup para generar un único instalador `ArbitraPDF_Setup.exe`.

Aunque internamente la aplicación instalada pueda contener varios archivos, el usuario distribuye y ejecuta un único instalador.

## Experiencia esperada

1. Descargar `ArbitraPDF_Setup.exe`.
2. Ejecutar el instalador.
3. Instalar.
4. Abrir ArbitraPDF desde Inicio o un acceso directo.
5. Usar las herramientas sin Python, pip ni archivos BAT.

## Conversión de Office

La aplicación puede funcionar para tareas PDF sin Microsoft Office.

Para convertir Word, Excel y PowerPoint con máxima fidelidad:

- usar Microsoft Office local cuando esté disponible;
- usar LibreOffice como alternativa compatible;
- si no existe un motor de conversión apropiado, informar y omitir el archivo sin detener el trabajo completo.

## SmartScreen y firma de código

Durante pruebas internas, los ejecutables no firmados pueden mostrar “Editor desconocido” o advertencias de SmartScreen.

Antes de una distribución pública madura se evaluará:

- certificado de firma de código;
- firma del ejecutable;
- firma del instalador;
- hashes/checksums publicados en la web.

## Versionado

Se propone versionado semántico:

`MAJOR.MINOR.PATCH`

Ejemplos:

- `1.0.0` primera versión pública estable;
- `1.1.0` nuevas herramientas compatibles;
- `1.1.1` corrección de errores.

## Versiones futuras

Posibles canales:

- instalable, recomendado;
- portable, opcional;
- beta/pruebas para usuarios voluntarios.
