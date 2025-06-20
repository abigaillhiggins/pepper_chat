#!/usr/bin/env python3

from orchestrator3 import Orchestrator3

def test_orchestrator3():
    print("Testing Orchestrator3 with weather query and metric conversion...")
    try:
        orchestrator = Orchestrator3()
        
        # Test weather query
        test_query = "what's the weather like in sydney today"
        print(f"\nTesting query: {test_query}")
        
        response = orchestrator.handle_input(test_query)
        print(f"Response: {response}")
        
        # Test metric conversion directly
        print(f"\nTesting metric conversion...")
        test_text = "It's 62 degrees Fahrenheit in Sydney today."
        converted = orchestrator.convert_to_metric(test_text)
        print(f"Original: {test_text}")
        print(f"Converted: {converted}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_orchestrator3() 