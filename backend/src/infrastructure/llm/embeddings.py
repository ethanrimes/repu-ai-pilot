# backend/src/infrastructure/llm/embeddings.py
# Path: backend/src/infrastructure/llm/embeddings.py

from typing import List, Union, Optional
import openai
from openai import AsyncOpenAI
import numpy as np
from functools import lru_cache
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config.settings import get_settings

settings = get_settings()

@lru_cache()
def get_openai_client() -> AsyncOpenAI:
    """Get OpenAI client instance"""
    return AsyncOpenAI(api_key=settings.openai_api_key)

class EmbeddingService:
    """Service for generating text embeddings"""
    
    def __init__(self, model: str = None):
        self.client = get_openai_client()
        self.model = model or settings.embedding_model or "text-embedding-3-small"
        self.dimension = 1536  # Default for OpenAI embeddings
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text"""
        # Clean and truncate text if needed
        text = text.strip()
        if not text:
            # Return zero vector for empty text
            return [0.0] * self.dimension
        
        # OpenAI has a token limit, so we might need to truncate
        # Rough estimate: 1 token ≈ 4 characters
        max_chars = 8000  # Conservative limit
        if len(text) > max_chars:
            text = text[:max_chars]
        
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=text
            )
            
            return response.data[0].embedding
        
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise
    
    async def get_embeddings_batch(self, texts: List[str], batch_size: int = 20) -> List[List[float]]:
        """Get embeddings for multiple texts in batches"""
        embeddings = []
        
        # Process in batches to avoid rate limits
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=batch
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
                
                # Small delay between batches to avoid rate limits
                if i + batch_size < len(texts):
                    await asyncio.sleep(0.1)
            
            except Exception as e:
                print(f"Error in batch {i//batch_size}: {e}")
                # Return zero vectors for failed batch
                embeddings.extend([[0.0] * self.dimension] * len(batch))
        
        return embeddings
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def find_most_similar(self, query_embedding: List[float], 
                         embeddings: List[List[float]], 
                         top_k: int = 5) -> List[tuple[int, float]]:
        """Find most similar embeddings to query"""
        similarities = []
        
        for i, embedding in enumerate(embeddings):
            similarity = self.cosine_similarity(query_embedding, embedding)
            similarities.append((i, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]

# Singleton instance
_embedding_service: Optional[EmbeddingService] = None

def get_embedding_service() -> EmbeddingService:
    """Get singleton embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service

async def get_embeddings(text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
    """Convenience function to get embeddings"""
    service = get_embedding_service()
    
    if isinstance(text, str):
        return await service.get_embedding(text)
    else:
        return await service.get_embeddings_batch(text)

async def test_embeddings():
    """Test embedding generation"""
    test_texts = [
        "Manual de instalación de frenos para Mazda CX-30",
        "How to install brake pads",
        "Política de devoluciones"
    ]
    
    print("Testing embedding service...")
    service = get_embedding_service()
    
    # Test single embedding
    embedding = await service.get_embedding(test_texts[0])
    print(f"✅ Single embedding generated: dimension={len(embedding)}")
    
    # Test batch embeddings
    embeddings = await service.get_embeddings_batch(test_texts)
    print(f"✅ Batch embeddings generated: count={len(embeddings)}")
    
    # Test similarity
    similarities = service.find_most_similar(embeddings[0], embeddings[1:])
    print(f"✅ Similarity search working")
    
    for idx, similarity in similarities:
        print(f"   Text {idx+1}: similarity={similarity:.3f}")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_embeddings())