"""
Main entry point for the AI Parliament backend.
Initializes FastAPI server, RAG system, and all components.
"""

import logging
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.llm.client import LLMClient
from app.rag.vector_store import VectorStore
from app.rag.retriever import RAGRetriever
from app.api import routes

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('backend.log')
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Parliament API",
    description="API REST para el sistema de debates multidisciplinarios del Parlamento Virtual de IA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
vector_store: VectorStore = None
rag_retriever: RAGRetriever = None
llm_client: LLMClient = None


@app.on_event("startup")
async def startup_event():
    """Initialize all components on server startup."""
    global vector_store, rag_retriever, llm_client

    logger.info("=" * 80)
    logger.info("AI PARLIAMENT BACKEND - STARTING UP")
    logger.info("=" * 80)

    try:
        # 1. Initialize LLM Client
        logger.info("Step 1/3: Initializing LLM Client...")
        llm_client = LLMClient()

        # Test connectivity (optional, can be slow)
        if settings.debug:
            logger.info("Testing LLM connectivity...")
            is_connected = llm_client.verificar_conectividad()
            if is_connected:
                logger.info("✓ LLM connectivity verified")
            else:
                logger.warning("⚠ LLM connectivity test failed (may still work)")
        else:
            logger.info("✓ LLM Client initialized (skipping connectivity test)")

        # 2. Initialize Vector Store and RAG
        logger.info("Step 2/3: Initializing RAG System...")
        vector_store = VectorStore()
        doc_count = vector_store.inicializar()

        # Load initial documents if vector store is empty
        if doc_count == 0:
            logger.info("Vector store is empty. Loading initial documents...")
            loaded = vector_store.cargar_documentos_iniciales()
            logger.info(f"✓ Loaded {loaded} documents into vector store")
        else:
            logger.info(f"✓ Vector store initialized with {doc_count} existing documents")

        # Create RAG retriever
        rag_retriever = RAGRetriever(vector_store)
        logger.info("✓ RAG system initialized successfully")

        # 3. Initialize API routes with dependencies
        logger.info("Step 3/3: Initializing API routes...")
        routes.inicializar_dependencias(llm_client, rag_retriever)
        logger.info("✓ API routes initialized")

        # Success!
        logger.info("=" * 80)
        logger.info("✓ SERVER INITIALIZATION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"RAG: {doc_count or loaded} documents loaded")
        logger.info(f"Models: {settings.model_gemini}, {settings.model_llama}")
        logger.info(f"Server: http://{settings.host}:{settings.port}")
        logger.info(f"Docs: http://{settings.host}:{settings.port}/docs")
        logger.info("=" * 80)

    except Exception as e:
        logger.error("=" * 80)
        logger.error("❌ STARTUP FAILED")
        logger.error("=" * 80)
        logger.error(f"Error during startup: {e}", exc_info=True)
        logger.error("=" * 80)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on server shutdown."""
    logger.info("=" * 80)
    logger.info("AI PARLIAMENT BACKEND - SHUTTING DOWN")
    logger.info("=" * 80)

    # Cleanup logic here if needed
    logger.info("✓ Shutdown complete")


# Include API routes
app.include_router(routes.router, prefix="/api/v1", tags=["debates"])


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with basic information."""
    return {
        "mensaje": "AI Parliament Backend API",
        "version": "1.0.0",
        "documentacion": "/docs",
        "health": "/api/v1/health"
    }


def main():
    """Main entry point for running the server."""
    logger.info(f"Starting server on {settings.host}:{settings.port}")

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )


if __name__ == "__main__":
    main()
