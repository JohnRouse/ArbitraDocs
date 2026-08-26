# Web pública de ArbitraPDF

## Objetivo

La web será la cara pública del proyecto y el punto de descarga de la aplicación de escritorio. No será necesaria para procesar documentos.

## Principio fundamental

**Los expedientes se procesan localmente en la computadora del usuario.**

La web no debe pedir que el usuario suba PDFs, ZIP, RAR, correos o anexos para utilizar las funciones principales de ArbitraPDF.

## Estructura inicial propuesta

### Inicio

- nombre y marca ArbitraPDF;
- mensaje principal: herramientas para expedientes y documentos PDF;
- explicación breve del procesamiento local;
- botón de descarga para Windows;
- capturas de la aplicación;
- herramientas destacadas.

### Herramientas

Catálogo visual similar al concepto de una suite PDF, dividido en:

#### PDF

- Unir.
- Dividir / Extraer.
- Reordenar.
- Foliar.
- Comprimir.
- Escala de grises.
- A4.
- Imágenes ↔ PDF.

#### Expedientes

- Procesar expediente.
- Foliación correlativa.
- Certificación al reverso.
- Escrito + Anexos.
- Correos + Adjuntos.

### Descargar

- versión actual;
- número de versión;
- requisitos de Windows;
- tamaño aproximado;
- notas de versión;
- checksum cuando se implemente;
- futura firma digital del instalador.

### Privacidad y seguridad

Explicar en lenguaje simple:

- procesamiento local;
- no subida de documentos;
- funcionamiento offline del motor documental;
- temporales locales;
- dependencias externas utilizadas.

### Documentación / Ayuda

- manual de cada herramienta;
- preguntas frecuentes;
- problemas conocidos;
- tutoriales cortos;
- solución de errores.

### Changelog

Historial de versiones y cambios relevantes.

### Reportar un problema

Enlace al sistema de issues o formulario controlado. Debe advertir que no se adjunten expedientes reales o información confidencial.

### Apoyar el proyecto

ArbitraPDF podrá ofrecer aportes o donaciones voluntarias mediante proveedores externos como PayPal, Ko-fi, Buy Me a Coffee, GitHub Sponsors u otro que se defina.

El apoyo económico no debe ser requisito para usar las funciones principales de la primera etapa.

## Modelo inicial de distribución

- aplicación gratuita;
- descarga directa del instalador;
- sin cuenta obligatoria;
- donaciones voluntarias;
- sin procesamiento documental en servidor.

## Actualizaciones

La web publicará cada nueva versión. En una fase posterior, la aplicación podrá consultar si existe una versión nueva, sin enviar información documental del usuario.
