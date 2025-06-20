#!/usr/bin/env python3

from agents.search_agent import SearchAgent
import time

def test_search():
    print("Testing Search Agent...")
    search_agent = SearchAgent()
    
    test_queries = [
        "what's the weather like in sydney today",
        "latest news on donald trump",
        "current time in new york",
        "population of tokyo"
    ]
    
    for query in test_queries:
        print(f"\n--- Testing: {query} ---")
        try:
            start_time = time.time()
            response = search_agent.get_response(query)
            end_time = time.time()
            
            print(f"Response: {response}")
            print(f"Time taken: {(end_time - start_time)*1000:.2f} ms")
            
        except Exception as e:
            print(f"Error: {str(e)}")
        
        time.sleep(2)  # Wait between queries

if __name__ == "__main__":
    test_search() 