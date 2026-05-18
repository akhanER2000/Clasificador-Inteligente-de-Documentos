"""
Clasificador de documentos usando Groq Vision API.
Recibe una imagen/documento y determina su tipo y destino.
"""
import os
import base64
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

CLASSIFICATION_PROMPT = """Analiza esta imagen de un documento y clasifícalo. Responde ÚNICAMENTE con un JSON válido sin markdown, sin explicaciones adicionales.

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
"""


def encode_image_to_base64(file_path: str) -> str:
    """Convierte una imagen a base64."""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_mime_type(filename: str) -> str:
    """Determina el MIME type basado en la extensión."""
    ext = filename.lower().split(".")[-1]
    mime_map = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "gif": "image/gif",
        "webp": "image/webp",
        "pdf": "application/pdf",
    }
    return mime_map.get(ext, "image/png")


def classify_document(file_path: str) -> dict:
    """
    Clasifica un documento usando Groq Vision API.
    
    Args:
        file_path: Ruta al archivo de imagen del documento.
        
    Returns:
        dict con classification info (document_type, confidence, destination_format)
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY no configurada en .env")

    client = Groq(api_key=api_key)
    
    # Codificar imagen
    image_base64 = encode_image_to_base64(file_path)
    mime_type = get_mime_type(file_path)
    
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": CLASSIFICATION_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_base64}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=500,
            temperature=0.1,
        )
        
        raw_response = response.choices[0].message.content.strip()
        
        # Limpiar respuesta si viene con markdown
        if raw_response.startswith("```"):
            raw_response = raw_response.split("\n", 1)[1]
            raw_response = raw_response.rsplit("```", 1)[0].strip()
        
        classification = json.loads(raw_response)
        
        # Validar campos requeridos
        required_fields = ["document_type", "confidence", "destination_format"]
        for field in required_fields:
            if field not in classification:
                raise ValueError(f"Campo faltante en respuesta: {field}")
        
        return classification
        
    except json.JSONDecodeError as e:
        # Fallback si no se puede parsear
        return {
            "document_type": "otro",
            "confidence": 0.3,
            "destination_format": "word",
            "reasoning": f"No se pudo clasificar automáticamente. Error: {str(e)}",
            "raw_response": raw_response
        }
    except Exception as e:
        raise RuntimeError(f"Error al clasificar documento: {str(e)}")


def classify_document_from_bytes(file_bytes: bytes, filename: str) -> dict:
    """
    Clasifica un documento desde bytes en memoria.
    
    Args:
        file_bytes: Contenido del archivo en bytes.
        filename: Nombre original del archivo.
        
    Returns:
        dict con classification info
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY no configurada en .env")

    client = Groq(api_key=api_key)
    
    image_base64 = base64.b64encode(file_bytes).decode("utf-8")
    mime_type = get_mime_type(filename)
    
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": CLASSIFICATION_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_base64}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=500,
            temperature=0.1,
        )
        
        raw_response = response.choices[0].message.content.strip()
        
        if raw_response.startswith("```"):
            raw_response = raw_response.split("\n", 1)[1]
            raw_response = raw_response.rsplit("```", 1)[0].strip()
        
        classification = json.loads(raw_response)
        
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
