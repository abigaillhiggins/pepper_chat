# Pepper Robot Assistant System

This project implements a comprehensive system for Pepper, a humanoid robot assistant, combining emotional voice response capabilities with emotion-based movement choreography.

## System Components

### 1. Emotional Voice Response System

The voice system processes speech input, generates responses using an LLM, and converts responses to natural-sounding speech with emotional expression.

#### Features
- Real-time speech-to-text using Vosk
- Natural, expressive text-to-speech using ElevenLabs (emotion-aware)
- LLM-based emotion detection for each sentence
- Conversational memory using LangChain
- Web search capabilities using DuckDuckGo
- Interactive voice-based conversation

#### Setup for Voice System

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install ffmpeg (includes ffplay, required for TTS playback):
- **macOS:**
  ```bash
  brew install ffmpeg
  ```
- **Linux (Debian/Ubuntu):**
  ```bash
  sudo apt update && sudo apt install ffmpeg
  ```
- **Other Linux distros:**
  Use your package manager to install `ffmpeg`.

4. Create a .env file:
```bash
cp .env.template .env
```

5. Add your API keys to the .env file:
- OPENAI_API_KEY: Your OpenAI API key
- ELEVENLABS_API_KEY: Your ElevenLabs API key

6. Download Vosk model:
```bash
# Download the small model for English
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
```

### 2. Emotion-Based Choreography System

The choreography system enables Pepper to perform emotion-based movements in response to emotional tags, designed to be modular and easily extensible.

#### Structure
```
.
├── README.md
├── orchestrate_choreography.py    # Main orchestration file
└── choreography/
    ├── choreography_engine.py     # Core engine for handling movements
    ├── happy.py                   # Happy emotion movements
    ├── sad.py                     # Sad emotion movements
    └── test_choreography_engine.py # Test suite
```

#### Components

1. **ChoreographyEngine**: Core class that manages and executes emotion-based movements
   - Dynamically loads movement handlers from Python files
   - Provides error handling and case-insensitive emotion matching

2. **Emotion Handlers**: Individual Python files for each emotion (e.g., happy.py, sad.py)
   - Each file contains an `execute_movement()` function
   - Defines specific movement sequences for that emotion

3. **ChoreographyOrchestrator**: Main interface for executing movements
   - Manages the ChoreographyEngine
   - Provides a simple API for emotion-based movement execution

#### Usage

```python
from orchestrate_choreography import ChoreographyOrchestrator

# Create orchestrator
orchestrator = ChoreographyOrchestrator()

# Execute movement for an emotion
orchestrator.handle_emotion('happy')
```

#### Adding New Emotions

To add a new emotion:
1. Create a new Python file in the `choreography` directory (e.g., `excited.py`)
2. Implement the `execute_movement()` function
3. The system will automatically load the new emotion handler

Example:
```python
# choreography/excited.py
def execute_movement():
    """
    Execute the movement sequence for the 'excited' emotion.
    """
    # Add your movement commands here
    pass
```

## Testing

### Voice System Testing
Run the main script:
```bash
python orchestrator.py
```

The system will:
1. Listen for voice input
2. Convert speech to text using Vosk
3. Process the text through the LangChain agent
4. Generate a response
5. Detect the emotion of each sentence in the response using an LLM
6. Convert each sentence to expressive speech using ElevenLabs, matching the detected emotion
7. Play the expressive response through your speakers

### Choreography System Testing
Run the test suite:
```bash
python -m unittest choreography/test_choreography_engine.py -v
```

The test suite verifies:
- Proper initialization
- Movement execution
- Error handling
- Case insensitivity
- Edge cases

## Requirements

- Python 3.8+
- Microphone for voice input
- Speakers for voice output
- Internet connection for API access
- Pepper robot hardware (for movement execution)

## Future Improvements

### Voice System
- Enhanced emotion detection accuracy
- More natural speech synthesis
- Improved conversation memory
- Better noise handling

### Choreography System
- Add more emotion handlers
- Implement actual Pepper movement commands
- Add movement sequence timing control
- Add movement combination capabilities
- Integration with voice system for synchronized movement and speech

## Note

Make sure your microphone is properly configured and working before running the script. The system will automatically detect and use your default microphone. 