# Decisiones de diseño registradas

## ADR-001 — Procesamiento local

**Decisión:** los documentos se procesan localmente.

**Motivo:** los expedientes pueden contener información confidencial y archivos de gran tamaño.

## ADR-002 — El usuario final no instala Python

**Decisión:** la aplicación pública se empaqueta como aplicación Windows.

**Motivo:** Python es un detalle interno de implementación.

## ADR-003 — No detener por archivos incompatibles

**Decisión:** los archivos no convertibles se omiten y se reportan.

**Motivo:** un único anexo extraño no debe bloquear un expediente de miles de páginas.

## ADR-004 — CAD no es requisito inicial

**Decisión:** DWG/DXF/DWF se omiten si no existe un conversor local.

**Motivo:** incorporar un motor CAD completo incrementa complejidad y dependencias.

## ADR-005 — Excel prioriza completar la impresión

**Decisión:** ofrecer modos “1 página de ancho” y “Toda la hoja en 1 página”.

**Motivo:** en hojas complejas importa más obtener una representación completa que preservar un tamaño de letra cómodo.

## ADR-006 — Orden automático + corrección manual

**Decisión:** ArbitraPDF intenta detectar el orden, pero siempre permite que el usuario lo modifique.

**Motivo:** los anexos reales no siempre están bien nombrados.

## ADR-007 — Drag & drop como fuente de verdad

**Decisión:** en la herramienta Escrito + Anexos, el orden visual final será el orden del PDF final.

## ADR-008 — Certificación no altera foliación

**Decisión:** la función zipper inserta certificaciones sin volver a foliar el PDF principal.

## ADR-009 — Web separada del procesamiento

**Decisión:** la web sirve para distribución, información y comunidad; no para procesar expedientes.

## ADR-010 — Licencia pendiente

**Decisión:** no elegir una licencia hasta decidir si el proyecto será open source, source-available o solo freeware.
