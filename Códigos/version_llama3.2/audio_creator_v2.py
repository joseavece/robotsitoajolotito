import os
import speech_recognition as sr
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from openai import OpenAI

# 1. Verificar API Key
if not os.environ.get("GEMINI_API_KEY"):
    raise ValueError("❌ Error: La variable de entorno GEMINI_API_KEY no está configurada.")

# 2. Definir el esquema de salida estructurada (Pydantic)
class AnimatronicoResponse(BaseModel):
    respuesta_texto: str = Field(description="Texto breve que dirá el animatrónico.")
    expresion_facial: str = Field(description="Preset: alegria, sorpresa, enojo, duda, neutral")
    mirada_x: int = Field(description="Posición horizontal de los ojos de -100 a 100")
    mirada_y: int = Field(description="Posición vertical de los ojos de -100 a 100")

# 3. Inicializar cliente de Gemini y sesión de chat
client = OpenAI(
    base_url="http://localhost:11434/v1", #Declaración del puerto de localhost donde se alojará la IA
    api_key = "unneeded" #Para este modelo local, no hace falta el uso de una API_KEY
)
chat_session = client.chats.create(model="gemini-3.8-flash")

system_instruction = (
    "Eres 'Anima', el cerebro de una cabeza robótica animatrónica. "
    "Mantén una conversación fluida, divertida y muy breve (máximo 1 o 2 oraciones). "
    "Devuelve siempre la estructura solicitada para mover los servos."
)

print("🤖 Sistema Animatrónico listo. Habla al micrófono (Presiona Ctrl+C para salir)...")
recognizer = sr.Recognizer()
mic = sr.Microphone(device_index=1)

while True:
    try:
        with mic as source:
            print("\n🎤 Escuchando...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        
        print("🔄 Procesando voz (STT)...")
        texto_usuario = recognizer.recognize_google(audio, language="es-ES")
        print(f"🗣️ Usuario dice: '{texto_usuario}'")
        
        # Enviar texto al chat con Gemini forzando el esquema JSON
        #prompt_completo = f"[Instrucción del Sistema: {system_instruction}]\nUsuario: {texto_usuario}"
        response = client.chat.completions.create(
            model="llama3.2:3b",
            messages=[
                {"role": "system", "content": f"{system_instruction}"},
                {"role": "user", "content": f"{texto_usuario}"}
            ],
            temperature=0.7,
            max_tokens=150  # Limitar tokens de respuesta acelera aún más el audio
        )
        
        print(f"🦾 Respuesta Estructurada (JSON):\n{response.text}")

    except sr.WaitTimeoutError:
        print("⌛ Tiempo de espera agotado, sin voz detectada.")
    except sr.UnknownValueError:
        print("❓ No se pudo entender el audio.")
    except KeyboardInterrupt:
        print("\n👋 Saliendo del sistema animatrónico...")
        break
    except Exception as e:
        print(f"⚠️ Ocurrió un error: {e}")