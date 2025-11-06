"""
Vector store management using ChromaDB.
Handles document storage and semantic search.
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Optional, Any
import logging
import os
from pathlib import Path

from app.rag.embeddings import EmbeddingGenerator
from app.core.config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    """Manages ChromaDB vector store for semantic search."""

    def __init__(self, persist_dir: str = None, embedding_model: str = None):
        """
        Initialize the vector store.

        Args:
            persist_dir: Directory to persist ChromaDB data
            embedding_model: Name of the embedding model to use
        """
        self.persist_dir = persist_dir or settings.chroma_persist_dir
        self.embedding_model = embedding_model or settings.embedding_model
        self.embedding_generator = EmbeddingGenerator(self.embedding_model)
        self.client = None
        self.collection = None
        self.collection_name = "ai_parliament_knowledge"

        logger.info(f"Initializing VectorStore with persist_dir: {self.persist_dir}")

    def inicializar(self):
        """Initialize or load ChromaDB collection."""
        try:
            # Create persist directory if it doesn't exist
            os.makedirs(self.persist_dir, exist_ok=True)

            # Initialize ChromaDB client with persistence
            self.client = chromadb.PersistentClient(path=self.persist_dir)

            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )

            doc_count = self.collection.count()
            logger.info(f"VectorStore initialized with {doc_count} documents")

            return doc_count

        except Exception as e:
            logger.error(f"Error initializing VectorStore: {e}")
            raise

    def agregar_documentos(
        self,
        documentos: List[str],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> int:
        """
        Add documents to the vector store.

        Args:
            documentos: List of document texts
            metadatas: List of metadata dicts for each document
            ids: Optional list of document IDs (will auto-generate if not provided)

        Returns:
            Number of documents added
        """
        if not self.collection:
            raise RuntimeError("VectorStore not initialized. Call inicializar() first.")

        if len(documentos) != len(metadatas):
            raise ValueError("Number of documents and metadatas must match")

        try:
            # Generate IDs if not provided
            if ids is None:
                existing_count = self.collection.count()
                ids = [f"doc_{existing_count + i}" for i in range(len(documentos))]

            # Generate embeddings
            logger.info(f"Generating embeddings for {len(documentos)} documents")
            embeddings = self.embedding_generator.generar_embeddings_batch(documentos)

            # Add to collection
            self.collection.add(
                documents=documentos,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )

            logger.info(f"Added {len(documentos)} documents to VectorStore")
            return len(documentos)

        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise

    def buscar(
        self,
        query: str,
        top_k: int = 5,
        filtros: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for documents similar to the query.

        Args:
            query: Search query text
            top_k: Number of results to return
            filtros: Optional metadata filters

        Returns:
            List of matching documents with metadata and scores
        """
        if not self.collection:
            raise RuntimeError("VectorStore not initialized. Call inicializar() first.")

        try:
            # Generate query embedding
            query_embedding = self.embedding_generator.generar_embedding(query)

            # Search in collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filtros if filtros else None,
                include=["documents", "metadatas", "distances"]
            )

            # Format results
            formatted_results = []
            if results and results['documents'] and len(results['documents']) > 0:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'id': results['ids'][0][i],
                        'texto': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'score': 1 - results['distances'][0][i]  # Convert distance to similarity score
                    })

            logger.info(f"Found {len(formatted_results)} results for query: {query[:50]}...")
            return formatted_results

        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise

    def cargar_documentos_iniciales(self, data_dir: str = None):
        """
        Load initial documents from the data directory.

        Args:
            data_dir: Path to the data directory containing documents
        """
        if data_dir is None:
            # Default to app/rag/data
            data_dir = Path(__file__).parent / "data"

        if not os.path.exists(data_dir):
            logger.warning(f"Data directory not found: {data_dir}")
            return 0

        total_loaded = 0
        categories = ["estudios", "estadisticas", "casos_historicos", "falacias"]

        for categoria in categories:
            categoria_path = Path(data_dir) / categoria

            if not categoria_path.exists():
                logger.warning(f"Category directory not found: {categoria_path}")
                continue

            # Load all .txt and .md files from the category
            for file_path in categoria_path.glob("*.txt"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        contenido = f.read()

                    if contenido.strip():
                        metadata = {
                            "categoria": categoria,
                            "fuente": file_path.stem,
                            "ruta": str(file_path)
                        }

                        self.agregar_documentos(
                            documentos=[contenido],
                            metadatas=[metadata],
                            ids=[f"{categoria}_{file_path.stem}"]
                        )
                        total_loaded += 1
                        logger.info(f"Loaded document: {file_path.name}")

                except Exception as e:
                    logger.error(f"Error loading file {file_path}: {e}")

            # Also load .md files
            for file_path in categoria_path.glob("*.md"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        contenido = f.read()

                    if contenido.strip():
                        metadata = {
                            "categoria": categoria,
                            "fuente": file_path.stem,
                            "ruta": str(file_path)
                        }

                        self.agregar_documentos(
                            documentos=[contenido],
                            metadatas=[metadata],
                            ids=[f"{categoria}_{file_path.stem}"]
                        )
                        total_loaded += 1
                        logger.info(f"Loaded document: {file_path.name}")

                except Exception as e:
                    logger.error(f"Error loading file {file_path}: {e}")

        logger.info(f"Total documents loaded: {total_loaded}")
        return total_loaded

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        if not self.collection:
            return {"error": "VectorStore not initialized"}

        try:
            count = self.collection.count()
            return {
                "total_documentos": count,
                "collection_name": self.collection_name,
                "persist_dir": self.persist_dir,
                "embedding_model": self.embedding_model
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {"error": str(e)}

    def limpiar_coleccion(self):
        """Clear all documents from the collection (use with caution)."""
        if not self.client:
            raise RuntimeError("VectorStore not initialized")

        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("Collection cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise
