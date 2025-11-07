"""
Configuration management for the AI Parliament backend.
Loads environment variables and provides centralized configuration.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Groq API Configuration (previously OpenRouter)
    openrouter_api_key: str  # Variable name kept for compatibility
    openrouter_base_url: str = "https://api.groq.com/openai/v1"

    # LLM Models (Groq)
    model_gemini: str = "llama-3.3-70b-versatile"  # Variable name kept for compatibility (complex agents)
    model_llama: str = "llama-3.1-8b-instant"  # Fast model for simple agents

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # RAG Configuration
    chroma_persist_dir: str = "./chroma_db"
    embedding_model: str = "all-MiniLM-L6-v2"
    rag_top_k: int = 5

    # Debate Configuration
    default_rounds: int = 3  # Reduced to respect Groq rate limits
    max_tokens_per_argument: int = 180  # Short, concise arguments
    temperature_default: float = 0.7

    # Rate Limiting (Groq: 1K RPM for 70b, 14.4K RPM for 8b)
    api_call_delay: float = 2.5  # Seconds between API calls to stay under 1K RPM
    max_retries: int = 2

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()


# Constants
class AgentRole:
    """Agent role identifiers."""
    MODERADOR = "moderador"
    ECONOMISTA = "economista"
    SOCIOLOGO = "sociologo"
    CIENTIFICO = "cientifico"
    AMBIENTALISTA = "ambientalista"
    ETICO = "etico"
    PRAGMATICO = "pragmatico"
    CRITICO = "critico"
    SECRETARIO = "secretario"
    ANALISTA_RAG = "analista_rag"
    SINTETIZADOR = "sintetizador"


class DebateFase:
    """Debate phase identifiers."""
    INICIALIZACION = "inicializacion"
    RONDA_INICIAL = "ronda_inicial"
    DEBATE_LIBRE = "debate_libre"
    INTERPELACIONES = "interpelaciones"
    SINTESIS = "sintesis"
    COMPLETADO = "completado"


# Agent model assignments
AGENT_MODELS = {
    AgentRole.MODERADOR: settings.model_gemini,
    AgentRole.ECONOMISTA: settings.model_gemini,
    AgentRole.SOCIOLOGO: settings.model_llama,
    AgentRole.CIENTIFICO: settings.model_llama,
    AgentRole.AMBIENTALISTA: settings.model_llama,
    AgentRole.ETICO: settings.model_gemini,
    AgentRole.PRAGMATICO: settings.model_llama,
    AgentRole.CRITICO: settings.model_llama,
    AgentRole.SECRETARIO: settings.model_llama,
    AgentRole.ANALISTA_RAG: settings.model_gemini,
    AgentRole.SINTETIZADOR: settings.model_gemini,
}


# Agent temperature settings (creativity vs determinism)
AGENT_TEMPERATURES = {
    AgentRole.MODERADOR: 0.7,
    AgentRole.ECONOMISTA: 0.6,
    AgentRole.SOCIOLOGO: 0.7,
    AgentRole.CIENTIFICO: 0.5,
    AgentRole.AMBIENTALISTA: 0.6,
    AgentRole.ETICO: 0.8,
    AgentRole.PRAGMATICO: 0.6,
    AgentRole.CRITICO: 0.7,
    AgentRole.SECRETARIO: 0.3,
    AgentRole.ANALISTA_RAG: 0.4,
    AgentRole.SINTETIZADOR: 0.7,
}
