# Privacidad

## Principio

Los documentos del usuario pertenecen al usuario. **ArbitraDocs** está diseñado para procesarlos localmente en su computadora siempre que sea técnicamente viable.

## Documentos

La arquitectura prevista no requiere que el usuario suba sus archivos a servidores de ArbitraDocs para utilizar las herramientas principales.

Esto incluye, entre otros:

- PDF;
- documentos Word;
- hojas de cálculo Excel;
- presentaciones PowerPoint;
- imágenes;
- carpetas procesadas por herramientas especiales.

## Contraseñas

Las contraseñas utilizadas en herramientas como Proteger PDF o Desbloquear PDF:

- no deben almacenarse permanentemente;
- no deben enviarse a servidores externos;
- deben existir únicamente durante la operación necesaria.

## OCR y conversiones

OCR y conversiones deben utilizar motores locales cuando sea posible. Si en el futuro se evaluara un servicio externo opcional, deberá quedar claramente identificado y requerir una decisión explícita del usuario.

## Datos de uso

En la primera versión pública no se prevé telemetría documental invasiva.

Si en el futuro se incorpora analítica opcional:

- deberá documentarse;
- no podrá incluir contenido de documentos;
- no podrá incluir nombres/rutas de archivos;
- deberá respetar el consentimiento del usuario.

## Temporales

Durante conversiones o procesamiento pueden crearse copias temporales locales.

La aplicación debe:

- utilizar ubicaciones temporales controladas;
- eliminarlas al finalizar cuando sea seguro;
- no conservarlas innecesariamente.

## Web

La página web podrá registrar los datos técnicos habituales del alojamiento web, pero la aplicación de escritorio no dependerá de la web para procesar documentos.

## Donaciones

Las donaciones se gestionarán mediante proveedores externos. ArbitraDocs no necesita acceder a los datos financieros del usuario.
