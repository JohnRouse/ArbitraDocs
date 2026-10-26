# ArbitraDocs — reglas de Codex

- Dirección actual: construir ArbitraDocs Web como suite de herramientas PDF y expedientes; conservar el proyecto WinUI 3 existente sin eliminar su código.
- `web/` es un prototipo local mientras no existan autenticación, autorización, cifrado, límites de recursos, retención y seguridad. No desplegar públicamente.
- No subir PDFs reales, credenciales, tokens, datos de clientes, bases de datos o temporales a GitHub.
- Documentar cada nueva herramienta. «Disponible» solo si existe un endpoint funcional probado.
- Pruebas de regresión obligatorias para PDF con rotaciones 90/180/270, normalización A4, folios, orden de ZIP/RAR y seguridad de rutas al incorporar esas funciones.
- Mantener endpoints API estables al mejorar diseño; usar navegador y Playwright con servidor local.
- Ejecutar pytest antes de commits; evitar cambios del motor documental innecesarios al rediseñar UI.
- No fusionar a main ni publicar una nueva versión sin aprobación explícita.
