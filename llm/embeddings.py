# Embedding model (MiniLM)
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
from config.settings import settings
from utils.logger import log


class EmbeddingModel:
    """Sentence transformer for generating embeddings"""
    
    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL
        log.info(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        log.info(f"Embedding model loaded. Dimension: {self.dimension}")
    
    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Generate embeddings for text(s)
        
        Args:
            texts: Single text or list of texts
            
        Returns:
            numpy array of embeddings
        """
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False
        )
        
        return embeddings
    
    def encode_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Generate embeddings for large batches
        
        Args:
            texts: List of texts
            batch_size: Batch size for encoding
            
        Returns:
            numpy array of embeddings
        """
        return self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=len(texts) > 100
        )
    
    def get_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        emb1 = self.encode(text1)
        emb2 = self.encode(text2)
        
        # Cosine similarity
        similarity = np.dot(emb1[0], emb2[0]) / (
            np.linalg.norm(emb1[0]) * np.linalg.norm(emb2[0])
        )
        
        return float(similarity)


# Global instance
embedding_model = EmbeddingModel()