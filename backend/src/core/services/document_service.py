# backend/src/core/services/document_service.py
# Path: backend/src/core/services/document_service.py

import os
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import asyncio
from datetime import datetime

from backend.src.core.models.document import (
    Document, DocumentCreate, DocumentUpdate,
    Chunk, ChunkCreate,
    DocumentArticleLink, DocumentVehicleLink,
    DocumentType, DocumentCategory, ChunkStrategy
)
from backend.src.infrastructure.database.repositories.document_repo import DocumentRepository
from backend.src.infrastructure.llm.embeddings import get_embedding_service
from backend.src.infrastructure.llm.chunking.text_chunker import TextChunker
from backend.src.shared.utils.logger import get_logger

logger = get_logger(__name__)

class DocumentService:
    """Service for managing document operations"""
    
    def __init__(self, repository: DocumentRepository, chunking_config: Dict[str, Any]):
        self.repository = repository
        self.text_chunker = TextChunker(chunking_config)
        self.embedding_service = get_embedding_service()
    
    async def process_document(
        self, 
        file_path: str,
        title: str,
        document_type: Optional[DocumentType] = None,
        category: Optional[DocumentCategory] = None,
        subcategory: Optional[str] = None,
        meta_data: Optional[Dict[str, Any]] = None,
        article_ids: Optional[List[int]] = None,
        vehicle_ids: Optional[List[int]] = None,
        chunk_strategy: Optional[ChunkStrategy] = None
    ) -> Tuple[Document, List[Chunk]]:
        """Process a single document: create, chunk, embed, and link"""
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract hierarchy from file path
        path_parts = Path(file_path).parts
        hierarchy = self._extract_hierarchy(path_parts)
        
        # Merge provided meta_data with extracted meta_data
        file_meta_data = {
            'file_size': os.path.getsize(file_path),
            'file_extension': Path(file_path).suffix,
            'created_at': datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
            'modified_at': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
        }

        if meta_data:
            file_meta_data.update(meta_data)
        
        # Create document
        document_create = DocumentCreate(
            title=title,
            filename=os.path.basename(file_path),
            file_path=file_path,
            document_type=document_type,
            category=category,
            subcategory=subcategory,
            content=content,
            language=self._detect_language(content),
            meta_data=file_meta_data,
            hierarchy=hierarchy
        )
        
        document = await self.repository.create_document(document_create)
        logger.info(f"Created document: {document.id} - {document.title}")
        
        # Chunk the document
        chunk_config = self._get_chunk_config(document_type, chunking_config)
        chunks_data = self.text_chunker.chunk_text(
            content, 
            strategy=chunk_strategy or chunk_config.get('strategy', 'recursive'),
            meta_data={'document_id': document.id, 'document_type': document_type}
        )
        
        # Create chunks with embeddings
        chunks = await self._create_chunks_with_embeddings(document.id, chunks_data)
        logger.info(f"Created {len(chunks)} chunks for document {document.id}")
        
        # Create article links if provided
        if article_ids:
            article_links = [
                DocumentArticleLink(
                    document_id=document.id,
                    article_id=article_id,
                    relevance_score=1.0
                )
                for article_id in article_ids
            ]
            await self.repository.add_article_links(article_links)
            logger.info(f"Linked document {document.id} to {len(article_ids)} articles")
        
        # Create vehicle links if provided
        if vehicle_ids:
            vehicle_links = [
                DocumentVehicleLink(
                    document_id=document.id,
                    vehicle_id=vehicle_id,
                    relevance_score=1.0
                )
                for vehicle_id in vehicle_ids
            ]
            await self.repository.add_vehicle_links(vehicle_links)
            logger.info(f"Linked document {document.id} to {len(vehicle_ids)} vehicles")
        
        # Mark document as processed
        await self.repository.mark_document_processed(document.id)
        
        return document, chunks
    
    async def process_directory(
        self,
        directory_path: str,
        file_processors: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process all documents in a directory"""
        results = {
            'processed_files': 0,
            'total_documents': 0,
            'total_chunks': 0,
            'errors': [],
            'stats_by_category': {}
        }
        
        # Walk through directory
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if not file.endswith(('.md', '.json', '.txt')):
                    continue
                
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, directory_path)
                
                try:
                    # Get processor info for this file if provided
                    processor_info = None
                    if file_processors:
                        processor_info = file_processors.get(relative_path, {})
                    
                    # Process the document
                    document, chunks = await self.process_document(
                        file_path=file_path,
                        title=processor_info.get('title', self._generate_title(file)),
                        document_type=processor_info.get('document_type'),
                        category=processor_info.get('category'),
                        subcategory=processor_info.get('subcategory'),
                        meta_data=processor_info.get('meta_data'),
                        article_ids=processor_info.get('article_ids'),
                        vehicle_ids=processor_info.get('vehicle_ids')
                    )
                    
                    results['processed_files'] += 1
                    results['total_documents'] += 1
                    results['total_chunks'] += len(chunks)
                    
                    # Update category stats
                    category = document.category or 'uncategorized'
                    if category not in results['stats_by_category']:
                        results['stats_by_category'][category] = {
                            'documents': 0,
                            'chunks': 0
                        }
                    results['stats_by_category'][category]['documents'] += 1
                    results['stats_by_category'][category]['chunks'] += len(chunks)
                    
                except Exception as e:
                    error_msg = f"Error processing {file_path}: {str(e)}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
        
        return results
    
    async def test_chunking(
        self,
        file_paths: List[str],
        base_path: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """Test chunking on sample files without saving to database"""
        results = {}
        
        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Detect document type
                doc_type = self._detect_document_type(file_path, base_path)
                
                # Get chunking config
                chunk_config = self._get_chunk_config(doc_type, self.text_chunker.config)
                
                # Chunk the text
                chunks_data = self.text_chunker.chunk_text(
                    content,
                    strategy=chunk_config.get('strategy', 'recursive')
                )
                
                # Calculate statistics
                total_tokens = sum(chunk['tokens'] for chunk in chunks_data)
                avg_chunk_size = sum(len(chunk['content']) for chunk in chunks_data) / len(chunks_data) if chunks_data else 0
                
                results[file_path] = {
                    'total_chunks': len(chunks_data),
                    'avg_chunk_size': avg_chunk_size,
                    'total_tokens': total_tokens,
                    'chunk_samples': [
                        {
                            'index': i,
                            'size': len(chunk['content']),
                            'tokens': chunk['tokens'],
                            'preview': chunk['content'][:100] + '...' if len(chunk['content']) > 100 else chunk['content']
                        }
                        for i, chunk in enumerate(chunks_data[:3])  # First 3 chunks as samples
                    ]
                }
                
            except Exception as e:
                results[file_path] = {'error': str(e)}
        
        return results
    
    async def _create_chunks_with_embeddings(
        self,
        document_id: int,
        chunks_data: List[Dict[str, Any]]
    ) -> List[Chunk]:
        """Create chunks with embeddings"""
        # Extract text from chunks
        texts = [chunk['content'] for chunk in chunks_data]
        
        # Generate embeddings in batch
        embeddings = await self.embedding_service.get_embeddings_batch(texts)
        
        # Create chunk objects
        chunk_creates = []
        for i, (chunk_data, embedding) in enumerate(zip(chunks_data, embeddings)):
            chunk_create = ChunkCreate(
                document_id=document_id,
                content=chunk_data['content'],
                chunk_index=chunk_data['chunk_index'],
                meta_data=chunk_data['meta_data'],
                tokens=chunk_data['tokens'],
                chunk_strategy=ChunkStrategy(chunk_data['strategy']),
                embedding=embedding
            )
            chunk_creates.append(chunk_create)
        
        # Bulk create chunks
        return await self.repository.create_chunks_bulk(chunk_creates)
    
    def _extract_hierarchy(self, path_parts: Tuple[str, ...]) -> Dict[str, Any]:
        """Extract hierarchy from file path"""
        hierarchy = {}
        
        # Find the index of the data root
        try:
            data_root_idx = path_parts.index('unstructured_autoparts_data')
            relevant_parts = path_parts[data_root_idx + 1:]
            
            if len(relevant_parts) > 0:
                hierarchy['root'] = relevant_parts[0]
            if len(relevant_parts) > 1:
                hierarchy['level1'] = relevant_parts[1]
            if len(relevant_parts) > 2:
                hierarchy['level2'] = relevant_parts[2]
        except ValueError:
            # If we can't find the expected root, just use the last few parts
            if len(path_parts) > 1:
                hierarchy['root'] = path_parts[-2]
            if len(path_parts) > 2:
                hierarchy['level1'] = path_parts[-3]
        
        return hierarchy
    
    def _detect_language(self, content: str) -> str:
        """Simple language detection based on common words"""
        spanish_words = ['el', 'la', 'de', 'que', 'y', 'en', 'es', 'para']
        english_words = ['the', 'and', 'of', 'to', 'in', 'is', 'for', 'that']
        
        content_lower = content.lower()
        spanish_count = sum(1 for word in spanish_words if f' {word} ' in content_lower)
        english_count = sum(1 for word in english_words if f' {word} ' in content_lower)
        
        return 'es' if spanish_count > english_count else 'en'
    
    def _detect_document_type(self, file_path: str, base_path: Optional[str] = None) -> Optional[DocumentType]:
        """Detect document type from file path"""
        path_lower = file_path.lower()
        
        if 'manual' in path_lower:
            return DocumentType.MANUAL
        elif 'faq' in path_lower:
            return DocumentType.FAQ
        elif 'policy' in path_lower or 'policies' in path_lower:
            return DocumentType.POLICY
        elif 'diagnostic' in path_lower:
            return DocumentType.DIAGNOSTIC
        elif 'installation' in path_lower or 'install' in path_lower:
            return DocumentType.INSTALLATION
        elif 'catalog' in path_lower:
            return DocumentType.CATALOG
        elif 'specification' in path_lower or 'spec' in path_lower:
            return DocumentType.SPECIFICATION
        elif 'service' in path_lower:
            return DocumentType.SERVICE
        
        return None
    
    def _generate_title(self, filename: str) -> str:
        """Generate a readable title from filename"""
        # Remove extension
        name = os.path.splitext(filename)[0]
        
        # Replace underscores and hyphens with spaces
        name = name.replace('_', ' ').replace('-', ' ')
        
        # Capitalize words
        words = name.split()
        title_words = []
        
        for word in words:
            if word.lower() in ['de', 'la', 'el', 'en', 'y', 'o', 'para']:
                title_words.append(word.lower())
            else:
                title_words.append(word.capitalize())
        
        return ' '.join(title_words)
    
    def _get_chunk_config(self, document_type: Optional[DocumentType], base_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get chunking configuration for document type"""
        type_configs = base_config.get('document_type_config', {})
        
        if document_type and document_type.value in type_configs:
            config = type_configs[document_type.value].copy()
            # Merge with base text config
            base_text_config = base_config.get('text', {})
            return {**base_text_config, **config}
        
        return base_config.get('text', {})