# Desarrollo de ArbitraPDF

## Rama de desarrollo inicial

La primera implementación del nuevo motor se desarrolla en `dev/v0.1-core`.

El objetivo de esta etapa es construir funciones independientes de la interfaz gráfica y cubrirlas con pruebas antes de conectarlas a la futura aplicación de escritorio.

## Requisitos de desarrollo

- Python 3.11 o superior.
- Se recomienda Python 3.12 para el entorno de desarrollo y empaquetado estable.

## Instalación local

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Ejecutar pruebas

```bash
pytest -q
```

## Motor v0.1

La primera vertical funcional contiene:

- unión de PDFs;
- normalización a A4 vertical;
- preservación al 100 % de páginas que ya son A4 vertical;
- foliación ascendente/descendente;
- número, letras y número + letras;
- posiciones básicas de foliación;
- pipeline `unir → normalizar → foliar`.

## Corrección del problema de páginas A4 reducidas

Una página que ya sea A4 vertical, dentro de una tolerancia configurable, no se vuelve a colocar dentro de un rectángulo con margen.

Se copia directamente al documento de salida para conservar:

- escala 100 %;
- contenido vectorial;
- texto;
- márgenes originales.

Solo las páginas que realmente necesiten adaptación se colocan dentro de una nueva página A4.

## CLI temporal

Mientras se desarrolla la interfaz gráfica, el motor puede probarse desde terminal.

### Unir

```bash
arbitrapdf merge salida.pdf archivo1.pdf archivo2.pdf
```

### Normalizar

```bash
arbitrapdf normalize entrada.pdf salida.pdf
```

### Foliar

```bash
arbitrapdf foliate entrada.pdf salida.pdf --start 1 --mode numero+letras --position top-right
```

### Unir + A4 + foliar

```bash
arbitrapdf process salida.pdf archivo1.pdf archivo2.pdf --start 1
```

## Próximos módulos

Después de estabilizar este núcleo:

1. lectura de carpetas y ZIP;
2. orden cronológico/natural;
3. conversores de Office, imágenes, MSG/EML;
4. reportes;
5. foliación correlativa;
6. zipper;
7. Escrito + Anexos;
8. normalización de nombres y rutas;
9. interfaz gráfica con drag & drop.
