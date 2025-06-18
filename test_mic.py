import sounddevice as sd
import numpy as np

def test_microphone():
    print("Testing microphone...")
    print("Available devices:")
    print(sd.query_devices())
    
    # Try to record 1 second of audio
    print("\nRecording 1 second of audio...")
    recording = sd.rec(int(16000), samplerate=16000, channels=1, dtype='int16')
    sd.wait()
    
    # Check if we got any non-zero audio
    if np.any(recording):
        print("Microphone is working! Received audio input.")
    else:
        print("No audio detected. Please check your microphone settings.")

if __name__ == "__main__":
    test_microphone() 