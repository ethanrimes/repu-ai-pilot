# backend/src/infrastructure/database/repositories/document_repo.py
# Path: backend/src/infrastructure/database/repositories/document_repo.py

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import hashlib
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from pgvector.sqlalchemy import Vector

from backend.src.infrastructure.database.models.document import (
    Document as DocumentDB,
    Chunk as ChunkDB,
    DocumentArticleLink as DocumentArticleLinkDB,
    DocumentVehicleLink as DocumentVehicleLinkDB
)
from backend.src.core.models.document import (
    Document, DocumentCreate, DocumentUpdate, DocumentSearch,
    Chunk, ChunkCreate,
    DocumentArticleLink, DocumentVehicleLink,
    VectorSearchParams, SearchResult
)

class DocumentRepository:
    """Repository for document-related database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== Document Operations ====================
    
    async def create_document(self, document: DocumentCreate) -> Document:
        """Create a new document"""
        # Calculate content hash for deduplication
        content_hash = hashlib.sha256(document.content.encode()).hexdigest()
        
        # Check if document already exists
        existing = self.db.query(DocumentDB).filter_by(content_hash=content_hash).first()
        if existing:
            return Document.model_validate(existing)
        
        # Create new document
        db_document = DocumentDB(
            **document.model_dump(exclude={'content'}),
            content=document.content,
            content_hash=content_hash
        )
        
        self.db.add(db_document)
        self.db.commit()
        self.db.refresh(db_document)
        
        return Document.model_validate(db_document)
    
    async def get_document(self, document_id: int, include_chunks: bool = False) -> Optional[Document]:
        """Get document by ID"""
        query = self.db.query(DocumentDB)
        
        if include_chunks:
            query = query.options(
                joinedload(DocumentDB.chunks),
                joinedload(DocumentDB.article_links),
                joinedload(DocumentDB.vehicle_links)
            )
        
        db_document = query.filter(DocumentDB.id == document_id).first()
        
        if db_document:
            return Document.model_validate(db_document)
        return None
    
    async def update_document(self, document_id: int, update: DocumentUpdate) -> Optional[Document]:
        """Update document"""
        db_document = self.db.query(DocumentDB).filter(DocumentDB.id == document_id).first()
        
        if not db_document:
            return None
        
        update_data = update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_document, field, value)
        
        self.db.commit()
        self.db.refresh(db_document)
        
        return Document.model_validate(db_document)
    
    async def delete_document(self, document_id: int) -> bool:
        """Delete document and all related data"""
        db_document = self.db.query(DocumentDB).filter(DocumentDB.id == document_id).first()
        
        if not db_document:
            return False
        
        self.db.delete(db_document)
        self.db.commit()
        
        return True
    
    async def search_documents(self, params: DocumentSearch) -> Tuple[List[Document], int]:
        """Search documents with filters"""
        query = self.db.query(DocumentDB)
        
        # Apply filters
        if params.query:
            query = query.filter(
                DocumentDB.search_vector.match(params.query)
            )
        
        if params.document_type:
            query = query.filter(DocumentDB.document_type == params.document_type)
        
        if params.category:
            query = query.filter(DocumentDB.category == params.category)
        
        if params.subcategory:
            query = query.filter(DocumentDB.subcategory == params.subcategory)
        
        if params.language:
            query = query.filter(DocumentDB.language == params.language)
        
        # Filter by article IDs
        if params.article_ids:
            query = query.join(DocumentArticleLinkDB).filter(
                DocumentArticleLinkDB.article_id.in_(params.article_ids)
            )
        
        # Filter by vehicle IDs
        if params.vehicle_ids:
            query = query.join(DocumentVehicleLinkDB).filter(
                DocumentVehicleLinkDB.vehicle_id.in_(params.vehicle_ids)
            )
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        documents = query.offset(params.offset).limit(params.limit).all()
        
        return [Document.model_validate(doc) for doc in documents], total_count
    
    # ==================== Chunk Operations ====================
    
    async def create_chunk(self, chunk: ChunkCreate) -> Chunk:
        """Create a new chunk"""
        db_chunk = ChunkDB(**chunk.model_dump())
        
        self.db.add(db_chunk)
        self.db.commit()
        self.db.refresh(db_chunk)
        
        return Chunk.model_validate(db_chunk)
    
    async def create_chunks_bulk(self, chunks: List[ChunkCreate]) -> List[Chunk]:
        """Create multiple chunks in bulk"""
        db_chunks = [ChunkDB(**chunk.model_dump()) for chunk in chunks]
        
        self.db.bulk_save_objects(db_chunks, return_defaults=True)
        self.db.commit()
        
        return [Chunk.model_validate(chunk) for chunk in db_chunks]
    
    async def vector_search(self, params: VectorSearchParams) -> List[SearchResult]:
        """Perform vector similarity search"""
        # Base query
        query = self.db.query(
            ChunkDB,
            DocumentDB,
            func.cosine_distance(ChunkDB.embedding, params.embedding).label('distance')
        ).join(DocumentDB)
        
        # Apply meta_data filters
        if params.filters:
            for key, value in params.filters.items():
                query = query.filter(
                    ChunkDB.meta_data[key].astext == str(value)
                )
        
        # Order by similarity and limit
        results = query.order_by('distance').limit(params.limit).all()
        
        # Convert to search results
        search_results = []
        for chunk, document, distance in results:
            similarity_score = 1 - distance  # Convert distance to similarity
            
            if similarity_score >= params.similarity_threshold:
                search_results.append(SearchResult(
                    chunk=Chunk.model_validate(chunk),
                    document=Document.model_validate(document),
                    similarity_score=similarity_score
                ))
        
        return search_results
    
    async def hybrid_search(self, query_text: str, query_embedding: List[float], 
                           limit: int = 5, keyword_weight: float = 0.3) -> List[SearchResult]:
        """Perform hybrid search combining vector and keyword search"""
        # Vector search
        vector_results = self.db.query(
            ChunkDB,
            DocumentDB,
            func.cosine_distance(ChunkDB.embedding, query_embedding).label('vector_score')
        ).join(DocumentDB).order_by('vector_score').limit(limit * 2).all()
        
        # Keyword search
        keyword_results = self.db.query(
            ChunkDB,
            DocumentDB,
            func.ts_rank_cd(ChunkDB.search_vector, func.plainto_tsquery('spanish', query_text)).label('keyword_score')
        ).join(DocumentDB).filter(
            ChunkDB.search_vector.match(query_text)
        ).order_by('keyword_score').limit(limit * 2).all()
        
        # Combine results
        combined_scores = {}
        
        for chunk, document, score in vector_results:
            key = (chunk.id, document.id)
            combined_scores[key] = {
                'chunk': chunk,
                'document': document,
                'vector_score': 1 - score,
                'keyword_score': 0
            }
        
        for chunk, document, score in keyword_results:
            key = (chunk.id, document.id)
            if key in combined_scores:
                combined_scores[key]['keyword_score'] = score
            else:
                combined_scores[key] = {
                    'chunk': chunk,
                    'document': document,
                    'vector_score': 0,
                    'keyword_score': score
                }
        
        # Calculate combined scores
        final_results = []
        for data in combined_scores.values():
            combined_score = (
                data['vector_score'] * (1 - keyword_weight) +
                data['keyword_score'] * keyword_weight
            )
            
            final_results.append(SearchResult(
                chunk=Chunk.model_validate(data['chunk']),
                document=Document.model_validate(data['document']),
                similarity_score=combined_score
            ))
        
        # Sort by combined score and limit
        final_results.sort(key=lambda x: x.similarity_score, reverse=True)
        return final_results[:limit]
    
    # ==================== Link Operations ====================
    
    async def add_article_links(self, links: List[DocumentArticleLink]) -> List[DocumentArticleLink]:
        """Add document-article links"""
        db_links = []
        
        for link in links:
            # Check if link already exists
            existing = self.db.query(DocumentArticleLinkDB).filter_by(
                document_id=link.document_id,
                article_id=link.article_id
            ).first()
            
            if not existing:
                db_link = DocumentArticleLinkDB(**link.model_dump())
                self.db.add(db_link)
                db_links.append(db_link)
        
        self.db.commit()
        
        return [DocumentArticleLink.model_validate(link) for link in db_links]
    
    async def add_vehicle_links(self, links: List[DocumentVehicleLink]) -> List[DocumentVehicleLink]:
        """Add document-vehicle links"""
        db_links = []
        
        for link in links:
            # Check if link already exists
            existing = self.db.query(DocumentVehicleLinkDB).filter_by(
                document_id=link.document_id,
                vehicle_id=link.vehicle_id
            ).first()
            
            if not existing:
                db_link = DocumentVehicleLinkDB(**link.model_dump())
                self.db.add(db_link)
                db_links.append(db_link)
        
        self.db.commit()
        
        return [DocumentVehicleLink.model_validate(link) for link in db_links]
    
    async def get_documents_by_article(self, article_id: int) -> List[Document]:
        """Get all documents linked to an article"""
        documents = self.db.query(DocumentDB).join(DocumentArticleLinkDB).filter(
            DocumentArticleLinkDB.article_id == article_id
        ).all()
        
        return [Document.model_validate(doc) for doc in documents]
    
    async def get_documents_by_vehicle(self, vehicle_id: int) -> List[Document]:
        """Get all documents linked to a vehicle"""
        documents = self.db.query(DocumentDB).join(DocumentVehicleLinkDB).filter(
            DocumentVehicleLinkDB.vehicle_id == vehicle_id
        ).all()
        
        return [Document.model_validate(doc) for doc in documents]
    
    # ==================== Utility Operations ====================
    
    async def mark_document_processed(self, document_id: int) -> bool:
        """Mark document as processed"""
        result = self.db.query(DocumentDB).filter(
            DocumentDB.id == document_id
        ).update({"is_processed": True})
        
        self.db.commit()
        return result > 0
    
    async def get_unprocessed_documents(self, limit: int = 10) -> List[Document]:
        """Get unprocessed documents"""
        documents = self.db.query(DocumentDB).filter(
            DocumentDB.is_processed == False
        ).limit(limit).all()
        
        return [Document.model_validate(doc) for doc in documents]