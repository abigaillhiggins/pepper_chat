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
import re

# Load environment variables
load_dotenv()

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize ElevenLabs
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# Rachel's voice_id (default)
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"

# Initialize LangChain components
llm = ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo")
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
    system_message="""You are Pepper, a friendly humanoid robot assistant. \
    You speak clearly and politely, with a touch of playfulness. \
    You are curious, helpful, and love explaining things in a simple and engaging way. \
    You respond with warmth, often asking light follow-up questions to keep conversations going. \
    Avoid using complex jargon unless asked, and always try to make people smile. \
    IMPORTANT: Always keep your response under 220 characters, and if you must cut off, try to end with a complete sentence and proper punctuation (., !, or ?). If your response is short, still end with a complete sentence and punctuation. \
    Whenever possible, answer using your own knowledge. Do NOT use the search tool for jokes, stories, riddles, or any casually conversational or creative requests. Only use the search tool for specific current information, news, or questions about recent events that you cannot answer from your own training."""
)

# Initialize analysis agent for condensing search results
analysis_llm = ChatOpenAI(temperature=0.3, model_name="gpt-3.5-turbo")
analysis_memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
analysis_agent = initialize_agent(
    [],
    analysis_llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    memory=analysis_memory,
    verbose=True,
    handle_parsing_errors=True,
    system_message="""You are an assistant that provides clear, concise answers to user questions.\nYour task is to analyze search results and extract the most relevant information.\nGuidelines:\n- Keep responses under 100 characters\n- Focus only on information that directly answers the user's question\n- Use simple, clear language\n- Include specific numbers or facts when available\n- Be conversational but direct\n- If the search results don't provide a clear answer, say so briefly."""
)

def split_into_sentences(text):
    # Simple sentence splitter using regex
    sentence_endings = re.compile(r'(?<=[.!?]) +')
    return [s.strip() for s in sentence_endings.split(text) if s.strip()]

def is_conversational_or_creative(prompt):
    conversational_keywords = [
        "joke", "funny", "story", "riddle", "poem", "say hello", "how are you", "what would you do", "tell me about yourself", "let's talk", "let's chat", "make me laugh", "something interesting", "something exciting", "something happy", "something sad", "something angry", "something neutral"
    ]
    return any(word in prompt.lower() for word in conversational_keywords)

def chat_with_ai(prompt):
    try:
        if is_conversational_or_creative(prompt):
            # Use LLM directly for conversational/creative prompts
            response = llm.invoke(prompt).content.strip()
        else:
            # Use the agent (with tools) for everything else
            response = main_agent.run(prompt)
        return response
    except Exception as e:
        print(f"Error in chat_with_ai: {str(e)}")
        return "I apologize, but I encountered an error. Could you please try rephrasing your question?"

def text_to_speech(text, emotion="neutral"):
    # Map emotion to ElevenLabs voice_settings
    emotion_voice_settings = {
        "happy": {"stability": 0.3, "similarity_boost": 0.8},
        "sad": {"stability": 0.7, "similarity_boost": 0.5},
        "angry": {"stability": 0.2, "similarity_boost": 0.7},
        "neutral": {"stability": 0.5, "similarity_boost": 0.75},
    }
    settings = emotion_voice_settings.get(emotion, emotion_voice_settings["neutral"])
    start = time.time()
    audio = client.text_to_speech.convert(
        voice_id=VOICE_ID,
        text=text,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
        voice_settings=settings
    )
    end = time.time()
    print(f"TTS generation took {(end - start) * 1000:.2f} ms.")
    play(audio)

def get_emotional_tags_llm(sentence, llm):
    """
    Use the LLM to classify the emotion of a sentence. Only return one of: happy, sad, angry, neutral.
    """
    prompt = (
        f"Classify the emotion of the following sentence as one of: happy, sad, angry, or neutral. "
        f"Respond with only the tag (happy, sad, angry, or neutral) and nothing else.\n"
        f"Sentence: {sentence}"
    )
    response = llm.invoke(prompt)
    tag = response.content.strip().lower()
    # Fallback to neutral if the LLM returns something unexpected
    if tag not in ["happy", "sad", "angry", "neutral"]:
        tag = "neutral"
    return [tag]

def main():
    print("Welcome to Pepper, your AI Assistant with Speech Recognition and Emotion Labeling!")
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
                # Truncate response to 200 characters, ending at last full sentence if possible
                if len(response) > 200:
                    truncated = response[:200]
                    last_punct = max(truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))
                    if last_punct != -1:
                        response = truncated[:last_punct+1]
                    else:
                        response = truncated
                print(f"\nPepper: {response}")
                # Emotion labeling for each sentence in the AI response
                sentences = split_into_sentences(response)
                print("\nEmotion labels for each sentence in Pepper's response:")
                complete_sentences = []
                complete_emotions = []
                for i, sentence in enumerate(sentences, 1):
                    emotions = get_emotional_tags_llm(sentence, llm)
                    print(f"{i}. '{sentence}' -> {emotions}")
                    if sentence.endswith(('.', '!', '?')):
                        complete_sentences.append(sentence)
                        complete_emotions.append(emotions[0])
                if complete_sentences:
                    for sentence, emotion in zip(complete_sentences, complete_emotions):
                        text_to_speech(sentence, emotion)
                else:
                    print("No complete sentence to speak. Using fallback.")
                    text_to_speech(response)
            else:
                break
        else:
            print("No speech detected.")

if __name__ == "__main__":
    main() 