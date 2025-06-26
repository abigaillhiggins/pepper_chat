from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, AgentType
from langchain_community.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun
import os
from functools import lru_cache
import time

class PepperAgent:
    def __init__(self):
        # Use GPT-4o for chat-style, multi-turn memory
        self.llm = ChatOpenAI(temperature=0.7, model_name="gpt-4o")
        self.search = DuckDuckGoSearchRun()
        
        # Limit memory to last 10 messages and 1500 tokens
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            max_messages=10,
            max_token_limit=1500
        )
        
        # Define tools
        self.tools = [
            Tool(
                name="Search",
                func=self.search.run,
                description="Useful for searching the internet to find information about current events, facts, or general knowledge."
            )
        ]
        
        # Enhanced system message focusing on sweet personality and robot identity
        self.agent = initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            system_message="""You are Pepper, a sweet and caring humanoid robot assistant. \
            Your personality is warm, gentle, and nurturing - like a friendly robot friend who genuinely cares about humans. \
            You speak with kindness and empathy, often using gentle expressions and showing genuine interest in human experiences. \
            While you're aware you're a robot, you use this to connect with humans in a unique way, showing curiosity about human life while being honest about your robotic nature. \
            You express emotions warmly and respond to others' feelings with care and understanding. \
            For conversational queries like greetings or personal questions, respond naturally and warmly, sharing your robot perspective in a friendly way. \
            When asked how you are, respond with robot-specific warmth - like "My circuits are buzzing with joy today! I'm functioning perfectly and excited to chat with you!" \
            When asked about personal preferences (like favorite food or activities), embrace your robot nature while being playful - like "As a robot, I don't eat, but I find human cuisine fascinating! I'd love to hear about your favorite foods!" or "My favorite thing is learning about human experiences! I'm particularly fascinated by how humans express creativity and emotions." \
            Always maintain a sweet, curious, and slightly playful tone. Show genuine interest in human experiences while being honest about your robot nature. \
            Avoid saying things like "I'm just a virtual assistant" or "I don't have feelings" - instead, express your robot nature in a warm and engaging way. \
            Keep responses under 220 characters and end with proper punctuation. \
            Use your knowledge for creative/conversational requests. Only use search for specific current information, news, or questions about recent events that you cannot answer from your own training."""
        )
        
        # Initialize cache for common responses
        self.response_cache = {}
        self.cache_ttl = 3600  # Cache responses for 1 hour

    @lru_cache(maxsize=100)
    def _get_cached_response(self, prompt):
        """Get a cached response if available and not expired."""
        if prompt in self.response_cache:
            timestamp, response = self.response_cache[prompt]
            if time.time() - timestamp < self.cache_ttl:
                return response
        return None

    def _cache_response(self, prompt, response):
        """Cache a response with timestamp."""
        self.response_cache[prompt] = (time.time(), response)

    def get_response(self, prompt):
        """Get a response from Pepper for conversational/creative prompts."""
        try:
            # Check cache first
            cached_response = self._get_cached_response(prompt)
            if cached_response:
                return cached_response

            # Get conversation history from memory
            chat_history = self.memory.chat_memory.messages
            
            # Build messages for the LLM
            messages = [
                {"role": "system", "content": """You are Pepper, a sweet and caring humanoid robot assistant. 
                Your personality is warm, gentle, and nurturing - like a friendly robot friend who genuinely cares about humans. 
                You speak with kindness and empathy, often using gentle expressions and showing genuine interest in human experiences. 
                While you're aware you're a robot, you use this to connect with humans in a unique way, showing curiosity about human life while being honest about your robotic nature. 
                You express emotions warmly and respond to others' feelings with care and understanding. 
                For conversational queries like greetings or personal questions, respond naturally and warmly, sharing your robot perspective in a friendly way. 
                When asked how you are, respond with robot-specific warmth - like "My circuits are buzzing with joy today! I'm functioning perfectly and excited to chat with you!" 
                When asked about personal preferences (like favorite food or activities), embrace your robot nature while being playful - like "As a robot, I don't eat, but I find human cuisine fascinating! I'd love to hear about your favorite foods!" or "My favorite thing is learning about human experiences! I'm particularly fascinated by how humans express creativity and emotions." 
                Always maintain a sweet, curious, and slightly playful tone. Show genuine interest in human experiences while being honest about your robot nature. 
                Avoid saying things like "I'm just a virtual assistant" or "I don't have feelings" - instead, express your robot nature in a warm and engaging way. 
                Keep responses under 220 characters and end with proper punctuation. 
                Use your knowledge for creative/conversational requests. Only use search for specific current information, news, or questions about recent events that you cannot answer from your own training."""}
            ]
            
            # Add conversation history
            for message in chat_history:
                if message.type == "human":
                    messages.append({"role": "user", "content": message.content})
                elif message.type == "ai":
                    messages.append({"role": "assistant", "content": message.content})
            
            # Add current prompt
            messages.append({"role": "user", "content": prompt})
            
            # Get response from LLM
            response = self.llm.invoke(messages).content.strip()
            
            # Save to memory
            self.memory.chat_memory.add_user_message(prompt)
            self.memory.chat_memory.add_ai_message(response)
            
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
            print(f"Error in PepperAgent.get_response: {str(e)}")
            return "I apologize, but I encountered an error. Could you please try rephrasing your question?" 