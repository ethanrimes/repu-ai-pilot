# docs/FILE_STRUCTURE.md
# Path: docs/FILE_STRUCTURE.md

# Project File Structure

## Overview

The project follows a modular architecture with clear separation between backend, frontend, and supporting scripts.

## Directory Structure


aftermarket-rag-colombia/
│
├── backend/                    # FastAPI backend application
│   ├── api/
│   │   ├── config/            # Configuration management
│   │   ├── middleware/        # Request/response middleware
│   │   ├── routers/          # API endpoints
│   │   ├── agents/           # LangChain agents and tools
│   │   ├── rai/              # Infosys RAI integration
│   │   ├── llm/              # LLM providers and utilities
│   │   ├── integrations/     # External service integrations
│   │   ├── models/           # Data models and schemas
│   │   ├── services/         # Business logic
│   │   ├── database/         # Database utilities
│   │   └── utils/            # Helper functions
│   │
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile            # Container configuration
│   └── fly.toml              # Fly.io deployment config
│
├── frontend/                  # Next.js frontend application
│   ├── src/
│   │   ├── app/              # Next.js app router pages
│   │   ├── components/       # React components
│   │   ├── hooks/            # Custom React hooks
│   │   ├── lib/              # Core libraries
│   │   ├── services/         # API services
│   │   ├── types/            # TypeScript types
│   │   └── locales/          # i18n translations
│   │
│   ├── package.json          # Node dependencies
│   └── vercel.json           # Vercel deployment config
│
├── scripts/                   # Utility scripts
│   ├── data_generation/      # Synthetic data generation
│   ├── setup/                # Setup and initialization
│   └── cli/                  # CLI tools
│
├── config/                    # Configuration files
│   ├── chunking_config.yaml  # Document chunking config
│   ├── intent_mappings.yaml  # Intent classification
│   └── prompts/              # LLM prompt templates
│
├── data/                      # Data directory
│   ├── brake_articles/       # TecDoc article JSONs
│   ├── generated/            # Generated synthetic data
│   └── documents/            # Uploaded documents
│
├── docs/                      # Documentation
│   ├── SETUP.md              # Setup guide
│   ├── ARCHITECTURE.md       # System architecture
│   └── DATABASE_SCHEMA.md    # Database design
│
├── docker/                    # Docker configurations
│   ├── docker-compose.yml    # Local development
│   └── docker-compose.prod.yml # Production
│
└── infosys-rai/              # Infosys RAI submodule


## Key Files

### Backend Core Files

| File | Purpose |
|------|---------|
| `backend/api/main.py` | FastAPI application entry point |
| `backend/api/config/settings.py` | Centralized configuration |
| `backend/api/agents/rag_agent.py` | Main RAG agent implementation |
| `backend/api/integrations/supabase/client.py` | Supabase connection |
| `backend/api/integrations/firebase/auth_client.py` | Firebase Auth |

### Frontend Core Files

| File | Purpose |
|------|---------|
| `frontend/src/app/layout.tsx` | Root layout component |
| `frontend/src/app/chat/page.tsx` | Chat interface page |
| `frontend/src/lib/firebase.ts` | Firebase initialization |
| `frontend/src/hooks/useAuth.ts` | Authentication hook |

### Configuration Files

| File | Purpose |
|------|---------|
| `.env` | Environment variables (not in git) |
| `.env.example` | Environment template |
| `config/chunking_config.yaml` | Document chunking settings |
| `config/intent_mappings.yaml` | Intent classification rules |

### Script Files

| File | Purpose |
|------|---------|
| `scripts/setup/init_supabase.py` | Database initialization |
| `scripts/data_generation/load_brake_articles.py` | Load article data |
| `scripts/cli/main.py` | CLI entry point |

## File Naming Conventions

- **Python files**: `snake_case.py`
- **TypeScript/React**: `PascalCase.tsx` for components, `camelCase.ts` for utilities
- **Configuration**: `snake_case.yaml` or `.json`
- **Documentation**: `UPPERCASE.md` for main docs

## Import Organization

### Python Imports
```python
# Standard library
import os
import sys

# Third-party
from fastapi import FastAPI
from pydantic import BaseModel

# Local application
from backend.api.config import settings
from backend.api.models import User
```

### TypeScript Imports
```typescript
// External libraries
import React from 'react';
import { useRouter } from 'next/navigation';

// Internal components
import { ChatInterface } from '@/components/chat';

// Types
import type { User } from '@/types';
```