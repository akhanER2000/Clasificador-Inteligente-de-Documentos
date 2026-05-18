"""
Extractor de datos estructurados usando Groq API.
Recibe una imagen de documento y extrae datos en formato JSON estructurado.
"""
import os
import base64
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

EXTRACTION_PROMPT_EXCEL = """Analiza esta imagen de documento y extrae TODOS los datos estructurados para generar un archivo Excel.

Responde ÚNICAMENTE con un JSON válido sin markdown ni explicaciones. Estructura:
{
  "title": "Título del documento",
  "tables": [
    {
      "sheet_name": "Nombre de la hoja",
      "headers": ["Columna1", "Columna2", "Columna3"],
      "rows": [
        ["valor1", "valor2", "valor3"],
        ["valor4", "valor5", "valor6"]
      ]
    }
  ],
  "metadata": {
    "fecha": "fecha del documento si existe",
    "numero": "número de documento si existe",
    "emisor": "quien emite el documento",
    "receptor": "a quien va dirigido",
    "total": "monto total si aplica"
  }
}

Instrucciones:
- Extrae TODOS los datos visibles en tablas, listas o campos clave-valor.
- Si hay múltiples tablas, crea múltiples objetos en el array "tables".
- Los valores numéricos deben ir como strings pero manteniendo el formato numérico.
- Si no hay tabla clara, crea una con los campos clave-valor encontrados.
"""

EXTRACTION_PROMPT_WORD = """Analiza esta imagen de documento y extrae TODO el contenido para generar un archivo Word.

Responde ÚNICAMENTE con un JSON válido sin markdown ni explicaciones. Estructura:
{
  "title": "Título del documento",
  "sections": [
    {
      "heading": "Título de sección (o null si no tiene)",
      "content": "Texto completo de la sección",
      "level": 1
    },
    {
      "heading": "Subsección",
      "content": "Texto de la subsección",
      "level": 2
    }
  ],
  "metadata": {
    "fecha": "fecha del documento si existe",
    "autor": "autor o emisor",
    "destinatario": "a quien va dirigido",
    "referencia": "número o código de referencia"
  }
}

Instrucciones:
- Extrae TODO el texto visible en el documento.
- Mantén la estructura jerárquica (títulos, subtítulos, párrafos).
- Preserva el orden original del contenido.
- Si hay listas, inclúyelas como parte del content con viñetas.
"""

SUMMARY_PROMPT = """Analiza esta imagen de documento y genera un resumen ejecutivo conciso.

Responde ÚNICAMENTE con un JSON válido sin markdown ni explicaciones. Estructura:
{
  "title": "Título descriptivo del documento",
  "document_type_description": "Descripción breve del tipo (ej: 'Factura comercial', 'Guía de procedimientos')",
  "key_points": [
    "Punto clave 1 (máximo 1 línea)",
    "Punto clave 2",
    "Punto clave 3",
    "Punto clave 4",
    "Punto clave 5"
  ],
  "important_values": {
    "campo1": "valor relevante",
    "campo2": "valor relevante"
  },
  "action_required": "Acción recomendada o 'Ninguna' si es solo informativo"
}

Instrucciones:
- Máximo 5 puntos clave, cada uno de 1 línea.
- Los important_values son los datos más críticos (montos, fechas límite, etc.)
- Sé conciso pero informativo.
"""


def extract_data(file_bytes: bytes, filename: str, destination_format: str) -> dict:
    """
    Extrae datos estructurados de un documento.
    
    Args:
        file_bytes: Contenido del archivo en bytes.
        filename: Nombre del archivo.
        destination_format: 'excel' o 'word' para determinar el tipo de extracción.
        
    Returns:
        dict con datos extraídos estructurados.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY no configurada en .env")

    client = Groq(api_key=api_key)
    
    image_base64 = base64.b64encode(file_bytes).decode("utf-8")
    
    ext = filename.lower().split(".")[-1]
    mime_map = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "gif": "image/gif",
        "webp": "image/webp",
    }
    mime_type = mime_map.get(ext, "image/png")
    
    # Seleccionar prompt según destino
    prompt = EXTRACTION_PROMPT_EXCEL if destination_format == "excel" else EXTRACTION_PROMPT_WORD
    
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_base64}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=4000,
            temperature=0.1,
        )
        
        raw_response = response.choices[0].message.content.strip()
        
        # Limpiar markdown si existe
        if raw_response.startswith("```"):
            raw_response = raw_response.split("\n", 1)[1]
            raw_response = raw_response.rsplit("```", 1)[0].strip()
        
        extracted = json.loads(raw_response)
        return extracted
        
    except json.JSONDecodeError:
        # Fallback con estructura mínima
        if destination_format == "excel":
            return {
                "title": "Documento",
                "tables": [{"sheet_name": "Datos", "headers": ["Contenido"], "rows": [["No se pudo extraer datos estructurados"]]}],
                "metadata": {}
            }
        else:
            return {
                "title": "Documento",
                "sections": [{"heading": None, "content": "No se pudo extraer el contenido del documento.", "level": 1}],
                "metadata": {}
            }
    except Exception as e:
        raise RuntimeError(f"Error al extraer datos: {str(e)}")


def generate_summary(file_bytes: bytes, filename: str) -> dict:
    """
    Genera un resumen ejecutivo del documento.
    
    Args:
        file_bytes: Contenido del archivo en bytes.
        filename: Nombre del archivo.
        
    Returns:
        dict con resumen ejecutivo.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY no configurada en .env")

    client = Groq(api_key=api_key)
    
    image_base64 = base64.b64encode(file_bytes).decode("utf-8")
    
    ext = filename.lower().split(".")[-1]
    mime_map = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "gif": "image/gif",
        "webp": "image/webp",
    }
    mime_type = mime_map.get(ext, "image/png")
    
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": SUMMARY_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_base64}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=1500,
            temperature=0.2,
        )
        
        raw_response = response.choices[0].message.content.strip()
        
        if raw_response.startswith("```"):
            raw_response = raw_response.split("\n", 1)[1]
            raw_response = raw_response.rsplit("```", 1)[0].strip()
        
        summary = json.loads(raw_response)
        return summary
        
    except json.JSONDecodeError:
        return {
            "title": "Documento",
            "document_type_description": "No clasificado",
            "key_points": ["No se pudo generar un resumen automático"],
            "important_values": {},
            "action_required": "Revisión manual recomendada"
        }
    except Exception as e:
        raise RuntimeError(f"Error al generar resumen: {str(e)}")
