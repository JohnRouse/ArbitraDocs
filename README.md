# ArbitraPDF

**Herramientas para expedientes y documentos PDF**

ArbitraPDF es un proyecto de aplicación de escritorio para Windows orientado a resolver tareas repetitivas y complejas relacionadas con la preparación, organización, conversión, foliación e impresión de expedientes judiciales, arbitrales, administrativos y otros conjuntos documentales.

El enfoque del proyecto es **local-first**: los documentos se procesan en la computadora del usuario y no necesitan cargarse a un servidor externo.

> Estado actual: prototipo funcional / etapa de diseño de la primera versión pública.

## Objetivo

Reducir el trabajo manual asociado a expedientes documentales de gran volumen, especialmente cuando contienen cientos o miles de páginas, múltiples carpetas, anexos, correos electrónicos y archivos en diferentes formatos.

ArbitraPDF busca combinar herramientas PDF de uso general con funciones especializadas para expedientes.

## Principios

- Procesamiento local.
- Privacidad por diseño.
- Orientado a grandes volúmenes.
- Automatización con control humano.
- Tolerancia a errores.
- Reportes claros.
- Instalación sencilla: el usuario final no necesita Python.

## Áreas de herramientas

### PDF generales

Unir, dividir, extraer, reordenar, girar/eliminar páginas, normalizar a A4, comprimir, escala de grises, imágenes ↔ PDF y foliación.

### Expedientes

Procesar expedientes desde ZIP/carpetas, foliación correlativa, certificación al reverso, Escrito + Anexos, bandeja drag & drop, MSG/EML con adjuntos, conversión de Office y **Normalizar nombres y rutas** para preparar carpetas complejas antes de moverlas a Windows, OneDrive o SharePoint.

Consulta [docs/FEATURES.md](docs/FEATURES.md).

## Aplicación de escritorio

La versión pública se distribuirá como instalador de Windows (`Setup.exe`) y no requerirá que el usuario instale Python.

Para Word, Excel y PowerPoint se priorizará Microsoft Office local; LibreOffice podrá utilizarse como alternativa.

## Web

La futura web servirá para presentar el proyecto, descargarlo, documentarlo, publicar versiones, explicar privacidad/seguridad y permitir aportes voluntarios. Los documentos no se procesarán en la web.

## Privacidad y seguridad

Consulta [PRIVACY.md](PRIVACY.md) y [SECURITY.md](SECURITY.md).

## Estado

Varias funciones ya han sido validadas mediante prototipos internos en Python: unión masiva, orden cronológico de carpetas, A4, foliación, foliación correlativa, compresión, escala de grises, conversiones y zipper.

Consulta [ROADMAP.md](ROADMAP.md).

## Licencia

Pendiente de definición. No debe asumirse que el proyecto es open source hasta que se adopte expresamente una licencia.
