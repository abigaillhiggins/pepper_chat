#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.search_agent3 import SearchAgent3
import time

def test_search_agent3():
    """Test the SearchAgent3 functionality."""
    print("Testing SearchAgent3...")
    print("=" * 50)
    
    # Initialize the agent
    try:
        agent = SearchAgent3()
        print("OK - SearchAgent3 initialized successfully")
    except Exception as e:
        print(f"ERROR - Failed to initialize SearchAgent3: {str(e)}")
        return False
    
    # Test queries
    test_queries = [
        "weather in New York",
        "current time in London",
        "population of Tokyo",
        "latest news about AI",
        "detailed information about climate change",
        "comprehensive guide to machine learning"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test {i}: {query} ---")
        
        try:
            start_time = time.time()
            response = agent.get_response(query)
            response_time = (time.time() - start_time) * 1000
            
            print(f"Query: {query}")
            print(f"Response: {response}")
            print(f"Response time: {response_time:.2f} ms")
            print(f"Response length: {len(response)} characters")
            
            if response and len(response) > 0:
                print("OK - Query successful")
            else:
                print("ERROR - Empty response")
                
        except Exception as e:
            print(f"ERROR - Query failed: {str(e)}")
    
    print("\n" + "=" * 50)
    print("SearchAgent3 testing completed!")
    return True

def test_api_connectivity():
    """Test direct API connectivity."""
    print("\nTesting API connectivity...")
    print("=" * 50)
    
    import requests
    
    try:
        # Test the API directly
        url = "http://192.168.194.33:8060/search"
        params = {"q": "test query", "format": "json"}
        
        print(f"Testing API endpoint: {url}")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            print("OK - API endpoint is accessible")
            
            try:
                data = response.json()
                print(f"OK - JSON response received")
                print(f"  - Query: {data.get('query', 'N/A')}")
                print(f"  - Number of results: {data.get('number_of_results', 'N/A')}")
                print(f"  - Results array length: {len(data.get('results', []))}")
                
                # Show first result if available
                results = data.get('results', [])
                if results:
                    first_result = results[0]
                    print(f"  - First result title: {first_result.get('title', 'N/A')[:50]}...")
                    print(f"  - First result URL: {first_result.get('url', 'N/A')}")
                
            except Exception as e:
                print(f"ERROR - Failed to parse JSON: {str(e)}")
        else:
            print(f"ERROR - API returned status code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("ERROR - Connection error - API endpoint may be unreachable")
    except requests.exceptions.Timeout:
        print("ERROR - Timeout error - API took too long to respond")
    except Exception as e:
        print(f"ERROR - API test failed: {str(e)}")

if __name__ == "__main__":
    print("SearchAgent3 Test Suite")
    print("=" * 50)
    
    # Test API connectivity first
    test_api_connectivity()
    
    # Test the agent
    test_search_agent3() 