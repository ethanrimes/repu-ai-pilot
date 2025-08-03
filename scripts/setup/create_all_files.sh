#!/bin/bash
# create_all_files.sh
# Path: scripts/setup/create_all_files.sh

echo "🚀 Creating complete project structure and files..."

# ============================================
# Create Directory Structure
# ============================================

# Backend directories
mkdir -p backend/api/config
mkdir -p backend/api/middleware
mkdir -p backend/api/routers/webhooks
mkdir -p backend/api/agents/{tools,agent_core,intents,states}
mkdir -p backend/api/rai/{moderation,explainability,fairness,hallucination}
mkdir -p backend/api/llm/{providers,chunking,prompts}
mkdir -p backend/api/integrations/{firebase,supabase/repositories,upstash,whatsapp,tecdoc}
mkdir -p backend/api/models/{database,schemas}
mkdir -p backend/api/services
mkdir -p backend/api/database/{migrations,repositories,schemas}
mkdir -p backend/api/utils
mkdir -p backend/api/tests/fixtures

# Frontend directories
mkdir -p frontend/src/app/{chat,admin/dashboard}
mkdir -p frontend/src/components/{chat,auth,common}
mkdir -p frontend/src/{hooks,lib,services,types,utils}
mkdir -p frontend/src/locales/{es,en}
mkdir -p frontend/public

# Scripts directories
mkdir -p scripts/{data_generation/prompts,setup,cli}

# Config directories
mkdir -p config/prompts

# Data directories
mkdir -p data/{brake_articles,generated,documents}

# Other directories
mkdir -p docker
mkdir -p docs
mkdir -p .github/workflows

# ============================================
# Create Python __init__.py files
# ============================================

# Backend __init__.py files
touch backend/__init__.py
touch backend/api/__init__.py
touch backend/api/config/__init__.py
touch backend/api/middleware/__init__.py
touch backend/api/routers/__init__.py
touch backend/api/routers/webhooks/__init__.py
touch backend/api/agents/__init__.py
touch backend/api/agents/tools/__init__.py
touch backend/api/agents/agent_core/__init__.py
touch backend/api/agents/intents/__init__.py
touch backend/api/agents/states/__init__.py
touch backend/api/rai/__init__.py
touch backend/api/rai/moderation/__init__.py
touch backend/api/rai/explainability/__init__.py
touch backend/api/rai/fairness/__init__.py
touch backend/api/rai/hallucination/__init__.py
touch backend/api/llm/__init__.py
touch backend/api/llm/providers/__init__.py
touch backend/api/llm/chunking/__init__.py
touch backend/api/llm/prompts/__init__.py
touch backend/api/integrations/__init__.py
touch backend/api/integrations/firebase/__init__.py
touch backend/api/integrations/supabase/__init__.py
touch backend/api/integrations/supabase/repositories/__init__.py
touch backend/api/integrations/upstash/__init__.py
touch backend/api/integrations/whatsapp/__init__.py
touch backend/api/integrations/tecdoc/__init__.py
touch backend/api/models/__init__.py
touch backend/api/models/database/__init__.py
touch backend/api/models/schemas/__init__.py
touch backend/api/services/__init__.py
touch backend/api/database/__init__.py
touch backend/api/database/migrations/__init__.py
touch backend/api/database/repositories/__init__.py
touch backend/api/database/schemas/__init__.py
touch backend/api/utils/__init__.py
touch backend/api/tests/__init__.py

# Scripts __init__.py files
touch scripts/__init__.py
touch scripts/data_generation/__init__.py
touch scripts/data_generation/prompts/__init__.py
touch scripts/setup/__init__.py
touch scripts/cli/__init__.py

# ============================================
# Create Backend Core Files
# ============================================

# Main application file
touch backend/api/main.py

# Config files
touch backend/api/config/settings.py
touch backend/api/config/firebase_config.py
touch backend/api/config/supabase_config.py
touch backend/api/config/upstash_config.py
touch backend/api/config/chunking_config.py
touch backend/api/config/rai_config.py
touch backend/api/config/tecdoc_config.py
touch backend/api/config/whatsapp_config.py
touch backend/api/config/llm_config.py

# Middleware files
touch backend/api/middleware/firebase_auth.py
touch backend/api/middleware/rate_limiter.py
touch backend/api/middleware/language_detector.py
touch backend/api/middleware/error_handler.py
touch backend/api/middleware/logging_middleware.py

# Router files
touch backend/api/routers/chat.py
touch backend/api/routers/documents.py
touch backend/api/routers/webhooks/whatsapp.py
touch backend/api/routers/admin.py
touch backend/api/routers/health.py
touch backend/api/routers/auth.py

# Agent files
touch backend/api/agents/conversation_manager.py
touch backend/api/agents/intent_classifier.py
touch backend/api/agents/fsm_map.py
touch backend/api/agents/menu_router.py

# Agent tools
touch backend/api/agents/tools/sql_tool.py
touch backend/api/agents/tools/vector_search_tool.py
touch backend/api/agents/tools/tecdoc_tool.py
touch backend/api/agents/tools/document_tool.py
touch backend/api/agents/tools/menu_builder.py

# Agent core
touch backend/api/agents/agent_core/base_agent.py
touch backend/api/agents/agent_core/rag_agent.py
touch backend/api/agents/agent_core/planner.py
touch backend/api/agents/agent_core/memory.py
touch backend/api/agents/agent_core/executor.py

# Agent intents
touch backend/api/agents/intents/product_search.py
touch backend/api/agents/intents/technical_info.py
touch backend/api/agents/intents/price_quote.py
touch backend/api/agents/intents/order_status.py
touch backend/api/agents/intents/return_policy.py
touch backend/api/agents/intents/support_faq.py
touch backend/api/agents/intents/human_escalation.py

# Agent states
touch backend/api/agents/states/greeting.py
touch backend/api/agents/states/intent_gathering.py
touch backend/api/agents/states/vehicle_selection.py
touch backend/api/agents/states/article_lookup.py
touch backend/api/agents/states/specification.py
touch backend/api/agents/states/order_lookup.py
touch backend/api/agents/states/faq_response.py
touch backend/api/agents/states/fallback.py

# RAI files
touch backend/api/rai/client.py
touch backend/api/rai/moderation/moderation_layer.py
touch backend/api/rai/moderation/safety_checks.py
touch backend/api/rai/moderation/privacy_checks.py
touch backend/api/rai/moderation/content_filter.py
touch backend/api/rai/explainability/chain_of_thought.py
touch backend/api/rai/explainability/thread_of_thoughts.py
touch backend/api/rai/explainability/graph_of_thoughts.py
touch backend/api/rai/explainability/chain_of_verification.py
touch backend/api/rai/fairness/bias_detection.py
touch backend/api/rai/fairness/bias_mitigation.py
touch backend/api/rai/hallucination/detector.py

# LLM files
touch backend/api/llm/provider_factory.py
touch backend/api/llm/embeddings.py
touch backend/api/llm/providers/openai_provider.py
touch backend/api/llm/providers/azure_provider.py
touch backend/api/llm/chunking/text_chunker.py
touch backend/api/llm/chunking/pdf_chunker.py
touch backend/api/llm/chunking/strategies.py
touch backend/api/llm/prompts/system_prompts.py
touch backend/api/llm/prompts/templates.py
touch backend/api/llm/prompts/localization.py

# Integration files
touch backend/api/integrations/firebase/auth_client.py
touch backend/api/integrations/firebase/user_manager.py
touch backend/api/integrations/supabase/client.py
touch backend/api/integrations/supabase/vector_store.py
touch backend/api/integrations/supabase/repositories/conversation_repo.py
touch backend/api/integrations/supabase/repositories/product_repo.py
touch backend/api/integrations/supabase/repositories/document_repo.py
touch backend/api/integrations/upstash/redis_client.py
touch backend/api/integrations/upstash/session_manager.py
touch backend/api/integrations/upstash/cache_manager.py
touch backend/api/integrations/whatsapp/webhook_handler.py
touch backend/api/integrations/whatsapp/message_processor.py
touch backend/api/integrations/whatsapp/template_messages.py
touch backend/api/integrations/whatsapp/media_handler.py
touch backend/api/integrations/tecdoc/client.py
touch backend/api/integrations/tecdoc/models.py
touch backend/api/integrations/tecdoc/cache_wrapper.py

# Model files
touch backend/api/models/database/company.py
touch backend/api/models/database/users.py
touch backend/api/models/database/sessions.py
touch backend/api/models/schemas/tecdoc.py
touch backend/api/models/schemas/chat.py
touch backend/api/models/schemas/documents.py
touch backend/api/models/schemas/company.py
touch backend/api/models/enums.py

# Database schema files
touch backend/api/database/schemas/tables.sql
touch backend/api/database/schemas/functions.sql
touch backend/api/database/schemas/indexes.sql
touch backend/api/database/schemas/triggers.sql

# Service files
touch backend/api/services/conversation_service.py
touch backend/api/services/document_service.py
touch backend/api/services/vector_service.py
touch backend/api/services/language_service.py
touch backend/api/services/search_service.py
touch backend/api/services/analytics_service.py
touch backend/api/services/rate_limit_service.py

# Utils files
touch backend/api/utils/validators.py
touch backend/api/utils/logger.py
touch backend/api/utils/metrics.py
touch backend/api/utils/i18n.py
touch backend/api/utils/helpers.py

# Test files
touch backend/api/tests/test_chunking.py
touch backend/api/tests/test_auth.py
touch backend/api/tests/test_integrations.py
touch backend/api/tests/fixtures/sample_data.py

# Dependencies
touch backend/api/dependencies.py

# Backend configuration files
touch backend/requirements.txt
touch backend/requirements-dev.txt
touch backend/Dockerfile
touch backend/fly.toml
touch backend/.env.example

# ============================================
# Create Frontend Files
# ============================================

# App files
touch frontend/src/app/layout.tsx
touch frontend/src/app/page.tsx
touch frontend/src/app/providers.tsx
touch frontend/src/app/chat/page.tsx
touch frontend/src/app/admin/page.tsx
touch frontend/src/app/admin/dashboard/page.tsx

# Component files
touch frontend/src/components/chat/ChatInterface.tsx
touch frontend/src/components/chat/MessageList.tsx
touch frontend/src/components/chat/MessageInput.tsx
touch frontend/src/components/chat/ThoughtProcess.tsx
touch frontend/src/components/chat/RAIIndicators.tsx
touch frontend/src/components/chat/LanguageToggle.tsx
touch frontend/src/components/auth/LoginForm.tsx
touch frontend/src/components/auth/SignupForm.tsx
touch frontend/src/components/auth/AuthGuard.tsx
touch frontend/src/components/common/Loading.tsx
touch frontend/src/components/common/ErrorBoundary.tsx
touch frontend/src/components/common/Header.tsx
touch frontend/src/components/common/Footer.tsx

# Hook files
touch frontend/src/hooks/useAuth.ts
touch frontend/src/hooks/useChat.ts
touch frontend/src/hooks/useLanguage.ts
touch frontend/src/hooks/useRAIMetrics.ts
touch frontend/src/hooks/useWebSocket.ts

# Lib files
touch frontend/src/lib/firebase.ts
touch frontend/src/lib/api.ts
touch frontend/src/lib/i18n.ts
touch frontend/src/lib/constants.ts

# Service files
touch frontend/src/services/auth.service.ts
touch frontend/src/services/chat.service.ts
touch frontend/src/services/analytics.service.ts
touch frontend/src/services/api.service.ts

# Type files
touch frontend/src/types/index.ts
touch frontend/src/types/chat.types.ts
touch frontend/src/types/rai.types.ts
touch frontend/src/types/auth.types.ts

# Utils files
touch frontend/src/utils/helpers.ts
touch frontend/src/utils/validators.ts
touch frontend/src/utils/formatters.ts

# Locale files
touch frontend/src/locales/es/common.json
touch frontend/src/locales/en/common.json

# Frontend configuration files
touch frontend/package.json
touch frontend/tsconfig.json
touch frontend/next.config.js
touch frontend/tailwind.config.js
touch frontend/postcss.config.js
touch frontend/vercel.json
touch frontend/.env.local.example

# ============================================
# Create Script Files
# ============================================

# Data generation scripts
touch scripts/data_generation/generate_all_data.py
touch scripts/data_generation/generate_company_data.py
touch scripts/data_generation/generate_documents.py
touch scripts/data_generation/load_brake_articles.py
touch scripts/data_generation/generate_embeddings.py
touch scripts/data_generation/prompts/manual_prompts.py
touch scripts/data_generation/prompts/faq_prompts.py
touch scripts/data_generation/prompts/policy_prompts.py

# Setup scripts
touch scripts/setup/init_supabase.py
touch scripts/setup/create_structure.sh
touch scripts/setup/setup_local.sh
touch scripts/setup/seed_data.py
touch scripts/setup/initialize_all.py
touch scripts/setup/clone_infosys_rai.sh
touch scripts/setup/create_all_files.sh

# CLI scripts
touch scripts/cli/main.py
touch scripts/cli/commands.py

# ============================================
# Create Config Files
# ============================================

touch config/chunking_config.yaml
touch config/rai_thresholds.yaml
touch config/intent_mappings.yaml
touch config/prompts/system_prompts_es.yaml
touch config/prompts/system_prompts_en.yaml

# ============================================
# Create Documentation Files
# ============================================

touch docs/README.md
touch docs/SETUP.md
touch docs/ARCHITECTURE.md
touch docs/DATABASE_SCHEMA.md
touch docs/API_REFERENCE.md
touch docs/DEPLOYMENT.md
touch docs/INTEGRATIONS.md
touch docs/INFOSYS_RAI.md
touch docs/LOCAL_DEVELOPMENT.md
touch docs/CONFIGURATION.md
touch docs/TROUBLESHOOTING.md
touch docs/FILE_STRUCTURE.md
touch docs/DATA_GENERATION.md

# ============================================
# Create Root Files
# ============================================

touch .env.example
touch .gitignore
touch README.md
touch Makefile
touch docker-compose.yml
touch docker-compose.prod.yml
touch .dockerignore

# ============================================
# Create GitHub Workflow Files
# ============================================

touch .github/workflows/ci.yml
touch .github/workflows/deploy-backend.yml
touch .github/workflows/deploy-frontend.yml
touch .github/workflows/tests.yml

echo "✅ All files created successfully!"
echo "📝 Total files created: $(find . -type f | wc -l)"
echo "📂 Total directories created: $(find . -type d | wc -l)"