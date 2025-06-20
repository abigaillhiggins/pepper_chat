#!/usr/bin/env python3

from agents.search_agent2 import SearchAgent2
import time

def test_google_search():
    print("Testing Google Search Agent...")
    try:
        search_agent = SearchAgent2()
        
        test_queries = [
            "what's the weather like in sydney today",
            "latest news on donald trump",
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
            
    except Exception as e:
        print(f"Failed to initialize SearchAgent2: {str(e)}")
        print("Make sure you have both GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID in your .env file")

if __name__ == "__main__":
    test_google_search() 