import socket
import wave
import time

ESP32_IP = "192.168.1.50"  # Cambia por la IP real del ESP32
ESP32_PORT = 1234

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

archivo_wav = "mensaje_robot.wav"

with wave.open(archivo_wav, "rb") as wf:
    rate = wf.getframerate()
    channels = wf.getnchannels()
    print(f"Enviando audio: {rate} Hz, {channels} canal(es)...")

    CHUNK_SIZE = 512
    # Calcula la duración en segundos de cada chunk para ajustar el ritmo
    chunk_delay = CHUNK_SIZE / rate 

    data = wf.readframes(CHUNK_SIZE)
    while data:
        sock.sendto(data, (ESP32_IP, ESP32_PORT))
        time.sleep(chunk_delay) # Mantiene el audio en tiempo real
        data = wf.readframes(CHUNK_SIZE)

print("Audio enviado con éxito. El ESP32 vuelve a silencio.")