import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the Python path so we can import the choreography module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from choreography.choreography_engine import ChoreographyEngine

class TestChoreographyEngine(unittest.TestCase):
    def setUp(self):
        """Set up test cases."""
        self.engine = ChoreographyEngine()
    
    def test_initialization(self):
        """Test that the engine initializes properly."""
        self.assertIsInstance(self.engine.emotion_handlers, dict)
        # Check that happy and sad handlers are loaded
        self.assertIn('happy', self.engine.emotion_handlers)
        self.assertIn('sad', self.engine.emotion_handlers)
    
    def test_execute_emotion_happy(self):
        """Test executing the happy emotion movement."""
        with patch('choreography.happy.execute_movement') as mock_happy:
            result = self.engine.execute_emotion('happy')
            self.assertTrue(result)
            mock_happy.assert_called_once()
    
    def test_execute_emotion_sad(self):
        """Test executing the sad emotion movement."""
        with patch('choreography.sad.execute_movement') as mock_sad:
            result = self.engine.execute_emotion('sad')
            self.assertTrue(result)
            mock_sad.assert_called_once()
    
    def test_execute_emotion_case_insensitive(self):
        """Test that emotion tags are case insensitive."""
        with patch('choreography.happy.execute_movement') as mock_happy:
            result = self.engine.execute_emotion('HAPPY')
            self.assertTrue(result)
            mock_happy.assert_called_once()
    
    def test_execute_nonexistent_emotion(self):
        """Test handling of non-existent emotion."""
        result = self.engine.execute_emotion('nonexistent')
        self.assertFalse(result)
    
    def test_execute_emotion_with_error(self):
        """Test handling of errors during movement execution."""
        with patch('choreography.happy.execute_movement', side_effect=Exception('Test error')):
            result = self.engine.execute_emotion('happy')
            self.assertFalse(result)

def main():
    """Run the tests."""
    unittest.main()

if __name__ == '__main__':
    main() 