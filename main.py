from dotenv import load_dotenv
import os
from elevenlabs import play
from elevenlabs.client import ElevenLabs
import time

# Load environment variables
load_dotenv()

# Initialize ElevenLabs
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# Rachel's voice_id (default)
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"

def chat_with_ai(prompt):
    # Instead, use the agent's run method or the LangChain ChatOpenAI interface for chat completions.
    # If you need to get a response, use:
    # ai_message = agent.run(user_input)
    pass

def text_to_speech(text):
    start = time.time()
    audio = client.text_to_speech.convert(
        voice_id=VOICE_ID,
        text=text,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
        optimize_streaming_latency=3
    )
    end = time.time()
    print(f"TTS generation took {(end - start) * 1000:.2f} ms.")
    play(audio)

def main():
    print("Welcome to the AI Chat Assistant!")
    print("Type 'quit' to exit.")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'quit':
            break
        
        # Convert response to speech
        text_to_speech(user_input)

if __name__ == "__main__":
    main() 