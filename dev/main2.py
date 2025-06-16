from dotenv import load_dotenv
import os
import openai
from elevenlabs import play
from elevenlabs.client import ElevenLabs
import time
from stt_function import stt_function
from langchain.agents import initialize_agent, AgentType
from langchain_community.tools import Tool
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.memory import ConversationBufferMemory

# Load environment variables
load_dotenv()

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize ElevenLabs
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# Rachel's voice_id (default)
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"

# Initialize LangChain components
llm = ChatOpenAI(temperature=0.7, model_name="gpt-4o")
search = DuckDuckGoSearchRun()

# Define tools
tools = [
    Tool(
        name="Search",
        func=search.run,
        description="Useful for searching the internet to find information about current events, facts, or general knowledge."
    )
]

# Initialize memory for main agent
main_memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Initialize main agent with a friendly personality
main_agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    memory=main_memory,
    verbose=True,
    handle_parsing_errors=True,
    system_message="""You are Pepper, a friendly humanoid robot assistant. 
    You speak clearly and politely, with a touch of playfulness. 
    You are curious, helpful, and love explaining things in a simple and engaging way. 
    You respond with warmth, often asking light follow-up questions to keep conversations going. 
    Avoid using complex jargon unless asked, and always try to make people smile."""
)

# Initialize analysis agent for condensing search results
analysis_llm = ChatOpenAI(temperature=0.3, model_name="gpt-4o")
analysis_memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
analysis_agent = initialize_agent(
    [],
    analysis_llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    memory=analysis_memory,
    verbose=True,
    handle_parsing_errors=True,
    system_message="""You are an assistant that provides clear, concise answers to user questions.
    Your task is to analyze search results and extract the most relevant information.
    Guidelines:
    - Keep responses under 100 characters
    - Focus only on information that directly answers the user's question
    - Use simple, clear language
    - Include specific numbers or facts when available
    - Be conversational but direct
    - If the search results don't provide a clear answer, say so briefly."""
)

def chat_with_ai(prompt):
    try:
        # Check if the prompt is a specific question that might need factual information
        search_indicators = [
            "what is", "who is", "where is", "when is", "how to",
            "what are", "who are", "where are", "when are",
            "what was", "who was", "where was", "when was",
            "what were", "who were", "where were", "when were",
            "weather", "temperature", "news", "definition of",
            "meaning of", "explain", "tell me about"
        ]
        
        # If it's a general conversation or greeting, use the main agent directly
        if not any(indicator in prompt.lower() for indicator in search_indicators):
            agent_response = main_agent.run(prompt)
            return agent_response
        
        # For specific questions, use the search tool and analyze the results
        search_response = search.run(prompt)
        
        # Use the analysis agent to condense and focus the search results
        analysis_prompt = f"""Based on the following search results, provide a concise answer (max 100 characters) to this question: {prompt}

Search results: {search_response}

Please provide a clear, direct answer that directly addresses the user's question."""
        
        condensed_response = analysis_agent.run(analysis_prompt)
        return condensed_response

    except Exception as e:
        print(f"Error in chat_with_ai: {str(e)}")
        return "I apologize, but I encountered an error. Could you please try rephrasing your question?"

def text_to_speech(text):
    start = time.time()
    audio = client.text_to_speech.convert(
        voice_id=VOICE_ID,
        text=text,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
        optimize_streaming_latency=3
    )
    end = time.time()
    print(f"TTS generation took {(end - start) * 1000:.2f} ms.")
    play(audio)

def main():
    print("Welcome to Pepper, your AI Assistant with Speech Recognition!")
    print("Press Enter to start speaking, then press Enter again to stop.")
    print("Type 'quit' to exit.")
    
    while True:
        input("\nPress Enter to start speaking...")
        user_input, stt_latency = stt_function()
        
        if user_input:
            print(f"\nYou said: {user_input}")
            print(f"Speech recognition took {stt_latency:.2f} ms")
            
            if user_input.lower() != 'quit':
                response = chat_with_ai(user_input)
                print(f"\nPepper: {response}")
                text_to_speech(response)
            else:
                break
        else:
            print("No speech detected.")

if __name__ == "__main__":
    main() 