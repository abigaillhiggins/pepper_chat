# Pepper Robot Assistant System

This project implements a comprehensive system for Pepper, a humanoid robot assistant, combining emotional voice response capabilities with emotion-based movement choreography.

## 🏗️ System Architecture

### Orchestrator4 - Multi-Agent Conversational AI System

Orchestrator4 is a sophisticated multi-agent conversational AI system designed for Pepper, a humanoid robot at the UC Collaborative Robotics Lab. The system integrates multiple specialized agents to handle different types of user queries with intelligent routing, fallback mechanisms, and Australian context awareness.

#### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           ORCHESTRATOR4 SYSTEM                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐             │
│  │   USER INPUT    │    │   SPEECH-TO-    │    │   MAIN LOOP     │             │
│  │   (Voice/Text)  │───▶│   TEXT (STT)    │───▶│   (main())      │             │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘             │
│                                │                                                │
│                                ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                        ORCHESTRATOR4 CLASS                                 │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐   │ │
│  │  │                    INPUT PROCESSING PIPELINE                        │   │ │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   │ │
│  │  │  │   handle_   │  │   Exception │  │   Keyword   │  │   Agent      │ │   │ │
│  │  │  │   input()   │──│   Handler   │──│   Analysis  │──│   Selection  │ │   │ │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │   │ │
│  │  └─────────────────────────────────────────────────────────────────────┘   │ │
│  │                                │                                            │ │
│  │                                ▼                                            │ │
│  │  │                    AGENT ECOSYSTEM                                   │   │ │
│  │  │                                                                       │   │ │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   │ │
│  │  │  │  PEPPER     │  │  SEARCH     │  │  SEARCH     │  │  SUMMARY    │ │   │ │
│  │  │  │  AGENT      │  │  AGENT      │  │  AGENT3     │  │  AGENT      │ │   │ │
│  │  │  │             │  │  (Fallback) │  │  (Primary)  │  │             │ │   │ │
│  │  │  │ • Conversa- │  │ • DuckDuckGo│  │ • Custom    │  │ • Australian│ │   │ │
│  │  │  │   tional    │  │ • Basic     │  │   Search    │  │   Context   │ │   │ │
│  │  │  │ • Memory    │  │ • Fallback  │  │ • Advanced  │  │   Units     │ │   │ │
│  │  │  │ • Personality│  │ • GPT-4o    │  │   Features  │  │ • Filtering │ │   │ │
│  │  │  │ • GPT-4o    │  │   Option    │  │   Features  │  │ • Metric    │ │   │ │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │   │ │
│  │  │       │                   │                   │                   │   │ │
│  │  │       └───────────────────┼───────────────────┼───────────────────┘   │ │
│  │  │                           │                   │                       │ │
│  │  │                           ▼                   ▼                       │ │
│  │  │  ┌─────────────────────────────────────────────────────────────────┐ │   │ │
│  │  │  │                RESPONSE PROCESSING PIPELINE                     │ │   │ │
│  │  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │ │   │ │
│  │  │  │  │   process_  │  │   Sentence  │  │   Emoji     │  │   TTS   │ │ │   │ │
│  │  │  │  │   response()│──│   Splitter  │──│   Filter    │──│   Engine │ │ │   │ │
│  │  │  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │ │   │ │
│  │  │  └─────────────────────────────────────────────────────────────────┘ │   │ │
│  │  └─────────────────────────────────────────────────────────────────────┘   │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                │                                                │
│                                ▼                                                │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐             │
│  │   PEPPER TTS    │    │   HTTP REQUEST  │    │   AUDIO OUTPUT  │             │
│  │   (10.0.0.244)  │◀───│   (Threaded)    │◀───│   (Robot Voice) │             │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘             │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

#### Agent Ecosystem

**🤖 PepperAgent** - Conversational personality and memory management
- Sweet, caring robot personality with GPT-4o
- Conversation memory (10 messages, 1500 tokens)
- Response caching and character limit enforcement (200 chars)

**🔍 SearchAgent3** - Advanced search with custom API
- Custom search API integration (contact me for details)
- Rate limiting, caching, and specialized formatting
- Error handling with fallback to SearchAgent

**🔍 SearchAgent** - Fallback search agent
- DuckDuckGo search integration
- Basic response formatting
- Used when SearchAgent3 fails

**📝 SummaryAgent** - Australian context and response filtering
- Metric unit conversion (Fahrenheit→Celsius, miles→km)
- Australian holiday filtering and Canberra-specific context
- Phonetic symbol rewriting for TTS

#### Key Features

- **Intelligent Routing**: Context-aware agent selection based on keyword analysis
- **Multi-Level Fallback**: SearchAgent3 → SearchAgent → PepperAgent
- **Australian Context**: Metric units, local holidays, Canberra-specific information
- **Performance Optimizations**: Response caching, rate limiting, threaded operations
- **Error Handling**: Comprehensive error handling at every level

## 🚀 Quick Start - Orchestrator4

### Prerequisites

- Python 3.8+
- OpenAI API key
- Microphone for voice input
- Pepper robot hardware (for TTS output)
- Network access to Pepper TTS endpoint (10.0.0.244:5000)
- Network access to custom search API (192.168.194.33:8060)

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd pepper-robot-assistant
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
cp .env.template .env
```

5. **Configure your .env file:**
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

6. **Download Vosk model for speech recognition:**
```bash
# Download the small model for English
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
```

### Running Orchestrator4

1. **Start the system:**
```bash
python orchestrator4.py
```

2. **Usage:**
- Press Enter to start speaking
- Speak your query clearly
- Press Enter again to stop recording
- The system will process your input and respond through Pepper's TTS

3. **Example queries:**
- **Conversational**: "Hello, how are you?", "Tell me a joke"
- **Search**: "What is the weather in Canberra?", "Who is the current Prime Minister?"
- **Summary**: "Summarize the latest news about AI"
- **Location**: "Where am I?" (returns UC Collaborative Robotics Lab info)
- **VC Info**: "Who is the VC of UC?" (returns Bill Shorten info)

### System Behavior

- **Agent Selection**: The system automatically routes queries to the most appropriate agent
- **Fallback System**: If SearchAgent3 fails, it falls back to SearchAgent, then to PepperAgent
- **Australian Context**: Responses are automatically converted to metric units and Australian context
- **TTS Output**: Responses are sent to Pepper's TTS system at 10.0.0.244:5000
- **Performance Monitoring**: The system provides profiling information for each interaction

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

### Orchestrator4 Testing
Run the main script:
```bash
python orchestrator4.py
```

The system will:
1. Listen for voice input using Vosk STT
2. Route the input to appropriate agents based on keyword analysis
3. Process through the selected agent (PepperAgent, SearchAgent3, SearchAgent, or SummaryAgent)
4. Apply Australian context and filtering if needed
5. Split response into sentences and filter emojis
6. Send to Pepper's TTS system for audio output
7. Provide performance profiling information

### Voice System Testing (Legacy)
Run the legacy script:
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
- OpenAI API key
- Microphone for voice input
- Speakers for voice output (legacy system)
- Pepper robot hardware (for TTS output and movement execution)
- Internet connection for API access
- Network access to Pepper TTS endpoint (10.0.0.244:5000)
- Network access to custom search API 

## Configuration

### Network Settings
- Pepper TTS: `10.0.0.244:5000`
- Search API: `192.168.194.33:8060`

### Agent Settings
- Memory: 10 messages, 1500 tokens
- Response Limit: 200 characters
- Cache TTL: 1 hour
- Search Rate Limit: 1 second

### Model Configuration
- Primary LLM: GPT-4o
- Temperature: 0.2-0.7 (varies by agent)
- System prompts: Specialized per agent

## Troubleshooting

### Common Issues

1. **Speech Recognition Not Working**
   - Ensure Vosk model is downloaded and in the correct location
   - Check microphone permissions and settings
   - Verify audio input device is working

2. **TTS Not Working**
   - Check network connectivity to Pepper TTS endpoint (10.0.0.244:5000)
   - Verify Pepper robot is powered on and accessible
   - Check firewall settings

3. **Search Not Working**
   - Verify network connectivity to search API 
   - Check API rate limiting
   - Ensure OpenAI API key is valid

4. **Agent Failures**
   - Check OpenAI API key and quota
   - Verify internet connectivity
   - Review error logs for specific agent issues

### Debug Mode

To enable detailed logging, modify the orchestrator4.py file to add logging statements or run with verbose output.

## Future Improvements

### Orchestrator4
- Enhanced agent selection algorithms
- More sophisticated fallback mechanisms
- Additional specialized agents
- Integration with choreography system
- Real-time performance monitoring dashboard

### Voice System (Legacy)
- Enhanced emotion detection accuracy
- More natural speech synthesis
- Improved conversation memory
- Better noise handling

### Choreography System
- Add more emotion handlers
- Implement actual Pepper movement commands
- Add movement sequence timing control
- Add movement combination capabilities
- Integration with Orchestrator4 for synchronized movement and speech

## Note

Make sure your microphone is properly configured and working before running the script. The system will automatically detect and use your default microphone. For Orchestrator4, ensure Pepper robot is accessible on the network and the TTS endpoint is responding. 
