#!/usr/bin/env python3

from agents.summary_agent import SummaryAgent

def test_summary_agent():
    """Test the summary agent with various queries."""
    agent = SummaryAgent()
    
    # Test cases
    test_cases = [
        {
            "query": "What's the weather like?",
            "search_response": "It's currently 75°F and sunny in New York."
        },
        {
            "query": "How far is it to the city?",
            "search_response": "The city is about 25 miles away."
        },
        {
            "query": "What public holiday is it today?",
            "search_response": "Today is Thanksgiving Day in the United States."
        },
        {
            "query": "What time is it?",
            "search_response": "It's currently 3:30 PM Eastern Time."
        }
    ]
    
    print("Testing SummaryAgent with Australian context filtering...\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}:")
        print(f"Query: {test_case['query']}")
        print(f"Original response: {test_case['search_response']}")
        
        filtered_response = agent.get_response(test_case['search_response'], test_case['query'])
        print(f"Filtered response: {filtered_response}")
        print("-" * 50)

if __name__ == "__main__":
    test_summary_agent() 