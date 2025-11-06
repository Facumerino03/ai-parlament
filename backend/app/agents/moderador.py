"""Moderador agent for orchestrating the debate."""

from app.agents.base_agent import BaseAgent
from app.llm.prompts import MODERADOR_PROMPT
from app.core.config import AGENT_MODELS, AGENT_TEMPERATURES, AgentRole


class Moderador(BaseAgent):
    """Moderator agent that orchestrates the debate."""

    def __init__(self, llm_client=None):
        super().__init__(
            nombre=AgentRole.MODERADOR,
            rol="Moderación y Orquestación",
            perspectiva="Neutral, facilitador del debate, buscador de consensos",
            system_prompt=MODERADOR_PROMPT,
            modelo=AGENT_MODELS[AgentRole.MODERADOR],
            temperature=AGENT_TEMPERATURES[AgentRole.MODERADOR],
            llm_client=llm_client
        )
