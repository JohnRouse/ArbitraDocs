# Especificación funcional

## 1. Unir PDF / documentos

Permitir seleccionar múltiples elementos y convertirlos en un solo PDF respetando el orden definido por el usuario.

Entradas previstas: PDF, Word, Excel, PowerPoint, imágenes, MSG, EML, ZIP/RAR en herramientas especializadas y carpetas.

## 2. Procesar expediente

Herramienta especializada para expedientes estructurados por carpetas.

### Orden

Cuando las carpetas representan fechas, por ejemplo `20200129`, `20200203`, `20200310`, se ordenan de menor a mayor.

Dentro de cada carpeta:

- conservar la secuencia original cuando sea relevante;
- usar orden natural cuando corresponda;
- no perder archivos repetidos con el mismo nombre.

### Salida

- único PDF;
- reporte de procesados;
- reporte de omitidos;
- número de páginas;
- estadísticas básicas.

## 3. Normalización A4

Objetivo: comportamiento equivalente a imprimir con papel A4 vertical y “ajustar a página”.

Reglas:

- salida 210 × 297 mm;
- vertical;
- conservar proporción;
- no recortar;
- no deformar;
- centrar contenido;
- páginas horizontales se ajustan dentro de A4 vertical;
- Carta, Legal, Oficio, A3, etc. se ajustan a A4;
- opción de no ampliar contenido pequeño.

## 4. Foliación

Modos: Número, Letras, Número + letras.

Sentido: Ascendente o Descendente.

Inicio configurable.

Posiciones: superior derecha, superior izquierda, superior centro, inferior derecha, inferior izquierda, inferior centro y futura posición personalizada.

### Regla número + letras

Número arriba y texto en letras debajo. Cuando la posición es derecha, ambos terminan exactamente en el mismo borde derecho.

```text
                         125
             CIENTO VEINTICINCO
```

## 5. Foliación correlativa

Seleccionar dos o más expedientes y definir su orden.

Ejemplo:

- Expediente A: 350 páginas.
- Expediente B: 120 páginas.
- Expediente C: 600 páginas.

Inicio 1, ascendente:

- A: 1–350.
- B: 351–470.
- C: 471–1070.

Los expedientes pueden permanecer como PDFs independientes. Opción adicional: unir todos al finalizar.

## 6. Certificación al reverso / Zipper

Entrada: PDF principal ya unido/foliado + página o PDF de certificación.

Salida: `P1, Certificación, P2, Certificación, P3, Certificación...`

Caso típico: principal 1000 páginas + certificación 1 página = salida 2000 páginas.

La foliación original no se modifica.

Opciones:

- insertar después de cada página;
- insertar antes de cada página;
- seleccionar una página específica si la certificación tiene varias;
- adaptar la certificación al tamaño de página;
- previsualizar total esperado.

## 7. Escala de grises

Opciones: Original / Escala de grises. Priorizar legibilidad y evitar rasterización innecesaria cuando técnicamente sea posible.

## 8. Compresión

Opciones: Original / Comprimido, con nivel o porcentaje de calidad. No se promete reducción exacta porque depende del contenido.

Reporte deseado: tamaño de entrada, tamaño final y porcentaje real de reducción.

## 9. Excel

Procesar automáticamente todas las pestañas visibles en su orden. Las ocultas no se incluyen por defecto.

### 1 página de ancho

Todas las columnas caben en una página de ancho. Las filas pueden continuar en varias páginas.

### Toda la hoja en 1 página

Cada pestaña completa se reduce a una sola página, aunque el contenido quede pequeño.

Área de impresión: respetar la definida; si no existe, utilizar el rango usado.

## 10. MSG / EML

Convertir primero el correo con De, Para, CC, Fecha, Asunto y cuerpo. Después incorporar sus adjuntos en el orden original.

Cada adjunto compatible se procesa según su formato. Evitar tratar logos e imágenes incrustadas del cuerpo como anexos independientes cuando sea posible.

Correos adjuntos dentro de otros correos: procesamiento recursivo con límite razonable.

## 11. Formatos CAD y desconocidos

No se requiere AutoCAD para el usuario.

DWG, DXF, DWF u otros formatos sin conversor local se omiten, no detienen el expediente y aparecen en el reporte.

## 12. Escrito + Anexos

### Objetivo

Automatizar el flujo: recibir escrito PDF + ZIP/RAR con anexos → descomprimir → detectar estructura → ordenar → convertir → unir.

### Anexos sueltos

`Anexo 1.pdf`, `Anexo 2.pdf`, `Anexo 3.pdf`: ordenar por numeración/orden natural.

### Anexos por carpetas

```text
Anexo 1/
  DNI.pdf
  Constancia.jpg

Anexo 2/
  Contrato.pdf
  Voucher.pdf
```

Recorrer subcarpetas de forma recursiva.

### Sin numeración clara

Usar orden natural y mostrarlo antes de procesar.

### Vista previa

El usuario debe poder revisar y corregir el orden detectado antes de generar el PDF.

## 13. Bandeja Drag & Drop para Escrito + Anexos

Permitir cualquier combinación:

```text
Escrito 1.pdf
Anexos 1.zip
Escrito 2.pdf
Anexos 2.rar
Documento adicional.pdf
Carpeta adicional/
```

Cada elemento aparece como tarjeta o bloque reordenable.

Funciones:

- arrastrar archivos a la aplicación;
- arrastrar tarjetas para cambiar el orden;
- expandir ZIP/RAR;
- mostrar anexos internos;
- reordenar archivos internos;
- mover bloques completos;
- procesar según el orden visual final.

El orden visual es la fuente de verdad para el PDF final.

## 14. Reportes

Cada operación compleja debe poder generar:

- archivos procesados correctamente;
- archivos omitidos;
- razón de omisión;
- cantidad de páginas;
- rutas/nombres;
- formatos incompatibles;
- errores de conversión;
- estadísticas relevantes.

Formatos previstos: TXT, CSV y futura vista dentro de la aplicación.

## 15. Normalizar nombres y rutas

### Objetivo

Preparar carpetas completas de expedientes antes de copiarlas, sincronizarlas o cargarlas a Windows, OneDrive, SharePoint u otros repositorios que puedan rechazar nombres o rutas problemáticas.

La herramienta debe aceptar una carpeta raíz y recorrer de forma recursiva todos sus archivos y subcarpetas, sin importar la extensión de los archivos.

### Modo de trabajo

El flujo previsto será:

1. Seleccionar carpeta principal.
2. Analizar sin modificar nada.
3. Mostrar problemas detectados y nombres propuestos.
4. Permitir revisar/corregir propuestas.
5. Aplicar cambios solo cuando el usuario confirme.
6. Generar registro de cambios.

### Problemas a detectar

- nombres excesivamente largos;
- rutas completas excesivamente largas;
- caracteres incompatibles o problemáticos como `< > : " / \\ | ? *`;
- saltos de línea o caracteres invisibles;
- espacios repetidos;
- puntos o espacios al final del nombre;
- nombres reservados de Windows como `CON`, `PRN`, `AUX`, `NUL`, `COM1`, `LPT1`, etc.;
- posibles colisiones de nombres después de normalizar;
- nombres de carpetas que contribuyan a superar el límite de la ruta completa.

### Reglas de seguridad

- conservar siempre la extensión original del archivo;
- no modificar el contenido del documento;
- no sobrescribir archivos existentes;
- resolver duplicados de forma segura, por ejemplo `Contrato.pdf`, `Contrato (2).pdf`;
- preservar el significado del nombre tanto como sea posible;
- evitar reemplazar nombres legibles por códigos incomprensibles salvo que sea imprescindible;
- trabajar sobre archivos de cualquier tipo, incluidos PDF, Office, imágenes, ZIP, RAR, CAD, videos u otros, porque esta herramienta modifica nombres/rutas y no el contenido.

### Perfiles previstos

- **Normalización suave:** corregir únicamente caracteres y terminaciones problemáticas.
- **Compatible con Windows:** aplicar reglas conservadoras para nombres y rutas de Windows.
- **Compatible con OneDrive/SharePoint:** aplicar reglas y límites conservadores para sincronización/carga.
- **Normalización estricta:** limpiar y acortar de forma más agresiva cuando el usuario lo necesite.

Los límites exactos de cada perfil deben definirse y probarse antes de la versión estable, ya que pueden depender del sistema operativo, cliente de sincronización y servicio utilizado.

### Vista previa

Mostrar una tabla con al menos:

- estado;
- ruta/nombre actual;
- problema detectado;
- nombre/ruta propuesta;
- longitud actual;
- longitud resultante.

Ejemplo conceptual:

| Estado | Nombre actual | Problema | Nombre propuesto |
|---|---|---|---|
| Advertencia | `Anexo Nº 2 - doc:*final?.pdf` | Símbolos | `Anexo Nº 2 - doc final.pdf` |
| Advertencia | ruta de 340 caracteres | Ruta larga | ruta abreviada |
| Correcto | `Anexo 3.pdf` | Ninguno | Sin cambios |

### Registro y deshacer

Antes de aplicar cambios debe generarse un registro con el mapeo:

`RUTA ORIGINAL → RUTA NUEVA`

Formato mínimo previsto: CSV.

Se planifica una opción **Deshacer última normalización**, siempre que la estructura no haya sido movida o modificada externamente después del cambio.

### Integración con otras herramientas

Además de existir como herramienta independiente, podrá ofrecerse opcionalmente antes de:

- Procesar expediente;
- Escrito + Anexos;
- copiar/preparar una carpeta para OneDrive/SharePoint.

El análisis previo nunca debe modificar automáticamente los nombres sin confirmación explícita del usuario.
