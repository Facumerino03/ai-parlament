"""Cientifico agent for scientific analysis."""

from app.agents.base_agent import BaseAgent
from app.llm.prompts import CIENTIFICO_PROMPT
from app.core.config import AGENT_MODELS, AGENT_TEMPERATURES, AgentRole


class Cientifico(BaseAgent):
    """Scientist agent for evidence-based analysis."""

    def __init__(self, llm_client=None):
        super().__init__(
            nombre=AgentRole.CIENTIFICO,
            rol="Análisis Científico",
            perspectiva="Evidencia empírica, datos, viabilidad técnica",
            system_prompt=CIENTIFICO_PROMPT,
            modelo=AGENT_MODELS[AgentRole.CIENTIFICO],
            temperature=AGENT_TEMPERATURES[AgentRole.CIENTIFICO],
            llm_client=llm_client
        )
