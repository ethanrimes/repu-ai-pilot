# RepuAI - Colombian Automotive Parts Assistant

An intelligent AI-powered chat assistant specialized in automotive parts for the Colombian aftermarket, with a focus on brake components. Built with FastAPI, Next.js, and integrated with TecDoc API for comprehensive vehicle and parts data.

## 🚀 Features

- **AI-Powered Chat Assistant**: Specialized chatbot for automotive parts inquiries using OpenAI GPT-4
- **Vehicle Identification**: Interactive vehicle selection using TecDoc API integration
- **Multi-language Support**: Full support for Spanish and English
- **Invite-Only Access**: Secure registration system with invite codes
- **Conversation State Management**: Structured conversation flows for different customer journeys
- **Real-time Parts Search**: Integration with TecDoc catalog for accurate parts information
- **Session Management**: Secure session handling with Redis and PostgreSQL
- **Rate Limiting**: Comprehensive rate limiting (per-minute, daily, weekly)
- **Document RAG System**: Vector search capabilities for technical documentation

## 🏗️ Architecture

### Tech Stack

**Backend:**
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (via Supabase) with pgvector extension
- **Cache**: Redis (via Upstash)
- **Authentication**: Firebase Auth + Custom Session Management
- **AI/ML**: OpenAI GPT-4 for chat, text-embedding-3-small for embeddings
- **External APIs**: TecDoc Catalog API (via RapidAPI)

**Frontend:**
- **Framework**: Next.js 14 with TypeScript
- **State Management**: Zustand
- **Styling**: Tailwind CSS + CSS Modules
- **Authentication**: Firebase SDK
- **Internationalization**: Custom i18n implementation

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL with pgvector extension
- Redis instance (or Upstash account)
- Firebase project
- OpenAI API key
- TecDoc API access (via RapidAPI)
- Supabase project

## 🛠️ Installation

### Backend Setup

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/repu-ai-pilot.git
cd repu-ai-pilot
```

2. **Set up Python environment:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment variables:**
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
# Database (Supabase)
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key
DATABASE_URL=postgresql://user:password@host:port/database

# Authentication (Firebase)
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your_auth_domain
FIREBASE_PROJECT_ID=your_project_id

# Cache (Upstash Redis)
UPSTASH_REDIS_REST_URL=your_redis_url
UPSTASH_REDIS_REST_TOKEN=your_redis_token

# OpenAI
OPENAI_API_KEY=your_openai_key

# TecDoc API (RapidAPI)
RAPIDAPI_KEY=your_rapidapi_key
RAPIDAPI_HOST=tecdoc-catalog.p.rapidapi.com

# WhatsApp Business API (Optional)
WHATSAPP_BUSINESS_ID=your_business_id
WHATSAPP_ACCESS_TOKEN=your_access_token
```

4. **Initialize the database:**
```bash
# Run migrations
python migrations/apply_migration.py

# Create initial invite codes
python scripts/create_invite_code.py --code "INITIAL-CODE-123" --max-uses 10
```

5. **Start the backend server:**
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Configure environment variables:**
```bash
cp .env.local.example .env.local
```

Edit `.env.local`:
```env
# Firebase
NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_auth_domain
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_storage_bucket
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id

# API
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Redis (for session management)
UPSTASH_REDIS_REST_URL=your_redis_url
UPSTASH_REDIS_REST_TOKEN=your_redis_token
```

4. **Start the development server:**
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## 📚 Project Structure

```
repu-ai-pilot/
├── backend/
│   ├── src/
│   │   ├── api/              # API routes and middleware
│   │   ├── core/             # Business logic and services
│   │   │   ├── agents/       # AI agents and tools
│   │   │   ├── conversation/ # Conversation state management
│   │   │   ├── models/       # Pydantic models
│   │   │   └── services/     # Business services
│   │   ├── infrastructure/   # External integrations
│   │   │   ├── cache/        # Redis integration
│   │   │   ├── database/     # PostgreSQL models and repos
│   │   │   ├── integrations/ # Firebase, TecDoc, WhatsApp
│   │   │   └── llm/          # OpenAI integration
│   │   └── shared/           # Shared utilities
│   └── tests/                # Test files
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js app directory
│   │   ├── components/       # React components
│   │   ├── hooks/            # Custom React hooks
│   │   ├── i18n/             # Internationalization
│   │   ├── lib/              # API clients and utilities
│   │   ├── stores/           # Zustand stores
│   │   └── styles/           # CSS modules
│   └── public/               # Static assets
└── config/                   # Configuration files
```

## 🔧 Key Features Implementation

### Conversation State Management

The system uses a finite state machine approach for managing conversations:

```python
class ConversationState(Enum):
    INTENT_MENU = "intent_menu"
    PRODUCT_SEARCH_INIT = "product_search_init"
    VEHICLE_IDENTIFICATION = "vehicle_identification"
    PART_TYPE_SELECTION = "part_type_selection"
    # ... more states
```

### Vehicle Identification Flow

1. User selects "Product Search" from menu
2. System presents vehicle identification options
3. User can search by:
   - VIN/License plate (not yet implemented)
   - Make/Model/Year selection via TecDoc API
4. Selected vehicle data is stored in conversation context

### Rate Limiting

Three-tier rate limiting system:
- **Per-minute**: 60 requests (configurable)
- **Daily**: 200 requests per user
- **Weekly**: 1000 requests per user

### Multi-language Support

Dynamic language switching with conversation reset:
```typescript
// Frontend language switching
const { changeLanguageWithReset } = useLanguageStore();
await changeLanguageWithReset('en'); // or 'es'
```

## 🚀 Deployment

### Backend Deployment (Fly.io)

```bash
cd backend
fly deploy
```

### Frontend Deployment (Vercel)

```bash
cd frontend
vercel deploy
```

## 📊 Database Schema

Key tables:
- `customers`: User accounts linked to Firebase
- `sessions`: Active user sessions
- `documents`: RAG system documents
- `chunks`: Document chunks with embeddings
- `orders`: Order management
- `stock`: Inventory tracking
- `prices`: Product pricing
- `invite_codes`: Registration invite codes

## 🔒 Security Features

- **Invite-only registration**: New users require valid invite codes
- **Session-based authentication**: Secure session management with Redis
- **Rate limiting**: Protection against abuse
- **Firebase authentication**: Secure user authentication
- **Environment-based configuration**: Sensitive data in environment variables

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📖 API Documentation

Once the backend is running, API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is proprietary and confidential.

## 🆘 Support

For issues and questions, please create an issue in the GitHub repository.

## 🗺️ Roadmap

- [ ] Implement VIN/License plate vehicle identification
- [ ] Add more conversation journeys (order status, returns, etc.)
- [ ] Integrate payment processing
- [ ] Add WhatsApp Business API support
- [ ] Implement advanced analytics dashboard
- [ ] Add voice input support
- [ ] Expand to more automotive part categories

## 🙏 Acknowledgments

- TecDoc for comprehensive automotive data
- OpenAI for GPT-4 and embedding models
- Supabase for PostgreSQL hosting with pgvector
- Upstash for Redis hosting
- Firebase for authentication services