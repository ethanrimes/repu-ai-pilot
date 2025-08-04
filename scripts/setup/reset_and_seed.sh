#!/bin/bash
# reset_and_seed.sh

echo "🔄 Complete Database Reset and Seed"
echo "=================================="

# 1. Reset database
echo "1️⃣ Resetting database..."
python scripts/setup/init_supabase.py --reset

# 2. Load brake articles with stock/prices
echo "2️⃣ Loading brake articles..."
python scripts/data_generation/load_brake_articles.py \
  --articles-path ~/Documents/Projects/repu-data/articles \
  --generate-stock \
  --generate-prices

# 3. Generate company data
echo "3️⃣ Generating company data..."
cd scripts/data_generation
python generate_company_data.py
cd ../..

# 4. Initialize documents
echo "4️⃣ Processing documents..."
cd backend/scripts
python initialize_documents.py
cd ../..

echo "✅ Database reset and seeded successfully!"