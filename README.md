# 📄 Clasificador Inteligente de Documentos

Sistema web de clasificación, conversión y resumen automático de documentos utilizando inteligencia artificial con la API de Groq.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-lightgrey?logo=flask)
![Groq](https://img.shields.io/badge/Groq-Llama%204%20Scout-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎯 Descripción

Esta aplicación recibe cualquier tipo de documento (imágenes de facturas, guías de trabajo, PDFs, archivos Word, Excel, PowerPoint, etc.) y de forma automática:

1. **Clasifica** el tipo de documento (factura, contrato, informe, guía de trabajo, etc.)
2. **Determina el destino** óptimo (Excel para datos tabulares, Word para documentos narrativos)
3. **Extrae los datos** estructurados del documento
4. **Genera el archivo** de salida (.xlsx o .docx) listo para descargar
5. **Produce un resumen ejecutivo** con los puntos clave del documento

---

## 🚀 Características

- **Clasificación automática** con IA multimodal (visión + texto)
- **Soporte multi-formato**: imágenes (PNG, JPG, WEBP, GIF), PDF, Word, Excel, PowerPoint, TXT, CSV
- **Enrutamiento inteligente**: documentos tabulares → Excel, documentos narrativos → Word
- **Resumen ejecutivo** con puntos clave y valores importantes
- **Interfaz web moderna** con drag & drop
- **Privacidad**: archivos temporales eliminados automáticamente tras la descarga
- **API REST** para integración con otros sistemas

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología |
|---|---|
| Backend | Python + Flask |
| IA / LLM | Groq API - `meta-llama/llama-4-scout-17b-16e-instruct` |
| Frontend | HTML5 + CSS3 + JavaScript (vanilla) |
| Generación Excel | openpyxl |
| Generación Word | python-docx |
| Lectura PDF | PyPDF2 |
| Lectura PowerPoint | python-pptx |

---

## 📋 Requisitos Previos

- Python 3.10 o superior
- Una API Key de [Groq](https://console.groq.com/) (plan gratuito disponible)

---

## ⚡ Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/akhanER2000/Clasificador-Inteligente-de-Documentos.git
cd Clasificador-Inteligente-de-Documentos
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar API Key

Edita el archivo `.env` en la raíz del proyecto:

```env
GROQ_API_KEY=gsk_tu_clave_aqui
```

> Obtén tu API Key gratuita en [console.groq.com](https://console.groq.com/)

### 5. Ejecutar la aplicación

```bash
python app.py
```

Abre tu navegador en **http://localhost:5000**

---

## 📁 Estructura del Proyecto

```
├── app.py                          # Servidor Flask (punto de entrada)
├── index.html                      # Interfaz web
├── requirements.txt                # Dependencias Python
├── .env                            # Configuración de API Key
├── .gitignore                      # Archivos excluidos de Git
├── architecture/
│   └── orchestrator.py             # Orquestador central del pipeline
├── tools/
│   ├── document_classifier.py      # Clasificación con Groq Vision (imágenes)
│   ├── text_classifier.py          # Clasificación con Groq texto (documentos)
│   ├── data_extractor.py           # Extracción de datos + resumen (imágenes)
│   ├── text_extractor.py           # Extracción de texto de archivos
│   ├── excel_generator.py          # Generador de .xlsx
│   ├── word_generator.py           # Generador de .docx
│   └── test_groq_connection.py     # Test de conexión con API
├── task_plan.md                    # Plan de trabajo
├── findings.md                     # Hallazgos técnicos
├── progress.md                     # Progreso del proyecto
└── gemini.md                       # Constitución del proyecto
```

---

## 🔄 Flujo de Procesamiento

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐     ┌──────────────┐
│  Documento  │────▶│ Clasificación│────▶│   Extracción    │────▶│  Generación  │
│  (entrada)  │     │  (tipo + dst)│     │ (datos/texto)   │     │ (xlsx/docx)  │
└─────────────┘     └──────────────┘     └─────────────────┘     └──────────────┘
                                                                         │
                                                                         ▼
                                                                  ┌──────────────┐
                                                                  │   Resumen    │
                                                                  │  Ejecutivo   │
                                                                  └──────────────┘
```

---

## 📊 Reglas de Enrutamiento

| Tipo de Documento | Formato Destino | Razón |
|---|---|---|
| Factura | Excel (.xlsx) | Datos tabulares numéricos |
| Orden de compra | Excel (.xlsx) | Listado de items con precios |
| Inventario | Excel (.xlsx) | Datos tabulares |
| Guía de trabajo | Word (.docx) | Documento narrativo/procedimental |
| Informe/Reporte | Word (.docx) | Texto extenso con secciones |
| Contrato | Word (.docx) | Documento legal narrativo |
| Carta/Memo | Word (.docx) | Texto narrativo |

---

## 🌐 API REST

### POST `/api/process`

Procesa un documento y devuelve clasificación, datos y resumen.

**Request:** `multipart/form-data` con campo `file`

**Response:**
```json
{
  "status": "completed",
  "filename": "factura.png",
  "classification": {
    "document_type": "factura",
    "confidence": 0.95,
    "destination_format": "excel",
    "reasoning": "Documento con datos tabulares y montos"
  },
  "summary": {
    "title": "Factura Comercial #001",
    "key_points": ["..."],
    "important_values": {"total": "$1,500.00"}
  },
  "output_file": {
    "filename": "factura_20250518_120000.xlsx",
    "format": "xlsx",
    "download_url": "/api/download/factura_20250518_120000.xlsx"
  }
}
```

### GET `/api/download/<filename>`

Descarga el archivo generado.

### GET `/api/health`

Verifica el estado del servidor y la configuración de la API.

---

## 🤖 Modelo Recomendado

**`meta-llama/llama-4-scout-17b-16e-instruct`** (Groq)

- Soporta entrada multimodal (texto + imágenes)
- Contexto de 128K tokens
- Ideal para OCR, clasificación visual y análisis de documentos
- Disponible en el plan gratuito de Groq

---

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

## 👤 Autor

Desarrollado por [@akhanER2000](https://github.com/akhanER2000)
