import os
import sys
import json
import sounddevice as sd
import vosk
import numpy as np
import time
import select

# Audio parameters
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 8000

# Initialize Vosk model
if not os.path.exists("model"):
    print("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
    sys.exit(1)

model = vosk.Model("model")

def stt_function():
    """
    Record audio and convert it to text using Vosk.
    
    Returns:
        tuple: (recognized_text, latency_ms)
            - recognized_text (str): The recognized text from speech
            - latency_ms (float): The time taken for STT processing in milliseconds
    """
    print("Listening... Press Enter to stop.")
    audio_chunks = []
    
    with sd.InputStream(samplerate=SAMPLE_RATE, blocksize=CHUNK_SIZE,
                      channels=CHANNELS, dtype='int16') as stream:
        start_time = time.time()
        while True:
            data, overflowed = stream.read(CHUNK_SIZE)
            if overflowed:
                print("Audio buffer overflow")
                continue
            audio_chunks.append(data)
            # Check for Enter key (non-blocking)
            if select.select([sys.stdin], [], [], 0)[0]:
                sys.stdin.readline()
                break
    
    stop_time = time.time()
    audio_data = np.concatenate(audio_chunks, axis=0).tobytes()
    recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE)
    recognizer.AcceptWaveform(audio_data)
    result = json.loads(recognizer.Result())
    recognized_text = result.get("text", "").strip()
    end_time = time.time()
    latency_ms = (end_time - stop_time) * 1000
    
    return recognized_text, latency_ms

# Example usage:
if __name__ == "__main__":
    print("Speech-to-Text Test")
    print("Press Enter to start speaking, then press Enter again to stop.")
    print("Type 'quit' to exit.")
    
    while True:
        input("\nPress Enter to start speaking...")
        text, latency = stt_function()
        
        if text:
            print(f"\nRecognized text: {text}")
            print(f"STT Latency: {latency:.2f} ms")
            if text.lower() == 'quit':
                break
        else:
            print("No speech detected.") 