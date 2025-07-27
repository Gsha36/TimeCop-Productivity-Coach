# TimeCop Productivity Coach 🚀

**AI-Powered Multi-Agent Productivity System**

TimeCop is an intelligent productivity coaching application that uses multiple AI agents to analyze your work patterns, provide insights, and offer personalized coaching advice. The system integrates with GitHub, Google Calendar, Gmail, and voice logging to provide comprehensive productivity analytics.

## 🌟 Features

- **Multi-Agent AI System**: Specialized AI agents for different aspects of productivity analysis
- **Voice Logging**: Record and analyze voice logs for activity tracking and mood analysis
- **Data Integration**: Connects with GitHub, Google Calendar, and Gmail for comprehensive data collection
- **Vector Memory**: Advanced RAG (Retrieval-Augmented Generation) system for historical context
- **Real-time Dashboard**: Interactive charts showing time distribution, focus trends, and context switches
- **Personalized Coaching**: AI-powered insights and recommendations based on your productivity patterns

## 🏗️ Architecture

### Backend (FastAPI)
- **User Proxy Agent**: Processes user input and routes requests
- **Voice Log Agent**: Handles voice transcription and analysis
- **Data Fetcher Agent**: Integrates with external APIs (GitHub, Google Calendar, Gmail)
- **Time Analyzer Agent**: Analyzes time allocation and productivity patterns
- **Insight Agent**: Generates actionable insights from data
- **Coach Agent**: Provides personalized productivity coaching
- **Memory Agent**: Manages long-term memory and context using vector embeddings

### Frontend (React)
- Interactive dashboard with productivity analytics
- Voice recording interface
- Memory browser for historical insights
- Real-time charts and visualizations

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework
- **AutoGen** - Multi-agent AI framework
- **Google Generative AI** - LLM integration
- **Faster Whisper** - Audio transcription
- **Scikit-learn** - Vector embeddings and similarity search
- **OpenAI** - Additional AI capabilities

### Frontend
- **React 18** - Modern UI framework
- **Recharts** - Data visualization
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client

## 📋 Prerequisites

- Python 3.11+
- Node.js 16+
- Git

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Gsha36/TimeCop-Productivity-Coach.git
cd TimeCop-Productivity-Coach
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Environment Configuration
Create a `.env` file in the root directory:
```env
# Google AI Configuration
GOOGLE_API_KEY=your_google_ai_api_key_here

# OpenAI Configuration (optional)
OPENAI_API_KEY=your_openai_api_key_here

# GitHub API (for data fetching)
GITHUB_TOKEN=your_github_token_here

# Google Calendar API (optional)
GOOGLE_CALENDAR_API_KEY=your_google_calendar_api_key_here
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

## 🏃‍♂️ Running the Application

### Start the Backend Server
```bash
# From the root directory
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

The backend API will be available at: `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Start the Frontend Development Server
```bash
# In a new terminal, from the frontend directory
cd frontend
npm start
```

The frontend will be available at: `http://localhost:3000`

## 📱 Usage

### 1. Voice Logging
- Click the microphone button to record voice logs
- The system automatically transcribes and analyzes mood, energy level, and activity type
- Voice logs are stored in vector memory for future reference

### 2. Productivity Analysis
- Enter queries in the main input field to get AI-powered productivity insights
- The system analyzes your GitHub activity, calendar events, and email patterns
- Get personalized coaching advice based on historical data

### 3. Dashboard Analytics
- View time distribution across different activity categories
- Track focus trends over the last 7 days
- Monitor context switching patterns
- Access historical memory and insights

### 4. Memory Browser
- Browse your historical productivity data
- Search through past insights and voice logs
- View trends and patterns over time

## 🔧 API Endpoints

### Core Endpoints
- `POST /analyze` - Main productivity analysis
- `POST /voice-log` - Process voice recordings
- `GET /memory/{user_id}` - Retrieve user memory and trends
- `GET /dashboard/{user_id}` - Get dashboard analytics
- `GET /health` - Health check

### Example API Usage

```bash
# Health check
curl http://localhost:8000/health

# Analyze productivity (requires form data)
curl -X POST "http://localhost:8000/analyze" \
  -F "user_input=How was my productivity today?" \
  -F "user_id=user123"

# Get dashboard data
curl http://localhost:8000/dashboard/user123
```

## 🧪 Development

### Project Structure
```
TimeCop-Productivity-Coach/
├── backend/
│   ├── app.py                 # FastAPI main application
│   ├── config.py             # Configuration settings
│   ├── agents/               # AI agent implementations
│   │   ├── coach_ag.py       # Coaching agent
│   │   ├── datafetch_ag.py   # Data fetching agent
│   │   ├── insight_ag.py     # Insight generation agent
│   │   ├── memory_ag.py      # Memory management agent
│   │   ├── timeanalyze_ag.py # Time analysis agent
│   │   ├── userproxy_ag.py   # User proxy agent
│   │   └── voicelog_ag.py    # Voice logging agent
│   └── tools/                # Integration tools
│       ├── github.py         # GitHub API integration
│       ├── gmail.py          # Gmail API integration
│       ├── google_calendar.py # Google Calendar integration
│       ├── vector_memory.py  # Vector memory system
│       └── whisper_transcriber.py # Audio transcription
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.js           # Main React application
│   │   ├── components/
│   │   │   └── Dashboard.jsx # Dashboard component
│   │   └── index.js
│   └── package.json
├── chroma/                   # Vector database storage
├── requirements.txt          # Python dependencies
└── README.md
```

### Running Tests
```bash
# Backend tests
python -m pytest

# Frontend tests
cd frontend
npm test
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request