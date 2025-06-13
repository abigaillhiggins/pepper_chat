import os
from dotenv import load_dotenv

def load_environment():
    """Load environment variables from .env file"""
    load_dotenv()
    
    required_vars = ['OPENAI_API_KEY', 'ELEVENLABS_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return {
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'elevenlabs_api_key': os.getenv('ELEVENLABS_API_KEY')
    }

def get_emotional_tags(text):
    """
    Analyze text and return emotional tags
    This is a placeholder function - you can enhance it with more sophisticated emotion detection
    """
    # Basic emotion mapping - can be enhanced with more sophisticated analysis
    emotions = {
        'happy': ['happy', 'joy', 'excited', 'great', 'wonderful'],
        'sad': ['sad', 'unhappy', 'depressed', 'miserable'],
        'angry': ['angry', 'mad', 'furious', 'annoyed'],
        'neutral': ['okay', 'fine', 'alright']
    }
    
    text_lower = text.lower()
    detected_emotions = []
    
    for emotion, keywords in emotions.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_emotions.append(emotion)
    
    return detected_emotions if detected_emotions else ['neutral'] 