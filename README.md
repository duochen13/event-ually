# AI Assistant - Highly Customized Chat Interface

A full-stack AI assistant application powered by Claude, built with Flask backend and React frontend. This highly customized assistant can integrate with multiple data sources like email, weather, calendar, and more to provide context-aware intelligent responses.

## Features

- **AI-Powered Conversations**: Real-time chat with Claude (Sonnet 4.5)
- **Multi-Conversation Management**: Create, switch between, and manage multiple chat sessions
- **Data Source Integration**: Connect email, weather, calendar, and custom data sources
- **Context-Aware Responses**: AI has access to your configured data sources for contextual answers
- **Persistent Storage**: All conversations and messages stored in SQLite database
- **Modern Chat UI**: Beautiful, responsive interface with real-time message updates
- **RESTful API**: Comprehensive backend API for conversations, messages, and data sources

## Project Structure

```
playground/
├── backend/                    # Flask backend
│   ├── app.py                 # Main Flask app with API routes
│   ├── models.py              # SQLAlchemy models (Conversation, Message, DataSource, Context)
│   ├── config.py              # Configuration
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example           # Environment variable template
│   └── instance/              # SQLite database (auto-created)
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── App.jsx           # Main React component
│   │   ├── App.css           # Styles
│   │   ├── main.jsx          # React entry point
│   │   ├── components/       # React components
│   │   │   ├── ChatMessage.jsx         # Message display component
│   │   │   ├── ChatInput.jsx           # Message input component
│   │   │   └── ConversationList.jsx    # Sidebar with conversations
│   │   └── services/
│   │       └── api.js        # API client
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
└── README.md                   # This file
```

## Prerequisites

- Python 3.7+
- Node.js 18+ and npm
- Anthropic API Key (for Claude AI integration)

## Installation & Setup

### 1. Backend Setup (Flask)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or on Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env

# Edit .env and add your Anthropic API key
# ANTHROPIC_API_KEY=your_api_key_here

# Run the Flask server
python app.py
```

The backend will start on `http://localhost:5000`

### 2. Frontend Setup (React)

Open a new terminal:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

The frontend will start on `http://localhost:5173`

## Getting Your Anthropic API Key

1. Visit [https://console.anthropic.com/](https://console.anthropic.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and add it to your `backend/.env` file

## Usage

1. Open your browser to `http://localhost:5173`
2. Click "Start New Conversation" or the "+" button in the sidebar
3. Type your message and press Enter (Shift+Enter for new line)
4. The AI assistant will respond using Claude Sonnet 4.5
5. Switch between conversations using the sidebar
6. Delete conversations you no longer need

## API Endpoints

### Conversation Operations
- `GET /api/conversations` - Get all conversations
- `POST /api/conversations` - Create a new conversation
- `GET /api/conversations/<id>` - Get a conversation with all messages
- `DELETE /api/conversations/<id>` - Delete a conversation
- `PUT /api/conversations/<id>/title` - Update conversation title

### Message Operations
- `POST /api/conversations/<id>/messages` - Send a message and get AI response

### Data Source Operations
- `GET /api/data-sources` - Get all data sources
- `POST /api/data-sources` - Create a new data source
- `PUT /api/data-sources/<id>` - Update a data source
- `DELETE /api/data-sources/<id>` - Delete a data source
- `POST /api/data-sources/<id>/contexts` - Add context to a data source

### Health Check
- `GET /api/health` - Health check (includes API key configuration status)

## Testing the API

You can test the API using curl:

```bash
# Health check
curl http://localhost:5000/api/health

# Create a conversation
curl -X POST http://localhost:5000/api/conversations \
  -H "Content-Type: application/json" \
  -d '{"title": "My First Chat"}'

# Send a message (replace 1 with actual conversation ID)
curl -X POST http://localhost:5000/api/conversations/1/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello, AI assistant!"}'

# Get all conversations
curl http://localhost:5000/api/conversations

# Delete a conversation (replace 1 with actual conversation ID)
curl -X DELETE http://localhost:5000/api/conversations/1
```

## Technology Stack

**Backend:**
- Flask 3.0.0 - Web framework
- Flask-CORS 4.0.0 - Cross-Origin Resource Sharing
- Flask-SQLAlchemy 3.1.1 - ORM for database operations
- Anthropic SDK 0.39.0 - Claude AI integration
- SQLite - Database

**Frontend:**
- React 18.2.0 - UI library
- Vite 5.0.8 - Build tool and dev server
- Axios 1.6.0 - HTTP client

## Data Source Integration

The AI assistant supports multiple data sources for context-aware responses:

### Available Data Sources
- Email (Gmail API)
- Weather data
- Calendar events
- Custom data sources (extensible)

### Adding a Data Source

```python
# Example: Add a weather data source via API
curl -X POST http://localhost:5000/api/data-sources \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Weather",
    "type": "api",
    "enabled": true,
    "config": {"api_key": "your_weather_api_key"}
  }'
```

### Adding Context to a Data Source

```python
# Add weather context
curl -X POST http://localhost:5000/api/data-sources/1/contexts \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Current temperature: 72°F, Sunny",
    "summary": "Pleasant weather conditions"
  }'
```

## Development Notes

- The backend runs on port 5000
- The frontend runs on port 5173
- CORS is configured to allow requests from the frontend
- Conversations persist in `backend/instance/ai_assistant.db`
- Both servers must be running for the app to work
- API key is required for AI responses (falls back to placeholder message if not configured)

## Troubleshooting

**Port already in use:**
```bash
# Kill process on port 5000 (backend)
lsof -ti:5000 | xargs kill -9

# Kill process on port 5173 (frontend)
lsof -ti:5173 | xargs kill -9
```

**Cannot connect to backend:**
- Ensure Flask server is running on port 5000
- Check console for CORS errors
- Verify backend terminal shows no errors

**AI not responding:**
- Verify `ANTHROPIC_API_KEY` is set in `backend/.env`
- Check backend logs for API errors
- Ensure you have API credits in your Anthropic account

**Module not found errors:**
- Backend: Activate virtual environment and run `pip install -r requirements.txt`
- Frontend: Run `npm install` in the frontend directory

## Deployment

This application is configured for deployment on multiple platforms:

### Render (Backend)
- Configuration: `render.yaml`
- Set `ANTHROPIC_API_KEY` in Render environment variables
- Uses Gunicorn for production serving

### Vercel (Frontend)
- Configuration: `vercel.json`
- Update `VITE_API_URL` to your Render backend URL
- Automatically builds and deploys

## Changelog

### 2026-01-13 (Latest)
**AI Assistant Transformation**
- Transformed from Task Manager to AI Assistant chat interface
- Integrated Claude Sonnet 4.5 for AI responses
- Implemented conversation management system
- Added data source integration framework (email, weather, etc.)
- Created modern chat UI with message bubbles and typing indicators
- Built comprehensive REST API for chat operations
- Added context-aware AI responses with data source support
- Updated all documentation to reflect AI assistant features

**Daily AI Update & Documentation Enhancements**
- Daily AI update automation executed successfully
- Enhanced changelog with detailed deployment guide and automation script documentation
- All deployment configurations verified and documented

**Deployment Infrastructure**
- Added deployment configuration for Render (backend) and Vercel (frontend)
- Added `render.yaml` with Flask backend deployment settings using Gunicorn
- Added `vercel.json` with React frontend deployment settings
- Added comprehensive `DEPLOYMENT.md` guide with step-by-step instructions
- Added `backend/.env.example` for environment variable configuration

**Automation & Developer Tools**
- Added `auto_commit.sh` automation script for AI-assisted daily updates
- Configured automated git workflows for maintenance tasks
- Updated README with deployment instructions and troubleshooting guide

### 2026-01-11
**Initial Deployment Setup**
- Created deployment configuration for Render and Vercel platforms
- Added UI screenshot to showcase the application interface
- Initial repository setup and documentation structure

### 2026-01-11 (Initial Release)
**Core Application Launch**
- Full-stack task manager with Flask backend and React frontend
- RESTful API with CRUD operations (Create, Read, Update, Delete)
- SQLite database with SQLAlchemy ORM for data persistence
- Responsive UI with gradient design and modern styling
- Task completion tracking with checkbox interface
- CORS configuration for cross-origin requests
- Health check endpoint for monitoring
- Complete API documentation with curl examples

## Next Steps

Consider adding:
- Streaming responses for real-time AI message generation
- File upload support for document analysis
- Voice input/output for hands-free interaction
- Multi-user authentication and authorization
- Conversation sharing and export
- Advanced data source integrations (Slack, GitHub, etc.)
- RAG (Retrieval-Augmented Generation) for custom knowledge bases
- Message editing and regeneration
- Dark mode toggle
- Mobile app version
- Unit and integration tests

## Contributing

This is a personal side project by a senior software engineer at Meta. Feel free to fork and customize for your own use case.

## License

MIT License - feel free to use and modify as needed.
