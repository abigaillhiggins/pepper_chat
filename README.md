# Emotional Voice Response System

This project implements an interactive voice-based conversational agent using LangChain, Vosk for speech-to-text, and ElevenLabs for text-to-speech. The system processes voice input, generates responses using an LLM, and converts the responses to natural-sounding speech.

## Features

- Real-time speech-to-text using Vosk
- Natural text-to-speech using ElevenLabs
- Conversational memory using LangChain
- Web search capabilities using DuckDuckGo
- Interactive voice-based conversation

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a .env file:
```bash
cp .env.template .env
```

4. Add your API keys to the .env file:
- OPENAI_API_KEY: Your OpenAI API key
- ELEVENLABS_API_KEY: Your ElevenLabs API key

5. Download Vosk model:
```bash
# Download the small model for English
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
```

## Usage

Run the main script:
```bash
python main2.py
```

The system will:
1. Listen for voice input
2. Convert speech to text using Vosk
3. Process the text through the LangChain agent
4. Generate a response
5. Convert the response to speech using ElevenLabs
6. Play the response through your speakers

## Requirements

- Python 3.8+
- Microphone for voice input
- Speakers for voice output
- Internet connection for API access

## Note

Make sure your microphone is properly configured and working before running the script. The system will automatically detect and use your default microphone. 