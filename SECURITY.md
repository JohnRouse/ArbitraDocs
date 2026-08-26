# Seguridad

## Modelo de seguridad

ArbitraPDF procesa documentos localmente. El objetivo es minimizar superficies de riesgo y evitar que documentos sensibles deban transmitirse por Internet.

## Principios

- No subir archivos a servidores externos.
- No enviar copias silenciosas de documentos.
- No incluir telemetría documental.
- No registrar contenido de documentos en servicios remotos.
- Trabajar con temporales locales.
- Limpiar temporales al finalizar cuando sea seguro.
- Mantener dependencias actualizadas.
- Reportar errores sin incluir contenido sensible.

## Dependencias

La aplicación podrá utilizar bibliotecas de terceros, entre ellas:

- PyMuPDF;
- Pillow;
- extract-msg;
- pywin32;
- componentes locales para RAR.

Antes de una publicación estable deben revisarse sus licencias y políticas de actualización.

## Microsoft Office / LibreOffice

Cuando se utilicen, serán aplicaciones locales instaladas en la PC. ArbitraPDF no debe enviar el archivo a un servicio de Office en la nube para realizar conversiones.

## Red

El motor documental debe funcionar sin conexión. Una futura función de actualización podrá realizar solicitudes de red exclusivamente para:

- comprobar la versión disponible;
- descargar una actualización si el usuario lo solicita.

Nunca deberá adjuntar documentos ni información extraída de ellos.

## Archivos potencialmente maliciosos

Los documentos de terceros pueden contener contenido hostil. Consideraciones futuras:

- abrir Office en modo no interactivo;
- deshabilitar macros durante conversión cuando sea posible;
- evitar ejecución de contenido embebido;
- validar rutas al extraer ZIP/RAR para prevenir path traversal;
- limitar recursividad de archivos comprimidos y correos;
- imponer límites razonables de recursos.

## Auditoría

El diseño debe facilitar que un área de TI pueda revisar:

- código fuente;
- dependencias;
- accesos a red;
- rutas temporales;
- comportamiento de conversión.

## Reporte de vulnerabilidades

El canal formal de reporte de vulnerabilidades se definirá antes de la publicación pública.
