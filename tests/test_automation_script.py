"""Tests for AutomationScript model."""

import pytest
from unittest.mock import Mock
import time

from src.models.automation_script import AutomationScript, TriggerConditions, AutomationEffect
from src.models.specialist import Specialist, SpecialistStats
from src.models.incident import Incident


class TestTriggerConditions:
    """Test TriggerConditions class."""

    def test_to_dict(self):
        """Test converting trigger conditions to dictionary."""
        conditions = TriggerConditions(
            max_difficulty=2,
            specialty_match=True,
            specialist_available=True,
            min_accuracy=85.0
        )
        expected = {
            "max_difficulty": 2,
            "specialty_match": True,
            "specialist_available": True,
            "min_accuracy": 85.0
        }
        assert conditions.to_dict() == expected

    def test_from_dict(self):
        """Test creating trigger conditions from dictionary."""
        data = {
            "max_difficulty": 3,
            "specialty_match": False,
            "specialist_available": True,
            "min_accuracy": 90.0
        }
        conditions = TriggerConditions.from_dict(data)
        assert conditions.max_difficulty == 3
        assert conditions.specialty_match is False
        assert conditions.specialist_available is True
        assert conditions.min_accuracy == 90.0

    def test_from_dict_partial(self):
        """Test creating trigger conditions from partial dictionary."""
        data = {"max_difficulty": 2}
        conditions = TriggerConditions.from_dict(data)
        assert conditions.max_difficulty == 2
        assert conditions.specialty_match is None
        assert conditions.specialist_available is None
        assert conditions.min_accuracy is None


class TestAutomationScript:
    """Test AutomationScript class."""

    @pytest.fixture
    def sample_script_data(self):
        """Sample automation script data for testing."""
        return {
            "id": "auto_assign_network_low",
            "name": "Auto-Assign Network (Low Priority)",
            "description": "Automatically assigns low-difficulty network security incidents",
            "required_level": 3,
            "specialty": "Network Security",
            "trigger_conditions": {
                "max_difficulty": 2,
                "specialty_match": True,
                "specialist_available": True
            },
            "effect": "auto_assign",
            "effect_magnitude": 1.0
        }

    @pytest.fixture
    def sample_specialist(self):
        """Sample specialist for testing."""
        return Specialist(
            id="spec_001",
            name="Alice Chen",
            specialty="Network Security",
            level=5,
            xp=1000,
            stats=SpecialistStats(speed=85.0, accuracy=90.0, experience_bonus=1.2),
            automation_scripts=["auto_assign_network_low"]
        )

    @pytest.fixture
    def sample_incident(self):
        """Sample incident for testing."""
        return Incident(
            id="inc_001",
            incident_type="DDoS Attack",
            specialty_required="Network Security",
            difficulty=2,
            sla_seconds=300,
            base_reward=500,
            xp_reward=100,
            client_id="client_001"
        )

    def test_initialization_from_dict(self, sample_script_data):
        """Test creating automation script from dictionary."""
        script = AutomationScript.from_dict(sample_script_data)

        assert script.id == "auto_assign_network_low"
        assert script.name == "Auto-Assign Network (Low Priority)"
        assert script.required_level == 3
        assert script.specialty == "Network Security"
        assert script.effect == "auto_assign"
        assert script.effect_magnitude == 1.0
        assert isinstance(script.trigger_conditions, TriggerConditions)

    def test_initialization_validation(self):
        """Test that invalid effects raise ValueError."""
        data = {
            "id": "test_script",
            "name": "Test Script",
            "description": "Test description",
            "required_level": 1,
            "specialty": "Network Security",
            "trigger_conditions": {},
            "effect": "invalid_effect"
        }

        with pytest.raises(ValueError, match="Unsupported automation effect"):
            AutomationScript.from_dict(data)

    def test_evaluate_triggers_all_conditions_met(self, sample_script_data, sample_specialist, sample_incident):
        """Test trigger evaluation when all conditions are met."""
        script = AutomationScript.from_dict(sample_script_data)

        # Ensure specialist is available
        sample_specialist.status = "available"

        assert script.evaluate_triggers(sample_specialist, sample_incident) is True

    def test_evaluate_triggers_difficulty_too_high(self, sample_script_data, sample_specialist, sample_incident):
        """Test trigger evaluation when incident difficulty exceeds max_difficulty."""
        script = AutomationScript.from_dict(sample_script_data)
        sample_incident.difficulty = 3  # Higher than max_difficulty of 2

        assert script.evaluate_triggers(sample_specialist, sample_incident) is False

    def test_evaluate_triggers_specialty_mismatch(self, sample_script_data, sample_specialist, sample_incident):
        """Test trigger evaluation when specialty doesn't match."""
        script = AutomationScript.from_dict(sample_script_data)
        sample_incident.specialty_required = "Malware Analysis"  # Different from specialist's specialty

        assert script.evaluate_triggers(sample_specialist, sample_incident) is False

    def test_evaluate_triggers_specialist_not_available(self, sample_script_data, sample_specialist, sample_incident):
        """Test trigger evaluation when specialist is not available."""
        script = AutomationScript.from_dict(sample_script_data)
        sample_specialist.status = "busy"

        assert script.evaluate_triggers(sample_specialist, sample_incident) is False

    def test_evaluate_triggers_min_accuracy_not_met(self, sample_script_data, sample_specialist, sample_incident):
        """Test trigger evaluation when specialist accuracy is below minimum."""
        # Create script with min_accuracy requirement
        data = sample_script_data.copy()
        data["trigger_conditions"]["min_accuracy"] = 95.0
        script = AutomationScript.from_dict(data)

        # Specialist has 90% accuracy, below required 95%
        assert script.evaluate_triggers(sample_specialist, sample_incident) is False

    def test_evaluate_triggers_with_string_difficulty(self, sample_script_data, sample_specialist):
        """Ensure evaluate_triggers handles incident difficulty provided as a string."""
        # Create script that should allow up to difficulty 3
        data = sample_script_data.copy()
        data["trigger_conditions"]["max_difficulty"] = 3
        script = AutomationScript.from_dict(data)

        # Incident with difficulty as string (simulating bad JSON input)
        inc = Incident(
            id="inc_str",
            incident_type="Test",
            specialty_required="Network Security",
            difficulty="2",
            sla_seconds=300,
            base_reward=100,
            xp_reward=10,
            client_id="client_001"
        )

        # Should not raise and should return True because difficulty 2 <= max_difficulty 3
        assert script.evaluate_triggers(sample_specialist, inc) is True

    def test_apply_effect_auto_assign_success(self, sample_script_data, sample_specialist, sample_incident):
        """Test applying auto_assign effect successfully."""
        script = AutomationScript.from_dict(sample_script_data)

        result = script.apply_effect(sample_specialist, sample_incident)

        assert result["success"] is True
        assert result["effect_type"] == "auto_assign"
        assert result["details"]["assigned_incident"] == "inc_001"
        assert result["details"]["assigned_specialist"] == "spec_001"
        assert sample_incident.status == "assigned"
        assert sample_incident.assigned_specialist_id == "spec_001"
        assert sample_specialist.status == "busy"

    def test_apply_effect_auto_assign_specialist_busy(self, sample_script_data, sample_specialist, sample_incident):
        """Test applying auto_assign effect when specialist is busy."""
        script = AutomationScript.from_dict(sample_script_data)
        sample_specialist.status = "busy"

        result = script.apply_effect(sample_specialist, sample_incident)

        assert result["success"] is False
        assert "error" in result["details"]
        assert sample_incident.status == "pending"  # Unchanged

    def test_apply_effect_speed_boost(self):
        """Test applying speed_boost effect."""
        data = {
            "id": "speed_boost_test",
            "name": "Speed Boost Test",
            "description": "Test speed boost",
            "required_level": 8,
            "specialty": "Network Security",
            "trigger_conditions": {},
            "effect": "speed_boost",
            "effect_magnitude": 1.25
        }
        script = AutomationScript.from_dict(data)

        specialist = Specialist(
            id="spec_001",
            name="Test Specialist",
            specialty="Network Security",
            level=10,
            xp=1000,
            stats=SpecialistStats(speed=80.0, accuracy=90.0, experience_bonus=1.0)
        )

        result = script.apply_effect(specialist)

        assert result["success"] is True
        assert result["effect_type"] == "speed_boost"
        assert result["details"]["original_speed"] == 80.0
        assert result["details"]["new_speed"] == 100.0  # 80 * 1.25
        assert specialist.stats.speed == 100.0

    def test_apply_effect_accuracy_boost(self):
        """Test applying accuracy_boost effect."""
        data = {
            "id": "accuracy_boost_test",
            "name": "Accuracy Boost Test",
            "description": "Test accuracy boost",
            "required_level": 10,
            "specialty": "Digital Forensics",
            "trigger_conditions": {},
            "effect": "accuracy_boost",
            "effect_magnitude": 1.15
        }
        script = AutomationScript.from_dict(data)

        specialist = Specialist(
            id="spec_001",
            name="Test Specialist",
            specialty="Digital Forensics",
            level=12,
            xp=1000,
            stats=SpecialistStats(speed=80.0, accuracy=85.0, experience_bonus=1.0)
        )

        result = script.apply_effect(specialist)

        assert result["success"] is True
        assert result["effect_type"] == "accuracy_boost"
        assert result["details"]["original_accuracy"] == 85.0
        assert abs(result["details"]["new_accuracy"] - 97.75) < 0.01  # 85 * 1.15, capped at 100
        assert abs(specialist.stats.accuracy - 97.75) < 0.01

    def test_apply_effect_xp_boost(self):
        """Test applying xp_boost effect."""
        data = {
            "id": "xp_boost_test",
            "name": "XP Boost Test",
            "description": "Test XP boost",
            "required_level": 12,
            "specialty": "Any",
            "trigger_conditions": {},
            "effect": "xp_boost",
            "effect_magnitude": 1.2
        }
        script = AutomationScript.from_dict(data)

        specialist = Specialist(
            id="spec_001",
            name="Test Specialist",
            specialty="Network Security",
            level=15,
            xp=1000,
            stats=SpecialistStats(speed=80.0, accuracy=85.0, experience_bonus=1.0)
        )

        result = script.apply_effect(specialist)

        assert result["success"] is True
        assert result["effect_type"] == "xp_boost"
        assert result["details"]["original_xp_bonus"] == 1.0
        assert result["details"]["new_xp_bonus"] == 1.2
        assert specialist.stats.experience_bonus == 1.2

    def test_can_be_used_by_level_too_low(self, sample_script_data):
        """Test can_be_used_by when specialist level is too low."""
        script = AutomationScript.from_dict(sample_script_data)

        specialist = Specialist(
            id="spec_001",
            name="Test Specialist",
            specialty="Network Security",
            level=2,  # Below required level 3
            xp=100,
            stats=SpecialistStats(speed=80.0, accuracy=85.0, experience_bonus=1.0),
            automation_scripts=["auto_assign_network_low"]
        )

        assert script.can_be_used_by(specialist) is False

    def test_can_be_used_by_specialty_mismatch(self, sample_script_data):
        """Test can_be_used_by when specialty doesn't match."""
        script = AutomationScript.from_dict(sample_script_data)

        specialist = Specialist(
            id="spec_001",
            name="Test Specialist",
            specialty="Malware Analysis",  # Different from required "Network Security"
            level=5,
            xp=1000,
            stats=SpecialistStats(speed=80.0, accuracy=85.0, experience_bonus=1.0),
            automation_scripts=["auto_assign_network_low"]
        )

        assert script.can_be_used_by(specialist) is False

    def test_can_be_used_by_not_unlocked(self, sample_script_data):
        """Test can_be_used_by when script is not unlocked."""
        script = AutomationScript.from_dict(sample_script_data)

        specialist = Specialist(
            id="spec_001",
            name="Test Specialist",
            specialty="Network Security",
            level=5,
            xp=1000,
            stats=SpecialistStats(speed=80.0, accuracy=85.0, experience_bonus=1.0),
            automation_scripts=[]  # Script not unlocked
        )

        assert script.can_be_used_by(specialist) is False

    def test_can_be_used_by_success(self, sample_script_data):
        """Test can_be_used_by when all requirements are met."""
        script = AutomationScript.from_dict(sample_script_data)

        specialist = Specialist(
            id="spec_001",
            name="Test Specialist",
            specialty="Network Security",
            level=5,
            xp=1000,
            stats=SpecialistStats(speed=80.0, accuracy=85.0, experience_bonus=1.0),
            automation_scripts=["auto_assign_network_low"]
        )

        assert script.can_be_used_by(specialist) is True

    def test_to_dict(self, sample_script_data):
        """Test converting automation script to dictionary."""
        script = AutomationScript.from_dict(sample_script_data)
        result = script.to_dict()

        assert result["id"] == "auto_assign_network_low"
        assert result["name"] == "Auto-Assign Network (Low Priority)"
        assert result["required_level"] == 3
        assert result["specialty"] == "Network Security"
        assert result["effect"] == "auto_assign"
        assert result["effect_magnitude"] == 1.0
        assert isinstance(result["trigger_conditions"], dict)

    def test_repr(self, sample_script_data):
        """Test string representation of automation script."""
        script = AutomationScript.from_dict(sample_script_data)
        repr_str = repr(script)

        assert "AutomationScript" in repr_str
        assert "auto_assign_network_low" in repr_str
        assert "auto_assign" in repr_str
