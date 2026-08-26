# Arquitectura propuesta

## Visión general

ArbitraPDF debe separar tres capas:

1. Interfaz de usuario.
2. Motor de procesamiento.
3. Adaptadores de formatos externos.

La interfaz no debe contener lógica documental compleja.

## Estructura conceptual

```text
arbitrapdf/
├── app/
│   ├── gui/
│   ├── state/
│   └── controllers/
├── core/
│   ├── pdf/
│   ├── archives/
│   ├── foliation/
│   ├── conversion/
│   ├── email/
│   ├── excel/
│   ├── zipper/
│   └── reporting/
├── adapters/
│   ├── microsoft_office/
│   ├── libreoffice/
│   └── rar/
├── models/
├── utils/
└── tests/
```

## Motor PDF

Tecnología de referencia actual: PyMuPDF.

Responsabilidades: lectura/escritura, unión, extracción, normalización, foliación, intercalado y manipulación de páginas.

## Conversión Office

Orden de preferencia:

1. Microsoft Office local, cuando esté instalado.
2. LibreOffice local como alternativa.

No se deben subir documentos a servicios de conversión externos.

## Archivos comprimidos

ZIP: soporte nativo de Python.

RAR: adaptador local. Si el motor requerido no está disponible, informar al usuario.

La extracción debe hacerse en carpetas temporales controladas.

## Drag & Drop

La interfaz mantiene una estructura de nodos: documento, archivo comprimido, carpeta, grupo/anexo y archivo interno.

Cada nodo tiene: ID, nombre, tipo, posición, estado, hijos, ruta temporal y convertibilidad.

El árbol visual se transforma finalmente en una secuencia plana de documentos para el motor de unión.

## Pipeline

```text
Entrada
  ↓
Inspección
  ↓
Orden / drag & drop
  ↓
Extracción
  ↓
Conversión
  ↓
Normalización
  ↓
Color / compresión
  ↓
Unión
  ↓
Foliación
  ↓
Reporte
  ↓
Salida
```

No todas las herramientas utilizan todas las etapas.

## Grandes expedientes

Criterios:

- procesamiento incremental;
- evitar cargar el expediente completo en RAM;
- progreso por archivo/página;
- archivos temporales en disco;
- cancelación entre operaciones seguras;
- limpieza de temporales;
- logs locales.

## Empaquetado Windows

Objetivo público: el usuario no instala Python.

Propuesta:

- PyInstaller en modo `onedir` para estabilidad;
- Inno Setup para producir un único instalador;
- acceso directo;
- desinstalador;
- versionado;
- futura firma digital de código.

## Configuración

La configuración del usuario debe almacenarse localmente.

Ejemplos: posición de folio, tamaño de fuente, margen A4, último modo de Excel y preferencias de salida.

No almacenar documentos ni datos sensibles de expedientes como configuración persistente.

## Actualizaciones

En una fase posterior podrá existir un comprobador de versiones. Debe limitarse a consultar la versión disponible.

No debe enviar nombres de expedientes, documentos, rutas, contenido ni metadatos documentales.

## Tests

Prioridades:

- orden natural;
- orden de carpetas;
- anexos;
- PDFs repetidos;
- ZIP con nombres duplicados;
- páginas A4;
- orientación;
- foliación;
- español en letras;
- correlación;
- zipper;
- Excel;
- EML/MSG;
- cancelación;
- archivos corruptos.
