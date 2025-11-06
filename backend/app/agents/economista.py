"""Economista agent for economic analysis."""

from app.agents.base_agent import BaseAgent
from app.llm.prompts import ECONOMISTA_PROMPT
from app.core.config import AGENT_MODELS, AGENT_TEMPERATURES, AgentRole


class Economista(BaseAgent):
    """Economist agent for analyzing economic viability and impacts."""

    def __init__(self, llm_client=None):
        super().__init__(
            nombre=AgentRole.ECONOMISTA,
            rol="Análisis Económico",
            perspectiva="Costos, beneficios, viabilidad financiera, impacto en mercados",
            system_prompt=ECONOMISTA_PROMPT,
            modelo=AGENT_MODELS[AgentRole.ECONOMISTA],
            temperature=AGENT_TEMPERATURES[AgentRole.ECONOMISTA],
            llm_client=llm_client
        )
