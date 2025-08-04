# backend/api/llm/chunking/text_chunker.py
"""Text chunking implementation with multiple strategies
Path: backend/api/llm/chunking/text_chunker.py
"""

from typing import List, Dict, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
import tiktoken
import hashlib

class TextChunker:
    def __init__(self, config: Dict):
        self.config = config
        self.strategy = config.get('default_strategy', 'recursive')
        
    def chunk_text(self, 
                   text: str, 
                   strategy: Optional[str] = None,
                   meta_data: Optional[Dict] = None) -> List[Dict]:
        """Chunk text using specified strategy"""
        
        strategy = strategy or self.strategy
        
        if strategy == 'recursive':
            chunks = self._recursive_chunk(text)
        elif strategy == 'fixed':
            chunks = self._fixed_chunk(text)
        elif strategy == 'semantic':
            chunks = self._semantic_chunk(text)
        else:
            raise ValueError(f"Unknown chunking strategy: {strategy}")
        
        # Add meta_data to each chunk
        result = []
        for i, chunk in enumerate(chunks):
            chunk_data = {
                'content': chunk,
                'chunk_index': i,
                'chunk_hash': hashlib.md5(chunk.encode()).hexdigest(),
                'meta_data': meta_data or {},
                'tokens': self._count_tokens(chunk),
                'strategy': strategy
            }
            result.append(chunk_data)
            
        return result
    
    def _recursive_chunk(self, text: str) -> List[str]:
        """Recursive character text splitting"""
        text_config = self.config.get('text', {})
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=text_config.get('chunk_size', 1000),
            chunk_overlap=text_config.get('chunk_overlap', 200),
            separators=text_config.get('separators', ["\n\n", "\n", ". ", " ", ""]),
            length_function=len
        )
        
        return splitter.split_text(text)
    
    def _fixed_chunk(self, text: str) -> List[str]:
        """Fixed size chunking"""
        text_config = self.config.get('text', {})
        
        splitter = CharacterTextSplitter(
            chunk_size=text_config.get('chunk_size', 1000),
            chunk_overlap=text_config.get('chunk_overlap', 200),
            separator="\n",
            length_function=len
        )
        
        return splitter.split_text(text)
    
    def _semantic_chunk(self, text: str) -> List[str]:
        """Semantic chunking based on sentence embeddings"""
        # Implementation would use sentence-transformers
        # For now, fallback to recursive
        return self._recursive_chunk(text)
    
    def _count_tokens(self, text: str, model: str = "gpt-3.5-turbo") -> int:
        """Count tokens in text"""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except:
            encoding = tiktoken.get_encoding("cl100k_base")
            
        return len(encoding.encode(text))