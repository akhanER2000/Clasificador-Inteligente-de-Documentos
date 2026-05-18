# Constitución del Proyecto - Clasificador Inteligente de Documentos

## Variables Invariantes
- **API Provider**: Groq (exclusivo)
- **Modelo Visión**: `llama-3.2-90b-vision-preview`
- **Modelo Texto**: `llama-3.1-70b-versatile`
- **Idioma de interfaz**: Español
- **Archivos temporales**: Se eliminan después del procesamiento
- **Privacidad**: Ningún documento se almacena permanentemente

## Esquema JSON de Entrada
```json
{
  "file": "binary (imagen o PDF)",
  "filename": "string",
  "mime_type": "string (image/png, image/jpeg, application/pdf)"
}
```

## Esquema JSON de Salida (Clasificación)
```json
{
  "classification": {
    "document_type": "string (factura|guia_trabajo|informe|contrato|orden_compra|inventario|carta|otro)",
    "confidence": "float (0-1)",
    "destination_format": "string (excel|word)"
  },
  "extracted_data": {
    "fields": [
      {"key": "string", "value": "string"}
    ],
    "tables": [
      {
        "headers": ["string"],
        "rows": [["string"]]
      }
    ]
  },
  "summary": {
    "title": "string",
    "key_points": ["string"],
    "total_items": "integer"
  },
  "output_file": {
    "filename": "string",
    "format": "string (xlsx|docx)",
    "download_url": "string"
  }
}
```

## Reglas de Enrutamiento
| Tipo | Formato Destino | Razón |
|------|----------------|-------|
| Factura | Excel | Datos tabulares numéricos |
| Orden de compra | Excel | Listado de items con precios |
| Inventario | Excel | Datos tabulares |
| Guía de trabajo | Word | Documento narrativo/procedimental |
| Informe/Reporte | Word | Texto extenso con secciones |
| Contrato | Word | Documento legal narrativo |
| Carta/Memo | Word | Texto narrativo |
| Otro | Word | Default para documentos no clasificados |

## Reglas de Comportamiento
1. SIEMPRE clasificar antes de extraer datos.
2. NUNCA almacenar documentos del usuario de forma permanente.
3. SIEMPRE generar un resumen ejecutivo.
4. El resumen debe tener máximo 5 puntos clave.
5. Los archivos generados se nombran: `{tipo}_{timestamp}.{ext}`
