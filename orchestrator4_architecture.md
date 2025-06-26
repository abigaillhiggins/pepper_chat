# Orchestrator4 System Architecture

## 🏗️ System Overview

Orchestrator4 is a multi-agent conversational AI system designed for Pepper, a humanoid robot at the UC Collaborative Robotics Lab. The system integrates multiple specialized agents to handle different types of user queries with intelligent routing, fallback mechanisms, and Australian context awareness.

## 📊 System Architecture Diagram

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
│  │  ┌─────────────────────────────────────────────────────────────────────┐   │ │
│  │  │                    AGENT ECOSYSTEM                                   │   │ │
│  │  │                                                                       │   │ │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   │ │
│  │  │  │  PEPPER     │  │  SEARCH     │  │  SEARCH     │  │  SUMMARY    │ │   │ │
│  │  │  │  AGENT      │  │  AGENT      │  │  AGENT3     │  │  AGENT      │ │   │ │
│  │  │  │             │  │  (Fallback) │  │  (Primary)  │  │             │ │   │ │
│  │  │  │ • Conversa- │  │ • DuckDuckGo│  │ • Custom    │  │ • Australian│ │   │ │
│  │  │  │   tional    │  │ • Basic     │  │   Search    │  │   Context   │ │   │ │
│  │  │  │ • Memory    │  │   Search    │  │   API       │  │ • Metric    │ │   │ │
│  │  │  │ • Personality│  │ • Fallback  │  │ • Advanced  │  │   Units     │ │   │ │
│  │  │  │ • GPT-4o    │  │   Option    │  │   Features  │  │ • Filtering │ │   │ │
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

## 🔧 Core Components

### 1. **Orchestrator4 Class** - Central Controller
- **Purpose**: Main orchestrator that manages the entire conversation flow
- **Key Methods**:
  - `__init__()`: Initializes all agents and TTS configuration
  - `handle_input()`: Routes user input to appropriate agents
  - `process_response()`: Processes and formats responses for TTS
  - `speak()` / `speak_threaded()`: Manages TTS output

### 2. **Agent Ecosystem** - Specialized AI Agents

#### **PepperAgent** 🤖
- **Role**: Conversational personality and memory management
- **Technology**: GPT-4o with ConversationBufferMemory
- **Features**:
  - Sweet, caring robot personality
  - Conversation memory (10 messages, 1500 tokens)
  - Response caching for efficiency
  - Character limit enforcement (200 chars)
  - DuckDuckGo search integration for current events

#### **SearchAgent3** 🔍
- **Role**: Advanced search with custom API
- **Technology**: Custom search API + GPT-4o processing
- **Features**:
  - Custom search API integration (192.168.194.33:8060)
  - Rate limiting and caching
  - Specialized formatting for weather, time, population
  - Conversational response generation
  - Error handling with fallback

#### **SearchAgent** 🔍
- **Role**: Fallback search agent
- **Technology**: DuckDuckGo search + basic processing
- **Features**:
  - Backup search functionality
  - Basic response formatting
  - Used when SearchAgent3 fails

#### **SummaryAgent** 📝
- **Role**: Australian context and response filtering
- **Technology**: GPT-4o with Australian context awareness
- **Features**:
  - Metric unit conversion (Fahrenheit→Celsius, miles→km, etc.)
  - Australian holiday filtering
  - Location context (Canberra, Australia)
  - Phonetic symbol rewriting for TTS
  - Response summarization

### 3. **Input Processing Pipeline**

#### **Exception Handler**
- **Location Queries**: "where am i", "where are we" → Direct response
- **VC Queries**: "who is the vc of uc" → Direct response

#### **Keyword Analysis**
- **Summary Keywords**: "summarize", "summary", "brief" → SummaryAgent
- **Conversational Keywords**: "hello", "how are you", "joke" → PepperAgent
- **Advanced Search Keywords**: "what is", "who is", "current" → SearchAgent3

#### **Agent Selection Logic**
```
User Input → Exception Check → Keyword Analysis → Agent Selection
     ↓              ↓              ↓              ↓
   Direct      SummaryAgent   PepperAgent   SearchAgent3
  Response         ↓              ↓              ↓
                   ↓              ↓              ↓
              [Processing]   [Processing]   [Processing]
                   ↓              ↓              ↓
              [SummaryAgent] [Response]   [SummaryAgent]
                   ↓              ↓              ↓
              [Response]     [Response]   [Response]
```

### 4. **Response Processing Pipeline**

#### **Sentence Processing**
- **Sentence Splitter**: Breaks response into individual sentences
- **Emoji Filter**: Removes emoji-only sentences from TTS
- **TTS Engine**: Converts text to speech via HTTP requests

#### **TTS Management**
- **Synchronous TTS**: `speak()` for immediate output
- **Threaded TTS**: `speak_threaded()` for non-blocking operations
- **Search Feedback**: "Allow me to search the web for you" after 1.5s delay

### 5. **External Integrations**

#### **Pepper Robot TTS**
- **Endpoint**: `http://10.0.0.244:5000/say`
- **Protocol**: HTTP GET with text parameter
- **Threading**: Non-blocking TTS for better UX

#### **Custom Search API**
- **Endpoint**: `http://192.168.194.33:8060/search`
- **Format**: JSON responses
- **Rate Limiting**: 1 second minimum between requests

## 🔄 Data Flow

### **Primary Flow (Search Queries)**
1. User Input → Keyword Analysis → SearchAgent3
2. SearchAgent3 → Custom Search API → Raw Results
3. Raw Results → SummaryAgent → Australian Context
4. Processed Response → Sentence Splitter → Emoji Filter
5. Filtered Sentences → TTS Engine → Pepper Robot

### **Fallback Flow**
1. SearchAgent3 Failure → SearchAgent (DuckDuckGo)
2. SearchAgent Failure → PepperAgent (Conversational)
3. All Failures → Error Message

### **Conversational Flow**
1. User Input → Keyword Analysis → PepperAgent
2. PepperAgent → GPT-4o → Memory Storage
3. Response → Sentence Processing → TTS

## 🛡️ Error Handling & Resilience

### **Multi-Level Fallback System**
1. **SearchAgent3** (Primary) → **SearchAgent** (Fallback) → **PepperAgent** (Conversational)
2. **Agent Failures** → Graceful error messages
3. **TTS Failures** → Silent failure with logging
4. **Network Issues** → Timeout handling and retry logic

### **Performance Optimizations**
- **Response Caching**: 1-hour TTL for repeated queries
- **Rate Limiting**: Prevents API abuse
- **Threaded Operations**: Non-blocking TTS and search feedback
- **Memory Management**: Limited conversation history

## 🎯 Key Features

### **Intelligent Routing**
- Context-aware agent selection
- Keyword-based classification
- Exception handling for common queries

### **Australian Context**
- Metric unit conversion
- Local holiday awareness
- Canberra-specific information
- Timezone handling

### **User Experience**
- Non-blocking TTS operations
- Search progress feedback
- Emoji filtering for natural speech
- Character-limited responses

### **Robustness**
- Multi-level fallback system
- Comprehensive error handling
- Performance monitoring
- Caching for efficiency

## 🔧 Configuration

### **Network Settings**
- Pepper TTS: `10.0.0.244:5000`
- Search API: `192.168.194.33:8060`

### **Agent Settings**
- Memory: 10 messages, 1500 tokens
- Response Limit: 200 characters
- Cache TTL: 1 hour
- Search Rate Limit: 1 second

### **Model Configuration**
- Primary LLM: GPT-4o
- Temperature: 0.2-0.7 (varies by agent)
- System prompts: Specialized per agent
