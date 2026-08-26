# Formatos de archivo

## Soporte previsto

| Tipo | Extensiones | Estrategia |
|---|---|---|
| PDF | `.pdf` | Motor PDF nativo |
| Word | `.doc`, `.docx`, `.rtf`, `.odt` | Office / LibreOffice |
| Excel | `.xls`, `.xlsx`, `.xlsm`, `.xlsb`, `.ods` | Excel / LibreOffice |
| PowerPoint | `.ppt`, `.pptx`, `.odp` | PowerPoint / LibreOffice |
| Correo | `.msg`, `.eml` | Parser local + conversión |
| Imagen | `.jpg`, `.jpeg`, `.png`, `.tif`, `.tiff`, `.bmp`, `.gif`, `.webp` | Conversión local |
| ZIP | `.zip` | Soporte nativo |
| RAR | `.rar` | Motor/adaptador local |
| CAD | `.dwg`, `.dxf`, `.dwf`, etc. | Omitir si no existe conversor local |

## Regla general para formatos no compatibles

Un archivo no compatible:

1. no debe detener la tarea;
2. debe quedar marcado como omitido;
3. debe aparecer en el reporte;
4. debe conservar su nombre/ruta para facilitar su identificación.

## Fidelidad

Word, Excel y PowerPoint pueden verse diferentes según el motor disponible.

Prioridad:

1. Microsoft Office.
2. LibreOffice.
3. Omitir con explicación si no existe un conversor seguro/local.

## Excel

El modo de impresión se configura temporalmente para exportar. El archivo original no se guarda ni modifica.
