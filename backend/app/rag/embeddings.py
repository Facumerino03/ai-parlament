"""
Embedding generation using Sentence-Transformers.
Handles text-to-vector conversion for semantic search.
"""

from sentence_transformers import SentenceTransformer
from typing import List, Union
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generates embeddings for text using Sentence-Transformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding generator.

        Args:
            model_name: Name of the Sentence-Transformers model to use
        """
        self.model_name = model_name
        self.model = None
        self._cache = {}
        logger.info(f"Initializing EmbeddingGenerator with model: {model_name}")

    def _load_model(self):
        """Lazy load the model on first use."""
        if self.model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully")

    def generar_embedding(self, texto: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            texto: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        # Check cache first
        if texto in self._cache:
            logger.debug(f"Cache hit for text: {texto[:50]}...")
            return self._cache[texto]

        self._load_model()

        try:
            embedding = self.model.encode(texto, convert_to_tensor=False)
            embedding_list = embedding.tolist()

            # Cache the result
            self._cache[texto] = embedding_list

            logger.debug(f"Generated embedding for text: {texto[:50]}...")
            return embedding_list

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def generar_embeddings_batch(self, textos: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts efficiently.

        Args:
            textos: List of texts to embed

        Returns:
            List of embedding vectors
        """
        self._load_model()

        # Separate cached and uncached texts
        cached_embeddings = {}
        uncached_texts = []
        uncached_indices = []

        for idx, texto in enumerate(textos):
            if texto in self._cache:
                cached_embeddings[idx] = self._cache[texto]
            else:
                uncached_texts.append(texto)
                uncached_indices.append(idx)

        # Generate embeddings for uncached texts
        if uncached_texts:
            try:
                logger.info(f"Generating embeddings for {len(uncached_texts)} texts")
                embeddings = self.model.encode(uncached_texts, convert_to_tensor=False)
                embeddings_list = [emb.tolist() for emb in embeddings]

                # Cache new embeddings
                for texto, embedding in zip(uncached_texts, embeddings_list):
                    self._cache[texto] = embedding

                # Combine cached and new embeddings in correct order
                result = [None] * len(textos)
                for idx, embedding in cached_embeddings.items():
                    result[idx] = embedding
                for idx, embedding in zip(uncached_indices, embeddings_list):
                    result[idx] = embedding

                return result

            except Exception as e:
                logger.error(f"Error generating batch embeddings: {e}")
                raise
        else:
            # All texts were cached
            return [cached_embeddings[idx] for idx in range(len(textos))]

    def clear_cache(self):
        """Clear the embedding cache."""
        self._cache.clear()
        logger.info("Embedding cache cleared")

    def get_cache_size(self) -> int:
        """Get the number of cached embeddings."""
        return len(self._cache)
