from typing import Dict, Callable
import importlib
import os

class ChoreographyEngine:
    """
    A class that manages and executes emotion-based movement sequences for Pepper robot.
    
    This engine dynamically loads movement handlers from Python files in the choreography directory.
    Each emotion (like 'happy', 'sad') should have its own Python file with an execute_movement() function
    that defines the specific movement sequence for that emotion.
    
    Attributes:
        emotion_handlers (Dict[str, Callable]): A dictionary mapping emotion names to their
            corresponding movement functions. For example: {'happy': happy.execute_movement}
    """
    
    def __init__(self):
        """
        Initialize the ChoreographyEngine.
        Creates an empty dictionary for emotion handlers and loads all available handlers.
        """
        self.emotion_handlers: Dict[str, Callable] = {}
        self._load_emotion_handlers()
    
    def _load_emotion_handlers(self):
        """
        Dynamically load all emotion handler modules from the choreography directory.
        
        This method:
        1. Scans the choreography directory for Python files
        2. For each file (excluding __init__.py), attempts to import it as a module
        3. If the module has an execute_movement function, adds it to emotion_handlers
        
        Example:
            If there's a file 'happy.py' with an execute_movement() function,
            it will be loaded and accessible via emotion_handlers['happy']
        """
        choreography_dir = os.path.dirname(os.path.abspath(__file__))
        for filename in os.listdir(choreography_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                emotion_name = filename[:-3]  # Remove .py extension
                try:
                    module = importlib.import_module(f"choreography.{emotion_name}")
                    if hasattr(module, 'execute_movement'):
                        self.emotion_handlers[emotion_name] = module.execute_movement
                except ImportError as e:
                    print(f"Warning: Could not load {emotion_name} handler: {e}")
    
    def execute_emotion(self, emotion_tag: str) -> bool:
        """
        Execute the movement sequence corresponding to the given emotion tag.
        
        Args:
            emotion_tag (str): The emotion tag to execute movement for (e.g., 'happy', 'sad')
            
        Returns:
            bool: True if movement was executed successfully, False otherwise
            
        Example:
            >>> engine = ChoreographyEngine()
            >>> engine.execute_emotion('happy')  # Executes the happy movement sequence
            True
        """
        emotion_tag = emotion_tag.lower()
        if emotion_tag in self.emotion_handlers:
            try:
                self.emotion_handlers[emotion_tag]()
                return True
            except Exception as e:
                print(f"Error executing movement for {emotion_tag}: {e}")
                return False
        else:
            print(f"No movement handler found for emotion: {emotion_tag}")
            return False 