"""Sintetizador agent for final synthesis of the debate."""

from app.agents.base_agent import BaseAgent
from app.llm.prompts import SINTETIZADOR_PROMPT
from app.core.config import AGENT_MODELS, AGENT_TEMPERATURES, AgentRole


class Sintetizador(BaseAgent):
    """Synthesizer agent for generating final conclusions and proposals."""

    def __init__(self, llm_client=None):
        super().__init__(
            nombre=AgentRole.SINTETIZADOR,
            rol="Síntesis Final",
            perspectiva="Análisis holístico, integración de perspectivas, conclusiones balanceadas",
            system_prompt=SINTETIZADOR_PROMPT,
            modelo=AGENT_MODELS[AgentRole.SINTETIZADOR],
            temperature=AGENT_TEMPERATURES[AgentRole.SINTETIZADOR],
            llm_client=llm_client
        )
