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
