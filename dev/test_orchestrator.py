import sys
import os
from dotenv import load_dotenv

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator import Orchestrator

def test_orchestrator():
    # Load environment variables
    load_dotenv()
    
    # Check required environment variables
    required_vars = ["OPENAI_API_KEY", "ELEVENLABS_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file")
        return
    
    # Initialize orchestrator
    orchestrator = Orchestrator()
    
    # Test cases
    test_cases = [
        # Creative/Conversational queries
        "Tell me a joke",
        "How are you doing today?",
        "What's your favorite color?",
        "What do you like to do for fun?",
        "Can you tell me about yourself?",
        
        # Factual queries
        "What's the current weather in New York?",
        "Who won the last World Cup?",
        "What's the latest news about AI?",
        "What's the time in Tokyo?",
        "What's the population of London?"
    ]
    
    print("\nTesting Orchestrator with various queries...")
    for query in test_cases:
        print(f"\n{'='*50}")
        print(f"Testing query: {query}")
        print(f"{'='*50}")
        
        try:
            response = orchestrator.handle_input(query)
            print(f"\nResponse: {response}")
        except Exception as e:
            print(f"Error processing query: {str(e)}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_orchestrator() 