# backend/src/infrastructure/database/models/document.py
# Path: backend/src/infrastructure/database/models/document.py

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float, DateTime, 
    ForeignKey, UniqueConstraint, Index, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import TSVECTOR
from pgvector.sqlalchemy import Vector
from datetime import datetime

Base = declarative_base()

class Document(Base):
    """Document table model"""
    __tablename__ = 'documents'
    
    # Primary fields
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    document_type = Column(String(50))
    category = Column(String(100))
    subcategory = Column(String(100))
    content = Column(Text)
    content_hash = Column(String(64), unique=True, index=True)
    language = Column(String(2), default='es')
    meta_data = Column(JSON, default=dict)
    hierarchy = Column(JSON, default=dict)
    is_processed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Full text search
    search_vector = Column(TSVECTOR)
    
    # Relationships
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")
    article_links = relationship("DocumentArticleLink", back_populates="document", cascade="all, delete-orphan")
    vehicle_links = relationship("DocumentVehicleLink", back_populates="document", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_documents_type', 'document_type'),
        Index('idx_documents_category', 'category'),
        Index('idx_documents_subcategory', 'subcategory'),
        Index('idx_documents_language', 'language'),
        Index('idx_documents_processed', 'is_processed'),
        Index('idx_documents_search', 'search_vector', postgresql_using='gin'),
    )

class Chunk(Base):
    """Document chunks table model"""
    __tablename__ = 'chunks'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536))  # OpenAI embedding dimension
    meta_data = Column(JSON, default=dict)
    tokens = Column(Integer)
    chunk_strategy = Column(String(50), default='recursive')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Full text search
    search_vector = Column(TSVECTOR)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    
    # Indexes
    __table_args__ = (
        Index('idx_chunks_document_id', 'document_id'),
        Index('idx_chunks_embedding', 'embedding', postgresql_using='ivfflat', 
              postgresql_with={'lists': 100}, postgresql_ops={'embedding': 'vector_cosine_ops'}),
        Index('idx_chunks_search', 'search_vector', postgresql_using='gin'),
    )

class DocumentArticleLink(Base):
    """Links documents to TecDoc article IDs"""
    __tablename__ = 'document_article_links'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    article_id = Column(Integer, nullable=False)
    relevance_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="article_links")
    
    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint('document_id', 'article_id', name='uq_document_article'),
        Index('idx_doc_article_links_doc_id', 'document_id'),
        Index('idx_doc_article_links_article_id', 'article_id'),
    )

class DocumentVehicleLink(Base):
    """Links documents to vehicle IDs"""
    __tablename__ = 'document_vehicle_links'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    vehicle_id = Column(Integer, nullable=False)
    relevance_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="vehicle_links")
    
    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint('document_id', 'vehicle_id', name='uq_document_vehicle'),
        Index('idx_doc_vehicle_links_doc_id', 'document_id'),
        Index('idx_doc_vehicle_links_vehicle_id', 'vehicle_id'),
    )