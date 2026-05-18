"""
Clasificador y extractor para documentos de texto (no-imagen).
Usa Groq con modelo de texto para clasificar y extraer datos de documentos
cuyo contenido ya fue convertido a texto plano.
"""
import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

CLASSIFICATION_TEXT_PROMPT = """Analiza el siguiente texto extraído de un documento y clasifícalo. Responde ÚNICAMENTE con un JSON válido sin markdown, sin explicaciones adicionales.

El JSON debe tener esta estructura exacta:
{
  "document_type": "factura|guia_trabajo|informe|contrato|orden_compra|inventario|carta|otro",
  "confidence": 0.95,
  "destination_format": "excel|word",
  "reasoning": "Breve explicación de por qué se clasificó así"
}

Reglas de enrutamiento:
- factura → excel (datos tabulares numéricos)
- orden_compra → excel (listado de items con precios)
- inventario → excel (datos tabulares)
- guia_trabajo → word (documento narrativo/procedimental)
- informe → word (texto extenso con secciones)
- contrato → word (documento legal narrativo)
- carta → word (texto narrativo)
- otro → word (default)

TEXTO DEL DOCUMENTO:
"""

EXTRACTION_TEXT_EXCEL_PROMPT = """Analiza el siguiente texto de un documento y extrae TODOS los datos estructurados para generar un archivo Excel.

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
- Extrae TODOS los datos en tablas, listas o campos clave-valor.
- Si hay múltiples tablas, crea múltiples objetos en el array "tables".
- Los valores numéricos deben ir como strings manteniendo formato numérico.
- Si no hay tabla clara, crea una con los campos clave-valor encontrados.

TEXTO DEL DOCUMENTO:
"""

EXTRACTION_TEXT_WORD_PROMPT = """Analiza el siguiente texto de un documento y extrae TODO el contenido para generar un archivo Word.

Responde ÚNICAMENTE con un JSON válido sin markdown ni explicaciones. Estructura:
{
  "title": "Título del documento",
  "sections": [
    {
      "heading": "Título de sección (o null si no tiene)",
      "content": "Texto completo de la sección",
      "level": 1
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
- Extrae TODO el texto del documento.
- Mantén la estructura jerárquica (títulos, subtítulos, párrafos).
- Preserva el orden original del contenido.

TEXTO DEL DOCUMENTO:
"""

SUMMARY_TEXT_PROMPT = """Analiza el siguiente texto de un documento y genera un resumen ejecutivo conciso.

Responde ÚNICAMENTE con un JSON válido sin markdown ni explicaciones. Estructura:
{
  "title": "Título descriptivo del documento",
  "document_type_description": "Descripción breve del tipo",
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

TEXTO DEL DOCUMENTO:
"""

MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"


def _get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY no configurada en .env")
    return Groq(api_key=api_key)


def _call_groq_text(prompt: str, text: str, max_tokens: int = 4000) -> str:
    """Llama a Groq con un prompt de texto puro (sin visión)."""
    client = _get_client()
    
    # Limitar texto a ~12000 caracteres para no exceder contexto
    truncated_text = text[:12000]
    if len(text) > 12000:
        truncated_text += "\n\n[... texto truncado ...]"
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt + truncated_text,
            }
        ],
        max_tokens=max_tokens,
        temperature=0.1,
    )
    
    raw = response.choices[0].message.content.strip()
    
    # Limpiar markdown
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0].strip()
    
    return raw


def classify_text_document(text: str) -> dict:
    """Clasifica un documento a partir de su texto extraído."""
    try:
        raw = _call_groq_text(CLASSIFICATION_TEXT_PROMPT, text, max_tokens=500)
        classification = json.loads(raw)
        
        required_fields = ["document_type", "confidence", "destination_format"]
        for field in required_fields:
            if field not in classification:
                raise ValueError(f"Campo faltante: {field}")
        
        return classification
    except json.JSONDecodeError:
        return {
            "document_type": "otro",
            "confidence": 0.3,
            "destination_format": "word",
            "reasoning": "No se pudo clasificar automáticamente"
        }
    except Exception as e:
        raise RuntimeError(f"Error al clasificar documento: {str(e)}")


def extract_text_data(text: str, destination_format: str) -> dict:
    """Extrae datos estructurados del texto según el formato destino."""
    prompt = EXTRACTION_TEXT_EXCEL_PROMPT if destination_format == "excel" else EXTRACTION_TEXT_WORD_PROMPT
    
    try:
        raw = _call_groq_text(prompt, text, max_tokens=4000)
        return json.loads(raw)
    except json.JSONDecodeError:
        if destination_format == "excel":
            return {
                "title": "Documento",
                "tables": [{"sheet_name": "Datos", "headers": ["Contenido"], "rows": [["No se pudo extraer datos"]]}],
                "metadata": {}
            }
        else:
            return {
                "title": "Documento",
                "sections": [{"heading": None, "content": text[:5000], "level": 1}],
                "metadata": {}
            }
    except Exception as e:
        raise RuntimeError(f"Error al extraer datos: {str(e)}")


def generate_text_summary(text: str) -> dict:
    """Genera un resumen ejecutivo a partir del texto."""
    try:
        raw = _call_groq_text(SUMMARY_TEXT_PROMPT, text, max_tokens=1500)
        return json.loads(raw)
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
