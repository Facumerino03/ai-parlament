"""
Debate Orchestrator - The central coordinator of the AI Parliament.
Manages all phases of the debate and coordinates agent interactions.
"""

from typing import Dict, List, Optional, Generator, Any
import logging
import random

from app.core.debate_state import DebateState
from app.core.config import DebateFase, AgentRole, settings
from app.llm.client import LLMClient
from app.rag.retriever import RAGRetriever

# Import all agents
from app.agents.moderador import Moderador
from app.agents.economista import Economista
from app.agents.sociologo import Sociologo
from app.agents.cientifico import Cientifico
from app.agents.ambientalista import Ambientalista
from app.agents.etico import Etico
from app.agents.pragmatico import Pragmatico
from app.agents.critico import Critico
from app.agents.secretario import Secretario
from app.agents.analista_rag import AnalistaRAG
from app.agents.sintetizador import Sintetizador

logger = logging.getLogger(__name__)


class OrquestadorDebate:
    """Orchestrates the entire debate process."""

    def __init__(
        self,
        llm_client: LLMClient,
        rag_retriever: RAGRetriever
    ):
        """
        Initialize the debate orchestrator.

        Args:
            llm_client: LLM client for making API calls
            rag_retriever: RAG retriever for knowledge base access
        """
        self.llm_client = llm_client
        self.rag_retriever = rag_retriever

        # Initialize all agents
        self.agentes: Dict[str, Any] = {
            AgentRole.MODERADOR: Moderador(llm_client),
            AgentRole.ECONOMISTA: Economista(llm_client),
            AgentRole.SOCIOLOGO: Sociologo(llm_client),
            AgentRole.CIENTIFICO: Cientifico(llm_client),
            AgentRole.AMBIENTALISTA: Ambientalista(llm_client),
            AgentRole.ETICO: Etico(llm_client),
            AgentRole.PRAGMATICO: Pragmatico(llm_client),
            AgentRole.CRITICO: Critico(llm_client),
            AgentRole.SECRETARIO: Secretario(llm_client),
            AgentRole.ANALISTA_RAG: AnalistaRAG(llm_client, rag_retriever),
            AgentRole.SINTETIZADOR: Sintetizador(llm_client)
        }

        # Perspective agents (those who actively debate)
        self.agentes_perspectiva = [
            AgentRole.ECONOMISTA,
            AgentRole.SOCIOLOGO,
            AgentRole.CIENTIFICO,
            AgentRole.AMBIENTALISTA,
            AgentRole.ETICO,
            AgentRole.PRAGMATICO,
            AgentRole.CRITICO
        ]

        self.estado: Optional[DebateState] = None

        logger.info("OrquestadorDebate initialized with all agents")

    def iniciar_debate(
        self,
        tema: str,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Initialize a new debate.

        Args:
            tema: The debate topic
            config: Optional configuration parameters

        Returns:
            Debate ID
        """
        if config is None:
            config = {
                "num_rondas": settings.default_rounds,
                "perspectivas": self.agentes_perspectiva
            }

        # Create debate state
        self.estado = DebateState(tema, config)

        logger.info(
            f"Debate initiated: id={self.estado.debate_id}, tema={tema[:50]}..."
        )

        return self.estado.debate_id

    def ejecutar_ronda_inicial(self) -> Generator[Dict[str, Any], None, None]:
        """
        Execute the initial round where each agent presents their position.

        Yields:
            Argument dicts as they are generated
        """
        if not self.estado:
            raise RuntimeError("Debate not initialized. Call iniciar_debate() first.")

        self.estado.cambiar_fase(DebateFase.RONDA_INICIAL)

        logger.info("Starting initial round")

        moderador = self.agentes[AgentRole.MODERADOR]

        contexto_rag_inicial = self.rag_retriever.obtener_contexto_inicial(
            self.estado.tema
        )

        intro = moderador.generar_argumento(
            tema=self.estado.tema,
            contexto_debate=[],
            contexto_rag=contexto_rag_inicial,
            instruccion_especifica="Presenta el tema del debate de forma clara y estructurada. "
                                   "Identifica las principales perspectivas que deben considerarse."
        )

        arg = self.estado.agregar_argumento(
            agente=AgentRole.MODERADOR,
            rol=moderador.rol,
            contenido=intro
        )

        self.estado.tema_reformulado = self.estado.tema
        yield arg

        agentes_activos = self.estado.config.get("perspectivas", self.agentes_perspectiva)

        for agente_nombre in agentes_activos:
            agente = self.agentes[agente_nombre]

            logger.info(f"Generating initial argument for: {agente_nombre}")

            contexto_rag = self.rag_retriever.recuperar_contexto(
                query=f"{self.estado.tema} {agente.perspectiva}",
                top_k=3
            )
            contexto_rag_formatted = self.rag_retriever.formatear_para_agente(
                contexto_rag, max_chars=1500
            )

            argumento = agente.generar_argumento(
                tema=self.estado.tema,
                contexto_debate=self.estado.obtener_contexto_para_agente(agente_nombre),
                contexto_rag=contexto_rag_formatted,
                instruccion_especifica="Presenta tu postura inicial sobre el tema desde tu perspectiva única. "
                                       "Identifica los aspectos más importantes a considerar desde tu enfoque."
            )

            arg = self.estado.agregar_argumento(
                agente=agente_nombre,
                rol=agente.rol,
                contenido=argumento,
                referencias_rag=[doc['id'] for doc in contexto_rag]
            )

            yield arg

        logger.info("Initial round completed")

    def ejecutar_debate_libre(
        self,
        num_rondas: Optional[int] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Execute free debate rounds where agents respond to each other.

        Args:
            num_rondas: Number of rounds (uses config default if not provided)

        Yields:
            Argument dicts as they are generated
        """
        if not self.estado:
            raise RuntimeError("Debate not initialized")

        self.estado.cambiar_fase(DebateFase.DEBATE_LIBRE)

        if num_rondas is None:
            num_rondas = self.estado.config.get("num_rondas", settings.default_rounds)

        logger.info(f"Starting free debate: {num_rondas} rounds")

        moderador = self.agentes[AgentRole.MODERADOR]
        critico = self.agentes[AgentRole.CRITICO]

        for ronda in range(1, num_rondas + 1):
            self.estado.ronda_actual = ronda
            logger.info(f"Free debate round {ronda}/{num_rondas}")

            mod_analisis = moderador.generar_argumento(
                tema=self.estado.tema,
                contexto_debate=self.estado.obtener_contexto_para_agente(AgentRole.MODERADOR, ultimo_n=15),
                instruccion_especifica=f"Analiza el debate hasta ahora (Ronda {ronda}). "
                                       "Identifica los principales puntos de tensión y áreas de posible consenso. "
                                       "Señala qué agentes deben profundizar en qué aspectos."
            )

            arg = self.estado.agregar_argumento(
                agente=AgentRole.MODERADOR,
                rol=moderador.rol,
                contenido=mod_analisis
            )
            yield arg

            agentes_activos = self.estado.config.get("perspectivas", self.agentes_perspectiva)
            agentes_a_responder = self._seleccionar_agentes_para_ronda(
                agentes_activos,
                ronda,
                num_a_seleccionar=min(3, len(agentes_activos))
            )

            for idx, agente_nombre in enumerate(agentes_a_responder):
                agente = self.agentes[agente_nombre]

                logger.info(f"Agent {agente_nombre} responding in round {ronda}")

                contexto_rag = None
                if agente_nombre in [AgentRole.ECONOMISTA, AgentRole.CIENTIFICO]:
                    docs = self.rag_retriever.recuperar_contexto(
                        query=f"{self.estado.tema} {mod_analisis[:200]}",
                        top_k=2
                    )
                    contexto_rag = self.rag_retriever.formatear_para_agente(docs, max_chars=800)

                ultimos_args = self.estado.argumentos[-5:]
                ultimo_agente = ultimos_args[-1]['agente'] if ultimos_args else None

                if idx > 0 and ultimo_agente:
                    instruccion = (
                        f"Responde DIRECTAMENTE al argumento de {ultimo_agente}. "
                        f"Usa '@{ultimo_agente}:' para dirigirte a ese agente. "
                        f"Contraargumenta, complementa o cuestiona su punto. Sé breve y específico."
                    )
                else:
                    instruccion = (
                        f"Responde a los puntos del debate. Si alguien dijo algo relevante para tu área, "
                        f"respóndele directamente con '@NombreAgente:'. Sé breve."
                    )

                respuesta = agente.generar_argumento(
                    tema=self.estado.tema,
                    contexto_debate=self.estado.obtener_contexto_para_agente(agente_nombre, ultimo_n=8),
                    contexto_rag=contexto_rag,
                    instruccion_especifica=instruccion
                )

                arg = self.estado.agregar_argumento(
                    agente=agente_nombre,
                    rol=agente.rol,
                    contenido=respuesta
                )
                yield arg

            if ronda % 2 == 0:
                logger.info(f"Critic analyzing round {ronda}")

                contexto_falacias = self.rag_retriever.buscar_falacias(
                    "argumentos debate falacias lógicas"
                )

                critica = critico.generar_argumento(
                    tema=self.estado.tema,
                    contexto_debate=self.estado.obtener_contexto_para_agente(AgentRole.CRITICO, ultimo_n=10),
                    contexto_rag=contexto_falacias,
                    instruccion_especifica="Analiza los argumentos recientes. "
                                           "Identifica falacias lógicas, supuestos problemáticos, "
                                           "o inconsistencias. Sé constructivo."
                )

                arg = self.estado.agregar_argumento(
                    agente=AgentRole.CRITICO,
                    rol=critico.rol,
                    contenido=critica
                )
                yield arg

        logger.info("Free debate completed")

    def ejecutar_interpelaciones(self) -> Generator[Dict[str, Any], None, None]:
        """
        Execute directed questions (interpelaciones) from moderator to agents.

        Yields:
            Argument dicts as they are generated
        """
        if not self.estado:
            raise RuntimeError("Debate not initialized")

        self.estado.cambiar_fase(DebateFase.INTERPELACIONES)

        logger.info("Starting interpelaciones phase")

        moderador = self.agentes[AgentRole.MODERADOR]

        preguntas_prompt = moderador.generar_argumento(
            tema=self.estado.tema,
            contexto_debate=self.estado.obtener_contexto_para_agente(AgentRole.MODERADOR, ultimo_n=20),
            instruccion_especifica="Genera 3-5 preguntas clave que quedan por resolver. "
                                   "Cada pregunta debe dirigirse a un agente específico. "
                                   "Formato: '[AGENTE]: Pregunta'"
        )

        arg = self.estado.agregar_argumento(
            agente=AgentRole.MODERADOR,
            rol=moderador.rol,
            contenido=preguntas_prompt
        )
        yield arg

        agentes_activos = self.estado.config.get("perspectivas", self.agentes_perspectiva)

        for agente_nombre in agentes_activos[:5]:
            agente = self.agentes[agente_nombre]

            logger.info(f"Interpelación to: {agente_nombre}")

            pregunta_especifica = f"El moderador te hace una pregunta directa sobre aspectos no resueltos. "
            f"Responde de forma concisa y clara desde tu perspectiva."

            respuesta = agente.generar_argumento(
                tema=self.estado.tema,
                contexto_debate=self.estado.obtener_contexto_para_agente(agente_nombre, ultimo_n=10),
                instruccion_especifica=pregunta_especifica
            )

            arg = self.estado.agregar_argumento(
                agente=agente_nombre,
                rol=agente.rol,
                contenido=respuesta
            )
            yield arg

        logger.info("Interpelaciones phase completed")

    def ejecutar_sintesis(self) -> Generator[Dict[str, Any], None, None]:
        """
        Execute final synthesis phase.

        Yields:
            Final synthesis arguments
        """
        if not self.estado:
            raise RuntimeError("Debate not initialized")

        self.estado.cambiar_fase(DebateFase.SINTESIS)

        logger.info("Starting synthesis phase")

        sintetizador = self.agentes[AgentRole.SINTETIZADOR]

        contexto_completo_resumido = self._preparar_contexto_completo_para_sintesis()

        sintesis = sintetizador.generar_argumento(
            tema=self.estado.tema,
            contexto_debate=self.estado.argumentos,
            instruccion_especifica="Analiza TODO el debate completo. "
                                   "Genera:\n"
                                   "1. CONSENSOS ALCANZADOS (lista explícita)\n"
                                   "2. DISENSOS REMANENTES (lista explícita)\n"
                                   "3. PROPUESTAS HÍBRIDAS (soluciones integradoras)\n"
                                   "4. RESUMEN EJECUTIVO\n\n"
                                   "Sé balanceado, comprehensivo y claro."
        )

        arg = self.estado.agregar_argumento(
            agente=AgentRole.SINTETIZADOR,
            rol=sintetizador.rol,
            contenido=sintesis
        )
        yield arg

        self._extraer_conclusiones_de_sintesis(sintesis)

        secretario = self.agentes[AgentRole.SECRETARIO]

        acta_estadisticas = secretario.generar_argumento(
            tema=self.estado.tema,
            contexto_debate=self.estado.argumentos[-5:],
            instruccion_especifica="Genera ESTADÍSTICAS del debate (NO repitas consensos del Sintetizador):\n"
                                   "- Total de intervenciones por agente\n"
                                   "- Principales temas mencionados\n"
                                   "- Nivel de acuerdo/desacuerdo general\n"
                                   "- Momentos clave del debate\n"
                                   "Formato: Lista concisa, no repitas conclusiones."
        )

        arg = self.estado.agregar_argumento(
            agente=AgentRole.SECRETARIO,
            rol=secretario.rol,
            contenido=acta_estadisticas
        )
        yield arg

        logger.info("Synthesis phase completed")

    def ejecutar_debate_completo(self) -> Generator[Dict[str, Any], None, None]:
        """
        Execute the complete debate process.

        Yields:
            All arguments as they are generated
        """
        logger.info("Starting complete debate execution")

        try:
            yield from self.ejecutar_ronda_inicial()

            yield from self.ejecutar_debate_libre()

            yield from self.ejecutar_sintesis()

            self.estado.completar_debate()

            logger.info(
                f"Debate completed successfully: "
                f"id={self.estado.debate_id}, "
                f"arguments={len(self.estado.argumentos)}"
            )

        except Exception as e:
            logger.error(f"Error during debate execution: {e}")
            raise

    def obtener_resultado_final(self) -> Dict[str, Any]:
        """
        Get the final result of the debate.

        Returns:
            Complete debate result dict
        """
        if not self.estado:
            raise RuntimeError("Debate not initialized")

        if self.estado.fase_actual != DebateFase.COMPLETADO:
            raise RuntimeError("Debate not completed yet")

        duracion = None
        if self.estado.timestamp_fin:
            duracion = (self.estado.timestamp_fin - self.estado.timestamp_inicio).total_seconds()

        return {
            "debate_id": self.estado.debate_id,
            "tema": self.estado.tema,
            "tema_reformulado": self.estado.tema_reformulado,
            "acta_completa": self.estado.generar_acta(),
            "consensos": self.estado.consensos,
            "disensos": self.estado.disensos,
            "propuestas_hibridas": self.estado.propuestas_hibridas,
            "resumen_ejecutivo": self._generar_resumen_ejecutivo(),
            "argumentos": self.estado.argumentos,
            "timestamp_inicio": self.estado.timestamp_inicio.isoformat(),
            "timestamp_fin": self.estado.timestamp_fin.isoformat() if self.estado.timestamp_fin else None,
            "duracion_segundos": duracion,
            "estadisticas": self.estado.obtener_estadisticas()
        }

    def _seleccionar_agentes_para_ronda(
        self,
        agentes_disponibles: List[str],
        ronda: int,
        num_a_seleccionar: int
    ) -> List[str]:
        """Select agents to participate in a round (rotation + some randomness)."""
        n = len(agentes_disponibles)
        inicio = ((ronda - 1) * num_a_seleccionar) % n

        seleccionados = []
        for i in range(num_a_seleccionar):
            idx = (inicio + i) % n
            seleccionados.append(agentes_disponibles[idx])

        return seleccionados

    def _preparar_contexto_completo_para_sintesis(self) -> str:
        """Prepare condensed context of entire debate for synthesizer."""
        resumen_parts = [f"DEBATE COMPLETO - {len(self.estado.argumentos)} intervenciones\n"]

        for arg in self.estado.argumentos:
            resumen_parts.append(f"\n[{arg['agente']}]: {arg['contenido'][:500]}...")

        return "\n".join(resumen_parts[:100])

    def _extraer_conclusiones_de_sintesis(self, sintesis_texto: str):
        """Extract consensus, dissents, and proposals from synthesis text (simple parsing)."""
        lineas = sintesis_texto.split('\n')

        seccion_actual = None
        for linea in lineas:
            linea_lower = linea.lower().strip()
            linea_stripped = linea.strip()

            if 'consenso' in linea_lower and ':' in linea_lower:
                seccion_actual = 'consenso'
                continue
            elif 'disenso' in linea_lower and ':' in linea_lower:
                seccion_actual = 'disenso'
                continue
            elif 'propuesta' in linea_lower and (':' in linea_lower or 'híbrida' in linea_lower):
                seccion_actual = 'propuesta'
                continue
            elif 'resumen' in linea_lower and ':' in linea_lower:
                seccion_actual = None
                continue

            if linea_stripped and seccion_actual:
                contenido = linea_stripped.lstrip('*-•123456789. ')

                if seccion_actual == 'propuesta':
                    if len(contenido) > 15:
                        self.estado.agregar_propuesta(contenido)
                elif linea_stripped.startswith(('-', '•', '*')):
                    if len(contenido) > 20:
                        if seccion_actual == 'consenso':
                            self.estado.agregar_consenso(contenido)
                        elif seccion_actual == 'disenso':
                            self.estado.agregar_disenso(contenido)

        logger.info(
            f"Extracted: {len(self.estado.consensos)} consensos, "
            f"{len(self.estado.disensos)} disensos, "
            f"{len(self.estado.propuestas_hibridas)} propuestas"
        )

    def _generar_resumen_ejecutivo(self) -> str:
        """Generate executive summary from the debate."""
        if not self.estado.consensos and not self.estado.disensos:
            return f"Debate sobre: {self.estado.tema}\n\nDebate completado. Ver secciones de consensos y propuestas más abajo."

        resumen = []
        resumen.append(f"Tema debatido: {self.estado.tema}")

        total_items = len(self.estado.consensos) + len(self.estado.disensos)
        resumen.append(f"\nSe identificaron {len(self.estado.consensos)} consensos y {len(self.estado.disensos)} disensos principales.")

        if self.estado.propuestas_hibridas:
            resumen.append(f"Se propusieron {len(self.estado.propuestas_hibridas)} soluciones integradoras.")

        resumen.append("\nVer detalles completos en las secciones siguientes.")

        return "\n".join(resumen)
