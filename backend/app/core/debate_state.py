"""
Debate state management.
Maintains the complete state of a debate in progress.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import uuid
import json
import logging

from app.core.config import DebateFase

logger = logging.getLogger(__name__)


class DebateState:
    """Maintains the complete state of a debate."""

    def __init__(self, tema: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize debate state.

        Args:
            tema: The debate topic
            config: Optional configuration parameters
        """
        self.debate_id = str(uuid.uuid4())
        self.tema = tema
        self.tema_reformulado = None  # Set by moderator
        self.config = config or {}

        # State tracking
        self.fase_actual = DebateFase.INICIALIZACION
        self.ronda_actual = 0

        # Debate content
        self.argumentos: List[Dict[str, Any]] = []
        self.consensos: List[str] = []
        self.disensos: List[str] = []
        self.propuestas_hibridas: List[str] = []

        # Timestamps
        self.timestamp_inicio = datetime.utcnow()
        self.timestamp_fin: Optional[datetime] = None

        # Metadata
        self.metadata: Dict[str, Any] = {
            "perspectivas_activas": config.get("perspectivas", []),
            "num_rondas_configuradas": config.get("num_rondas", 5),
            "profundidad_rag": config.get("profundidad_rag", 5)
        }

        logger.info(
            f"DebateState initialized: id={self.debate_id}, tema={tema[:50]}..."
        )

    def agregar_argumento(
        self,
        agente: str,
        rol: str,
        contenido: str,
        referencias_rag: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add an argument to the debate.

        Args:
            agente: Agent identifier
            rol: Agent role description
            contenido: Argument content
            referencias_rag: Optional RAG references
            metadata: Optional additional metadata

        Returns:
            The formatted argument dict
        """
        argumento = {
            "id": len(self.argumentos),
            "agente": agente,
            "rol": rol,
            "contenido": contenido,
            "fase": self.fase_actual,
            "ronda": self.ronda_actual,
            "timestamp": datetime.utcnow().isoformat(),
            "referencias_rag": referencias_rag or [],
            "metadata": metadata or {}
        }

        self.argumentos.append(argumento)

        logger.debug(
            f"Argument added: agent={agente}, fase={self.fase_actual}, "
            f"ronda={self.ronda_actual}, length={len(contenido)}"
        )

        return argumento

    def cambiar_fase(self, nueva_fase: str):
        """
        Change the current debate phase.

        Args:
            nueva_fase: New phase identifier
        """
        logger.info(
            f"Phase change: {self.fase_actual} -> {nueva_fase} "
            f"(debate_id={self.debate_id})"
        )
        self.fase_actual = nueva_fase

        # Reset round counter for new debate phase
        if nueva_fase == DebateFase.DEBATE_LIBRE:
            self.ronda_actual = 1

    def avanzar_ronda(self):
        """Advance to the next round within the current phase."""
        self.ronda_actual += 1
        logger.debug(
            f"Round advanced: ronda={self.ronda_actual} "
            f"(fase={self.fase_actual}, debate_id={self.debate_id})"
        )

    def obtener_contexto_para_agente(
        self,
        agente: str,
        ultimo_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get relevant context for an agent.

        Args:
            agente: Agent identifier
            ultimo_n: Number of recent arguments to include

        Returns:
            List of relevant argument dicts
        """
        # Return last N arguments
        return self.argumentos[-ultimo_n:] if self.argumentos else []

    def agregar_consenso(self, consenso: str):
        """Add an identified consensus."""
        self.consensos.append(consenso)
        logger.info(f"Consensus added (total={len(self.consensos)}): {consenso[:100]}...")

    def agregar_disenso(self, disenso: str):
        """Add an identified dissent."""
        self.disensos.append(disenso)
        logger.info(f"Dissent added (total={len(self.disensos)}): {disenso[:100]}...")

    def agregar_propuesta(self, propuesta: str):
        """Add a hybrid proposal."""
        self.propuestas_hibridas.append(propuesta)
        logger.info(f"Proposal added (total={len(self.propuestas_hibridas)}): {propuesta[:100]}...")

    def generar_acta(self) -> str:
        """
        Generate formal minutes/transcript of the debate.

        Returns:
            Formatted transcript as string
        """
        acta_parts = []

        # Header
        acta_parts.append("=" * 80)
        acta_parts.append("ACTA DEL DEBATE - PARLAMENTO VIRTUAL DE IA")
        acta_parts.append("=" * 80)
        acta_parts.append(f"\nID del Debate: {self.debate_id}")
        acta_parts.append(f"Tema: {self.tema_reformulado or self.tema}")
        acta_parts.append(f"Fecha: {self.timestamp_inicio.strftime('%Y-%m-%d %H:%M:%S')} UTC")

        if self.timestamp_fin:
            duracion = (self.timestamp_fin - self.timestamp_inicio).total_seconds()
            acta_parts.append(f"Duración: {duracion:.0f} segundos")

        acta_parts.append(f"\nTotal de Intervenciones: {len(self.argumentos)}")
        acta_parts.append("\n" + "=" * 80)

        # Arguments by phase
        fases_presentes = {}
        for arg in self.argumentos:
            fase = arg.get('fase', 'desconocida')
            if fase not in fases_presentes:
                fases_presentes[fase] = []
            fases_presentes[fase].append(arg)

        for fase, args in fases_presentes.items():
            acta_parts.append(f"\n\n{'=' * 80}")
            acta_parts.append(f"FASE: {fase.upper()}")
            acta_parts.append(f"{'=' * 80}\n")

            for arg in args:
                acta_parts.append(f"\n[{arg['agente'].upper()}] - {arg['rol']}")
                if arg.get('ronda', 0) > 0:
                    acta_parts.append(f"Ronda: {arg['ronda']}")
                acta_parts.append(f"Timestamp: {arg['timestamp']}")
                acta_parts.append(f"\n{arg['contenido']}")
                if arg.get('referencias_rag'):
                    acta_parts.append(f"\nReferencias RAG: {', '.join(arg['referencias_rag'])}")
                acta_parts.append("\n" + "-" * 80)

        # Synthesis section
        if self.consensos or self.disensos or self.propuestas_hibridas:
            acta_parts.append(f"\n\n{'=' * 80}")
            acta_parts.append("SÍNTESIS FINAL")
            acta_parts.append(f"{'=' * 80}\n")

            if self.consensos:
                acta_parts.append("\nCONSENSOS ALCANZADOS:")
                for i, consenso in enumerate(self.consensos, 1):
                    acta_parts.append(f"{i}. {consenso}")

            if self.disensos:
                acta_parts.append("\n\nDISENSOS REMANENTES:")
                for i, disenso in enumerate(self.disensos, 1):
                    acta_parts.append(f"{i}. {disenso}")

            if self.propuestas_hibridas:
                acta_parts.append("\n\nPROPUESTAS HÍBRIDAS:")
                for i, propuesta in enumerate(self.propuestas_hibridas, 1):
                    acta_parts.append(f"{i}. {propuesta}")

        # Footer
        acta_parts.append("\n\n" + "=" * 80)
        acta_parts.append("FIN DEL ACTA")
        acta_parts.append("=" * 80)

        return "\n".join(acta_parts)

    def completar_debate(self):
        """Mark the debate as completed."""
        self.fase_actual = DebateFase.COMPLETADO
        self.timestamp_fin = datetime.utcnow()
        logger.info(
            f"Debate completed: id={self.debate_id}, "
            f"duration={(self.timestamp_fin - self.timestamp_inicio).total_seconds():.0f}s, "
            f"arguments={len(self.argumentos)}"
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize state to dictionary.

        Returns:
            Dict representation of the debate state
        """
        return {
            "debate_id": self.debate_id,
            "tema": self.tema,
            "tema_reformulado": self.tema_reformulado,
            "fase_actual": self.fase_actual,
            "ronda_actual": self.ronda_actual,
            "timestamp_inicio": self.timestamp_inicio.isoformat(),
            "timestamp_fin": self.timestamp_fin.isoformat() if self.timestamp_fin else None,
            "argumentos": self.argumentos,
            "consensos": self.consensos,
            "disensos": self.disensos,
            "propuestas_hibridas": self.propuestas_hibridas,
            "metadata": self.metadata,
            "total_argumentos": len(self.argumentos)
        }

    def guardar_a_archivo(self, filepath: str):
        """
        Save debate state to JSON file.

        Args:
            filepath: Path to save the JSON file
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            logger.info(f"Debate state saved to: {filepath}")
        except Exception as e:
            logger.error(f"Error saving debate state: {e}")
            raise

    @classmethod
    def cargar_desde_archivo(cls, filepath: str) -> 'DebateState':
        """
        Load debate state from JSON file.

        Args:
            filepath: Path to the JSON file

        Returns:
            DebateState instance
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Create instance
            state = cls(tema=data['tema'], config=data.get('metadata', {}))

            # Restore state
            state.debate_id = data['debate_id']
            state.tema_reformulado = data.get('tema_reformulado')
            state.fase_actual = data['fase_actual']
            state.ronda_actual = data['ronda_actual']
            state.argumentos = data['argumentos']
            state.consensos = data['consensos']
            state.disensos = data['disensos']
            state.propuestas_hibridas = data['propuestas_hibridas']
            state.timestamp_inicio = datetime.fromisoformat(data['timestamp_inicio'])
            if data.get('timestamp_fin'):
                state.timestamp_fin = datetime.fromisoformat(data['timestamp_fin'])

            logger.info(f"Debate state loaded from: {filepath}")
            return state

        except Exception as e:
            logger.error(f"Error loading debate state: {e}")
            raise

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Get statistics about the debate.

        Returns:
            Dict with debate statistics
        """
        # Count arguments by agent
        args_por_agente = {}
        for arg in self.argumentos:
            agente = arg['agente']
            args_por_agente[agente] = args_por_agente.get(agente, 0) + 1

        # Calculate duration
        duracion = None
        if self.timestamp_fin:
            duracion = (self.timestamp_fin - self.timestamp_inicio).total_seconds()

        return {
            "debate_id": self.debate_id,
            "fase_actual": self.fase_actual,
            "total_argumentos": len(self.argumentos),
            "argumentos_por_agente": args_por_agente,
            "consensos": len(self.consensos),
            "disensos": len(self.disensos),
            "propuestas": len(self.propuestas_hibridas),
            "duracion_segundos": duracion,
            "completado": self.fase_actual == DebateFase.COMPLETADO
        }
