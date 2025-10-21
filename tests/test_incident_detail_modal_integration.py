import pygame
import pytest

from src.models.incident import Incident
from src.ui.modals.incident_detail_modal import IncidentDetailModal


def test_incident_detail_modal_renders_without_exception(tmp_path):
    """Integration: create a simple Incident and ensure modal render_content runs."""
    # Create an offscreen surface to avoid interfering with other tests' display state
    pygame.font.init()
    screen = pygame.Surface((800, 600))

    # Construct a minimal incident
    incident = Incident(
        id="test_inc_001",
        incident_type="Test Attack",
        specialty_required="Network Security",
        difficulty=2,
        sla_seconds=300,
        base_reward=500,
        xp_reward=100,
        client_id="client_001",
        description="This is a test incident for integration testing."
    )

    # Create a dummy game state with only the methods the modal uses
    class DummyGameState:
        def __init__(self, incidents):
            self.incidents = incidents

        def get_incident_by_id(self, incident_id):
            return next((i for i in self.incidents if i.id == incident_id), None)

    gs = DummyGameState([incident])

    modal = IncidentDetailModal(screen, gs, incident_id=incident.id)

    # Create a content rectangle that matches modal internals and call render_content
    content_rect = pygame.Rect(10, 10, 500, 300)
    # Call the modal's render_content directly to exercise drawing logic on an offscreen surface
    modal.render_content(screen, content_rect)

    # If we get here, rendering logic ran without raising
    assert True
