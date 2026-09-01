# ArbitraDocs

**Suite gratuita de herramientas documentales**

ArbitraDocs es una aplicación de escritorio orientada a trabajar con PDF, documentos de Office e imágenes mediante herramientas simples, especializadas y de uso gratuito.

El proyecto adopta un enfoque **local-first**: siempre que sea técnicamente posible, los documentos se procesan en la computadora del usuario y no necesitan cargarse a servidores externos.

> Estado actual: desarrollo inicial / construcción del núcleo modular.

## Objetivo

Crear una suite documental gratuita que reúna en una sola aplicación las operaciones más habituales sobre PDF y documentos, junto con herramientas especiales nacidas de necesidades documentales reales.

## Principios

- Herramientas gratuitas.
- Procesamiento local por defecto.
- Privacidad por diseño.
- Interfaz sencilla para usuarios no técnicos.
- Drag & drop cuando aporte utilidad.
- El usuario final no necesita instalar Python.
- Los archivos originales no se modifican salvo que la herramienta lo indique y el usuario lo confirme.
- Errores recuperables y mensajes comprensibles.

## Catálogo previsto

### Herramientas PDF

- Unir PDF.
- Comprimir PDF.
- OCR en PDF.
- Dividir PDF.
- Girar PDF.
- Aplanar PDF.
- Proteger PDF.
- Desbloquear PDF.
- Firmar PDF.
- Marca de agua en PDF.
- Recortar PDF.

### Conversión desde PDF

- PDF a JPG.
- PDF a PNG.
- PDF a WEBP.
- PDF a Word.
- PDF a Excel.
- PDF a PowerPoint.

### Conversión hacia PDF

- Word a PDF.
- Excel a PDF.
- PowerPoint a PDF.
- JPG a PDF.
- PNG a PDF.
- WEBP a PDF.

### Herramientas especiales ArbitraDocs

- **Foliar PDF:** numeración ascendente/descendente, número, letras o ambos, incluida foliación correlativa.
- **Certificar PDF:** intercalar una página de certificación antes o después de cada página del documento sin alterar su foliación original.
- **Normalizar nombres:** analizar y corregir nombres/rutas problemáticos en PDFs, otros archivos y carpetas, con vista previa y control del usuario.

Consulta [docs/FEATURES.md](docs/FEATURES.md) y [docs/TOOL_CATALOG.md](docs/TOOL_CATALOG.md).

## Aplicación de escritorio

La versión pública se distribuirá como instalador de Windows y no requerirá que el usuario tenga Python instalado.

Algunas conversiones podrán utilizar componentes locales como Microsoft Office, LibreOffice, Tesseract u otras bibliotecas libres, según la herramienta y la fidelidad requerida.

## Web

La futura web de ArbitraDocs servirá para presentar las herramientas, descargar la aplicación, publicar documentación y versiones, explicar privacidad/seguridad y permitir aportes voluntarios.

El objetivo no es obligar al usuario a cargar sus documentos a una web para utilizar la suite.

## Privacidad y seguridad

Consulta [PRIVACY.md](PRIVACY.md) y [SECURITY.md](SECURITY.md).

## Desarrollo

El primer núcleo ya trabaja sobre unión, normalización A4 y foliación. Este código se reutilizará como base de la nueva suite modular.

Consulta [ROADMAP.md](ROADMAP.md).

## Licencia

La licencia del código aún está pendiente de definición. Que ArbitraDocs sea gratuito para el usuario no implica necesariamente que todo el código sea open source; esta decisión se documentará antes del lanzamiento estable.
