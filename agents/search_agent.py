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
            Focus on providing concise, search-based answers."""
        )
        
        # Initialize cache for common responses
        self.response_cache = {}
        self.cache_ttl = 3600  # Cache responses for 1 hour
        self.cache_lock = threading.Lock()

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

    def _parallel_search_and_llm(self, prompt):
        """Execute search and LLM calls in parallel."""
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            # Start both tasks
            search_future = executor.submit(self.search.run, prompt)
            llm_future = executor.submit(self.llm.invoke, f"Please provide a factual response to: {prompt}")
            
            # Get results
            try:
                search_result = search_future.result(timeout=5)  # 5 second timeout for search
                llm_result = llm_future.result(timeout=5)  # 5 second timeout for LLM
                
                # Combine results if search was successful
                if search_result:
                    return f"Based on search results: {search_result}"
                return llm_result.content.strip()
            except concurrent.futures.TimeoutError:
                # If search times out, use LLM result
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

            # Add a small delay to avoid rate limits
            time.sleep(1)
            
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