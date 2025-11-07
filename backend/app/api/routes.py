"""
API routes for the AI Parliament backend.
Implements REST endpoints and Server-Sent Events streaming.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from typing import Dict, Any
from datetime import datetime
import asyncio
import json
import logging

from app.api.models import (
    IniciarDebateRequest,
    IniciarDebateResponse,
    EstadoDebateResponse,
    ResultadoDebateResponse,
    EjecutarDebateResponse,
    HealthResponse,
    ErrorResponse
)
from app.core.orquestador import OrquestadorDebate
from app.core.config import DebateFase, settings
from app.llm.client import LLMClient
from app.rag.vector_store import VectorStore
from app.rag.retriever import RAGRetriever

logger = logging.getLogger(__name__)

router = APIRouter()

debates_activos: Dict[str, Dict[str, Any]] = {}

llm_client: LLMClient = None
rag_retriever: RAGRetriever = None

def inicializar_dependencias(client: LLMClient, retriever: RAGRetriever):
    """Initialize global dependencies."""
    global llm_client, rag_retriever
    llm_client = client
    rag_retriever = retriever
    logger.info("API dependencies initialized")


@router.post(
    "/debate/iniciar",
    response_model=IniciarDebateResponse,
    summary="Iniciar un nuevo debate",
    description="Crea un nuevo debate con el tema especificado y configuración opcional."
)
async def iniciar_debate(request: IniciarDebateRequest):
    """Initiate a new debate."""
    try:
        logger.info(f"Initiating debate with topic: {request.tema[:50]}...")

        # Create orchestrator
        orquestador = OrquestadorDebate(llm_client, rag_retriever)

        # Prepare config
        config = None
        if request.config:
            config = request.config.model_dump()

        # Initialize debate
        debate_id = orquestador.iniciar_debate(request.tema, config)

        # Store in active debates
        debates_activos[debate_id] = {
            "orquestador": orquestador,
            "status": "iniciado",
            "en_ejecucion": False
        }

        return IniciarDebateResponse(
            debate_id=debate_id,
            status="iniciado",
            tema=request.tema,
            timestamp=orquestador.estado.timestamp_inicio
        )

    except Exception as e:
        logger.error(f"Error initiating debate: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/debate/{debate_id}/ejecutar",
    response_model=EjecutarDebateResponse,
    summary="Ejecutar debate",
    description="Inicia la ejecución del debate. Use /stream para seguimiento en tiempo real."
)
async def ejecutar_debate(debate_id: str, background_tasks: BackgroundTasks):
    """Execute a debate in the background."""
    if debate_id not in debates_activos:
        raise HTTPException(status_code=404, detail="Debate no encontrado")

    debate_info = debates_activos[debate_id]

    if debate_info["en_ejecucion"]:
        raise HTTPException(status_code=400, detail="Debate ya en ejecución")

    # Mark as running
    debate_info["en_ejecucion"] = True
    debate_info["status"] = "ejecutando"

    # Start execution in background
    background_tasks.add_task(ejecutar_debate_background, debate_id)

    return EjecutarDebateResponse(
        status="ejecutando",
        mensaje=f"Debate iniciado. Use /debate/{debate_id}/stream para seguimiento en tiempo real",
        debate_id=debate_id
    )


async def ejecutar_debate_background(debate_id: str):
    """Execute debate in background."""
    try:
        debate_info = debates_activos[debate_id]
        orquestador = debate_info["orquestador"]

        logger.info(f"Starting background execution for debate: {debate_id}")

        argumento_count = 0
        for argumento in orquestador.ejecutar_debate_completo():
            argumento_count += 1
            logger.debug(f"Generated argument #{argumento_count} from {argumento.get('agente', 'unknown')}")

            await asyncio.sleep(0.1)

        debate_info["status"] = "completado"
        logger.info(f"Debate {debate_id} completed successfully with {argumento_count} arguments")

    except Exception as e:
        logger.error(f"Error in background debate execution: {e}", exc_info=True)
        debate_info["status"] = "error"
        debate_info["error"] = str(e)


@router.get(
    "/debate/{debate_id}/stream",
    summary="Stream del debate en tiempo real",
    description="Conexión Server-Sent Events para recibir argumentos en tiempo real."
)
async def stream_debate(debate_id: str):
    """Stream debate arguments in real-time using Server-Sent Events."""
    if debate_id not in debates_activos:
        raise HTTPException(status_code=404, detail="Debate no encontrado")

    async def event_generator():
        """Generate SSE events for the debate."""
        debate_info = debates_activos[debate_id]
        orquestador = debate_info["orquestador"]
        estado = orquestador.estado

        last_sent_index = 0
        ping_counter = 0

        logger.info(f"SSE stream started for debate: {debate_id}")

        try:
            # Send initial connection event
            yield {
                "event": "connected",
                "data": json.dumps({
                    "debate_id": debate_id,
                    "mensaje": "Conexión establecida"
                })
            }

            wait_count = 0
            while not debate_info.get("en_ejecucion") and debate_info.get("status") != "completado":
                await asyncio.sleep(0.5)
                wait_count += 1
                if wait_count % 2 == 0:
                    logger.debug(f"Waiting for execution to start (debate: {debate_id})")
                    yield {
                        "event": "waiting",
                        "data": json.dumps({"mensaje": "Esperando inicio de ejecución..."})
                    }

            logger.info(f"Debate execution started, beginning stream (debate: {debate_id})")

            while True:
                if estado.fase_actual == DebateFase.COMPLETADO:
                    logger.info(f"Debate completed, sending final arguments (debate: {debate_id})")

                    for i in range(last_sent_index, len(estado.argumentos)):
                        arg = estado.argumentos[i]
                        logger.debug(f"Sending final argument {i+1}/{len(estado.argumentos)} from {arg.get('agente')}")
                        yield {
                            "event": "argumento",
                            "data": json.dumps(arg)
                        }

                    yield {
                        "event": "completado",
                        "data": json.dumps({
                            "debate_id": debate_id,
                            "status": "completado",
                            "total_argumentos": len(estado.argumentos)
                        })
                    }
                    logger.info(f"Stream completed successfully (debate: {debate_id})")
                    break

                current_count = len(estado.argumentos)
                if current_count > last_sent_index:
                    logger.info(f"Sending {current_count - last_sent_index} new arguments (debate: {debate_id})")
                    for i in range(last_sent_index, current_count):
                        arg = estado.argumentos[i]
                        logger.debug(f"Sending argument {i+1}: {arg.get('agente')} - {arg.get('contenido')[:50]}...")
                        yield {
                            "event": "argumento",
                            "data": json.dumps(arg)
                        }
                    last_sent_index = current_count

                if debate_info.get("status") == "error":
                    logger.error(f"Debate error detected in stream (debate: {debate_id})")
                    yield {
                        "event": "error",
                        "data": json.dumps({
                            "error": "ejecucion_fallida",
                            "mensaje": debate_info.get("error", "Error desconocido")
                        })
                    }
                    break

                ping_counter += 1
                if ping_counter % 10 == 0:
                    yield {
                        "event": "ping",
                        "data": json.dumps({
                            "timestamp": datetime.utcnow().isoformat(),
                            "argumentos_enviados": last_sent_index
                        })
                    }

                await asyncio.sleep(1)

        except asyncio.CancelledError:
            logger.info(f"Stream cancelled for debate: {debate_id}")
        except Exception as e:
            logger.error(f"Error in event generator for debate {debate_id}: {e}", exc_info=True)
            yield {
                "event": "error",
                "data": json.dumps({
                    "error": "stream_error",
                    "mensaje": str(e)
                })
            }

    return EventSourceResponse(event_generator())


@router.get(
    "/debate/{debate_id}/estado",
    response_model=EstadoDebateResponse,
    summary="Obtener estado actual del debate",
    description="Devuelve el estado actual del debate sin los argumentos completos."
)
async def obtener_estado_debate(debate_id: str):
    """Get current state of a debate."""
    if debate_id not in debates_activos:
        raise HTTPException(status_code=404, detail="Debate no encontrado")

    debate_info = debates_activos[debate_id]
    orquestador = debate_info["orquestador"]
    estado = orquestador.estado

    status = "en_progreso"
    if estado.fase_actual == DebateFase.COMPLETADO:
        status = "completado"
    elif debate_info.get("status") == "error":
        status = "error"

    return EstadoDebateResponse(
        debate_id=debate_id,
        tema=estado.tema,
        fase_actual=estado.fase_actual,
        ronda_actual=estado.ronda_actual,
        total_argumentos=len(estado.argumentos),
        timestamp_inicio=estado.timestamp_inicio.isoformat(),
        status=status
    )


@router.get(
    "/debate/{debate_id}/resultado",
    response_model=ResultadoDebateResponse,
    summary="Obtener resultado final del debate",
    description="Devuelve el resultado completo del debate. Solo disponible cuando está completado."
)
async def obtener_resultado_debate(debate_id: str):
    """Get final result of a completed debate."""
    if debate_id not in debates_activos:
        raise HTTPException(status_code=404, detail="Debate no encontrado")

    debate_info = debates_activos[debate_id]
    orquestador = debate_info["orquestador"]
    estado = orquestador.estado

    if estado.fase_actual != DebateFase.COMPLETADO:
        raise HTTPException(
            status_code=425,  # Too Early
            detail="El debate aún no ha sido completado"
        )

    try:
        resultado = orquestador.obtener_resultado_final()
        return ResultadoDebateResponse(**resultado)

    except Exception as e:
        logger.error(f"Error obtaining debate result: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Verifica el estado del sistema."
)
async def health_check():
    """Health check endpoint."""
    try:
        rag_initialized = rag_retriever is not None
        if rag_initialized:
            pass

        return HealthResponse(
            status="ok",
            rag_initialized=rag_initialized,
            modelos_disponibles=[
                settings.model_gemini,
                settings.model_llama
            ],
            version="1.0.0"
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="degraded",
            rag_initialized=False,
            modelos_disponibles=[],
            version="1.0.0"
        )


@router.delete(
    "/debate/{debate_id}",
    summary="Eliminar debate",
    description="Elimina un debate de la memoria (limpieza)."
)
async def eliminar_debate(debate_id: str):
    """Delete a debate from memory."""
    if debate_id not in debates_activos:
        raise HTTPException(status_code=404, detail="Debate no encontrado")

    del debates_activos[debate_id]
    logger.info(f"Debate deleted: {debate_id}")

    return {"mensaje": "Debate eliminado exitosamente", "debate_id": debate_id}


@router.get(
    "/debates",
    summary="Listar debates activos",
    description="Lista todos los debates actualmente en memoria."
)
async def listar_debates():
    """List all active debates."""
    debates_lista = []

    for debate_id, debate_info in debates_activos.items():
        orquestador = debate_info["orquestador"]
        estado = orquestador.estado

        debates_lista.append({
            "debate_id": debate_id,
            "tema": estado.tema[:100],
            "fase_actual": estado.fase_actual,
            "status": debate_info.get("status", "desconocido"),
            "total_argumentos": len(estado.argumentos),
            "timestamp_inicio": estado.timestamp_inicio.isoformat()
        })

    return {
        "total": len(debates_lista),
        "debates": debates_lista
    }
