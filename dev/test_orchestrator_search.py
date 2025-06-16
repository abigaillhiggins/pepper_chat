import sys
import os
import time

# Ensure the parent directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator import Orchestrator


def test_search_queries():
    orchestrator = Orchestrator()
    search_queries = [
        "What's the current weather in New York?",
        "Who won the last World Cup?",
        "What's the latest news about AI?",
        "What's the time in Tokyo?",
        "What's the population of London?",
        "What is the capital of Canada?",
        "How tall is Mount Everest?",
        "Who is the president of France?",
        "What is the speed of light?",
        "When was the Declaration of Independence signed?"
    ]

    for query in search_queries:
        print("="*50)
        print(f"Testing search query: {query}")
        start = time.time()
        response = orchestrator.handle_input(query)
        elapsed = time.time() - start
        print(f"Response: {response}")
        print(f"Time taken: {elapsed:.2f} seconds\n")

if __name__ == "__main__":
    test_search_queries() 