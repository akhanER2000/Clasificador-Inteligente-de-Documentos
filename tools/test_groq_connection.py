"""
Script de prueba atómico para validar la conexión con Groq API.
Ejecutar: python tools/test_groq_connection.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def test_connection():
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key or api_key == "tu_api_key_de_groq_aqui":
        print("❌ ERROR: Configura tu GROQ_API_KEY en el archivo .env")
        return False
    
    try:
        client = Groq(api_key=api_key)
        
        # Test con modelo de texto
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": "Responde solo 'OK' si puedes leer esto."}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ Conexión exitosa con Groq API")
        print(f"   Modelo: meta-llama/llama-4-scout-17b-16e-instruct")
        print(f"   Respuesta: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
