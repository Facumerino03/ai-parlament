"""Pragmatico agent for practical implementation analysis."""

from app.agents.base_agent import BaseAgent
from app.llm.prompts import PRAGMATICO_PROMPT
from app.core.config import AGENT_MODELS, AGENT_TEMPERATURES, AgentRole


class Pragmatico(BaseAgent):
    """Pragmatist agent for feasibility and implementation analysis."""

    def __init__(self, llm_client=None):
        super().__init__(
            nombre=AgentRole.PRAGMATICO,
            rol="Análisis Pragmático",
            perspectiva="Implementación práctica, viabilidad real, obstáculos",
            system_prompt=PRAGMATICO_PROMPT,
            modelo=AGENT_MODELS[AgentRole.PRAGMATICO],
            temperature=AGENT_TEMPERATURES[AgentRole.PRAGMATICO],
            llm_client=llm_client
        )
