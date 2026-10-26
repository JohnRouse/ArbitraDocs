# ArbitraDocs Web — prototipo inicial

La suite web se desarrollará aquí sin eliminar la aplicación de escritorio.

**Estado:** primer prototipo local preparado para VS Code / Codex CLI. No publicarlo en Internet; faltan autenticación, permisos, antivirus, límites de uso y almacenamiento multiusuario.

El paquete de arranque funcional, entregado en la conversación de diseño de la transición web, contiene:
- Interfaz responsive con catálogo de 21 herramientas marcadas disponible/próximamente.
- Biblioteca local persistente: subir, listar, descargar y eliminar PDFs.
- Herramientas iniciales operativas: unir PDF, extraer páginas y girar PDF.
- Pruebas pytest de subida y procesamiento.

## Uso del paquete de arranque

Descomprimir el paquete en la raíz del repositorio para crear web/server, web/client, web/tests y los archivos de requisitos (sin sobrescribir trabajo posterior). Dentro de web:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
$env:ARBITRADOCS_WEB_DEV_MODE = "1"
python -m uvicorn server.app:app --reload --host 127.0.0.1 --port 8000
```

Navegar a http://127.0.0.1:8000. Ejecutar pruebas con `python -m pytest tests -q`.

Los datos residen por defecto en `web/.local-data/`. No añadir expedientes reales al repositorio.

Diseño y requisitos de producción: [docs/WEB_PLATFORM_V1.md](../docs/WEB_PLATFORM_V1.md).
