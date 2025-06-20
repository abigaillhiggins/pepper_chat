from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain_community.tools import Tool
from langchain.memory import ConversationBufferMemory
import time
from functools import lru_cache
import concurrent.futures
import threading
import re
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GoogleSearchTool:
    """Custom Google Search tool for LangChain."""
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        if not self.search_engine_id:
            raise ValueError("GOOGLE_SEARCH_ENGINE_ID not found in environment variables")
    
    def run(self, query):
        """Execute Google Custom Search."""
        try:
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': 3  # Get top 3 results
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if 'items' in data and data['items']:
                # Combine snippets from top results
                snippets = []
                for item in data['items'][:3]:
                    if 'snippet' in item:
                        snippets.append(item['snippet'])
                
                return ' '.join(snippets)
            else:
                return None
                
        except Exception as e:
            print(f"Google Search error: {str(e)}")
            return None

class SearchAgent2:
    def __init__(self):
        # Use GPT-4o for chat-style, multi-turn memory
        self.llm = ChatOpenAI(temperature=0.7, model_name="gpt-4o")
        self.search = GoogleSearchTool()
        
        # Limit memory to last 3 messages and 500 tokens
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            max_messages=3,
            max_token_limit=500
        )
        
        # Define tools
        self.tools = [
            Tool(
                name="GoogleSearch",
                func=self.search.run,
                description="Useful for searching the internet to find information about current events, facts, or general knowledge using Google Custom Search."
            )
        ]
        
        # Condensed system message focusing on search functionality
        self.agent = initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            system_message="""You are a factual assistant. Use Google Search for accurate, up-to-date information. \
            Keep responses under 220 characters and end with proper punctuation. \
            Focus on providing concise, search-based answers. \
            ALWAYS use metric units: Celsius for temperature, kilometers for distance, kilograms for weight, meters for height. \
            For weather queries, include temperature in Celsius and conditions. \
            For time queries, include only the current time. \
            For population queries, include only the number."""
        )
        
        # Initialize cache for common responses
        self.response_cache = {}
        self.cache_ttl = 3600  # Cache responses for 1 hour
        self.cache_lock = threading.Lock()
        self.last_search_time = 0
        self.min_search_interval = 1  # Minimum seconds between searches

    @lru_cache(maxsize=100)
    def _get_cached_response(self, prompt):
        """Get a cached response if available and not expired."""
        with self.cache_lock:
            if prompt in self.response_cache:
                timestamp, response = self.response_cache[prompt]
                if time.time() - timestamp < self.cache_ttl:
                    return response
        return None

    def _cache_response(self, prompt, response):
        """Cache a response with timestamp."""
        with self.cache_lock:
            self.response_cache[prompt] = (time.time(), response)

    def _optimize_query(self, prompt):
        """Optimize the search query for better results."""
        prompt_lower = prompt.lower()
        
        # Weather queries
        if "weather" in prompt_lower:
            location = self._extract_location(prompt)
            if location and location != "that location":
                return f"current weather {location} temperature today"
            return "current weather temperature today"
        
        # News queries
        if any(word in prompt_lower for word in ["news", "latest", "current"]):
            # Extract key terms for news
            words = prompt.split()
            key_terms = [word for word in words if word.lower() not in 
                        ["what", "is", "the", "latest", "news", "on", "about", "current", "today"]]
            if key_terms:
                return f"latest news {' '.join(key_terms[:3])} today"
            return "latest news today"
        
        # Time queries
        if "time" in prompt_lower:
            location = self._extract_location(prompt)
            if location and location != "that location":
                return f"current time {location} now"
            return "current time now"
        
        # Population queries
        if "population" in prompt_lower:
            location = self._extract_location(prompt)
            if location and location != "that location":
                return f"population {location} 2024"
            return prompt
        
        # General optimization - remove common words and focus on key terms
        stop_words = {"what", "is", "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        words = [word for word in prompt.split() if word.lower() not in stop_words]
        return " ".join(words[:5])  # Limit to 5 key words

    def _try_multiple_search_strategies(self, prompt):
        """Try multiple search strategies to improve success rate."""
        strategies = [
            prompt,  # Original query
            self._optimize_query(prompt),  # Optimized query
            f"{prompt} 2024",  # Add current year for recent info
            f"latest {prompt}",  # Add "latest" for current info
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                print(f"Trying Google search strategy {i+1}: {strategy}")
                result = self.search.run(strategy)
                if result and len(result.strip()) > 10:  # Ensure we got meaningful results
                    print(f"Google search strategy {i+1} succeeded!")
                    return result
                else:
                    print(f"Google search strategy {i+1} returned empty or short result")
            except Exception as e:
                print(f"Google search strategy {i+1} failed: {strategy} - {str(e)}")
                continue
        
        return None

    def _make_conversational(self, prompt, text):
        """Convert factual search results into a conversational, symbol-free, non-repetitive response."""
        # Clean the text
        text = text.replace('°', ' degrees')
        text = text.replace(':', '')
        text = re.sub(r'\[.*?\]', '', text)
        text = re.sub(r'\(.*?\)', '', text)
        text = re.sub(r'[^\w\s.,?!]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()

        prompt_lower = prompt.lower()
        location = self._extract_location(prompt)

        # Helper to extract numbers or names
        def extract_temperature(s):
            # Look for temperature patterns
            patterns = [
                r'(\d{1,3})\s*degrees?\s*(celsius|fahrenheit)?',
                r'(\d{1,3})\s*(celsius|fahrenheit)',
                r'(\d{1,3})\s*°\s*(c|f)',
                r'(\d{1,3})'
            ]
            for pattern in patterns:
                match = re.search(pattern, s, re.I)
                if match:
                    temp = match.group(1)
                    unit = match.group(2) if len(match.groups()) > 1 and match.group(2) else "degrees"
                    return f"{temp} {unit}"
            return None

        def extract_population(s):
            # Look for population patterns
            patterns = [
                r'(\d+[,.]?\d*\s*(million|billion|thousand|people))',
                r'(\d{1,3}(,\d{3})+)',
                r'(\d+)'
            ]
            for pattern in patterns:
                match = re.search(pattern, s, re.I)
                if match:
                    return match.group(0)
            return None

        def extract_time(s):
            match = re.search(r'(\d{1,2}:\d{2}(?:\s*[APMapm]{2})?)', s)
            if match:
                return match.group(1)
            return None

        def extract_name(s):
            # Try to extract a proper name (two capitalized words)
            match = re.search(r'([A-Z][a-z]+ [A-Z][a-z]+)', s)
            if match:
                return match.group(1)
            # Try to extract a single capitalized word (for capitals)
            match = re.search(r'([A-Z][a-z]+)', s)
            if match:
                return match.group(1)
            return None

        # Weather
        if "weather" in prompt_lower:
            temp = extract_temperature(text)
            if temp:
                return f"It's about {temp} in {location} right now."
            return f"Sorry, I couldn't find the current temperature for {location}."
        
        # Time
        elif "time" in prompt_lower:
            t = extract_time(text)
            if t:
                return f"The current time in {location} is {t}."
            return f"Sorry, I couldn't find the current time for {location}."
        
        # Population
        elif "population" in prompt_lower:
            pop = extract_population(text)
            if pop:
                return f"The population of {location} is {pop}."
            return f"Sorry, I couldn't find the population for {location}."
        
        # News queries
        elif any(word in prompt_lower for word in ["news", "latest", "current"]):
            # Extract the most relevant sentence
            sentences = text.split('.')
            for sentence in sentences:
                if len(sentence.strip()) > 20 and any(word in sentence.lower() for word in prompt_lower.split()):
                    return sentence.strip() + "."
            return sentences[0].strip() + "." if sentences else text
        
        # General fallback
        else:
            # Return the first concise sentence
            first_sentence = text.split('.')[0]
            return first_sentence if len(first_sentence.split()) > 2 else text

    def _extract_location(self, prompt):
        """Extract location from prompt for conversational responses."""
        # More comprehensive location extraction
        patterns = [
            r'in ([A-Za-z ]+)',
            r'of ([A-Za-z ]+)',
            r'at ([A-Za-z ]+)',
            r'([A-Za-z ]+) weather',
            r'([A-Za-z ]+) time',
            r'([A-Za-z ]+) population'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, prompt, re.I)
            if match:
                location = match.group(1).strip()
                # Filter out common words that aren't locations
                if location.lower() not in ["that", "this", "the", "current", "latest"]:
                    return location
        
        return "that location"

    def _format_search_response(self, prompt, search_result):
        """Format the search result based on the query type and make it conversational."""
        prompt_lower = prompt.lower()
        
        if "weather" in prompt_lower:
            # Extract temperature and conditions
            parts = search_result.split(".")
            for part in parts:
                if "°" in part or "temperature" in part.lower() or "degrees" in part.lower():
                    return self._make_conversational(prompt, part.strip())
            return self._make_conversational(prompt, search_result.split(".")[0].strip())
        
        elif "time" in prompt_lower:
            # Extract just the time
            parts = search_result.split(".")
            for part in parts:
                if ":" in part and any(str(i) in part for i in range(24)):
                    return self._make_conversational(prompt, part.strip())
            return self._make_conversational(prompt, search_result.split(".")[0].strip())
        
        elif "population" in prompt_lower:
            return self._make_conversational(prompt, search_result.split('.')[0].strip())
        
        # Add more cases as needed
        return self._make_conversational(prompt, search_result)

    def _parallel_search_and_llm(self, prompt):
        """Execute search and LLM calls in parallel with improved error handling."""
        current_time = time.time()
        if current_time - self.last_search_time < self.min_search_interval:
            time.sleep(self.min_search_interval)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            # Start both tasks
            search_future = executor.submit(self._try_multiple_search_strategies, prompt)
            llm_future = executor.submit(self.llm.invoke, f"Please provide a factual response to: {prompt}")
            
            # Get results
            try:
                search_result = search_future.result(timeout=10)  # Increased timeout for search
                self.last_search_time = time.time()
                
                if search_result:
                    formatted_result = self._format_search_response(prompt, search_result)
                    return formatted_result
                    
                # If search fails, use LLM result
                llm_result = llm_future.result(timeout=5)
                return llm_result.content.strip()
                
            except concurrent.futures.TimeoutError:
                # If search times out, use LLM result
                try:
                    return llm_future.result(timeout=2).content.strip()
                except:
                    return "I apologize, but I encountered an error while searching. Could you please try rephrasing your question?"
            except Exception as e:
                print(f"Search error: {str(e)}")
                try:
                    return llm_future.result(timeout=2).content.strip()
                except:
                    return "I apologize, but I encountered an error while searching. Could you please try rephrasing your question?"

    def get_response(self, prompt):
        """Get a response using the search agent for factual queries."""
        try:
            # Check cache first
            cached_response = self._get_cached_response(prompt)
            if cached_response:
                return cached_response

            # Use parallel processing for search and LLM
            response = self._parallel_search_and_llm(prompt)
            
            # Truncate response to 200 characters, ending at last full sentence if possible
            if len(response) > 200:
                truncated = response[:200]
                last_punct = max(truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))
                if last_punct != -1:
                    response = truncated[:last_punct+1]
                else:
                    response = truncated
            
            # Cache the response
            self._cache_response(prompt, response)
            return response
            
        except Exception as e:
            print(f"Error in SearchAgent2.get_response: {str(e)}")
            # Fallback to LLM for rate-limited queries
            try:
                fallback_prompt = f"Please provide a factual response to: {prompt}"
                response = self.llm.invoke(fallback_prompt).content.strip()
                return response
            except Exception as e2:
                print(f"Error in fallback response: {str(e2)}")
                return "I apologize, but I encountered an error while searching. Could you please try rephrasing your question?" 