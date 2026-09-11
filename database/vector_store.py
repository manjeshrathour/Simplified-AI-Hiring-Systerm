# Vector database (FAISS)
import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Tuple
from config.settings import settings
from utils.logger import log


class VectorStore:
    """FAISS-based vector store for semantic search"""
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = None
        self.metadata = []
        self.index_path = settings.FAISS_INDEX_PATH
        self.metadata_path = f"{self.index_path}_metadata.pkl"
        
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize or load FAISS index"""
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            self.load_index()
        else:
            # Create new index with Inner Product (for cosine similarity)
            self.index = faiss.IndexFlatIP(self.dimension)
            log.info(f"Created new FAISS index with dimension {self.dimension}")
    
    def add_vectors(self, vectors: np.ndarray, metadata: List[Dict]):
        """Add vectors to the index
        
        Args:
            vectors: numpy array of shape (n, dimension)
            metadata: list of metadata dicts for each vector
        """
        if vectors.shape[1] != self.dimension:
            raise ValueError(f"Vector dimension {vectors.shape[1]} doesn't match index dimension {self.dimension}")
        
        # Normalize vectors for cosine similarity
        faiss.normalize_L2(vectors)
        
        # Add to index
        self.index.add(vectors)
        self.metadata.extend(metadata)
        
        log.info(f"Added {len(vectors)} vectors to index. Total: {self.index.ntotal}")
    
    def search(self, query_vector: np.ndarray, k: int = 5) -> List[Tuple[Dict, float]]:
        """Search for similar vectors
        
        Args:
            query_vector: query vector of shape (1, dimension)
            k: number of results to return
            
        Returns:
            List of (metadata, score) tuples
        """
        if self.index.ntotal == 0:
            log.warning("Vector store is empty")
            return []
        
        # Normalize query vector
        query_vector = query_vector.reshape(1, -1)
        faiss.normalize_L2(query_vector)
        
        # Search
        scores, indices = self.index.search(query_vector, min(k, self.index.ntotal))
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1 and idx < len(self.metadata):
                results.append((self.metadata[idx], float(score)))
        
        return results
    
    def save_index(self):
        """Save index and metadata to disk"""
        try:
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(self.index, self.index_path)
            
            # Save metadata
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)
            
            log.info(f"Saved index to {self.index_path}")
            
        except Exception as e:
            log.error(f"Failed to save index: {e}")
    
    def load_index(self):
        """Load index and metadata from disk"""
        try:
            # Load FAISS index
            self.index = faiss.read_index(self.index_path)
            
            # Load metadata
            with open(self.metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
            
            log.info(f"Loaded index from {self.index_path} with {self.index.ntotal} vectors")
            
        except Exception as e:
            log.error(f"Failed to load index: {e}")
            self.index = faiss.IndexFlatIP(self.dimension)
            self.metadata = []
    
    def clear(self):
        """Clear the index"""
        self.index.reset()
        self.metadata = []
        log.info("Cleared vector store")
    
    def get_stats(self) -> Dict:
        """Get index statistics"""
        return {
            "total_vectors": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "metadata_count": len(self.metadata)
        }


# Global instance
vector_store = VectorStore()