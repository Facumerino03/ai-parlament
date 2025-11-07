"""Analista RAG agent for retrieving information from knowledge base."""

from typing import Optional
from app.agents.base_agent import BaseAgent
from app.llm.prompts import ANALISTA_RAG_PROMPT
from app.core.config import AGENT_MODELS, AGENT_TEMPERATURES, AgentRole
from app.rag.retriever import RAGRetriever


class AnalistaRAG(BaseAgent):
    """RAG Analyst agent for information retrieval and summarization."""

    def __init__(self, llm_client=None, rag_retriever: Optional[RAGRetriever] = None):
        super().__init__(
            nombre=AgentRole.ANALISTA_RAG,
            rol="Análisis de Información",
            perspectiva="Búsqueda y síntesis de evidencia desde la base de conocimiento",
            system_prompt=ANALISTA_RAG_PROMPT,
            modelo=AGENT_MODELS[AgentRole.ANALISTA_RAG],
            temperature=AGENT_TEMPERATURES[AgentRole.ANALISTA_RAG],
            max_tokens=220, 
            llm_client=llm_client
        )
        self.rag_retriever = rag_retriever

    def buscar_informacion(self, query: str, categoria: Optional[str] = None) -> str:
        """
        Search for information in the knowledge base.

        Args:
            query: Search query
            categoria: Optional category filter

        Returns:
            Formatted information from RAG
        """
        if not self.rag_retriever:
            return "Sistema RAG no disponible."

        if categoria:
            resultados = self.rag_retriever.buscar_por_categoria(query, categoria)
        else:
            resultados = self.rag_retriever.recuperar_contexto(query)

        return self.rag_retriever.formatear_para_agente(resultados)
