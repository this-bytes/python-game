"""Tests for GameState model."""

import pytest
from unittest.mock import Mock, patch
import time
import json

from src.models.game_state import GameState, GameMetrics
from src.models.specialist import Specialist, SpecialistStats
from src.models.incident import Incident
from src.models.client import Client
from src.models.automation_script import AutomationScript, TriggerConditions


class TestGameMetrics:
    """Test GameMetrics class."""

    def test_to_dict(self):
        """Test converting metrics to dictionary."""
        metrics = GameMetrics(
            total_incidents_handled=10,
            total_incidents_failed=2,
            total_profit=5000.0,
            total_xp_awarded=1500,
            average_resolution_time=120.5,
            sla_compliance_rate=85.0,
            automation_scripts_triggered=5,
            specialist_utilization_rate=75.0
        )

        result = metrics.to_dict()
        assert result["total_incidents_handled"] == 10
        assert result["total_profit"] == 5000.0
        assert result["sla_compliance_rate"] == 85.0

    def test_from_dict(self):
        """Test creating metrics from dictionary."""
        data = {
            "total_incidents_handled": 15,
            "total_incidents_failed": 3,
            "total_profit": 7500.0
        }

        metrics = GameMetrics.from_dict(data)
        assert metrics.total_incidents_handled == 15
        assert metrics.total_incidents_failed == 3
        assert metrics.total_profit == 7500.0
        assert metrics.average_resolution_time == 0.0  # Default value


class TestGameState:
    """Test GameState class."""

    @pytest.fixture
    def mock_json_loader(self):
        """Mock JSON loader for testing."""
        with patch('src.models.game_state.JSONLoader') as mock_loader:
            loader_instance = Mock()
            loader_instance.load_data.side_effect = self._mock_load_data
            mock_loader.return_value = loader_instance
            yield loader_instance

    def _mock_load_data(self, filename):
        """Mock data loading for tests."""
        # Handle both with and without .json extension
        filename_base = filename.replace('.json', '')
        
        if filename_base == "specialists":
            return {
                "specialists": [
                    {
                        "id": "spec_001",
                        "name": "Alice Chen",
                        "specialty": "Network Security",
                        "level": 3,
                        "xp": 500,
                        "stats": {"speed": 85.0, "accuracy": 90.0, "experience_bonus": 1.2},
                        "automation_scripts": []
                    }
                ]
            }
        elif filename_base == "clients":
            return {
                "clients": [
                    {
                        "id": "client_001",
                        "name": "TechCorp Inc.",
                        "industry": "Technology",
                        "incident_rate_per_minute": 0.5,
                        "sla_multiplier": 1.0,
                        "reputation": 80,
                        "contract_value": 10000
                    }
                ]
            }
        elif filename_base == "automation_scripts":
            return {
                "automation_scripts": [
                    {
                        "id": "auto_test",
                        "name": "Test Automation",
                        "description": "Test script",
                        "required_level": 1,
                        "specialty": "Network Security",
                        "trigger_conditions": {"max_difficulty": 2},
                        "effect": "auto_assign",
                        "effect_magnitude": 1.0
                    }
                ]
            }
        elif filename_base == "incidents":
            return {
                "incident_types": [
                    {
                        "id": "ddos_attack",
                        "name": "DDoS Attack",
                        "specialty_required": "Network Security",
                        "difficulty_range": [1, 5],
                        "base_sla_seconds": 300,
                        "base_reward": 500,
                        "xp_reward": 100
                    }
                ]
            }
        return {}

    @pytest.fixture
    def sample_game_state(self, mock_json_loader):
        """Sample game state for testing."""
        return GameState()

    def test_initialization(self, mock_json_loader):
        """Test game state initialization."""
        game_state = GameState()

        assert len(game_state.specialists) == 1
        assert len(game_state.clients) == 1
        assert len(game_state.automation_scripts) == 1
        assert game_state.current_money == 5000.0
        assert game_state.max_active_incidents == 50
        assert not game_state.is_paused

    def test_update_paused_game(self, sample_game_state):
        """Test that paused game doesn't update."""
        sample_game_state.is_paused = True
        initial_time = sample_game_state.current_time

        sample_game_state.update(1.0)

        assert sample_game_state.current_time == initial_time

    def test_update_running_game(self, sample_game_state):
        """Test game state update when running."""
        initial_time = sample_game_state.current_time

        sample_game_state.update(2.0)

        assert sample_game_state.current_time == initial_time + 2.0

    def test_get_specialist_by_id(self, sample_game_state):
        """Test getting specialist by ID."""
        specialist = sample_game_state.get_specialist_by_id("spec_001")
        assert specialist is not None
        assert specialist.name == "Alice Chen"

        # Test non-existent ID
        assert sample_game_state.get_specialist_by_id("nonexistent") is None

    def test_get_client_by_id(self, sample_game_state):
        """Test getting client by ID."""
        client = sample_game_state.get_client_by_id("client_001")
        assert client is not None
        assert client.name == "TechCorp Inc."

    def test_get_automation_script_by_id(self, sample_game_state):
        """Test getting automation script by ID."""
        script = sample_game_state.get_automation_script_by_id("auto_test")
        assert script is not None
        assert script.name == "Test Automation"

    def test_get_available_specialists(self, sample_game_state):
        """Test getting available specialists."""
        available = sample_game_state.get_available_specialists()
        assert len(available) == 1  # Initially all specialists are available

        # Make specialist busy
        sample_game_state.specialists[0].status = "busy"
        available = sample_game_state.get_available_specialists()
        assert len(available) == 0

    def test_assign_incident_to_specialist_success(self, sample_game_state):
        """Test successful incident assignment."""
        # Create a pending incident
        incident = Incident(
            id="test_incident",
            incident_type="Test Incident",
            specialty_required="Network Security",
            difficulty=2,
            sla_seconds=300,
            base_reward=500,
            xp_reward=100,
            client_id="client_001"
        )
        sample_game_state.incidents.append(incident)

        # Assign incident
        success = sample_game_state.assign_incident_to_specialist("test_incident", "spec_001")

        assert success is True
        assert incident.status == "assigned"
        assert incident.assigned_specialist_id == "spec_001"
        assert sample_game_state.specialists[0].status == "busy"

    def test_assign_incident_to_specialist_specialty_mismatch(self, sample_game_state):
        """Test assignment failure due to specialty mismatch."""
        # Create incident requiring different specialty
        incident = Incident(
            id="test_incident",
            incident_type="Test Incident",
            specialty_required="Malware Analysis",  # Different from specialist's specialty
            difficulty=2,
            sla_seconds=300,
            base_reward=500,
            xp_reward=100,
            client_id="client_001"
        )
        sample_game_state.incidents.append(incident)

        success = sample_game_state.assign_incident_to_specialist("test_incident", "spec_001")

        assert success is False
        assert incident.status == "pending"

    def test_hire_specialist_success(self, sample_game_state):
        """Test successful specialist hiring."""
        specialist_data = {
            "id": "spec_002",
            "name": "Bob Smith",
            "specialty": "Malware Analysis",
            "level": 1,
            "xp": 0,
            "stats": {"speed": 80.0, "accuracy": 85.0, "experience_bonus": 1.0}
        }

        success = sample_game_state.hire_specialist(specialist_data)

        assert success is True
        assert len(sample_game_state.specialists) == 2
        assert sample_game_state.current_money == 3000.0  # 5000 - 2000

    def test_hire_specialist_insufficient_funds(self, sample_game_state):
        """Test hiring failure due to insufficient funds."""
        sample_game_state.current_money = 1000.0  # Less than hire cost

        specialist_data = {
            "id": "spec_002",
            "name": "Bob Smith",
            "specialty": "Malware Analysis",
            "level": 1,
            "xp": 0,
            "stats": {"speed": 80.0, "accuracy": 85.0, "experience_bonus": 1.0}
        }

        success = sample_game_state.hire_specialist(specialist_data)

        assert success is False
        assert len(sample_game_state.specialists) == 1  # No new specialist added

    def test_upgrade_specialist_success(self, sample_game_state):
        """Test successful specialist upgrade."""
        initial_speed = sample_game_state.specialists[0].stats.speed

        success = sample_game_state.upgrade_specialist("spec_001", "speed")

        assert success is True
        assert sample_game_state.specialists[0].stats.speed == initial_speed + 5.0
        assert sample_game_state.current_money == 4000.0  # 5000 - 1000

    def test_upgrade_specialist_insufficient_funds(self, sample_game_state):
        """Test upgrade failure due to insufficient funds."""
        sample_game_state.current_money = 500.0  # Less than upgrade cost

        success = sample_game_state.upgrade_specialist("spec_001", "speed")

        assert success is False

    def test_get_game_time_elapsed(self, sample_game_state):
        """Test getting elapsed game time."""
        initial_time = sample_game_state.get_game_time_elapsed()

        # Simulate time passing
        sample_game_state.current_time += 10.0

        elapsed = sample_game_state.get_game_time_elapsed()
        assert elapsed == initial_time + 10.0

    def test_get_game_summary(self, sample_game_state):
        """Test getting game summary."""
        summary = sample_game_state.get_game_summary()

        assert "game_time" in summary
        assert "current_money" in summary
        assert "specialists_count" in summary
        assert "active_incidents_count" in summary
        assert "metrics" in summary
        assert summary["specialists_count"] == 1
        assert summary["current_money"] == 5000.0

    def test_to_dict(self, sample_game_state):
        """Test converting game state to dictionary."""
        data = sample_game_state.to_dict()

        assert "specialists" in data
        assert "incidents" in data
        assert "clients" in data
        assert "current_money" in data
        assert "metrics" in data
        assert len(data["specialists"]) == 1

    def test_from_dict(self, mock_json_loader):
        """Test creating game state from dictionary."""
        data = {
            "specialists": [
                {
                    "id": "spec_001",
                    "name": "Alice Chen",
                    "specialty": "Network Security",
                    "level": 3,
                    "xp": 500,
                    "stats": {"speed": 85.0, "accuracy": 90.0, "experience_bonus": 1.2},
                    "automation_scripts": []
                }
            ],
            "incidents": [],
            "clients": [
                {
                    "id": "client_001",
                    "name": "TechCorp Inc.",
                    "industry": "Technology",
                    "incident_rate_per_minute": 0.5,
                    "sla_multiplier": 1.0,
                    "reputation": 80,
                    "contract_value": 10000
                }
            ],
            "current_money": 3000.0,
            "total_money_earned": 1000.0,
            "metrics": {"total_incidents_handled": 5}
        }

        game_state = GameState.from_dict(data)

        assert len(game_state.specialists) == 1
        assert len(game_state.clients) == 1
        assert game_state.current_money == 3000.0
        assert game_state.total_money_earned == 1000.0
        assert game_state.metrics.total_incidents_handled == 5

    @patch('random.random')
    @patch('random.choice')
    def test_incident_generation(self, mock_choice, mock_random, sample_game_state):
        """Test incident generation."""
        from src.core.incident_generator import IncidentTemplate
        
        # Mock random functions to ensure incident generation
        mock_random.return_value = 0.1  # Below generation probability threshold
        
        # Create a mock IncidentTemplate object
        mock_template = IncidentTemplate(
            id="ddos_attack",
            name="DDoS Attack",
            description="Distributed Denial of Service attack",
            specialty_required="Network Security",
            difficulty_range=[1, 5],
            base_sla_seconds=300,
            base_reward=500,
            xp_reward=100
        )
        mock_choice.return_value = mock_template

        # Ensure we have capacity for incidents
        sample_game_state.incidents = []

        # Update to trigger incident generation
        sample_game_state.update(120.0)  # 2 minutes

        # Should have generated incidents
        assert len(sample_game_state.incidents) > 0

    @patch('random.random')
    def test_incident_resolution_success(self, mock_random, sample_game_state):
        """Test successful incident resolution."""
        # Mock random for guaranteed success
        mock_random.return_value = 0.1  # Below success probability threshold
        
        # Clear initial incidents generated on game state creation
        sample_game_state.incidents.clear()
        
        # Create and assign incident
        incident = Incident(
            id="test_incident",
            incident_type="Test Incident",
            specialty_required="Network Security",
            difficulty=1,  # Easy difficulty for high success chance
            sla_seconds=300,
            base_reward=500,
            xp_reward=100,
            client_id="client_001"
        )
        sample_game_state.incidents.append(incident)

        # Assign to specialist
        sample_game_state.assign_incident_to_specialist("test_incident", "spec_001")

        # Simulate resolution (specialist becomes available again)
        sample_game_state.specialists[0].status = "available"

        # Update to trigger resolution check
        initial_money = sample_game_state.current_money
        initial_xp = sample_game_state.specialists[0].xp

        sample_game_state.update(1.0)

        # Incident should be resolved
        assert len(sample_game_state.incidents) == 0
        assert sample_game_state.current_money > initial_money
        assert sample_game_state.specialists[0].xp > initial_xp

    def test_sla_violation_penalty(self, sample_game_state):
        """Test SLA violation penalties."""
        # Clear initial incidents generated on game state creation
        sample_game_state.incidents.clear()
        
        # Create incident that's already past SLA
        incident = Incident(
            id="test_incident",
            incident_type="Test Incident",
            specialty_required="Network Security",
            difficulty=2,
            sla_seconds=1,  # Very short SLA
            base_reward=500,
            xp_reward=100,
            client_id="client_001",
            spawn_time=sample_game_state.current_time - 10  # Already past SLA
        )
        sample_game_state.incidents.append(incident)

        initial_money = sample_game_state.current_money

        # Update to trigger SLA check
        sample_game_state.update(1.0)

        # Incident should be failed due to SLA violation
        assert len(sample_game_state.incidents) == 0
        assert sample_game_state.current_money < initial_money  # Penalty applied

    def test_repr(self, sample_game_state):
        """Test string representation of game state."""
        # Clear initial incidents for consistent repr test
        sample_game_state.incidents.clear()
        
        repr_str = repr(sample_game_state)

        assert "GameState" in repr_str
        assert "specialists=1" in repr_str
        assert "incidents=0" in repr_str
        assert "money=$5000" in repr_str