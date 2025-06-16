from elevenlabs import play
from elevenlabs.client import ElevenLabs
import os
import time

class TTSAgent:
    def __init__(self):
        self.client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
        self.voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel's voice
        
        # Emotion-based voice settings
        self.emotion_settings = {
            "happy": {"stability": 0.3, "similarity_boost": 0.8},
            "sad": {"stability": 0.7, "similarity_boost": 0.5},
            "angry": {"stability": 0.2, "similarity_boost": 0.7},
            "neutral": {"stability": 0.5, "similarity_boost": 0.75}
        }

    def speak(self, text, emotion="neutral"):
        """Convert text to speech with emotion-based voice settings."""
        try:
            start_time = time.time()
            
            # Get voice settings for the emotion
            settings = self.emotion_settings.get(emotion, self.emotion_settings["neutral"])
            
            # Generate audio with emotion settings
            audio = self.client.text_to_speech.convert(
                voice_id=self.voice_id,
                text=text,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
                voice_settings=settings,
                optimize_streaming_latency=0
            )
            
            # Play the audio
            play(audio)
            
            return (time.time() - start_time) * 1000  # Return processing time in ms
            
        except Exception as e:
            print(f"Error in TTSAgent.speak: {str(e)}")
            return 0 