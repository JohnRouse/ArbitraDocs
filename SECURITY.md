# Seguridad

## Modelo de seguridad

ArbitraDocs procesa documentos localmente siempre que sea técnicamente viable. El objetivo es minimizar superficies de riesgo y evitar que documentos sensibles deban transmitirse por Internet.

## Principios

- No subir archivos a servidores externos por defecto.
- No enviar copias silenciosas de documentos.
- No incluir telemetría documental.
- No registrar contenido de documentos en servicios remotos.
- Trabajar con temporales locales.
- Limpiar temporales al finalizar cuando sea seguro.
- Mantener dependencias actualizadas.
- Reportar errores sin incluir contenido sensible.

## Dependencias

La suite podrá utilizar bibliotecas y componentes de terceros, por ejemplo:

- PyMuPDF u otro motor PDF local;
- Pillow para imágenes;
- Tesseract/OCRmyPDF para OCR;
- pywin32 para integración local con Microsoft Office;
- LibreOffice como alternativa de conversión;
- otras bibliotecas específicas para conversión, firma o cifrado.

Antes de una publicación estable deben revisarse licencias, mantenimiento y seguridad de cada dependencia.

## Microsoft Office / LibreOffice

Cuando se utilicen, serán aplicaciones locales instaladas en la PC. ArbitraDocs no debe enviar documentos a servicios de Office en la nube para convertirlos sin una función explícita y futura que lo indique claramente.

## Protección y desbloqueo de PDF

- Proteger PDF debe utilizar cifrado soportado y bibliotecas mantenidas.
- Las contraseñas no deben guardarse en logs ni configuración persistente.
- Desbloquear PDF solo eliminará protección cuando el usuario proporcione una contraseña válida o el archivo sea legítimamente accesible.
- No se implementará cracking o fuerza bruta de contraseñas.

## OCR

El OCR debe ejecutarse localmente en la configuración estándar. Los archivos temporales generados durante OCR deben tratarse como contenido sensible.

## Red

El núcleo documental debe funcionar sin conexión cuando la herramienta no requiera componentes externos.

Una futura función de actualización podrá realizar solicitudes de red para:

- comprobar la versión disponible;
- descargar una actualización si el usuario lo solicita.

Nunca deberá adjuntar documentos, contraseñas ni contenido extraído de ellos.

## Archivos potencialmente maliciosos

Los documentos de terceros pueden contener contenido hostil. Consideraciones:

- abrir Office en modo no interactivo;
- deshabilitar macros durante conversión cuando sea posible;
- evitar ejecución de contenido embebido;
- validar archivos y rutas;
- imponer límites razonables de recursos;
- tratar PDFs y documentos corruptos como errores recuperables.

## Auditoría

El diseño debe facilitar que un área de TI pueda revisar:

- código fuente disponible;
- dependencias;
- accesos a red;
- rutas temporales;
- comportamiento de conversión;
- manejo de contraseñas;
- mecanismos de actualización.

## Reporte de vulnerabilidades

El canal formal de reporte de vulnerabilidades se definirá antes de la publicación pública.
