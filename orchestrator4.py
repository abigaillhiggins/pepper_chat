from dotenv import load_dotenv
import os
import requests
import threading
from agents.pepper_agent import PepperAgent
from agents.search_agent import SearchAgent
from agents.search_agent3 import SearchAgent3
from agents.summary_agent import SummaryAgent
from utils.sentence_splitter import split_into_sentences
from stt_function import stt_function
import time
import re

# Load environment variables
load_dotenv()

class Orchestrator4:
    def __init__(self):
        print("Initializing Orchestrator4...")
        self.pepper_agent = PepperAgent()
        self.search_agent = SearchAgent()
        self.search_agent3 = SearchAgent3()
        self.summary_agent = SummaryAgent()
        self.pepper_ip = "10.0.0.244"
        self.pepper_port = 5000

    def speak(self, text):
        """Send text to Pepper's TTS endpoint."""
        try:
            url = f"http://{self.pepper_ip}:{self.pepper_port}/say"
            params = {"text": text}
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error in TTS: {str(e)}")
            return None

    def speak_threaded(self, text):
        """Send text to Pepper's TTS endpoint in a separate thread."""
        def speak_in_thread():
            try:
                url = f"http://{self.pepper_ip}:{self.pepper_port}/say"
                params = {"text": text}
                response = requests.get(url, params=params)
                response.raise_for_status()
            except Exception as e:
                print(f"Error in threaded TTS: {str(e)}")
        
        thread = threading.Thread(target=speak_in_thread)
        thread.daemon = True
        thread.start()
        return thread

    def contains_only_emoji(self, text):
        """Check if text contains only emojis and whitespace."""
        # Remove whitespace and check if remaining characters are emojis
        cleaned_text = re.sub(r'\s+', '', text)
        if not cleaned_text:
            return False
        
        # Unicode emoji ranges
        emoji_pattern = re.compile(
            r'[\U0001F600-\U0001F64F]'  # emoticons
            r'|[\U0001F300-\U0001F5FF]'  # symbols & pictographs
            r'|[\U0001F680-\U0001F6FF]'  # transport & map symbols
            r'|[\U0001F1E0-\U0001F1FF]'  # flags (iOS)
            r'|[\U00002600-\U000027BF]'  # miscellaneous symbols
            r'|[\U0001F900-\U0001F9FF]'  # supplemental symbols and pictographs
            r'|[\U0001F018-\U0001F270]'  # various symbols
            r'|[\U0001F004]'              # mahjong tile red dragon
            r'|[\U0001F0CF]'              # playing card black joker
            r'|[\U0001F170-\U0001F251]'   # enclosed alphanumeric supplement
        )
        
        # Check if all non-whitespace characters are emojis
        non_emoji_chars = re.sub(emoji_pattern, '', cleaned_text)
        return len(non_emoji_chars) == 0

    def filter_emoji_sentences(self, sentences):
        """Filter out sentences that contain only emojis."""
        return [sentence for sentence in sentences if not self.contains_only_emoji(sentence)]

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
        
        # Filter out emoji-only sentences
        filtered_sentences = self.filter_emoji_sentences(sentences)
        
        tts_timings = []
        total_tts_time = 0

        for sentence in filtered_sentences:
            start_time = time.time()
            self.speak(sentence)
            tts_time = (time.time() - start_time) * 1000
            tts_timings.append((sentence, tts_time))
            total_tts_time += tts_time

        return filtered_sentences, tts_timings, total_tts_time

    def handle_input(self, user_input):
        """Handle user input by routing to appropriate agent and processing response."""
        start_time = time.time()
        
        # Handle specific exception queries first
        user_input_lower = user_input.lower().strip()
        
        # Exception for location query
        if user_input_lower in ["where am i", "where are we", "what is my location", "where are you"]:
            response = "You are at the UC Collaborative Robotics Lab in Canberra, Australia."
        
        # Exception for VC query
        elif user_input_lower in ["who is the vc of uc", "who is the vice chancellor of uc", "who is the vice chancellor of university of canberra", "who is the vc of university of canberra"]:
            response = "The Vice Chancellor of the University of Canberra is Bill Shorten."
        
        else:
            # Check if it's a conversational query first
            conversational_keywords = [
                "how are you", "hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening",
                "how's it going", "what's up", "how do you feel", "tell me about yourself", "who are you",
                "what are you", "what can you do", "what do you like", "what's your favorite",
                "joke", "funny", "story", "riddle", "poem", "let's talk", "let's chat",
                "make me laugh", "something interesting", "something exciting"
            ]
            
            # Check for summary requests
            summary_keywords = ["summarize", "summary", "brief", "overview", "sum up"]
            if any(keyword in user_input.lower() for keyword in summary_keywords):
                response = self.summary_agent.get_response(user_input)
            
            # Check for advanced search requests (search_agent3) - expanded keywords
            advanced_search_keywords = [
                "detailed", "comprehensive", "in-depth", "research", "advanced", "extensive",
                "tell me more about", "what is", "who is", "when is", "where is", "why is", "how is",
                "current", "latest", "recent", "today", "now", "weather", "time", "population",
                "news", "information", "facts", "data", "statistics"
            ]
            
            # Check if it's a conversational query first
            if any(keyword in user_input.lower() for keyword in conversational_keywords):
                try:
                    response = self.pepper_agent.get_response(user_input)
                except Exception as e:
                    print(f"Pepper agent failed: {str(e)}")
                    response = "I'm having trouble processing that right now. Could you try rephrasing?"
            
            # Check for advanced search requests (search_agent3)
            elif any(keyword in user_input.lower() for keyword in advanced_search_keywords):
                try:
                    print("Using advanced search agent (search_agent3)...")
                    search_start_time = time.time()
                    search_tts_thread = None
                    
                    # Start a timer to check if we need to play the TTS message
                    def check_and_play_tts():
                        time.sleep(1.5)  # Wait 1.5 seconds
                        if not hasattr(self, '_search_completed') or not self._search_completed:
                            print("Search taking longer than 1.5s, playing TTS message")
                            self.speak_threaded("Allow me to search the web for you")
                    
                    tts_timer_thread = threading.Thread(target=check_and_play_tts)
                    tts_timer_thread.daemon = True
                    tts_timer_thread.start()
                    
                    self._search_completed = False
                    raw_response = self.search_agent3.get_response(user_input)
                    self._search_completed = True
                    
                    if not raw_response or raw_response.strip() == "":
                        raise Exception("Empty search response from search_agent3")
                    
                    # Filter the response through the summary agent for Australian context
                    response = self.summary_agent.get_response(raw_response, user_input)
                    
                except Exception as e:
                    print(f"Advanced search failed: {str(e)}. Falling back to regular search.")
                    # Fall back to regular search agent
                    try:
                        search_start_time = time.time()
                        search_tts_thread = None
                        
                        # Start a timer to check if we need to play the TTS message
                        def check_and_play_tts():
                            time.sleep(1.5)  # Wait 1.5 seconds
                            if not hasattr(self, '_search_completed') or not self._search_completed:
                                print("Search taking longer than 1.5s, playing TTS message")
                                self.speak_threaded("Allow me to search the web for you")
                        
                        tts_timer_thread = threading.Thread(target=check_and_play_tts)
                        tts_timer_thread.daemon = True
                        tts_timer_thread.start()
                        
                        self._search_completed = False
                        raw_search_response = self.search_agent.get_response(user_input)
                        self._search_completed = True
                        
                        raw_response = raw_search_response.replace("Based on search results:", "").strip()
                        if not raw_response:
                            raise Exception("Empty search response from regular search")
                        
                        # Filter the response through the summary agent for Australian context
                        response = self.summary_agent.get_response(raw_response, user_input)
                        
                    except Exception as e2:
                        print(f"Regular search also failed: {str(e2)}. Falling back to conversational response.")
                        response = self.pepper_agent.get_response(
                            f"I notice you're asking about {user_input}. While I can't access current information right now, "
                            f"I'd be happy to chat about this topic from my perspective. What would you like to know?"
                        )
            
            # Default to Pepper's personality for everything else
            else:
                try:
                    response = self.pepper_agent.get_response(user_input)
                except Exception as e:
                    print(f"Error in handle_input: {str(e)}")
                    return "I apologize, but I encountered an error. Could you please try rephrasing your question?"
        
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

def main():
    print("Welcome to Pepper, your AI Assistant with Speech Recognition and HTTP-based TTS!")
    print("Press Enter to start speaking, then press Enter again to stop.")
    print("Type 'quit' to exit.")
    
    orchestrator = Orchestrator4()
    
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
