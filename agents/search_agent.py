from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain_community.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.memory import ConversationBufferMemory
import time
from functools import lru_cache
import concurrent.futures
import threading

class SearchAgent:
    def __init__(self):
        # Use GPT-4o for chat-style, multi-turn memory
        self.llm = ChatOpenAI(temperature=0.7, model_name="gpt-4o")
        self.search = DuckDuckGoSearchRun()
        
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
                name="Search",
                func=self.search.run,
                description="Useful for searching the internet to find information about current events, facts, or general knowledge."
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
            system_message="""You are a factual assistant. Use search for accurate, up-to-date information. \
            Keep responses under 220 characters and end with proper punctuation. \
            Focus on providing concise, search-based answers. \
            For weather queries, include temperature and conditions. \
            For time queries, include only the current time. \
            For population queries, include only the number."""
        )
        
        # Initialize cache for common responses
        self.response_cache = {}
        self.cache_ttl = 3600  # Cache responses for 1 hour
        self.cache_lock = threading.Lock()
        self.last_search_time = 0
        self.min_search_interval = 2  # Minimum seconds between searches

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

    def _make_conversational(self, prompt, text):
        """Convert factual search results into a conversational, symbol-free, non-repetitive response."""
        import re
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
            match = re.search(r'(\d{1,3})\s*degrees?\s*(celsius|fahrenheit)?', s, re.I)
            if match:
                temp = match.group(1)
                unit = match.group(2) if match.group(2) else "degrees"
                return f"{temp} {unit}"
            match = re.search(r'(\d{1,3})', s)
            if match:
                return f"{match.group(1)} degrees"
            return None
        def extract_population(s):
            # Look for numbers followed by 'million', 'billion', 'thousand', or 'people'
            match = re.search(r'(\d+[,.]?\d*\s*(million|billion|thousand|people))', s, re.I)
            if match:
                return match.group(0)
            # Look for large numbers with commas (e.g., 9,000,000)
            match = re.search(r'(\d{1,3}(,\d{3})+)', s)
            if match:
                return match.group(0)
            # Look for any standalone number (fallback)
            match = re.search(r'(\d+)', s)
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
        # Capital
        elif "capital" in prompt_lower:
            city = extract_name(text)
            if city and city.lower() != location.lower():
                return f"The capital is {city}."
            return f"Sorry, I couldn't find the capital for {location}."
        # President
        elif "president" in prompt_lower:
            name = extract_name(text)
            if name and name.lower() not in location.lower():
                return f"The president is {name}."
            return f"Sorry, I couldn't find the president for {location}."
        # Mount Everest
        elif "mount everest" in prompt_lower:
            height = extract_population(text) or extract_temperature(text)
            if height:
                return f"Mount Everest is {height} tall."
            return f"Sorry, I couldn't find the height of Mount Everest."
        # Speed of light
        elif "speed of light" in prompt_lower:
            speed = extract_population(text) or extract_temperature(text)
            if speed:
                return f"The speed of light is {speed}."
            return f"Sorry, I couldn't find the speed of light."
        # Declaration of Independence
        elif "declaration of independence" in prompt_lower:
            year = re.search(r'(17\d{2}|18\d{2})', text)
            if year:
                return f"The Declaration of Independence was signed in {year.group(1)}."
            return f"Sorry, I couldn't find the year the Declaration of Independence was signed."
        # General fallback
        else:
            # Return the first concise sentence
            first_sentence = text.split('.')[0]
            return first_sentence if len(first_sentence.split()) > 2 else text

    def _extract_location(self, prompt):
        """Extract location from prompt for conversational responses."""
        import re
        match = re.search(r'in ([A-Za-z ]+)', prompt)
        if match:
            return match.group(1).strip()
        match = re.search(r'of ([A-Za-z ]+)', prompt)
        if match:
            return match.group(1).strip()
        return "that location"

    def _format_search_response(self, prompt, search_result):
        """Format the search result based on the query type and make it conversational."""
        prompt_lower = prompt.lower()
        
        if "weather" in prompt_lower:
            # Extract temperature and conditions
            parts = search_result.split(".")
            for part in parts:
                if "°" in part or "temperature" in part.lower():
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
            city = self._extract_location(prompt)
            return self._make_conversational(prompt, search_result.split('.')[0].strip())
        # Add more cases as needed
        return self._make_conversational(prompt, search_result)

    def _parallel_search_and_llm(self, prompt):
        """Execute search and LLM calls in parallel."""
        current_time = time.time()
        if current_time - self.last_search_time < self.min_search_interval:
            time.sleep(self.min_search_interval)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            # Start both tasks
            search_future = executor.submit(self.search.run, prompt)
            llm_future = executor.submit(self.llm.invoke, f"Please provide a factual response to: {prompt}")
            
            # Get results
            try:
                search_result = search_future.result(timeout=5)  # 5 second timeout for search
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
            print(f"Error in SearchAgent.get_response: {str(e)}")
            # Fallback to LLM for rate-limited queries
            try:
                fallback_prompt = f"Please provide a factual response to: {prompt}"
                response = self.llm.invoke(fallback_prompt).content.strip()
                return response
            except Exception as e2:
                print(f"Error in fallback response: {str(e2)}")
                return "I apologize, but I encountered an error while searching. Could you please try rephrasing your question?" 