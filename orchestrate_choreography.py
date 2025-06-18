from choreography.choreography_engine import ChoreographyEngine

class ChoreographyOrchestrator:
    def __init__(self):
        self.engine = ChoreographyEngine()
    
    def handle_emotion(self, emotion_tag: str) -> bool:
        """
        Handle an emotion tag by executing the corresponding movement.
        
        Args:
            emotion_tag (str): The emotion tag to handle
            
        Returns:
            bool: True if movement was executed successfully, False otherwise
        """
        return self.engine.execute_emotion(emotion_tag)

def main():
    # Example usage
    orchestrator = ChoreographyOrchestrator()
    
    # Example emotion handling
    test_emotions = ["happy", "sad"]
    for emotion in test_emotions:
        success = orchestrator.handle_emotion(emotion)
        print(f"Handled {emotion}: {'Success' if success else 'Failed'}")

if __name__ == "__main__":
    main() 