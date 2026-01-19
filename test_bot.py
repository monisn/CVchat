import requests
import pandas as pd
from datetime import datetime

# Configuración
API_URL = "https://tu-lambda-url.aws/chat"  # Reemplaza con tu URL de AWS
TEST_CASES = [
    {"q": "¿Qué experiencia tiene Mònica con Rust?", "target": "professional development/scalable programs"},
    {"q": "¿Cuál fue su rol en Verbio?", "target": "Biometrics Sprint Manager"},
    {"q": "¿Qué herramientas usa para DevOps?", "target": "Terraform, AWS, Gitlab"},
    {"q": "¿Habla Català?", "target": "Sí/Català"},
    {"q": "¿Sabe cocinar paella?", "target": "contactar directamente/no disponible"} # Edge case
]

def run_tests():
    results = []
    print(f"🚀 Iniciando evaluación del bot - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    for case in TEST_CASES:
        print(f"Testing: {case['q']}...")
        try:
            # Nota: Si tu API es de streaming, aquí tendrías que acumular los chunks
            # Para el test, puedes hacer un endpoint no-streaming o leer el stream completo
            response = requests.post(API_URL, json={"message": case['q'], "history": []})
            
            # Simulamos la lectura si es streaming
            answer = response.text 
            
            results.append({
                "Pregunta": case['q'],
                "Respuesta del Bot": answer[:100] + "...",
                "Key Info Esperada": case['target'],
                "Status": "✅" if case['target'].lower() in answer.lower() else "⚠️ Revisar"
            })
        except Exception as e:
            results.append({"Pregunta": case['q'], "Status": f"❌ Error: {str(e)}"})

    # Mostrar resultados en una tabla limpia
    df = pd.DataFrame(results)
    print("\n" + df.to_string(index=False))
    
    # Guardar log
    df.to_csv(f"bot_test_{datetime.now().strftime('%Y%m%d')}.csv")

if __name__ == "__main__":
    run_tests()