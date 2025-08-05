# backend/src/infrastructure/database/repositories/document_repo.py
# Path: backend/src/infrastructure/database/repositories/document_repo.py

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import hashlib
import json
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from pgvector.sqlalchemy import Vector

from src.infrastructure.database.models.document import (
    Document as DocumentDB,
    Chunk as ChunkDB,
    DocumentArticleLink as DocumentArticleLinkDB,
    DocumentVehicleLink as DocumentVehicleLinkDB
)
from src.core.models.document import (
    Document, DocumentCreate, DocumentUpdate, DocumentSearch,
    Chunk, ChunkCreate,
    DocumentArticleLink, DocumentVehicleLink,
    VectorSearchParams, SearchResult
)
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

class DocumentRepository:
    """Repository for document-related database operations"""
    
    def __init__(self, db: Session):
        self.db = db
        logger.debug(f"DocumentRepository initialized with session: {db}")
    
    # ==================== Document Operations ====================
    
    async def create_document(self, document: DocumentCreate) -> Document:
        """Create a new document"""
        logger.info(f"Creating document: {document.title}")
        logger.debug(f"Document type: {type(document)}")
        logger.debug(f"Document fields: {document.model_fields_set}")
        
        try:
            # Calculate content hash for deduplication
            content_hash = hashlib.sha256(document.content.encode()).hexdigest()
            logger.debug(f"Content hash: {content_hash}")
            
            # Check if document already exists
            existing = self.db.query(DocumentDB).filter_by(content_hash=content_hash).first()
            if existing:
                logger.info(f"Document already exists with ID: {existing.id}")
                result = Document.model_validate(existing)
                logger.info(f"Validated existing document: {result.id}")
                logger.info(f"Validation result: {result}")
                return result

            # Log the document data before conversion
            logger.debug("Converting Pydantic model to dict...")
            try:
                document_dict = document.model_dump(exclude={'content'})
                logger.debug(f"Document dict keys: {list(document_dict.keys())}")
                logger.debug(f"Document dict: {json.dumps({k: str(v)[:100] if isinstance(v, str) else v for k, v in document_dict.items()}, indent=2)}")
            except Exception as e:
                logger.error(f"Error converting document to dict: {e}", exc_info=True)
                raise
            
            # Create new document
            logger.debug("Creating DocumentDB instance...")
            try:
                db_document = DocumentDB(
                    **document_dict,
                    content=document.content,
                    content_hash=content_hash
                )
                logger.debug(f"DocumentDB instance created successfully")
                logger.debug(f"DB Document attributes: {vars(db_document)}")
            except Exception as e:
                logger.error(f"Error creating DocumentDB instance: {e}", exc_info=True)
                raise
            
            # Add to database
            logger.debug("Adding document to database session...")
            try:
                self.db.add(db_document)
                logger.debug("Document added to session")
                
                logger.debug("Committing transaction...")
                self.db.commit()
                logger.debug("Transaction committed successfully")
                
                logger.debug("Refreshing document instance...")
                self.db.refresh(db_document)
                logger.debug(f"Document refreshed, ID: {db_document.id}")
            except Exception as e:
                logger.error(f"Database error: {e}", exc_info=True)
                self.db.rollback()
                raise
            
            # Convert back to Pydantic model
            logger.debug("Converting SQLAlchemy model back to Pydantic...")
            try:
                result = Document.model_validate(db_document)
                logger.info(f"Document created successfully with ID: {result.id}")
                return result
            except Exception as e:
                logger.error(f"Error validating result model: {e}", exc_info=True)
                raise
                
        except Exception as e:
            logger.error(f"Unexpected error in create_document: {e}", exc_info=True)
            raise
    
    async def get_document(self, document_id: int, include_chunks: bool = False) -> Optional[Document]:
        """Get document by ID"""
        logger.debug(f"Getting document {document_id}, include_chunks={include_chunks}")
        
        query = self.db.query(DocumentDB)
        
        if include_chunks:
            query = query.options(
                joinedload(DocumentDB.chunks),
                joinedload(DocumentDB.article_links),
                joinedload(DocumentDB.vehicle_links)
            )
        
        db_document = query.filter(DocumentDB.id == document_id).first()
        
        if db_document:
            logger.debug(f"Document found: {db_document.title}")
            return Document.model_validate(db_document)
        
        logger.debug(f"Document {document_id} not found")
        return None
    
    async def update_document(self, document_id: int, update: DocumentUpdate) -> Optional[Document]:
        """Update document"""
        logger.debug(f"Updating document {document_id}")
        
        db_document = self.db.query(DocumentDB).filter(DocumentDB.id == document_id).first()
        
        if not db_document:
            logger.warning(f"Document {document_id} not found for update")
            return None
        
        update_data = update.model_dump(exclude_unset=True)
        logger.debug(f"Update data: {update_data}")
        
        for field, value in update_data.items():
            setattr(db_document, field, value)
        
        try:
            self.db.commit()
            self.db.refresh(db_document)
            logger.info(f"Document {document_id} updated successfully")
            return Document.model_validate(db_document)
        except Exception as e:
            logger.error(f"Error updating document: {e}", exc_info=True)
            self.db.rollback()
            raise
    
    async def delete_document(self, document_id: int) -> bool:
        """Delete document and all related data"""
        logger.debug(f"Deleting document {document_id}")
        
        db_document = self.db.query(DocumentDB).filter(DocumentDB.id == document_id).first()
        
        if not db_document:
            logger.warning(f"Document {document_id} not found for deletion")
            return False
        
        try:
            self.db.delete(db_document)
            self.db.commit()
            logger.info(f"Document {document_id} deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Error deleting document: {e}", exc_info=True)
            self.db.rollback()
            raise
    
    async def search_documents(self, params: DocumentSearch) -> Tuple[List[Document], int]:
        """Search documents with filters"""
        logger.debug(f"Searching documents with params: {params}")
        
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
        logger.debug(f"Found {total_count} documents matching criteria")
        
        # Apply pagination
        documents = query.offset(params.offset).limit(params.limit).all()
        
        return [Document.model_validate(doc) for doc in documents], total_count
    
    # ==================== Chunk Operations ====================
    
    async def create_chunk(self, chunk: ChunkCreate) -> Chunk:
        """Create a new chunk"""
        logger.debug(f"Creating chunk for document {chunk.document_id}, index {chunk.chunk_index}")
        
        try:
            db_chunk = ChunkDB(**chunk.model_dump())
            
            self.db.add(db_chunk)
            self.db.commit()
            self.db.refresh(db_chunk)
            
            logger.debug(f"Chunk created with ID: {db_chunk.id}")
            return Chunk.model_validate(db_chunk)
        except Exception as e:
            logger.error(f"Error creating chunk: {e}", exc_info=True)
            self.db.rollback()
            raise
    
    async def create_chunks_bulk(self, chunks: List[ChunkCreate]) -> List[Chunk]:
        """Create multiple chunks in bulk"""
        logger.debug(f"Creating {len(chunks)} chunks in bulk")
        
        try:
            # Create chunk instances
            db_chunks = []
            for chunk in chunks:
                db_chunk = ChunkDB(**chunk.model_dump())
                db_chunks.append(db_chunk)
            
            # Use add_all instead of bulk_save_objects for better ORM integration
            self.db.add_all(db_chunks)
            self.db.commit()
            
            # Refresh each chunk to get the created_at and other defaults
            for db_chunk in db_chunks:
                self.db.refresh(db_chunk)
            
            logger.info(f"Created {len(db_chunks)} chunks successfully")
            
            # Now validate without including the document relationship
            result_chunks = []
            for db_chunk in db_chunks:
                # Create a dict excluding the relationship
                chunk_dict = {
                    'id': db_chunk.id,
                    'document_id': db_chunk.document_id,
                    'content': db_chunk.content,
                    'chunk_index': db_chunk.chunk_index,
                    'meta_data': db_chunk.meta_data,
                    'tokens': db_chunk.tokens,
                    'chunk_strategy': db_chunk.chunk_strategy,
                    'embedding': db_chunk.embedding,
                    'created_at': db_chunk.created_at
                }
                result_chunks.append(Chunk.model_validate(chunk_dict))
            
            return result_chunks
            
        except Exception as e:
            logger.error(f"Error creating chunks in bulk: {e}", exc_info=True)
            self.db.rollback()
            raise
    
    async def hybrid_search(self, query_text: str, query_embedding: List[float], 
                           limit: int = 5, keyword_weight: float = 0.3) -> List[SearchResult]:
        """Perform hybrid search combining vector and keyword search"""
        logger.debug(f"Performing hybrid search: limit={limit}, keyword_weight={keyword_weight}")
        
        # Vector search
        vector_results = self.db.query(
            ChunkDB,
            DocumentDB,
            func.cosine_distance(ChunkDB.embedding, query_embedding).label('vector_score')
        ).join(DocumentDB).order_by('vector_score').limit(limit * 2).all()
        
        logger.debug(f"Vector search returned {len(vector_results)} results")
        
        # Keyword search
        keyword_results = self.db.query(
            ChunkDB,
            DocumentDB,
            func.ts_rank_cd(ChunkDB.search_vector, func.plainto_tsquery('spanish', query_text)).label('keyword_score')
        ).join(DocumentDB).filter(
            ChunkDB.search_vector.match(query_text)
        ).order_by('keyword_score').limit(limit * 2).all()
        
        logger.debug(f"Keyword search returned {len(keyword_results)} results")
        
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
        
        logger.debug(f"Returning {len(final_results[:limit])} final results")
        return final_results[:limit]
    
    # ==================== Link Operations ====================
    
    async def add_article_links(self, links: List[DocumentArticleLink]) -> List[DocumentArticleLink]:
        """Add document-article links"""
        logger.debug(f"Adding {len(links)} article links")
        
        db_links = []
        
        for link in links:
            # Check if link already exists
            existing = self.db.query(DocumentArticleLinkDB).filter_by(
                document_id=link.document_id,
                article_id=link.article_id
            ).first()
            
            if not existing:
                try:
                    db_link = DocumentArticleLinkDB(**link.model_dump())
                    self.db.add(db_link)
                    db_links.append(db_link)
                except Exception as e:
                    logger.error(f"Error adding article link: {e}", exc_info=True)
        
        if db_links:
            try:
                self.db.commit()
                logger.info(f"Added {len(db_links)} new article links")
            except Exception as e:
                logger.error(f"Error committing article links: {e}", exc_info=True)
                self.db.rollback()
                raise
        
        return [DocumentArticleLink.model_validate(link) for link in db_links]
    
    async def add_vehicle_links(self, links: List[DocumentVehicleLink]) -> List[DocumentVehicleLink]:
        """Add document-vehicle links"""
        logger.debug(f"Adding {len(links)} vehicle links")
        
        db_links = []
        
        for link in links:
            # Check if link already exists
            existing = self.db.query(DocumentVehicleLinkDB).filter_by(
                document_id=link.document_id,
                vehicle_id=link.vehicle_id
            ).first()
            
            if not existing:
                try:
                    db_link = DocumentVehicleLinkDB(**link.model_dump())
                    self.db.add(db_link)
                    db_links.append(db_link)
                except Exception as e:
                    logger.error(f"Error adding vehicle link: {e}", exc_info=True)
        
        if db_links:
            try:
                self.db.commit()
                logger.info(f"Added {len(db_links)} new vehicle links")
            except Exception as e:
                logger.error(f"Error committing vehicle links: {e}", exc_info=True)
                self.db.rollback()
                raise
        
        return [DocumentVehicleLink.model_validate(link) for link in db_links]
    
    async def get_documents_by_article(self, article_id: int) -> List[Document]:
        """Get all documents linked to an article"""
        logger.debug(f"Getting documents for article {article_id}")
        
        documents = self.db.query(DocumentDB).join(DocumentArticleLinkDB).filter(
            DocumentArticleLinkDB.article_id == article_id
        ).all()
        
        logger.debug(f"Found {len(documents)} documents for article {article_id}")
        return [Document.model_validate(doc) for doc in documents]
    
    async def get_documents_by_vehicle(self, vehicle_id: int) -> List[Document]:
        """Get all documents linked to a vehicle"""
        logger.debug(f"Getting documents for vehicle {vehicle_id}")
        
        documents = self.db.query(DocumentDB).join(DocumentVehicleLinkDB).filter(
            DocumentVehicleLinkDB.vehicle_id == vehicle_id
        ).all()
        
        logger.debug(f"Found {len(documents)} documents for vehicle {vehicle_id}")
        return [Document.model_validate(doc) for doc in documents]
    
    # ==================== Utility Operations ====================
    
    async def mark_document_processed(self, document_id: int) -> bool:
        """Mark document as processed"""
        logger.debug(f"Marking document {document_id} as processed")
        
        try:
            result = self.db.query(DocumentDB).filter(
                DocumentDB.id == document_id
            ).update({"is_processed": True})
            
            self.db.commit()
            
            if result > 0:
                logger.info(f"Document {document_id} marked as processed")
                return True
            else:
                logger.warning(f"Document {document_id} not found for marking as processed")
                return False
        except Exception as e:
            logger.error(f"Error marking document as processed: {e}", exc_info=True)
            self.db.rollback()
            raise
    
    async def get_unprocessed_documents(self, limit: int = 10) -> List[Document]:
        """Get unprocessed documents"""
        logger.debug(f"Getting up to {limit} unprocessed documents")
        
        documents = self.db.query(DocumentDB).filter(
            DocumentDB.is_processed == False
        ).limit(limit).all()
        
        logger.debug(f"Found {len(documents)} unprocessed documents")
        return [Document.model_validate(doc) for doc in documents]