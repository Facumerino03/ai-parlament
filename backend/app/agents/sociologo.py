"""Sociologo agent for social analysis."""

from app.agents.base_agent import BaseAgent
from app.llm.prompts import SOCIOLOGO_PROMPT
from app.core.config import AGENT_MODELS, AGENT_TEMPERATURES, AgentRole


class Sociologo(BaseAgent):
    """Sociologist agent for analyzing social impacts and equity."""

    def __init__(self, llm_client=None):
        super().__init__(
            nombre=AgentRole.SOCIOLOGO,
            rol="Análisis Social",
            perspectiva="Impacto social, equidad, bienestar comunitario, justicia",
            system_prompt=SOCIOLOGO_PROMPT,
            modelo=AGENT_MODELS[AgentRole.SOCIOLOGO],
            temperature=AGENT_TEMPERATURES[AgentRole.SOCIOLOGO],
            llm_client=llm_client
        )
