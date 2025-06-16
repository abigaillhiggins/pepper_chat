from langchain_openai import ChatOpenAI
import os
import requests

class EmotionAgent:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.7, model_name="gpt-4o")
        self.emotion_endpoint = os.getenv("EMOTION_POST_ENDPOINT", "http://localhost:5000/emotion")
        self.use_emotion_server = os.getenv("USE_EMOTION_SERVER", "false").lower() == "true"

    def get_emotion(self, sentence):
        """Classify the emotion of a sentence using the LLM."""
        try:
            prompt = (
                f"Classify the emotion of the following sentence as one of: happy, sad, angry, or neutral. "
                f"Respond with only the tag (happy, sad, angry, or neutral) and nothing else.\n"
                f"Sentence: {sentence}"
            )
            response = self.llm.invoke(prompt)
            tag = response.content.strip().lower()
            
            # Fallback to neutral if the LLM returns something unexpected
            if tag not in ["happy", "sad", "angry", "neutral"]:
                tag = "neutral"
                
            return tag
            
        except Exception as e:
            print(f"Error in EmotionAgent.get_emotion: {str(e)}")
            return "neutral"

    def post_emotion(self, sentence, emotion):
        """Post the sentence and its emotion tag to the emotion server."""
        if not self.use_emotion_server:
            return
            
        try:
            payload = {"sentence": sentence, "emotion": emotion}
            resp = requests.post(self.emotion_endpoint, json=payload)
            print(f"POST to {self.emotion_endpoint}: {resp.status_code}")
        except Exception as e:
            print(f"Failed to POST emotion tag: {e}") 