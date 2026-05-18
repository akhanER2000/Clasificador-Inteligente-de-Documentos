"""
Orquestador Central - Capa de Navegación (Layer 2)
Coordina el flujo completo: Clasificación → Extracción → Generación → Resumen
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.document_classifier import classify_document_from_bytes
from tools.data_extractor import extract_data, generate_summary
from tools.text_extractor import extract_text_from_file
from tools.text_classifier import classify_text_document, extract_text_data, generate_text_summary
from tools.excel_generator import generate_excel
from tools.word_generator import generate_word


def process_document(file_bytes: bytes, filename: str) -> dict:
    """
    Pipeline completo de procesamiento de documento.
    
    Flujo:
    1. Clasificar el documento (tipo + destino)
    2. Extraer datos estructurados según destino
    3. Generar archivo de salida (Excel o Word)
    4. Generar resumen ejecutivo
    
    Args:
        file_bytes: Contenido del archivo en bytes.
        filename: Nombre original del archivo.
        
    Returns:
        dict con toda la información del procesamiento.
    """
    result = {
        "status": "processing",
        "filename": filename,
        "classification": None,
        "summary": None,
        "output_file": None,
        "error": None,
    }
    
    try:
        # PASO 1: Clasificación
        classification = classify_document_from_bytes(file_bytes, filename)
        result["classification"] = classification
        
        document_type = classification.get("document_type", "otro")
        destination_format = classification.get("destination_format", "word")
        
        # PASO 2: Extracción de datos
        extracted_data = extract_data(file_bytes, filename, destination_format)
        result["extracted_data"] = extracted_data
        
        # PASO 3: Generación de archivo
        if os.environ.get("VERCEL") or not os.access(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), os.W_OK):
            output_dir = "/tmp"
        else:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".tmp")
        
        if destination_format == "excel":
            output_path = generate_excel(extracted_data, document_type, output_dir)
        else:
            output_path = generate_word(extracted_data, document_type, output_dir)
        
        output_filename = os.path.basename(output_path)
        result["output_file"] = {
            "path": output_path,
            "filename": output_filename,
            "format": "xlsx" if destination_format == "excel" else "docx",
        }
        
        # PASO 4: Resumen ejecutivo
        summary = generate_summary(file_bytes, filename)
        result["summary"] = summary
        
        result["status"] = "completed"
        
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    return result


def cleanup_temp_files(filepath: str):
    """Elimina un archivo temporal después de la descarga."""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except OSError:
        pass


def process_text_document(file_bytes: bytes, filename: str) -> dict:
    """
    Pipeline de procesamiento para documentos de texto (PDF, Word, Excel, TXT, CSV, PPT).
    
    Flujo:
    1. Extraer texto del documento
    2. Clasificar usando texto
    3. Extraer datos estructurados
    4. Generar archivo de salida
    5. Generar resumen ejecutivo
    
    Args:
        file_bytes: Contenido del archivo en bytes.
        filename: Nombre original del archivo.
        
    Returns:
        dict con toda la información del procesamiento.
    """
    result = {
        "status": "processing",
        "filename": filename,
        "classification": None,
        "summary": None,
        "output_file": None,
        "error": None,
    }
    
    try:
        # PASO 1: Extraer texto del documento
        text = extract_text_from_file(file_bytes, filename)
        
        if not text or text.startswith("[") and text.endswith("]"):
            raise RuntimeError(f"No se pudo extraer texto del archivo: {text}")
        
        # PASO 2: Clasificación por texto
        classification = classify_text_document(text)
        result["classification"] = classification
        
        document_type = classification.get("document_type", "otro")
        destination_format = classification.get("destination_format", "word")
        
        # PASO 3: Extracción de datos estructurados
        extracted_data = extract_text_data(text, destination_format)
        result["extracted_data"] = extracted_data
        
        # PASO 4: Generación de archivo
        if os.environ.get("VERCEL") or not os.access(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), os.W_OK):
            output_dir = "/tmp"
        else:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".tmp")
        
        if destination_format == "excel":
            output_path = generate_excel(extracted_data, document_type, output_dir)
        else:
            output_path = generate_word(extracted_data, document_type, output_dir)
        
        output_filename = os.path.basename(output_path)
        result["output_file"] = {
            "path": output_path,
            "filename": output_filename,
            "format": "xlsx" if destination_format == "excel" else "docx",
        }
        
        # PASO 5: Resumen ejecutivo
        summary = generate_text_summary(text)
        result["summary"] = summary
        
        result["status"] = "completed"
        
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    return result
