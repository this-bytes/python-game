import pytest

from src.ui.player_engagement.engagement_manager import EngagementManager
from src.ui.player_engagement.urgency_system import UrgencySystem


class DummyIncident:
    def __init__(self, id: str, sla_percent: float):
        self.id = id
        self.sla_percent = sla_percent


class DummySpecialist:
    def __init__(self, id: str, burnout: int):
        self.id = id
        self.burnout = burnout


class DummyGameState:
    def __init__(self):
        self.incidents = []
        self.specialists = []
        self.money = 1000


def test_engagement_manager_initializes():
    gs = DummyGameState()
    em = EngagementManager((1280, 720), gs)
    assert em.screen_size == (1280, 720)


def test_urgency_system_detects_items():
    gs = DummyGameState()
    gs.incidents.append(DummyIncident('inc_1', 0.85))
    gs.specialists.append(DummySpecialist('spec_1', 85))

    us = UrgencySystem(gs)
    items = us.get_urgent_items()
    # Expect at least two urgent items
    assert any(i['type'] == 'incident' for i in items)
    assert any(i['type'] == 'specialist' for i in items)
