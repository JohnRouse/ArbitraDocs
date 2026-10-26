# ArbitraDocs Web — transición de producto

Estado: arquitectura propuesta y primera base funcional local distribuida para VS Code/Codex. **No existe aún un servicio público de almacenamiento.**

## Objetivo

ArbitraDocs evoluciona a una suite web de herramientas PDF y expedientes con biblioteca privada, procesamiento en servidor y resultados descargables. La aplicación WinUI 3 se conserva como alternativa local y como fuente de algoritmos validados.

## Recorrido previsto

Cuenta → espacio documental privado → subir archivos → escoger herramienta → configurar/previsualizar → ejecutar trabajo → guardar resultado en biblioteca o descargar → eliminación cuando corresponda.

## Arquitectura recomendada de producción

- Frontend web accesible en escritorio y móvil, con herramientas, biblioteca, historial y vista previa.
- API Python FastAPI autenticada: validar propietario/permiso **en cada operación**.
- PostgreSQL: usuarios, archivos, carpetas, metadatos, permisos y estado de trabajos.
- Almacenamiento de objetos privado S3-compatible: originales y resultados cifrados, nombres aleatorios y enlaces temporales con alcance limitado.
- Cola Redis con trabajadores separados: PDF, OCR, LibreOffice, ZIP/RAR; aislar CPU, RAM, disco temporal y privilegios.
- Subida reanudable/multipart directa a almacenamiento para expedientes de cientos de MB o GB; no cargar archivos enteros a memoria o a una petición de la API.
- Limpieza de temporales, retención definida, eliminación verificable, copias de seguridad y trazabilidad sin registrar contenido de documentos.

## Seguridad obligatoria antes de ponerlo en Internet

Autenticación, aislamiento multiusuario, revisión de permisos, límites por usuario, validación de formato real, antivirus, extracción segura de ZIP/RAR, límites contra archivos bomba, workers sandboxed, mitigación de SSRF, controles de descargas y auditorías. Mantener los buckets privados y cifrados. La guía OWASP para cargas de archivos es referencia base: https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html

**Cambio de privacidad:** el compromiso histórico «todo se procesa en la computadora del usuario» será exclusivo de la versión de escritorio. En web los archivos se transmiten y almacenan en servidores; deben actualizarse las políticas antes del despliegue.

## Licencias

El motor actual usa PyMuPDF, distribuido bajo AGPL o licencia comercial. Revisar obligaciones para servicios web antes de integrarlo o elegir componentes con licencias compatibles. No asumir libertad de publicar el motor cerrado.

## Catálogo de herramientas

1. PDF general: unir, dividir, extraer, reordenar, girar, comprimir, OCR, aplanar, recortar, marca de agua, proteger/desbloquear y firmar.
2. Conversiones: PDF ↔ JPG/PNG/WebP; Word/Excel/PPT ↔ PDF y exportaciones a Office.
3. Expedientes: A4 y márgenes, foliar (número/letras, ascendente/descendente), certificación al reverso o sello por página, ZIP/RAR/carpeta, escrito+anexos, inventario, normalizar nombres, detección de contrato/cláusula/pago.

## Fases

- Fase 1: prototipo local visual con biblioteca persistente, subida PDF, unión, extracción y rotación; pruebas.
- Fase 2: cuentas, almacenamiento privado S3, PostgreSQL, carga grande, trabajos asíncronos, permisos, cuotas, retención y borrado.
- Fase 3: suite PDF general y conversiones.
- Fase 4: herramientas avanzadas de arbitraje aprovechando el motor WinUI.
- Fase 5: auditoría, privacidad, licencias, costos y despliegue público controlado.

## Estado actual

La primera base de código de desarrollo fue preparada como paquete independiente para abrir con VS Code y Codex CLI. Es **exclusivamente localhost**, con biblioteca SQLite y almacenamiento local en carpeta privada, y todavía carece de usuarios, S3 y colas. No confundir con la arquitectura cloud final.
