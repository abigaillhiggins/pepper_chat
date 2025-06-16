from dotenv import load_dotenv
import os
from agents.pepper_agent import PepperAgent
from agents.search_agent import SearchAgent
from agents.tts_agent import TTSAgent
from utils.sentence_splitter import split_into_sentences
from stt_function import stt_function
import time

# Load environment variables
load_dotenv()

class Orchestrator:
    def __init__(self):
        print("Initializing Orchestrator...")
        self.pepper_agent = PepperAgent()
        self.search_agent = SearchAgent()
        self.tts_agent = TTSAgent()

    def classify_request_type(self, prompt):
        """Classify if the request is creative/conversational or factual."""
        conversational_keywords = [
            "joke", "funny", "story", "riddle", "poem", "say hello", 
            "how are you", "what would you do", "tell me about yourself", 
            "let's talk", "let's chat", "make me laugh", "something interesting", 
            "something exciting", "something happy", "something sad", 
            "something angry", "something neutral"
        ]
        return any(word in prompt.lower() for word in conversational_keywords)

    def process_response(self, response):
        """Process the response by splitting into sentences and handling TTS."""
        sentences = split_into_sentences(response)
        tts_timings = []
        total_tts_time = 0

        for sentence in sentences:
            start_time = time.time()
            self.tts_agent.speak(sentence)  # Removed emotion parameter
            tts_time = (time.time() - start_time) * 1000
            tts_timings.append((sentence, tts_time))
            total_tts_time += tts_time

        return sentences, tts_timings, total_tts_time

    def handle_input(self, user_input):
        """Handle user input by routing to appropriate agent and processing response."""
        start_time = time.time()
        
        # Check if it's a conversational/creative query
        conversational_keywords = [
            "how are you", "hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening",
            "how's it going", "what's up", "how do you feel", "tell me about yourself", "who are you",
            "what are you", "what can you do", "what do you like", "what's your favorite",
            "joke", "funny", "story", "riddle", "poem", "let's talk", "let's chat",
            "make me laugh", "something interesting", "something exciting"
        ]
        
        try:
            # If it's a conversational query, use Pepper's personality directly
            if any(keyword in user_input.lower() for keyword in conversational_keywords):
                response = self.pepper_agent.get_response(user_input)
            # For factual queries, use the search agent and format the response
            elif any(keyword in user_input.lower() for keyword in ["weather", "news", "current", "latest", "who", "what", "when", "where", "why", "how"]):
                search_response = self.search_agent.get_response(user_input)
                # Remove "Based on search results:" prefix if present
                response = search_response.replace("Based on search results:", "").strip()
                
                # Format the response based on the query type
                if "weather" in user_input.lower():
                    # Extract just the temperature and conditions
                    parts = response.split(".")
                    response = parts[0] if parts else response
                elif "time" in user_input.lower():
                    # Extract just the current time
                    parts = response.split(".")
                    response = parts[0] if parts else response
                elif "population" in user_input.lower():
                    # Format population response
                    response = f"The population of {user_input.split('of')[-1].strip()} is {response}"
                
                if not response:
                    response = "I'm sorry, I couldn't find that information. Could you please try rephrasing your question?"
            # Default to Pepper's personality for everything else
            else:
                response = self.pepper_agent.get_response(user_input)
            
            llm_time = (time.time() - start_time) * 1000
            
            # Process the response
            sentences, tts_timings, total_tts_time = self.process_response(response)
            
            # Print profiling summary
            print("\n--- Profiling Summary ---")
            print(f"LLM/Agent response: {llm_time:.2f} ms")
            print(f"TTS (total): {total_tts_time:.2f} ms")
            for sentence, tts_time in tts_timings:
                print(f"  TTS for: '{sentence[:30]}...' -> {tts_time:.2f} ms")
            print(f"TOTAL time: {llm_time + total_tts_time:.2f} ms")
            print("-------------------------\n")
            
            return response
            
        except Exception as e:
            print(f"Error in handle_input: {str(e)}")
            return "I apologize, but I encountered an error. Could you please try rephrasing your question?"

def main():
    print("Welcome to Pepper, your AI Assistant with Speech Recognition and Emotion Labeling!")
    print("Press Enter to start speaking, then press Enter again to stop.")
    print("Type 'quit' to exit.")
    
    orchestrator = Orchestrator()
    
    while True:
        input("\nPress Enter to start speaking...")
        user_input, stt_latency = stt_function()
        
        if user_input:
            print(f"\nYou said: {user_input}")
            print(f"Speech recognition took {stt_latency:.2f} ms")
            
            if user_input.lower() != 'quit':
                response = orchestrator.handle_input(user_input)
                print(f"\nPepper: {response}")
            else:
                break
        else:
            print("No speech detected.")

if __name__ == "__main__":
    main() 