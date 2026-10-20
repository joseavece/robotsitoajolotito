import speech_recognition as sr
import ollama
from pydantic import BaseModel, Field
from gtts import gTTS
import os
import json
import re

# 1. Esquema Pydantic estricto
class AnimatronicoResponse(BaseModel):
    respuesta_texto: str = Field(description="Texto breve sin emojis ni caracteres especiales.")
    expresion_facial: str = Field(description="Preset: alegria, sorpresa, enojo, duda, neutral")
    mirada_x: int = Field(description="Posición horizontal de los ojos de -100 a 100")
    mirada_y: int = Field(description="Posición vertical de los ojos de -100 a 100")

# 2. Configuración del modelo local
MODELO_LOCAL = "gemma2:2b"

system_instruction = (
    "Eres 'Anima', la voz y personalidad de una cabeza robótica animatrónica. "
    "Responde de forma natural, amigable, contextual y muy breve (máximo 1 o 2 oraciones). "
    "REGLA ESTRICTA: NO uses jamás emojis, símbolos, marcas de formato ni caritas en 'respuesta_texto'. Usa solo letras, números y signos de puntuación básicos."
)

print(f"🤖 Sistema Animatrónico con Memoria y '{MODELO_LOCAL}' listo...")

recognizer = sr.Recognizer()
recognizer.pause_threshold = 1.2
recognizer.energy_threshold = 300

# Micrófono fijo en el índice 3
mic = sr.Microphone(device_index=3)

# Historial de conversación para mantener el contexto entre turnos
historial_chat = [
    {'role': 'system', 'content': system_instruction}
]

def limpiar_texto_para_tts(texto: str) -> str:
    """Elimina emojis, caracteres especiales y basura sintáctica del JSON"""
    texto_limpio = re.sub(r'[^\w\s,.\xbf\u00bf?\u00a1!áéíóúÁÉÍÓÚñÑ]', '', texto)
    texto_limpio = ' '.join(texto_limpio.split())
    return texto_limpio

def hacer_que_hable(texto_raw):
    """Limpia el texto y genera el audio"""
    texto_limpio = limpiar_texto_para_tts(texto_raw)
    
    if not texto_limpio.strip():
        print(" El texto quedó vacío después de la limpieza. Omitiendo TTS.")
        return

    try:
        print(f" Generando voz para: '{texto_limpio}'")
        tts = gTTS(text=texto_limpio, lang='es', slow=False)
        audio_path = "respuesta_temp.mp3"
        tts.save(audio_path)
        
        # Reproducir de forma nativa en Windows
        os.system(f"start {audio_path}")
        
    except Exception as e:
        print(f" Error al reproducir audio: {e}")

while True:
    try:
        with mic as source:
            print("\n Escuchando... (Habla de forma natural)")
            recognizer.adjust_for_ambient_noise(source, duration=0.8)
            audio = recognizer.listen(source, phrase_time_limit=15)
        
        print(" Procesando voz (STT)...")
        texto_usuario = recognizer.recognize_google(audio, language="es-ES")
        print(f"🗣️ Usuario dice: '{texto_usuario}'")
        
        # 1. Añadir el mensaje del usuario al historial de la conversación
        historial_chat.append({'role': 'user', 'content': texto_usuario})
        
        print(" Procesando con Ollama y contexto...")
        # Se envía todo el historial acumulado para que el modelo recuerde la charla
        response = ollama.chat(
            model=MODELO_LOCAL,
            messages=historial_chat,
            format=AnimatronicoResponse.model_json_schema(),
            options={
                'temperature': 0.6, 
                'num_predict': 150  
            }
        )
        
        # Obtener la respuesta cruda del modelo (en formato JSON string)
        respuesta_modelo_raw = response['message']['content']
        
        # 2. Guardar también la respuesta del asistente en el historial
        historial_chat.append({'role': 'assistant', 'content': respuesta_modelo_raw})
        
        # Parsear respuesta JSON
        contenido_json = json.loads(respuesta_modelo_raw)
        print(f" JSON Generado:\n{json.dumps(contenido_json, indent=2, ensure_ascii=False)}")
        
        texto_para_voz = contenido_json.get("respuesta_texto", "")
        
        # Reproducir voz limpia
        hacer_que_hable(texto_para_voz)

    except sr.WaitTimeoutError:
        print(" Tiempo de espera agotado, sin voz detectada.")
    except sr.UnknownValueError:
        print(" No se logró entender la frase.")
    except KeyboardInterrupt:
        print("\n Saliendo del sistema...")
        break
    except Exception as e:
        print(f" Error: {e}")