"""
Aplicación Flask - Clasificador Inteligente de Documentos
Servidor web que expone la interfaz y la API de procesamiento.
"""
import os
import sys
import threading
import time
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from architecture.orchestrator import process_document, process_text_document, cleanup_temp_files

app = Flask(__name__, static_folder="static", static_url_path="/static")
CORS(app)

# Crear directorio temporal
os.makedirs(".tmp", exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "csv"}
IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    """Sirve la página principal."""
    return send_from_directory(".", "index.html")


@app.route("/api/process", methods=["POST"])
def api_process():
    """
    Endpoint principal de procesamiento.
    Recibe una imagen y devuelve clasificación, datos extraídos y resumen.
    """
    if "file" not in request.files:
        return jsonify({"error": "No se envió ningún archivo"}), 400
    
    file = request.files["file"]
    
    if file.filename == "":
        return jsonify({"error": "Nombre de archivo vacío"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            "error": f"Formato no soportado. Usa: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        }), 400
    
    # Leer bytes del archivo
    file_bytes = file.read()
    
    if len(file_bytes) > MAX_FILE_SIZE:
        return jsonify({"error": "El archivo excede el tamaño máximo de 20MB"}), 400
    
    # Determinar si es imagen o documento de texto
    ext = file.filename.rsplit(".", 1)[1].lower()
    
    if ext in IMAGE_EXTENSIONS:
        # Procesar como imagen (visión)
        result = process_document(file_bytes, file.filename)
    else:
        # Procesar como documento de texto (PDF, Word, Excel, etc.)
        result = process_text_document(file_bytes, file.filename)
    
    if result["status"] == "error":
        return jsonify({"error": result["error"]}), 500
    
    # Preparar respuesta
    response = {
        "status": "completed",
        "filename": result["filename"],
        "classification": result["classification"],
        "summary": result["summary"],
        "output_file": {
            "filename": result["output_file"]["filename"],
            "format": result["output_file"]["format"],
            "download_url": f"/api/download/{result['output_file']['filename']}",
        },
    }
    
    return jsonify(response)


@app.route("/api/download/<filename>")
def download_file(filename):
    """Descarga un archivo generado y programa su eliminación."""
    filepath = os.path.join(".tmp", filename)
    
    if not os.path.exists(filepath):
        return jsonify({"error": "Archivo no encontrado"}), 404
    
    # Programar eliminación después de 60 segundos
    def delayed_cleanup():
        time.sleep(60)
        cleanup_temp_files(filepath)
    
    threading.Thread(target=delayed_cleanup, daemon=True).start()
    
    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename,
    )


@app.route("/api/health")
def health():
    """Health check endpoint."""
    api_key = os.getenv("GROQ_API_KEY")
    return jsonify({
        "status": "ok",
        "api_configured": bool(api_key and api_key != "tu_api_key_de_groq_aqui"),
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    print(f"\n🚀 Clasificador Inteligente de Documentos")
    print(f"   Servidor corriendo en: http://localhost:{port}")
    print(f"   Modelo recomendado: meta-llama/llama-4-scout-17b-16e-instruct (Groq)")
    print(f"   Formatos aceptados: {', '.join(ALLOWED_EXTENSIONS)}")
    print(f"\n   Abre tu navegador en http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
