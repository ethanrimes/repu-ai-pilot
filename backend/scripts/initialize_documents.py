# backend/scripts/initialize_documents.py
# Path: backend/scripts/initialize_documents.py

import asyncio
import os
import sys
import json
from pathlib import Path
import yaml
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add project root (repu-ai-pilot/) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
print(f"Project root added to sys.path: {sys.path[-1]}")

from backend.src.config.settings import get_settings
from backend.src.infrastructure.integrations.supabase.supabase_config import get_supabase_client
from backend.src.infrastructure.database.models.document import Base
from backend.src.infrastructure.database.repositories.document_repo import DocumentRepository
from backend.src.core.services.document_service import DocumentService
from backend.src.core.models.document import DocumentType, DocumentCategory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Constants
UNSTRUCTURED_DATA_PATH = "/Users/ethankallett/Documents/Projects/repu-data/unstructured_autoparts_data"
CHUNKING_CONFIG_PATH = "config/chunking_config.yaml"

# Article ID mappings for manuals
ARTICLE_ID_MAPPINGS = {
    "manual_brake_disc_100032_advics_6716338.md": 6716338,
    "manual_brake_disc_100032_bendix_5988664.md": 5988664,
    "manual_brake_disc_100032_blueprint_5626927.md": 5626927,
    "manual_brake_disc_100032_blueprint_5607527.md": 5607527,
    "manual_brake_disc_100032_dba_6552458.md": 6552458,
    "manual_brake_disc_100032_febi_1629597.md": 1629597,
    "manual_brake_disc_100032_febi_951575.md": 951575,
    "manual_brake_disc_100032_hella_5086713.md": 5086713,
    "manual_brake_disc_100032_hella_pagid_5086714.md": 5086714,
    "manual_brake_disc_100032_herth_buss_7595774.md": 7595774,
    "manual_brake_disc_100032_herth_buss_7596487.md": 7596487,
    "manual_brake_disc_100032_hiq_9008533.md": 9008533,
    "manual_brake_disc_100032_mintex_8095287.md": 8095287,
    "manual_brake_disc_100032_nisshinbo_8272938.md": 8272938,
    "manual_brake_disc_100032_quaro_8670161.md": 8670161,
    "manual_brake_caliper_parts_100806_bleeder_screw_155265.md": 155265,
    "manual_brake_caliper_parts_100806_guide_bolt_1032537.md": 1032537,
    "manual_brake_caliper_parts_100806_guide_sleeve_kit_1043329.md": 1043329,
    "manual_brake_caliper_parts_100806_accessory_kit_5090433.md": 5090433,
    "manual_high_performance_brake_disc_102226_DBA2571S_6552459.md": 6552459,
    "manual_triscan_8105_101654.md": 4700838,
    "manual_quickbrake_109_1755.md": 958062,
    "manual_metzger_109_1755.md": 958060,
    "manual_herth_j3663026.md": 7599188,
    "manual_delphi_lx0571.md": 7967906,
    "manual_abs_1755q.md": 1602276,
    "manual_brake_pad_100030_5502475.md": 5502475,
    "manual_brake_pad_100030_8359945.md": 8359945,
    "manual_brake_pad_100030_2301246.md": 2301246,
    "manual_brake_pad_100030_1620122.md": 1620122,
    "manual_brake_pad_100030_8093374.md": 8093374,
    "manual_brake_pad_100030_6054253.md": 6054253,
    "manual_brake_pad_100030_6494849.md": 6494849
}

# Vehicle ID mappings
VEHICLE_ID_MAPPINGS = {
    "kia-k3.json": [131675, 131676, 134079, 134965, 135148, 135160, 141025, 141110],
    "mazda-cx-30.json": [137046, 137047, 137048, 137049, 137050, 137051, 138617, 138618, 
                         138619, 138673, 138817, 138818, 138827, 138828, 139259, 139260, 
                         143727, 145068, 145069],
    "toyota-corolla.json": [141200, 141203, 143553, 143554, 146358, 146360, 146503, 
                            148280, 149658, 149659]
}

# Category mappings based on directory structure
CATEGORY_MAPPINGS = {
    "faqs": DocumentCategory.FAQS,
    "legal": DocumentCategory.LEGAL,
    "policies": DocumentCategory.POLICIES,
    "shipping_info": DocumentCategory.SHIPPING_INFO,
    "store_info": DocumentCategory.STORE_INFO,
    "tech docs": DocumentCategory.TECH_DOCS
}

async def create_tables(database_url: str):
    """Create all document-related tables"""
    print("Creating database tables...")
    
    # Read and execute SQL
    sql_file = Path(__file__).parent.parent / "src" / "infrastructure" / "database" / "document_tables.sql"
    
    if sql_file.exists():
        engine = create_engine(database_url)
        
        with open(sql_file, 'r') as f:
            sql_content = f.read()
        
        # Execute SQL statements
        with engine.connect() as conn:
            # Split by semicolon and execute each statement
            statements = [s.strip() for s in sql_content.split(';') if s.strip()]
            
            for statement in statements:
                try:
                    conn.execute(statement)
                    conn.commit()
                except Exception as e:
                    print(f"Warning executing statement: {e}")
                    # Continue with other statements
        
        print("✅ Database tables created successfully")
    else:
        print("❌ SQL file not found, using SQLAlchemy to create tables...")
        
        # Fallback to SQLAlchemy
        engine = create_engine(database_url)
        Base.meta_data.create_all(bind=engine)
        print("✅ Tables created with SQLAlchemy")

def load_chunking_config() -> Dict[str, Any]:
    """Load chunking configuration"""
    config_path = Path(CHUNKING_CONFIG_PATH)
    
    if not config_path.exists():
        # Default configuration
        return {
            "default_strategy": "recursive",
            "text": {
                "chunk_size": 1000,
                "chunk_overlap": 200,
                "separators": ["\n\n", "\n", ". ", " ", ""]
            },
            "document_type_config": {
                "manual": {
                    "chunk_size": 1500,
                    "chunk_overlap": 300,
                    "strategy": "recursive"
                },
                "faq": {
                    "chunk_size": 800,
                    "chunk_overlap": 100,
                    "strategy": "recursive"
                },
                "policy": {
                    "chunk_size": 1200,
                    "chunk_overlap": 200,
                    "strategy": "recursive"
                }
            }
        }
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def get_file_processors() -> Dict[str, Dict[str, Any]]:
    """Build file processor configuration for each file"""
    processors = {}
    
    # Walk through the directory structure
    for root, dirs, files in os.walk(UNSTRUCTURED_DATA_PATH):
        for file in files:
            if not file.endswith(('.md', '.json', '.txt')):
                continue
            
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, UNSTRUCTURED_DATA_PATH)
            
            # Extract category and subcategory from path
            path_parts = Path(relative_path).parts
            category_name = path_parts[0] if len(path_parts) > 0 else None
            subcategory = path_parts[1] if len(path_parts) > 1 else None
            
            # Base processor config
            processor = {
                'title': generate_title_from_filename(file),
                'category': CATEGORY_MAPPINGS.get(category_name),
                'subcategory': subcategory,
                'meta_data': {
                    'original_path': relative_path,
                    'category_raw': category_name,
                }
            }
            
            # Detect document type
            if 'manual' in file.lower():
                processor['document_type'] = DocumentType.MANUAL
                # Add article ID if mapped
                if file in ARTICLE_ID_MAPPINGS:
                    processor['article_ids'] = [ARTICLE_ID_MAPPINGS[file]]
                    processor['meta_data']['article_id'] = ARTICLE_ID_MAPPINGS[file]
            elif 'faq' in file.lower():
                processor['document_type'] = DocumentType.FAQ
            elif 'policy' in file.lower() or 'policies' in relative_path.lower():
                processor['document_type'] = DocumentType.POLICY
            elif 'diagnostic' in file.lower():
                processor['document_type'] = DocumentType.DIAGNOSTIC
            elif 'installation' in file.lower() or 'install' in file.lower():
                processor['document_type'] = DocumentType.INSTALLATION
            elif 'spec' in file.lower():
                processor['document_type'] = DocumentType.SPECIFICATION
            elif 'service' in file.lower():
                processor['document_type'] = DocumentType.SERVICE
            
            # Add vehicle IDs for fluids documents
            if subcategory == 'fluids' and file.endswith('.md'):
                # Extract vehicle info from filename
                if 'kia_k3' in file.lower():
                    processor['vehicle_ids'] = VEHICLE_ID_MAPPINGS.get("kia-k3.json", [])
                elif 'mazda_cx30' in file.lower() or 'mazda_cx-30' in file.lower():
                    processor['vehicle_ids'] = VEHICLE_ID_MAPPINGS.get("mazda-cx-30.json", [])
                elif 'toyota_corolla' in file.lower():
                    processor['vehicle_ids'] = VEHICLE_ID_MAPPINGS.get("toyota-corolla.json", [])
            
            # Add vehicle IDs for torque specs
            if subcategory == 'torque' and file.endswith('.md'):
                if 'kia_k3' in file.lower():
                    processor['vehicle_ids'] = VEHICLE_ID_MAPPINGS.get("kia-k3.json", [])
                elif 'mazda_cx30' in file.lower():
                    processor['vehicle_ids'] = VEHICLE_ID_MAPPINGS.get("mazda-cx-30.json", [])
                elif 'corolla_cross' in file.lower():
                    processor['vehicle_ids'] = VEHICLE_ID_MAPPINGS.get("toyota-corolla.json", [])
            
            # Add brand meta_data for manuals
            if processor.get('document_type') == DocumentType.MANUAL:
                brand = extract_brand_from_filename(file)
                if brand:
                    processor['meta_data']['brand'] = brand
            
            processors[relative_path] = processor
    
    return processors

def generate_title_from_filename(filename: str) -> str:
    """Generate a readable title from filename"""
    # Remove extension
    name = os.path.splitext(filename)[0]
    
    # Replace underscores and hyphens with spaces
    name = name.replace('_', ' ').replace('-', ' ')
    
    # Handle common abbreviations
    replacements = {
        'es': 'Español',
        'en': 'English',
        'faq': 'FAQ',
        'csv': 'CSV',
        'json': 'JSON',
        'sla': 'SLA'
    }
    
    # Capitalize words
    words = name.split()
    title_words = []
    
    for word in words:
        word_lower = word.lower()
        if word_lower in replacements:
            title_words.append(replacements[word_lower])
        elif word_lower in ['de', 'la', 'el', 'en', 'y', 'o', 'para', 'of', 'the', 'and', 'for']:
            title_words.append(word_lower)
        else:
            title_words.append(word.capitalize())
    
    return ' '.join(title_words)

def extract_brand_from_filename(filename: str) -> Optional[str]:
    """Extract brand name from manual filename"""
    brands = ['advics', 'bendix', 'blueprint', 'dba', 'febi', 'hella', 'herth_buss', 
              'hiq', 'mintex', 'nisshinbo', 'quaro', 'pagid', 'triscan', 'quickbrake',
              'metzger', 'herth', 'delphi', 'abs']
    
    filename_lower = filename.lower()
    for brand in brands:
        if brand in filename_lower:
            return brand.replace('_', ' ').title()
    
    return None

async def test_sample_files(document_service: DocumentService):
    """Test chunking on sample files"""
    print("\n" + "="*50)
    print("Testing chunking on sample files...")
    print("="*50)
    
    sample_files = [
        os.path.join(UNSTRUCTURED_DATA_PATH, "tech docs", "manuals", "manual_brake_disc_100032_advics_6716338.md"),
        os.path.join(UNSTRUCTURED_DATA_PATH, "faqs", "faqs_es_json.md"),
        os.path.join(UNSTRUCTURED_DATA_PATH, "policies", "return_policy_es.md"),
        os.path.join(UNSTRUCTURED_DATA_PATH, "tech docs", "fluids", "mazda_cx30_specs.md"),
    ]
    
    # Filter existing files
    existing_samples = [f for f in sample_files if os.path.exists(f)]
    
    if not existing_samples:
        print("No sample files found for testing")
        return
    
    test_results = await document_service.test_chunking(existing_samples, UNSTRUCTURED_DATA_PATH)
    
    for file_path, results in test_results.items():
        print(f"\n📄 File: {os.path.basename(file_path)}")
        
        if 'error' in results:
            print(f"   ❌ Error: {results['error']}")
        else:
            print(f"   Total chunks: {results['total_chunks']}")
            print(f"   Average chunk size: {results['avg_chunk_size']:.0f} characters")
            print(f"   Total tokens: {results['total_tokens']}")
            
            if results.get('chunk_samples'):
                print("   Sample chunks:")
                for sample in results['chunk_samples']:
                    print(f"     - Chunk {sample['index']}: {sample['size']} chars, {sample['tokens']} tokens")
                    print(f"       Preview: {sample['preview']}")

async def main():
    """Main initialization function"""
    print("🚀 Initializing Document Processing System")
    print("="*50)
    
    # Get settings
    settings = get_settings()
    
    # Create database connection
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    await create_tables(settings.database_url)
    
    # Initialize services
    with SessionLocal() as db:
        repository = DocumentRepository(db)
        chunking_config = load_chunking_config()
        document_service = DocumentService(repository, chunking_config)
        
        # Test chunking first
        await test_sample_files(document_service)
        
        # Ask for confirmation before processing all files
        print("\n" + "="*50)
        print(f"Ready to process all files in: {UNSTRUCTURED_DATA_PATH}")
        response = input("Continue with full processing? (y/n): ")
        
        if response.lower() != 'y':
            print("Processing cancelled")
            return
        
        # Get file processors configuration
        file_processors = get_file_processors()
        
        print(f"\n📋 Found {len(file_processors)} files to process")
        
        # Process all documents
        print("\n🔄 Processing all documents...")
        results = await document_service.process_directory(
            UNSTRUCTURED_DATA_PATH, 
            file_processors
        )
        
        # Print results
        print("\n" + "="*50)
        print("📊 Processing Results")
        print("="*50)
        print(f"✅ Processed files: {results['processed_files']}")
        print(f"📄 Total documents: {results['total_documents']}")
        print(f"🧩 Total chunks: {results['total_chunks']}")
        
        if results['stats_by_category']:
            print("\n📈 Stats by Category:")
            for category, stats in results['stats_by_category'].items():
                print(f"   {category}: {stats['documents']} documents, {stats['chunks']} chunks")
        
        if results['errors']:
            print(f"\n❌ Errors encountered: {len(results['errors'])}")
            for error in results['errors'][:5]:  # Show first 5 errors
                print(f"   - {error}")
            
            if len(results['errors']) > 5:
                print(f"   ... and {len(results['errors']) - 5} more errors")
        
        print("\n✅ Document processing complete!")
        
        # Create summary report
        summary_path = "document_processing_summary.json"
        summary_data = {
            **results,
            'timestamp': datetime.now().isoformat(),
            'data_path': UNSTRUCTURED_DATA_PATH,
            'total_files_configured': len(file_processors)
        }
        
        with open(summary_path, 'w') as f:
            json.dump(summary_data, f, indent=2)
        print(f"\n📝 Summary report saved to: {summary_path}")

if __name__ == "__main__":
    asyncio.run(main())