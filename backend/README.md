# LawRo Unified Backend

AI-powered legal consultation and contract analysis platform - Unified backend service.

## Features

- **Authentication**: Firebase Authentication with email/password and social OAuth (Google, Kakao, Naver)
- **AI Chatbot**: RAG-based legal consultation (Phase 2)
- **Contract Analysis**: OCR and AI-powered contract parsing (Phase 3)

## Tech Stack

- **Framework**: FastAPI
- **Database**: Firebase Firestore
- **Vector DB**: ChromaDB (local file-based)
- **AI Models**: Upstage Solar-Pro, OpenAI GPT-4
- **Storage**: AWS S3
- **Deployment**: Docker

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Firebase initialization
│   ├── dependencies.py      # Common dependencies
│   ├── models/              # Pydantic models
│   ├── routers/             # API route handlers
│   ├── services/            # Business logic
│   └── utils/               # Utility functions
├── data/                    # ChromaDB storage
├── prompts/                 # AI prompt templates
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
└── .env                    # Environment variables
```

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Firebase project (see FIREBASE_SETUP.md)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd LawRo/backend
   ```

2. **Set up Firebase** (IMPORTANT!)
   Follow the detailed guide: [FIREBASE_SETUP.md](FIREBASE_SETUP.md)

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Place Firebase credentials**
   - Download `firebase-credentials.json` from Firebase Console
   - Place it in the `backend/` directory

### Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload
```

Server will be available at: http://localhost:8000

### Run with Docker

```bash
docker-compose up --build
```

## API Endpoints

### Health & Info
- `GET /` - API information
- `GET /health` - Health check
- `GET /stats` - System statistics

### Authentication (Phase 1 - ✅ Complete)
- `POST /auth/signup` - Register with email/password
- `POST /auth/login` - Login with email/password
- `GET /auth/profile` - Get current user profile
- `GET /auth/google/login` - Google OAuth (client-side)
- `POST /auth/google/callback` - Google OAuth callback
- `POST /auth/kakao/callback` - Kakao OAuth callback
- `POST /auth/naver/callback` - Naver OAuth callback

### Chatbot (Phase 2 - ✅ Complete)
- `POST /chat/send` - Send message to chatbot
- `GET /chat/history/{session_id}` - Get chat history
- `POST /chat/new-session` - Create new chat session
- `DELETE /chat/history/{session_id}` - Clear chat history

### Contract Analysis (Phase 3 - ✅ Complete)
- `POST /contract/api/upload` - Upload contract files
- `POST /contract/api/analyze-with-chatbot` - Analyze contract with chatbot
- `GET /contract/api/chatbot-status` - Check chatbot service status
- `GET /contract/health` - Contract service health check

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Authentication Flow

1. **Frontend**: User signs up/logs in using Firebase SDK
2. **Frontend**: Gets Firebase ID token
3. **Frontend**: Sends token in Authorization header: `Bearer <token>`
4. **Backend**: Verifies token using Firebase Admin SDK
5. **Backend**: Returns user data

## Development Phases

### ✅ Phase 1: Authentication & Infrastructure (COMPLETE)
- Firebase Authentication integration
- Basic FastAPI structure
- Docker setup
- API documentation

### ✅ Phase 2: Chatbot Service (COMPLETE)
- ChromaDB vector search
- LangChain RAG pipeline
- Upstage Solar-Pro integration
- Session management with Firestore (2-tier cache)
- Multi-language support
- Custom prompt injection for contract analysis

### ✅ Phase 3: Contract Parser (COMPLETE)
- Upstage Document OCR API integration
- GPT-4 contract parsing (simplified)
- AWS S3 file storage
- Chatbot integration for legal analysis
- Firestore caching for analyzed contracts
- Multi-page contract support

## Environment Variables

See `.env.example` for all required environment variables.

Key variables:
- `FIREBASE_CREDENTIALS_PATH` - Path to Firebase service account key
- `FIREBASE_API_KEY` - Firebase Web API key
- `UPSTAGE_API_KEY` - Upstage API key (for chatbot & OCR)
- `OPENAI_API_KEY` - OpenAI API key (for contract analysis)
- `AWS_ACCESS_KEY_ID` - AWS access key (for S3)
- `S3_BUCKET_NAME` - S3 bucket name

## Testing

Test authentication:
```bash
# Health check
curl http://localhost:8000/health

# Signup
curl -X POST http://localhost:8000/auth/signup   -H "Content-Type: application/json"   -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User"
  }'

# Login
curl -X POST http://localhost:8000/auth/login   -H "Content-Type: application/json"   -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

## Troubleshooting

See [FIREBASE_SETUP.md](FIREBASE_SETUP.md) for detailed troubleshooting.

Common issues:
- **Firebase not initialized**: Check `firebase-credentials.json` location
- **Invalid token**: Ensure frontend and backend use same Firebase project
- **Permission denied**: Check Firestore security rules

## Security

- Never commit `firebase-credentials.json`
- Never commit `.env` file
- Use HTTPS in production
- Enable Firebase App Check (recommended)
- Rotate API keys regularly

## License

[Your License]

## Contact

[Your Contact Information]

