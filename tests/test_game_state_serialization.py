"""Tests for GameState serialization and deserialization.

Verifies round-trip integrity for dual-mode backend architecture.
"""
import pytest
import time
from src.models.game_state import GameState, GameMetrics
from src.models.specialist import Specialist, SpecialistStats
from src.models.incident import Incident
from src.models.client import Client


class TestGameStateSerializationRoundTrip:
    """Test GameState to_dict() and from_dict() round-trip integrity."""

    def test_empty_game_state_round_trip(self):
        """Test round-trip with minimal game state."""
        # Create minimal game state
        original = GameState()
        original.specialists = []
        original.incidents = []
        original.clients = []
        
        # Serialize
        state_dict = original.to_dict()
        
        # Deserialize
        restored = GameState.from_dict(state_dict)
        
        # Verify
        assert restored.current_money == original.current_money
        assert restored.game_speed_multiplier == original.game_speed_multiplier
        assert restored.is_paused == original.is_paused
        assert len(restored.specialists) == 0
        assert len(restored.incidents) == 0
        assert len(restored.clients) == 0

    def test_game_state_with_specialists_round_trip(self):
        """Test round-trip with specialists."""
        # Create game state with specialists
        original = GameState()
        
        specialist1 = Specialist(
            id="spec_001",
            name="Test Specialist",
            specialty="Network Security",
            level=5,
            xp=1000,
            stats=SpecialistStats(speed=100.0, accuracy=85.0, experience_bonus=1.0)
        )
        specialist2 = Specialist(
            id="spec_002",
            name="Another Specialist",
            specialty="Cryptography",
            level=3,
            xp=500,
            stats=SpecialistStats(speed=95.0, accuracy=90.0, experience_bonus=1.0)
        )
        
        original.specialists = [specialist1, specialist2]
        original.incidents = []
        original.clients = []
        
        # Serialize
        state_dict = original.to_dict()
        
        # Deserialize
        restored = GameState.from_dict(state_dict)
        
        # Verify specialists
        assert len(restored.specialists) == 2
        assert restored.specialists[0].id == "spec_001"
        assert restored.specialists[0].name == "Test Specialist"
        assert restored.specialists[0].specialty == "Network Security"
        assert restored.specialists[0].level == 5
        assert restored.specialists[0].xp == 1000
        
        assert restored.specialists[1].id == "spec_002"
        assert restored.specialists[1].level == 3

    def test_game_state_with_incidents_round_trip(self):
        """Test round-trip with incidents."""
        original = GameState()
        
        incident = Incident(
            id="inc_001",
            incident_type="DDoS Attack",
            specialty_required="Network Security",
            difficulty=3,
            sla_seconds=300,
            base_reward=1000,
            xp_reward=150,
            client_id="client_001",
            status="pending"
        )
        
        original.specialists = []
        original.incidents = [incident]
        original.clients = []
        
        # Serialize
        state_dict = original.to_dict()
        
        # Deserialize
        restored = GameState.from_dict(state_dict)
        
        # Verify incident
        assert len(restored.incidents) == 1
        assert restored.incidents[0].id == "inc_001"
        assert restored.incidents[0].incident_type == "DDoS Attack"
        assert restored.incidents[0].difficulty == 3
        assert restored.incidents[0].status == "pending"

    def test_game_state_with_clients_round_trip(self):
        """Test round-trip with clients."""
        original = GameState()
        
        client = Client(
            id="client_001",
            name="Test Corp",
            industry="Technology",
            incident_rate_per_minute=0.5,
            sla_multiplier=1.0,
            reputation=75,
            contract_value=5000
        )
        
        original.specialists = []
        original.incidents = []
        original.clients = [client]
        
        # Serialize
        state_dict = original.to_dict()
        
        # Deserialize
        restored = GameState.from_dict(state_dict)
        
        # Verify client
        assert len(restored.clients) == 1
        assert restored.clients[0].id == "client_001"
        assert restored.clients[0].name == "Test Corp"
        assert restored.clients[0].reputation == 75

    def test_game_state_financial_data_round_trip(self):
        """Test round-trip with financial data."""
        original = GameState()
        original.specialists = []
        original.incidents = []
        original.clients = []
        
        original.current_money = 15000.50
        original.total_money_earned = 25000.75
        original.investments = {
            "stocks": 5000.0,
            "bonds": 3000.0
        }
        
        # Serialize
        state_dict = original.to_dict()
        
        # Deserialize
        restored = GameState.from_dict(state_dict)
        
        # Verify financial data
        assert restored.current_money == 15000.50
        assert restored.total_money_earned == 25000.75
        assert restored.investments == {"stocks": 5000.0, "bonds": 3000.0}

    def test_game_state_progression_data_round_trip(self):
        """Test round-trip with progression data."""
        original = GameState()
        original.specialists = []
        original.incidents = []
        original.clients = []
        
        original.prestige_points = 10
        original.prestige_upgrades = {"upgrade_1": 2, "upgrade_2": 1}
        original.total_prestiges = 3
        original.unlocked_achievements = ["ach_1", "ach_2", "ach_3"]
        original.achievement_progress = {"ach_4": 0.75, "ach_5": 0.3}
        
        # Serialize
        state_dict = original.to_dict()
        
        # Deserialize
        restored = GameState.from_dict(state_dict)
        
        # Verify progression data
        assert restored.prestige_points == 10
        assert restored.prestige_upgrades == {"upgrade_1": 2, "upgrade_2": 1}
        assert restored.total_prestiges == 3
        assert restored.unlocked_achievements == ["ach_1", "ach_2", "ach_3"]
        assert restored.achievement_progress == {"ach_4": 0.75, "ach_5": 0.3}

    def test_game_state_metrics_round_trip(self):
        """Test round-trip with game metrics."""
        original = GameState()
        original.specialists = []
        original.incidents = []
        original.clients = []
        
        original.metrics = GameMetrics(
            total_incidents_handled=50,
            total_incidents_failed=5,
            total_profit=10000.0,
            total_xp_awarded=5000,
            sla_compliance_rate=90.0,
            specialist_utilization_rate=75.5
        )
        
        # Serialize
        state_dict = original.to_dict()
        
        # Deserialize
        restored = GameState.from_dict(state_dict)
        
        # Verify metrics
        assert restored.metrics.total_incidents_handled == 50
        assert restored.metrics.total_incidents_failed == 5
        assert restored.metrics.total_profit == 10000.0
        assert restored.metrics.sla_compliance_rate == 90.0

    def test_game_state_game_time_round_trip(self):
        """Test round-trip with game timing data."""
        original = GameState()
        original.specialists = []
        original.incidents = []
        original.clients = []
        
        current_time = time.time()
        original.game_start_time = current_time - 1000
        original.current_time = current_time
        original.game_speed_multiplier = 2.0
        original.is_paused = True
        
        # Serialize
        state_dict = original.to_dict()
        
        # Deserialize
        restored = GameState.from_dict(state_dict)
        
        # Verify timing
        assert restored.game_start_time == original.game_start_time
        assert restored.current_time == original.current_time
        assert restored.game_speed_multiplier == 2.0
        assert restored.is_paused is True

    def test_game_state_complete_round_trip(self):
        """Test round-trip with full complex game state."""
        original = GameState()
        
        # Add specialists
        original.specialists = [
            Specialist(id=f"spec_{i}", name=f"Specialist {i}", 
                      specialty="Network Security", level=i+1, xp=i*100,
                      stats=SpecialistStats(speed=100.0, accuracy=85.0, experience_bonus=1.0))
            for i in range(3)
        ]
        
        # Add incidents
        original.incidents = [
            Incident(
                id=f"inc_{i}",
                incident_type="DDoS Attack",
                specialty_required="Network Security",
                difficulty=i+1,
                sla_seconds=300,
                base_reward=1000,
                xp_reward=100,
                client_id="client_001",
                status="pending"
            )
            for i in range(2)
        ]
        
        # Add clients
        original.clients = [
            Client(id=f"client_{i}", name=f"Client {i}", 
                  industry="Technology", reputation=70+i*5,
                  incident_rate_per_minute=0.5, sla_multiplier=1.0, contract_value=5000)
            for i in range(2)
        ]
        
        # Set various state
        original.current_money = 12345.67
        original.prestige_points = 5
        original.unlocked_achievements = ["ach_1", "ach_2"]
        original.metrics.total_incidents_handled = 100
        
        # Serialize
        state_dict = original.to_dict()
        
        # Verify serialized format
        assert "specialists" in state_dict
        assert "incidents" in state_dict
        assert "clients" in state_dict
        assert "current_money" in state_dict
        assert "metrics" in state_dict
        
        # Deserialize
        restored = GameState.from_dict(state_dict)
        
        # Verify everything
        assert len(restored.specialists) == 3
        assert len(restored.incidents) == 2
        assert len(restored.clients) == 2
        assert restored.current_money == 12345.67
        assert restored.prestige_points == 5
        assert len(restored.unlocked_achievements) == 2
        assert restored.metrics.total_incidents_handled == 100
        
        # Verify specific entities
        assert restored.specialists[0].name == "Specialist 0"
        assert restored.incidents[1].difficulty == 2
        assert restored.clients[1].reputation == 75

    def test_serialization_dict_structure(self):
        """Test that serialized dict has expected structure."""
        original = GameState()
        original.specialists = []
        original.incidents = []
        original.clients = []
        
        state_dict = original.to_dict()
        
        # Verify all expected keys are present
        expected_keys = [
            "specialists", "incidents", "clients",
            "game_start_time", "current_time", "game_speed_multiplier", "is_paused",
            "current_money", "total_money_earned", "investments",
            "prestige_points", "prestige_upgrades", "total_prestiges",
            "unlocked_achievements", "achievement_progress",
            "max_active_incidents", "max_specialists", "incident_generation_enabled",
            "metrics"
        ]
        
        for key in expected_keys:
            assert key in state_dict, f"Missing key: {key}"
        
        # Verify types
        assert isinstance(state_dict["specialists"], list)
        assert isinstance(state_dict["incidents"], list)
        assert isinstance(state_dict["clients"], list)
        assert isinstance(state_dict["current_money"], (int, float))
        assert isinstance(state_dict["metrics"], dict)
        assert isinstance(state_dict["is_paused"], bool)

    def test_serialization_handles_none_values(self):
        """Test that None values are handled properly."""
        original = GameState()
        original.specialists = []
        original.incidents = []
        original.clients = []
        original.investments = {}
        original.prestige_upgrades = {}
        
        # Serialize
        state_dict = original.to_dict()
        
        # Should not raise errors
        restored = GameState.from_dict(state_dict)
        
        assert restored.investments == {}
        assert restored.prestige_upgrades == {}

    def test_serialization_json_compatible(self):
        """Test that serialized state is JSON-compatible."""
        import json
        
        original = GameState()
        
        # Add some data
        original.specialists = [
            Specialist(id="spec_001", name="Test", specialty="Network Security", level=5, xp=1000,
                      stats=SpecialistStats(speed=100.0, accuracy=85.0, experience_bonus=1.0))
        ]
        original.specialists[0].assigned_incident_id = "inc_001"  # Set mutable state
        original.incidents = []
        original.clients = []
        
        # Serialize
        state_dict = original.to_dict()
        
        # Should be JSON serializable
        try:
            json_str = json.dumps(state_dict)
            assert len(json_str) > 0
            
            # Should be JSON deserializable
            parsed = json.loads(json_str)
            assert parsed["specialists"][0]["id"] == "spec_001"
            
        except (TypeError, ValueError) as e:
            pytest.fail(f"GameState serialization not JSON-compatible: {e}")
