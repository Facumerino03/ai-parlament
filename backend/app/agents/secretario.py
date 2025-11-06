"""Secretario agent for recording and structuring the debate."""

from app.agents.base_agent import BaseAgent
from app.llm.prompts import SECRETARIO_PROMPT
from app.core.config import AGENT_MODELS, AGENT_TEMPERATURES, AgentRole


class Secretario(BaseAgent):
    """Secretary agent for recording and organizing the debate."""

    def __init__(self, llm_client=None):
        super().__init__(
            nombre=AgentRole.SECRETARIO,
            rol="Registro y Estructura",
            perspectiva="Neutral, organizador, registrador oficial",
            system_prompt=SECRETARIO_PROMPT,
            modelo=AGENT_MODELS[AgentRole.SECRETARIO],
            temperature=AGENT_TEMPERATURES[AgentRole.SECRETARIO],
            llm_client=llm_client
        )
