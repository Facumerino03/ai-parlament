"""Etico agent for ethical analysis."""

from app.agents.base_agent import BaseAgent
from app.llm.prompts import ETICO_PROMPT
from app.core.config import AGENT_MODELS, AGENT_TEMPERATURES, AgentRole


class Etico(BaseAgent):
    """Ethicist agent for moral and philosophical analysis."""

    def __init__(self, llm_client=None):
        super().__init__(
            nombre=AgentRole.ETICO,
            rol="Análisis Ético",
            perspectiva="Implicaciones morales, dilemas éticos, valores",
            system_prompt=ETICO_PROMPT,
            modelo=AGENT_MODELS[AgentRole.ETICO],
            temperature=AGENT_TEMPERATURES[AgentRole.ETICO],
            llm_client=llm_client
        )
