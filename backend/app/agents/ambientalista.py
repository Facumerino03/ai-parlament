"""Ambientalista agent for environmental analysis."""

from app.agents.base_agent import BaseAgent
from app.llm.prompts import AMBIENTALISTA_PROMPT
from app.core.config import AGENT_MODELS, AGENT_TEMPERATURES, AgentRole


class Ambientalista(BaseAgent):
    """Environmentalist agent for ecological impact analysis."""

    def __init__(self, llm_client=None):
        super().__init__(
            nombre=AgentRole.AMBIENTALISTA,
            rol="Análisis Ambiental",
            perspectiva="Impacto ecológico, sostenibilidad, conservación",
            system_prompt=AMBIENTALISTA_PROMPT,
            modelo=AGENT_MODELS[AgentRole.AMBIENTALISTA],
            temperature=AGENT_TEMPERATURES[AgentRole.AMBIENTALISTA],
            llm_client=llm_client
        )
