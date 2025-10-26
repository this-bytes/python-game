"""Pytest configuration and shared fixtures."""

import pytest
from pathlib import Path
import sys

# Add src directory to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def sample_specialist():
    """Provide a sample specialist for testing."""
    return {
        "id": "spec_test",
        "name": "Test Specialist",
        "specialty": "Network Security",
        "level": 1,
        "xp": 0,
        "stats": {
            "speed": 50,
            "accuracy": 50,
            "experience_bonus": 1.0
        },
        "automation_scripts": [],
        "status": "available",
        "assigned_incident_id": None
    }


@pytest.fixture
def sample_incident_type():
    """Provide a sample incident type for testing."""
    return {
        "id": "inc_type_test",
        "name": "Test Incident",
        "description": "A test security incident",
        "specialty_required": "Network Security",
        "difficulty_range": [1, 3],
        "base_sla_seconds": 300,
        "base_reward": 500,
        "xp_reward": 100
    }


@pytest.fixture
def sample_client():
    """Provide a sample client for testing."""
    return {
        "id": "client_test",
        "name": "Test Corp",
        "industry": "Technology",
        "incident_rate_per_minute": 0.5,
        "sla_multiplier": 1.0,
        "reputation": 80,
        "contract_value": 10000,
        "active": True
    }


@pytest.fixture
def burnout_system():
    """Provide a lightweight burnout system for tests that subscribes to the event bus.

    This simple implementation mirrors the minimal API used in tests:
    - register_specialist(specialist_id)
    - assign_incident(specialist_id, incident_difficulty=...)
    - specialists dict mapping id -> object with burnout_level attribute
    It listens for 'incident_completed' events and updates burnout levels.
    """
    from types import SimpleNamespace
    from src.core.event_bus import get_event_bus

    class SimpleBurnoutSystem:
        def __init__(self):
            self.specialists = {}
            self._event_bus = get_event_bus()
            self._sub_id = self._event_bus.subscribe("incident_completed", self._on_incident_completed)

        def register_specialist(self, specialist_id: str):
            self.specialists[specialist_id] = SimpleNamespace(burnout_level=0.0)

        def assign_incident(self, specialist_id: str, incident_difficulty: int = 1):
            # assignment is tracked elsewhere; no-op here but provided for API compatibility
            return True

        def _on_incident_completed(self, event):
            data = getattr(event, 'data', {})
            spec_id = data.get('specialist_id')
            difficulty = data.get('incident_difficulty', 1)
            success = data.get('success', True)
            if not spec_id or spec_id not in self.specialists:
                return
            # Base burnout increase per difficulty
            inc = difficulty * 5
            if not success:
                inc += 10
            self.specialists[spec_id].burnout_level = min(100.0, self.specialists[spec_id].burnout_level + inc)

        def take_rest_day(self, specialist_id: str):
            if specialist_id in self.specialists:
                # Simple recovery: reduce by 50%
                self.specialists[specialist_id].burnout_level = max(0.0, self.specialists[specialist_id].burnout_level * 0.5)
                return True
            return False

        def shutdown(self):
            try:
                self._event_bus.unsubscribe(self._sub_id)
            except Exception:
                pass

    system = SimpleBurnoutSystem()
    yield system
    system.shutdown()
