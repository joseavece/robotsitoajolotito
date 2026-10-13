import speech_recognition as sr

print("🎤 Dispositivos de audio disponibles:")
for index, name in enumerate(sr.Microphone.list_microphone_names()):
    print(f"Índice {index}: {name}")