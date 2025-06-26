import requests
import json
import time
from functools import lru_cache
import threading
from langchain_openai import ChatOpenAI
import re

class SearchAgent3:
    def __init__(self):
        # Custom search API configuration
        self.search_api_url = "http://192.168.194.33:8060/search"
        self.search_api_format = "json"
        
        # LLM for processing search results
        self.llm = ChatOpenAI(temperature=0.3, model_name="gpt-4o")
        
        # Cache configuration
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

    def _search_api_call(self, query):
        """Make a call to the custom search API."""
        try:
            params = {
                "q": query,
                "format": self.search_api_format
            }
            
            response = requests.get(self.search_api_url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Search API error: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            return None

    def _extract_relevant_content(self, search_results, query):
        """Extract and format relevant content from search results."""
        if not search_results or 'results' not in search_results:
            return ""
        
        results = search_results['results']
        if not results:
            return ""
        
        # Combine content from top results
        combined_content = ""
        max_results = min(3, len(results))  # Use top 3 results
        
        for i in range(max_results):
            result = results[i]
            if 'content' in result and result['content']:
                combined_content += f"{result['content']} "
            if 'title' in result and result['title']:
                combined_content += f"{result['title']} "
        
        return combined_content.strip()

    def _make_conversational(self, prompt, search_content):
        """Convert search results into a conversational response."""
        if not search_content:
            return "I couldn't find specific information about that. Could you try rephrasing your question?"
        
        # Clean up the content
        import re
        cleaned_content = re.sub(r'[^\w\s.,?!]', '', search_content)
        cleaned_content = re.sub(r'\s+', ' ', cleaned_content).strip()
        
        # Use LLM to create a conversational response
        try:
            system_prompt = """You are a helpful assistant that converts search results into conversational responses. 
            Keep responses under 200 characters, natural and engaging. 
            Focus on the most relevant information from the search results."""
            
            user_prompt = f"Query: {prompt}\nSearch results: {cleaned_content[:1000]}\n\nCreate a conversational response:"
            
            response = self.llm.invoke([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]).content.strip()
            
            return response
            
        except Exception as e:
            print(f"LLM processing error: {str(e)}")
            # Fallback: return first sentence of search content
            first_sentence = cleaned_content.split('.')[0]
            return first_sentence if len(first_sentence.split()) > 2 else cleaned_content[:150]

    def _format_special_queries(self, prompt, search_results):
        """Handle special query types with specific formatting."""
        prompt_lower = prompt.lower()
        
        if "weather" in prompt_lower:
            return self._format_weather_response(prompt, search_results)
        elif "time" in prompt_lower:
            return self._format_time_response(prompt, search_results)
        elif "population" in prompt_lower:
            return self._format_population_response(prompt, search_results)
        else:
            return self._make_conversational(prompt, self._extract_relevant_content(search_results, prompt))

    def _format_weather_response(self, prompt, search_results):
        """Format weather-specific responses."""
        content = self._extract_relevant_content(search_results, prompt)
        
        # Extract temperature and conditions
        temp_match = re.search(r'(\d{1,3})\s*degrees?\s*(celsius|fahrenheit)?', content, re.I)
        if temp_match:
            temp = temp_match.group(1)
            unit = temp_match.group(2) if temp_match.group(2) else "degrees"
            location = self._extract_location(prompt)
            return f"It's about {temp} {unit} in {location} right now."
        
        return self._make_conversational(prompt, content)

    def _format_time_response(self, prompt, search_results):
        """Format time-specific responses."""
        content = self._extract_relevant_content(search_results, prompt)
        
        # Extract time
        time_match = re.search(r'(\d{1,2}:\d{2}(?:\s*[APMapm]{2})?)', content)
        if time_match:
            time_str = time_match.group(1)
            location = self._extract_location(prompt)
            return f"The current time in {location} is {time_str}."
        
        return self._make_conversational(prompt, content)

    def _format_population_response(self, prompt, search_results):
        """Format population-specific responses."""
        content = self._extract_relevant_content(search_results, prompt)
        
        # Extract population numbers
        pop_match = re.search(r'(\d+[,.]?\d*\s*(million|billion|thousand|people))', content, re.I)
        if pop_match:
            population = pop_match.group(0)
            location = self._extract_location(prompt)
            return f"The population of {location} is {population}."
        
        return self._make_conversational(prompt, content)

    def _extract_location(self, prompt):
        """Extract location from prompt for conversational responses."""
        match = re.search(r'in ([A-Za-z ]+)', prompt)
        if match:
            return match.group(1).strip()
        match = re.search(r'of ([A-Za-z ]+)', prompt)
        if match:
            return match.group(1).strip()
        return "that location"

    def get_response(self, prompt):
        """Get a response using the custom search API."""
        try:
            # Check cache first
            cached_response = self._get_cached_response(prompt)
            if cached_response:
                return cached_response

            # Rate limiting
            current_time = time.time()
            if current_time - self.last_search_time < self.min_search_interval:
                time.sleep(self.min_search_interval)
            
            # Make search API call
            search_results = self._search_api_call(prompt)
            
            if not search_results:
                return "I apologize, but I couldn't access the search service right now. Could you try again later?"
            
            # Process and format the response
            response = self._format_special_queries(prompt, search_results)
            
            # Truncate response if too long
            if len(response) > 200:
                truncated = response[:200]
                last_punct = max(truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))
                if last_punct != -1:
                    response = truncated[:last_punct+1]
                else:
                    response = truncated
            
            # Cache the response
            self._cache_response(prompt, response)
            self.last_search_time = time.time()
            
            return response
            
        except Exception as e:
            print(f"Error in SearchAgent3.get_response: {str(e)}")
            return "I apologize, but I encountered an error while searching. Could you please try rephrasing your question?" 