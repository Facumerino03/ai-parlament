"""
Pydantic models for API requests and responses.
Provides validation and serialization for the REST API.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


# Request Models

class ConfigDebate(BaseModel):
    """Configuration for a debate."""
    num_rondas: int = Field(default=5, ge=1, le=10, description="Number of debate rounds")
    perspectivas: Optional[List[str]] = Field(
        default=None,
        description="List of agent perspectives to include (None = all)"
    )
    profundidad_rag: int = Field(default=5, ge=1, le=10, description="RAG search depth (top-K)")


class IniciarDebateRequest(BaseModel):
    """Request to initiate a new debate."""
    tema: str = Field(..., min_length=10, max_length=500, description="The debate topic")
    config: Optional[ConfigDebate] = Field(default=None, description="Optional debate configuration")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "tema": "¿Debería implementarse una semana laboral de 4 días?",
                    "config": {
                        "num_rondas": 5,
                        "perspectivas": ["economista", "sociologo", "etico"],
                        "profundidad_rag": 5
                    }
                }
            ]
        }
    }


# Response Models

class IniciarDebateResponse(BaseModel):
    """Response after initiating a debate."""
    debate_id: str = Field(..., description="Unique debate identifier")
    status: str = Field(..., description="Status of the debate")
    tema: str = Field(..., description="The debate topic")
    timestamp: datetime = Field(..., description="Timestamp of debate initiation")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "debate_id": "123e4567-e89b-12d3-a456-426614174000",
                    "status": "iniciado",
                    "tema": "¿Debería implementarse una semana laboral de 4 días?",
                    "timestamp": "2024-11-06T10:30:00Z"
                }
            ]
        }
    }


class ArgumentoResponse(BaseModel):
    """Response model for a single argument."""
    id: int = Field(..., description="Argument ID within the debate")
    agente: str = Field(..., description="Agent identifier")
    rol: str = Field(..., description="Agent role description")
    contenido: str = Field(..., description="Argument content")
    fase: str = Field(..., description="Debate phase")
    ronda: int = Field(..., description="Round number (0 for initial phase)")
    timestamp: str = Field(..., description="ISO timestamp")
    referencias_rag: List[str] = Field(default=[], description="RAG document references")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")


class EstadoDebateResponse(BaseModel):
    """Response with current debate state."""
    debate_id: str = Field(..., description="Debate identifier")
    tema: str = Field(..., description="Debate topic")
    fase_actual: str = Field(..., description="Current debate phase")
    ronda_actual: int = Field(..., description="Current round number")
    total_argumentos: int = Field(..., description="Total number of arguments so far")
    timestamp_inicio: str = Field(..., description="Debate start timestamp")
    status: str = Field(..., description="Debate status (en_progreso, completado)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "debate_id": "123e4567-e89b-12d3-a456-426614174000",
                    "tema": "¿Semana laboral de 4 días?",
                    "fase_actual": "debate_libre",
                    "ronda_actual": 3,
                    "total_argumentos": 15,
                    "timestamp_inicio": "2024-11-06T10:30:00Z",
                    "status": "en_progreso"
                }
            ]
        }
    }


class ResultadoDebateResponse(BaseModel):
    """Complete debate result response."""
    debate_id: str = Field(..., description="Debate identifier")
    tema: str = Field(..., description="Debate topic")
    tema_reformulado: Optional[str] = Field(None, description="Reformulated topic by moderator")
    acta_completa: str = Field(..., description="Complete formatted transcript")
    consensos: List[str] = Field(default=[], description="Identified consensuses")
    disensos: List[str] = Field(default=[], description="Identified dissents")
    propuestas_hibridas: List[str] = Field(default=[], description="Hybrid proposals")
    resumen_ejecutivo: str = Field(..., description="Executive summary")
    argumentos: List[ArgumentoResponse] = Field(..., description="All arguments")
    timestamp_inicio: str = Field(..., description="Debate start timestamp")
    timestamp_fin: Optional[str] = Field(None, description="Debate end timestamp")
    duracion_segundos: Optional[float] = Field(None, description="Duration in seconds")
    estadisticas: Dict[str, Any] = Field(default={}, description="Debate statistics")


class EjecutarDebateResponse(BaseModel):
    """Response when starting debate execution."""
    status: str = Field(..., description="Execution status")
    mensaje: str = Field(..., description="Status message")
    debate_id: str = Field(..., description="Debate identifier")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "ejecutando",
                    "mensaje": "Debate iniciado. Use /debate/{debate_id}/stream para seguimiento en tiempo real",
                    "debate_id": "123e4567-e89b-12d3-a456-426614174000"
                }
            ]
        }
    }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="System status")
    rag_initialized: bool = Field(..., description="RAG system initialization status")
    modelos_disponibles: List[str] = Field(..., description="Available LLM models")
    version: str = Field(default="1.0.0", description="API version")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "ok",
                    "rag_initialized": True,
                    "modelos_disponibles": ["google/gemini-flash-1.5", "meta-llama/llama-3.1-8b-instruct"],
                    "version": "1.0.0"
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error type")
    mensaje: str = Field(..., description="Error message")
    detalles: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "error": "debate_no_encontrado",
                    "mensaje": "El debate con el ID especificado no fue encontrado",
                    "detalles": {"debate_id": "invalid-id"}
                }
            ]
        }
    }


# SSE Event Models (for documentation)

class SSEArgumentoEvent(BaseModel):
    """Server-Sent Event for argument."""
    event: str = Field(default="argumento", description="Event type")
    data: ArgumentoResponse = Field(..., description="Argument data")


class SSEFaseCambioEvent(BaseModel):
    """Server-Sent Event for phase change."""
    event: str = Field(default="fase_cambio", description="Event type")
    data: Dict[str, Any] = Field(..., description="Phase change data")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "event": "fase_cambio",
                    "data": {"fase": "debate_libre", "ronda": 1}
                }
            ]
        }
    }


class SSECompletadoEvent(BaseModel):
    """Server-Sent Event for debate completion."""
    event: str = Field(default="completado", description="Event type")
    data: Dict[str, str] = Field(..., description="Completion data")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "event": "completado",
                    "data": {
                        "debate_id": "123e4567-e89b-12d3-a456-426614174000",
                        "status": "completado"
                    }
                }
            ]
        }
    }
