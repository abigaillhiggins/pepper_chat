# Emotional Voice Response System

This project uses LangChain and PlayHT to create an emotional voice response system. It processes text through an LLM, assigns emotional tags, and converts the response to speech using PlayHT's voice synthesis.

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
- PLAYHT_API_KEY: Your PlayHT API key
- PLAYHT_USER_ID: Your PlayHT user ID

## Usage

Run the main script:
```bash
python main.py
``` 