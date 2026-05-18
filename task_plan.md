# Plan de Trabajo - Clasificador y Conversor de Documentos

## Descripción
Aplicación web que recibe documentos/imágenes (facturas, guías de trabajo, etc.), los clasifica automáticamente, determina si deben convertirse a Excel o Word, extrae datos estructurados, genera el archivo correspondiente y produce un resumen ejecutivo.

## Stack Tecnológico
- **Frontend**: HTML/CSS/JavaScript (interfaz web limpia)
- **Backend**: Python + Flask
- **IA**: Groq API con modelo `llama-3.2-90b-vision-preview` (recomendado para visión)
- **Generación de archivos**: openpyxl (Excel), python-docx (Word)
- **OCR/Visión**: Groq Vision API

## Fases
1. ✅ Protocolo 0: Inicialización
2. ✅ Fase B: Blueprint
3. ✅ Fase L: Link (Conectividad)
4. ✅ Fase A: Architect (Construcción)
5. ✅ Fase S: Stylize (Interfaz)
6. ✅ Fase T: Trigger (Despliegue)

## KPIs
- KPI-1: Clasificación automática del tipo de documento
- KPI-2: Enrutamiento condicional (Excel vs Word)
- KPI-3: Extracción y conversión de datos estructurados
- KPI-4: Resumen ejecutivo claro
- KPI-5: Integración con Groq API
