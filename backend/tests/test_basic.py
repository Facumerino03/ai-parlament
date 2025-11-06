"""
Basic tests for the AI Parliament backend.
These tests verify core functionality without requiring API keys.
"""

import pytest
from app.core.debate_state import DebateState
from app.core.config import DebateFase


def test_debate_state_creation():
    """Test creating a debate state."""
    tema = "¿Es ético el uso de IA en medicina?"
    estado = DebateState(tema)

    assert estado.debate_id is not None
    assert estado.tema == tema
    assert estado.fase_actual == DebateFase.INICIALIZACION
    assert estado.ronda_actual == 0
    assert len(estado.argumentos) == 0


def test_agregar_argumento():
    """Test adding an argument to debate state."""
    estado = DebateState("Tema de prueba")

    arg = estado.agregar_argumento(
        agente="economista",
        rol="Análisis Económico",
        contenido="Este es un argumento de prueba desde la perspectiva económica."
    )

    assert len(estado.argumentos) == 1
    assert arg['agente'] == "economista"
    assert arg['contenido'] == "Este es un argumento de prueba desde la perspectiva económica."
    assert arg['fase'] == DebateFase.INICIALIZACION


def test_cambiar_fase():
    """Test changing debate phase."""
    estado = DebateState("Tema de prueba")

    assert estado.fase_actual == DebateFase.INICIALIZACION

    estado.cambiar_fase(DebateFase.RONDA_INICIAL)
    assert estado.fase_actual == DebateFase.RONDA_INICIAL

    estado.cambiar_fase(DebateFase.DEBATE_LIBRE)
    assert estado.fase_actual == DebateFase.DEBATE_LIBRE
    assert estado.ronda_actual == 1  # Should reset to 1


def test_debate_state_to_dict():
    """Test serializing debate state to dict."""
    estado = DebateState("Tema de prueba")
    estado.agregar_argumento("economista", "Análisis Económico", "Contenido")

    data = estado.to_dict()

    assert data['debate_id'] == estado.debate_id
    assert data['tema'] == "Tema de prueba"
    assert data['total_argumentos'] == 1
    assert len(data['argumentos']) == 1


def test_generar_acta():
    """Test generating debate transcript."""
    estado = DebateState("¿Semana laboral de 4 días?")

    estado.cambiar_fase(DebateFase.RONDA_INICIAL)
    estado.agregar_argumento(
        "moderador",
        "Moderación",
        "Bienvenidos al debate sobre semana laboral."
    )
    estado.agregar_argumento(
        "economista",
        "Análisis Económico",
        "Desde una perspectiva económica..."
    )

    acta = estado.generar_acta()

    assert "ACTA DEL DEBATE" in acta
    assert "Semana laboral de 4 días" in acta
    assert "moderador" in acta.lower()
    assert "economista" in acta.lower()


def test_consensos_y_disensos():
    """Test adding consensus and dissent."""
    estado = DebateState("Tema de prueba")

    estado.agregar_consenso("Todos están de acuerdo en que X es importante.")
    estado.agregar_disenso("No hay acuerdo sobre Y.")

    assert len(estado.consensos) == 1
    assert len(estado.disensos) == 1
    assert "X es importante" in estado.consensos[0]


def test_completar_debate():
    """Test completing a debate."""
    estado = DebateState("Tema de prueba")

    assert estado.timestamp_fin is None
    assert estado.fase_actual != DebateFase.COMPLETADO

    estado.completar_debate()

    assert estado.timestamp_fin is not None
    assert estado.fase_actual == DebateFase.COMPLETADO


def test_obtener_estadisticas():
    """Test getting debate statistics."""
    estado = DebateState("Tema de prueba")
    estado.agregar_argumento("economista", "Análisis", "Contenido 1")
    estado.agregar_argumento("sociologo", "Análisis", "Contenido 2")
    estado.agregar_argumento("economista", "Análisis", "Contenido 3")

    stats = estado.obtener_estadisticas()

    assert stats['total_argumentos'] == 3
    assert stats['argumentos_por_agente']['economista'] == 2
    assert stats['argumentos_por_agente']['sociologo'] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
