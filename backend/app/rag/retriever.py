"""
RAG Retriever for semantic search and context retrieval.
Orchestrates document search and formatting for agent consumption.
"""

from typing import List, Dict, Optional, Any
import logging

from app.rag.vector_store import VectorStore
from app.core.config import settings

logger = logging.getLogger(__name__)


class RAGRetriever:
    """Retrieves and formats relevant context from the knowledge base."""

    def __init__(self, vector_store: VectorStore):
        """
        Initialize the RAG retriever.

        Args:
            vector_store: Initialized VectorStore instance
        """
        self.vector_store = vector_store
        logger.info("RAGRetriever initialized")

    def recuperar_contexto(
        self,
        query: str,
        top_k: int = None,
        filtros: Optional[Dict[str, Any]] = None,
        score_threshold: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context for a query.

        Args:
            query: Search query
            top_k: Number of results to return (uses config default if None)
            filtros: Optional metadata filters (e.g., {"categoria": "estudios"})
            score_threshold: Minimum similarity score (0-1)

        Returns:
            List of relevant documents with metadata
        """
        if top_k is None:
            top_k = settings.rag_top_k

        try:
            # Search in vector store
            results = self.vector_store.buscar(
                query=query,
                top_k=top_k,
                filtros=filtros
            )

            # Filter by score threshold
            filtered_results = [
                result for result in results
                if result.get('score', 0) >= score_threshold
            ]

            logger.info(
                f"Retrieved {len(filtered_results)} documents "
                f"(from {len(results)} results, threshold: {score_threshold})"
            )

            return filtered_results

        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []

    def formatear_para_agente(
        self,
        documentos: List[Dict[str, Any]],
        max_chars: int = 2000
    ) -> str:
        """
        Format retrieved documents for agent consumption.

        Args:
            documentos: List of document dicts from recuperar_contexto
            max_chars: Maximum total characters to include

        Returns:
            Formatted string with relevant information
        """
        if not documentos:
            return "No se encontró información relevante en la base de conocimiento."

        formatted_parts = ["INFORMACIÓN RELEVANTE DE LA BASE DE CONOCIMIENTO:\n"]
        current_length = len(formatted_parts[0])

        for idx, doc in enumerate(documentos, 1):
            # Extract document info
            texto = doc.get('texto', '')
            metadata = doc.get('metadata', {})
            score = doc.get('score', 0)
            fuente = metadata.get('fuente', 'Desconocida')
            categoria = metadata.get('categoria', 'general')

            # Truncate text if needed
            max_text_length = (max_chars - current_length - 200) // (len(documentos) - idx + 1)
            if len(texto) > max_text_length:
                texto = texto[:max_text_length] + "..."

            # Format document entry
            doc_entry = (
                f"\n[{idx}] Fuente: {fuente} (Categoría: {categoria}, Relevancia: {score:.2f})\n"
                f"{texto}\n"
                f"---\n"
            )

            # Check if adding this would exceed max_chars
            if current_length + len(doc_entry) > max_chars:
                formatted_parts.append(
                    f"\n[...{len(documentos) - idx + 1} documentos adicionales omitidos por límite de longitud...]"
                )
                break

            formatted_parts.append(doc_entry)
            current_length += len(doc_entry)

        result = "".join(formatted_parts)
        logger.debug(f"Formatted {len(documentos)} documents into {len(result)} characters")
        return result

    def buscar_por_categoria(
        self,
        query: str,
        categoria: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Search within a specific category.

        Args:
            query: Search query
            categoria: Category to filter by (estudios, estadisticas, etc.)
            top_k: Number of results

        Returns:
            List of matching documents
        """
        return self.recuperar_contexto(
            query=query,
            top_k=top_k,
            filtros={"categoria": categoria}
        )

    def buscar_evidencia_cientifica(self, query: str) -> str:
        """
        Search for scientific evidence (studies and statistics).

        Args:
            query: Search query

        Returns:
            Formatted string with scientific evidence
        """
        # Search in estudios and estadisticas
        estudios = self.buscar_por_categoria(query, "estudios", top_k=2)
        estadisticas = self.buscar_por_categoria(query, "estadisticas", top_k=2)

        combined = estudios + estadisticas
        return self.formatear_para_agente(combined, max_chars=1500)

    def buscar_casos_historicos(self, query: str) -> str:
        """
        Search for historical cases and precedents.

        Args:
            query: Search query

        Returns:
            Formatted string with historical cases
        """
        casos = self.buscar_por_categoria(query, "casos_historicos", top_k=3)
        return self.formatear_para_agente(casos, max_chars=1500)

    def buscar_falacias(self, query: str) -> str:
        """
        Search for relevant logical fallacies.

        Args:
            query: Search query (e.g., type of argument to check)

        Returns:
            Formatted string with fallacy information
        """
        falacias = self.buscar_por_categoria(query, "falacias", top_k=3)
        return self.formatear_para_agente(falacias, max_chars=1000)

    def obtener_contexto_inicial(self, tema: str) -> str:
        """
        Get initial context for a debate topic.
        Searches across all categories to provide broad context.

        Args:
            tema: The debate topic

        Returns:
            Formatted string with initial context
        """
        # Search broadly across all categories
        contexto = self.recuperar_contexto(
            query=tema,
            top_k=settings.rag_top_k,
            score_threshold=0.4  # Higher threshold for initial context
        )

        if not contexto:
            return (
                "No se encontró contexto específico en la base de conocimiento "
                "para este tema. El debate procederá basándose en el conocimiento "
                "general de los agentes."
            )

        return self.formatear_para_agente(contexto, max_chars=2500)
