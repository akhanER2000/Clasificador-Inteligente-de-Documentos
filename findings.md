# Hallazgos Técnicos

## Modelo Recomendado de Groq
- **Modelo**: `llama-3.2-90b-vision-preview`
- **Razón**: Soporta entrada multimodal (texto + imágenes), ideal para clasificar documentos escaneados, facturas e imágenes.
- **Alternativa para texto puro**: `llama-3.1-70b-versatile`

## Decisiones de Arquitectura
- Se usa Flask como backend ligero para servir la API y la interfaz web.
- Los archivos temporales se almacenan en `.tmp/` y se eliminan tras el procesamiento.
- La clasificación determina el destino: documentos tabulares → Excel, documentos narrativos → Word.

## Reglas de Clasificación
| Tipo de Documento | Destino |
|---|---|
| Factura | Excel (.xlsx) |
| Orden de compra | Excel (.xlsx) |
| Inventario | Excel (.xlsx) |
| Guía de trabajo | Word (.docx) |
| Informe/Reporte | Word (.docx) |
| Contrato | Word (.docx) |
| Carta/Memo | Word (.docx) |
