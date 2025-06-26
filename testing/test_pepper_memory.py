#!/usr/bin/env python3

from agents.pepper_agent import PepperAgent

def test_pepper_memory():
    """Test PepperAgent's conversation memory."""
    agent = PepperAgent()
    
    print("Testing PepperAgent conversation memory...\n")
    
    # Test conversation flow
    conversations = [
        "Hello! How are you today?",
        "What's your name?",
        "Do you remember what I just asked you?",
        "What did we talk about earlier?",
        "Can you tell me about yourself?",
        "What's your favorite color?",
        "Do you remember asking about my favorite color?",
        "What's the weather like?",
        "Can you summarize our conversation so far?"
    ]
    
    for i, message in enumerate(conversations, 1):
        print(f"User {i}: {message}")
        response = agent.get_response(message)
        print(f"Pepper {i}: {response}")
        print("-" * 50)

if __name__ == "__main__":
    test_pepper_memory() 