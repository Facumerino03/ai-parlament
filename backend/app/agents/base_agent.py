"""
Base Agent class that all specific agents inherit from.
Provides common functionality for generating arguments and managing state.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

from app.llm.client import LLMClient
from app.core.config import settings

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all debate agents."""

    def __init__(
        self,
        nombre: str,
        rol: str,
        perspectiva: str,
        system_prompt: str,
        modelo: str = None,
        temperature: float = None,
        max_tokens: int = None, 
        llm_client: LLMClient = None
    ):
        """
        Initialize a base agent.

        Args:
            nombre: Agent identifier (e.g., "economista", "moderador")
            rol: Short description of role (e.g., "Análisis Económico")
            perspectiva: Longer description of perspective
            system_prompt: System prompt defining agent personality and behavior
            modelo: LLM model to use (uses default if not provided)
            temperature: Sampling temperature (uses default if not provided)
            max_tokens: Max tokens per response (uses default if not provided)
            llm_client: LLM client instance (creates new if not provided)
        """
        self.nombre = nombre
        self.rol = rol
        self.perspectiva = perspectiva
        self.system_prompt = system_prompt
        self.modelo = modelo or settings.model_gemini
        self.temperature = temperature if temperature is not None else settings.temperature_default
        sensible_default_tokens = 180 
        self.max_tokens = max_tokens or sensible_default_tokens
        self.llm_client = llm_client or LLMClient()

        # Agent's own intervention history
        self.historial: List[Dict[str, Any]] = []

        logger.info(
            f"Initialized agent: {self.nombre} (role: {self.rol}, model: {self.modelo}, max_tokens: {self.max_tokens})"
        )

    def generar_argumento(
        self,
        tema: str,
        contexto_debate: List[Dict[str, Any]],
        contexto_rag: Optional[str] = None,
        instruccion_especifica: Optional[str] = None
    ) -> str:
        """
        Generate an argument for the debate.

        Args:
            tema: The debate topic
            contexto_debate: List of previous arguments from all agents
            contexto_rag: Optional additional context from RAG system
            instruccion_especifica: Optional specific instruction (e.g., "respond to X's point")

        Returns:
            Generated argument text
        """
        try:
            # Build user message
            user_message_parts = []

            # Add topic
            user_message_parts.append(f"TEMA DEL DEBATE:\n{tema}\n")

            # Add RAG context if available
            if contexto_rag:
                user_message_parts.append(f"\n{contexto_rag}\n")

            # Add debate history context (last N arguments)
            if contexto_debate:
                user_message_parts.append("\nINTERVENCIONES PREVIAS EN EL DEBATE:")
                # Include last 10 arguments to keep context manageable
                recent_args = contexto_debate[-10:]
                for arg in recent_args:
                    agente = arg.get('agente', 'Desconocido')
                    contenido = arg.get('contenido', '')
                    user_message_parts.append(f"\n[{agente}]: {contenido}")

            # Add own history (last 2 interventions)
            if self.historial:
                user_message_parts.append("\n\nTUS INTERVENCIONES PREVIAS:")
                for arg in self.historial[-2:]:
                    user_message_parts.append(f"- {arg.get('contenido_resumido', arg.get('contenido', ''))[:200]}...")

            # Add specific instruction if provided
            if instruccion_especifica:
                user_message_parts.append(f"\n\nINSTRUCCIÓN ESPECÍFICA:\n{instruccion_especifica}")
            else:
                user_message_parts.append(
                    "\n\nGenera tu argumento desde tu perspectiva única. "
                    "Aporta valor al debate sin repetir lo que otros ya dijeron."
                )

            # --- CAMBIO CLAVE ---
            # Se elimina el "CRÍTICO: 4 oraciones SÍ O SÍ"
            # Se reemplaza por un recordatorio que apunta al system_prompt
            
            user_message_parts.append(
                "\n\nRECORDATORIO IMPORTANTE:\n"
                "1. Revisa tu 'system_prompt'. Tus reglas de estilo y límite de palabras están ahí.\n"
                "2. CUMPLE ESE LÍMITE (ej. 'MÁX 110 palabras').\n"
                "3. ASEGÚRATE de terminar tu respuesta con una oración completa y un punto final. No dejes ideas a medias."
            )

            user_message = "\n".join(user_message_parts)

            # Prepare messages for LLM
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message}
            ]

            logger.debug(
                f"Agent {self.nombre} generating argument "
                f"(context: {len(contexto_debate)} args, RAG: {bool(contexto_rag)})"
            )

            # Generate response
            response = self.llm_client.generar_respuesta(
                model=self.modelo,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            # Store in history
            self._agregar_a_historial(response, tema, contexto_rag)

            logger.info(f"Agent {self.nombre} generated argument ({len(response)} chars)")

            # Limpieza simple para remover frases cortadas
            if not response.endswith(('.', '?', '!', '"', ']', '}')):
                last_punctuation = max(response.rfind('.'), response.rfind('?'), response.rfind('!'))
                if last_punctuation != -1:
                    response = response[:last_punctuation + 1]
                    logger.warning(f"Agent {self.nombre} response trimmed due to incomplete sentence.")
            
            return response

        except Exception as e:
            logger.error(f"Error generating argument for {self.nombre}: {e}")
            raise

    def puede_intervenir(self, contexto: Dict[str, Any]) -> bool:
        """
        Determine if the agent should intervene in the current context.

        Default implementation: agent can always intervene.
        Subclasses can override for more sophisticated logic.

        Args:
            contexto: Current debate context

        Returns:
            True if agent should intervene, False otherwise
        """
        # Basic implementation: intervene if not too many recent interventions
        if len(self.historial) >= 3:
            # Check if last intervention was very recent
            ultima_intervencion = self.historial[-1]
            tiempo_ultima = ultima_intervencion.get('timestamp')
            if tiempo_ultima:
                # Could add time-based logic here
                pass

        return True

    def formatear_argumento(
        self,
        texto: str,
        referencias_rag: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Format the generated argument into a structured dict.

        Args:
            texto: Raw argument text
            referencias_rag: Optional list of RAG document IDs referenced

        Returns:
            Formatted argument dict
        """
        return {
            "agente": self.nombre,
            "rol": self.rol,
            "contenido": texto,
            "timestamp": datetime.utcnow().isoformat(),
            "referencias_rag": referencias_rag or [],
            "metadata": {
                "modelo": self.modelo,
                "temperature": self.temperature,
                "longitud": len(texto),
                "max_tokens_limit": self.max_tokens
            }
        }

    def _agregar_a_historial(
        self,
        contenido: str,
        tema: str,
        contexto_rag: Optional[str] = None
    ):
        """
        Add intervention to agent's personal history.

        Args:
            contenido: Argument content
            tema: Debate topic
            contexto_rag: RAG context used (if any)
        """
        self.historial.append({
            "contenido": contenido,
            "contenido_resumido": contenido[:200] + "..." if len(contenido) > 200 else contenido,
            "tema": tema,
            "timestamp": datetime.utcnow().isoformat(),
            "uso_rag": bool(contexto_rag)
        })

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Get statistics about this agent's participation.

        Returns:
            Dict with participation statistics
        """
        if not self.historial:
            return {
                "nombre": self.nombre,
                "intervenciones": 0,
                "promedio_longitud": 0,
                "uso_rag": 0
            }

        total_intervenciones = len(self.historial)
        longitud_total = sum(len(h.get('contenido', '')) for h in self.historial)
        uso_rag_count = sum(1 for h in self.historial if h.get('uso_rag'))

        return {
            "nombre": self.nombre,
            "rol": self.rol,
            "intervenciones": total_intervenciones,
            "promedio_longitud": longitud_total // total_intervenciones if total_intervenciones > 0 else 0,
            "uso_rag": uso_rag_count,
            "modelo": self.modelo
        }

    def limpiar_historial(self):
        """Clear agent's intervention history."""
        self.historial = []
        logger.info(f"Cleared history for agent: {self.nombre}")

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}: nombre={self.nombre}, "
            f"rol={self.rol}, intervenciones={len(self.historial)}>"
        )
