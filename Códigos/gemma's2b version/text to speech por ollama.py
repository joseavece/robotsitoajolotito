import speech_recognition as sr
import ollama
from pydantic import BaseModel, Field

# 1. Definir el esquema de salida estructurada (Pydantic) - ¡Funciona igual con Ollama!
class AnimatronicoResponse(BaseModel):
    respuesta_texto: str = Field(description="Texto breve que dirá el animatrónico.")
    expresion_facial: str = Field(description="Preset: alegria, sorpresa, enojo, duda, neutral")
    mirada_x: int = Field(description="Posición horizontal de los ojos de -100 a 100")
    mirada_y: int = Field(description="Posición vertical de los ojos de -100 a 100")

# 2. Configuración del modelo local
MODELO_LOCAL = "gemma2:2b" # Puedes cambiarlo por 'phi3' o 'llama3' si lo deseas

system_instruction = (
    "Eres 'Anima', el cerebro de una cabeza robótica animatrónica. "
    "Mantén una conversación fluida, divertida y muy breve (máximo 2 o 3 oraciones). "
    "Devuelve siempre la estructura solicitada para mover los servos."
)

print(f" Sistema Animatrónico Local ({MODELO_LOCAL}) listo...")
print("Habla al micrófono (Presiona Ctrl+C para salir)...")

recognizer = sr.Recognizer()
mic = sr.Microphone(device_index=3) 

while True:
    try:
        with mic as source:
            print("\n🎤 Escuchando...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        
        print(" Procesando voz (STT)...")
        texto_usuario = recognizer.recognize_google(audio, language="es-ES")
        print(f"🗣️ Usuario dice: '{texto_usuario}'")
        
        # Enviar texto al modelo local en Ollama forzando el formato JSON con Pydantic
        response = ollama.chat(
            model=MODELO_LOCAL,
            messages=[
                {'role': 'system', 'content': system_instruction},
                {'role': 'user', 'content': texto_usuario}
            ],
            format=AnimatronicoResponse.model_json_schema(), # Fuerza la estructura exacta
            options={'temperature': 0.7}
        )
        
        print(f" Respuesta Estructurada (JSON):\n{response['message']['content']}")

    except sr.WaitTimeoutError:
        print(" Tiempo de espera agotado, sin voz detectada.")
    except sr.UnknownValueError:
        print(" No se pudo entender el audio.")
    except KeyboardInterrupt:
        print("\n Saliendo del sistema animatrónico...")
        break
    except Exception as e:
        print(f" Ocurrió un error: {e}")