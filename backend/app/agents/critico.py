"""Critico agent for critical analysis."""

from app.agents.base_agent import BaseAgent
from app.llm.prompts import CRITICO_PROMPT
from app.core.config import AGENT_MODELS, AGENT_TEMPERATURES, AgentRole


class Critico(BaseAgent):
    """Critic agent for identifying fallacies and questioning assumptions."""

    def __init__(self, llm_client=None):
        super().__init__(
            nombre=AgentRole.CRITICO,
            rol="Análisis Crítico",
            perspectiva="Cuestionar supuestos, identificar falacias, escepticismo constructivo",
            system_prompt=CRITICO_PROMPT,
            modelo=AGENT_MODELS[AgentRole.CRITICO],
            temperature=AGENT_TEMPERATURES[AgentRole.CRITICO],
            llm_client=llm_client
        )
