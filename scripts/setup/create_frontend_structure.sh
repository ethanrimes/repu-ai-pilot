#!/bin/bash
# create_frontend_structure.sh
# Path: frontend/create_frontend_structure.sh

echo "🎨 Creating Next.js frontend structure..."

# Create app directories
mkdir -p src/app/api/auth
mkdir -p src/app/api/chat
mkdir -p src/app/api/session
mkdir -p src/app/[locale]

# Create component directories
mkdir -p src/components/chat
mkdir -p src/components/auth
mkdir -p src/components/ui
mkdir -p src/components/layout

# Create lib directories
mkdir -p src/lib/firebase
mkdir -p src/lib/api
mkdir -p src/lib/redis

# Create hooks directory
mkdir -p src/hooks

# Create utils directory
mkdir -p src/utils

# Create types directory
mkdir -p src/types

# Create i18n directories
mkdir -p src/i18n
mkdir -p src/i18n/locales/es
mkdir -p src/i18n/locales/en

# Create middleware directory
mkdir -p src/middleware

# Create styles directory
mkdir -p src/styles

# ============================================
# Create App Router Files
# ============================================

# API Routes
touch src/app/api/auth/route.ts
touch src/app/api/auth/logout/route.ts
touch src/app/api/auth/session/route.ts
touch src/app/api/chat/route.ts
touch src/app/api/session/route.ts

# Internationalized Pages
touch src/app/[locale]/layout.tsx
touch src/app/[locale]/page.tsx
touch src/app/[locale]/loading.tsx
touch src/app/[locale]/error.tsx

# Root files
touch src/app/not-found.tsx
touch src/middleware.ts

# ============================================
# Create Component Files
# ============================================

# Chat Components
touch src/components/chat/ChatInterface.tsx
touch src/components/chat/MessageList.tsx
touch src/components/chat/MessageItem.tsx
touch src/components/chat/MessageInput.tsx
touch src/components/chat/ThinkingIndicator.tsx
touch src/components/chat/LanguageToggle.tsx

# Auth Components
touch src/components/auth/LoginForm.tsx
touch src/components/auth/SignupForm.tsx
touch src/components/auth/AuthGuard.tsx
touch src/components/auth/UserMenu.tsx

# UI Components
touch src/components/ui/Button.tsx
touch src/components/ui/Input.tsx
touch src/components/ui/Card.tsx
touch src/components/ui/LoadingSpinner.tsx
touch src/components/ui/ErrorMessage.tsx
touch src/components/ui/Toast.tsx

# Layout Components
touch src/components/layout/Header.tsx
touch src/components/layout/Footer.tsx

# ============================================
# Create Lib Files
# ============================================

# Firebase
touch src/lib/firebase/config.ts
touch src/lib/firebase/auth.ts
touch src/lib/firebase/client.ts

# API
touch src/lib/api/client.ts
touch src/lib/api/endpoints.ts
touch src/lib/api/types.ts

# Redis
touch src/lib/redis/client.ts
touch src/lib/redis/session.ts

# ============================================
# Create Hook Files
# ============================================

touch src/hooks/useAuth.ts
touch src/hooks/useChat.ts
touch src/hooks/useLocale.ts
touch src/hooks/useSession.ts
touch src/hooks/useToast.ts

# ============================================
# Create Utility Files
# ============================================

touch src/utils/constants.ts
touch src/utils/helpers.ts
touch src/utils/validators.ts
touch src/utils/formatters.ts

# ============================================
# Create Type Files
# ============================================

touch src/types/index.ts
touch src/types/chat.ts
touch src/types/auth.ts
touch src/types/api.ts

# ============================================
# Create i18n Files
# ============================================

touch src/i18n/config.ts
touch src/i18n/provider.tsx
touch src/i18n/locales/es/common.json
touch src/i18n/locales/es/chat.json
touch src/i18n/locales/es/auth.json
touch src/i18n/locales/en/common.json
touch src/i18n/locales/en/chat.json
touch src/i18n/locales/en/auth.json

# ============================================
# Create Style Files
# ============================================

touch src/styles/chat.module.css
touch src/styles/auth.module.css

# ============================================
# Create Configuration Files
# ============================================

touch .env.local.example

echo "✅ Frontend structure created successfully!"
echo "📁 Total directories created: $(find src -type d | wc -l)"
echo "📄 Total files created: $(find src -type f | wc -l)"