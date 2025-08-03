# docs/SETUP.md
# Path: docs/SETUP.md

# Setup Guide

## Prerequisites

### Required Software
- Python 3.10 or higher
- Node.js 18 or higher
- Docker and Docker Compose
- Git

### Required Accounts
1. **Supabase** - Database hosting
2. **Firebase** - Authentication
3. **Upstash** - Redis cache
4. **OpenAI** or **Azure OpenAI** - LLM provider
5. **RapidAPI** - TecDoc API access
6. **WhatsApp Business** - Messaging platform

## 🚀 Quick Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-org/aftermarket-rag-colombia
cd aftermarket-rag-colombia

# 2. Run the setup script
bash scripts/setup/create_all_files.sh

# 3. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 4. Initialize database
python scripts/setup/init_supabase.py

# 5. Load brake articles data
python scripts/data_generation/load_brake_articles.py \
  --articles-path /path/to/brake/articles

# 6. Start services
docker-compose up -d
python scripts/setup/initialize_all.py