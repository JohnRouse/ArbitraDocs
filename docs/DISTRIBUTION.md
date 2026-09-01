# Distribución e instalación

## Objetivo

El usuario común debe poder descargar e instalar **ArbitraDocs** como cualquier programa de Windows.

## Requisito clave

**El usuario final no necesita tener Python instalado.**

Python y las dependencias necesarias se empaquetarán dentro de la aplicación.

## Estrategia validada en prototipo

- PyInstaller para empaquetar la aplicación.
- Modo `onedir` por estabilidad con dependencias complejas.
- Inno Setup para generar un único instalador `ArbitraDocs_Setup.exe`.

Aunque internamente la aplicación instalada pueda contener varios archivos, el usuario distribuye y ejecuta un único instalador.

## Experiencia esperada

1. Descargar `ArbitraDocs_Setup.exe`.
2. Ejecutar el instalador.
3. Instalar.
4. Abrir ArbitraDocs desde Inicio o un acceso directo.
5. Usar las herramientas sin Python, pip ni archivos BAT.

## Componentes opcionales

La mayoría de herramientas PDF deben funcionar con los componentes incluidos en ArbitraDocs.

Algunas funciones pueden beneficiarse de software local adicional:

- Microsoft Office para conversiones Word/Excel/PowerPoint con alta fidelidad;
- LibreOffice como alternativa;
- motores OCR locales como Tesseract/OCRmyPDF.

La aplicación debe detectar estas capacidades y explicar claramente cuando una herramienta tenga limitaciones por falta de un componente opcional.

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
- `1.1.0` nuevas herramientas;
- `1.1.1` corrección de errores.

## Versiones futuras

Posibles canales:

- instalable, recomendado;
- portable, opcional;
- beta/pruebas para usuarios voluntarios.
