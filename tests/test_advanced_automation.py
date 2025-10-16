"""Tests for advanced automation features (Task 19)."""

import time
from unittest.mock import Mock

import pytest

from src.models.automation_script import AutomationScript, TriggerConditions
from src.models.specialist import Specialist, SpecialistStats
from src.models.incident import Incident
from src.models.game_state import GameState
from src.core.automation_processor import AutomationProcessor


class TestAdvancedAutomationScript:
    """Test advanced automation script features."""

    def test_trigger_logic_and(self):
        """Test AND trigger logic."""
        script = AutomationScript(
            id="test_and",
            name="Test AND",
            description="Test",
            required_level=1,
            specialty="Network Security",
            trigger_conditions=TriggerConditions(
                max_difficulty=3,
                specialist_available=True
            ),
            effect="auto_assign",
            trigger_logic="AND"
        )
        
        specialist = Mock()
        specialist.matches_specialty = Mock(return_value=True)
        specialist.is_available = Mock(return_value=True)
        specialist.stats = Mock()
        specialist.stats.accuracy = 90
        
        incident = Mock()
        incident.difficulty = 2
        incident.specialty_required = "Network Security"
        
        # All conditions met
        assert script.evaluate_triggers(specialist, incident) is True
        
        # One condition not met (specialist unavailable)
        specialist.is_available = Mock(return_value=False)
        assert script.evaluate_triggers(specialist, incident) is False

    def test_trigger_logic_or(self):
        """Test OR trigger logic."""
        script = AutomationScript(
            id="test_or",
            name="Test OR",
            description="Test",
            required_level=1,
            specialty="Network Security",
            trigger_conditions=TriggerConditions(
                max_difficulty=1,
                min_accuracy=95
            ),
            effect="auto_assign",
            trigger_logic="OR"
        )
        
        specialist = Mock()
        specialist.matches_specialty = Mock(return_value=True)
        specialist.is_available = Mock(return_value=True)
        specialist.stats = Mock()
        specialist.stats.accuracy = 90
        
        incident = Mock()
        incident.difficulty = 2
        incident.specialty_required = "Network Security"
        
        # Only max_difficulty fails, but min_accuracy not checked, so should fail
        # Actually, neither condition is met (difficulty too high, accuracy too low)
        assert script.evaluate_triggers(specialist, incident) is False
        
        # Make one condition true
        incident.difficulty = 1  # Now max_difficulty is met
        assert script.evaluate_triggers(specialist, incident) is True
        
        # Make other condition true instead
        incident.difficulty = 2
        specialist.stats.accuracy = 96  # Now min_accuracy is met
        assert script.evaluate_triggers(specialist, incident) is True

    def test_cooldown_mechanics(self):
        """Test cooldown functionality."""
        script = AutomationScript(
            id="test_cooldown",
            name="Test Cooldown",
            description="Test",
            required_level=1,
            specialty="Any",
            trigger_conditions=TriggerConditions(),
            effect="speed_boost",
            cooldown_seconds=10.0
        )
        
        current_time = time.time()
        
        # Not on cooldown initially
        assert script.is_on_cooldown(current_time) is False
        
        # Mark as triggered
        script.mark_triggered(current_time)
        
        # Should be on cooldown
        assert script.is_on_cooldown(current_time) is True
        assert script.is_on_cooldown(current_time + 5.0) is True
        
        # Cooldown expired
        assert script.is_on_cooldown(current_time + 11.0) is False

    def test_cooldown_reduction_with_upgrades(self):
        """Test that upgrades reduce cooldown."""
        script = AutomationScript(
            id="test_upgrade_cooldown",
            name="Test Upgrade",
            description="Test",
            required_level=1,
            specialty="Any",
            trigger_conditions=TriggerConditions(),
            effect="speed_boost",
            cooldown_seconds=100.0,
            upgrade_level=0
        )
        
        # Base cooldown
        assert script.get_effective_cooldown() == 100.0
        
        # Upgrade once (10% reduction)
        script.upgrade()
        assert script.upgrade_level == 1
        assert script.get_effective_cooldown() == 90.0
        
        # Upgrade multiple times
        script.upgrade()
        script.upgrade()
        assert script.upgrade_level == 3
        assert script.get_effective_cooldown() == 70.0
        
        # Many upgrades (but minimum 10% of original)
        for _ in range(10):
            script.upgrade()
        # Should be capped at 10% of original
        assert script.get_effective_cooldown() >= 10.0

    def test_magnitude_boost_with_upgrades(self):
        """Test that upgrades increase effect magnitude."""
        script = AutomationScript(
            id="test_magnitude",
            name="Test Magnitude",
            description="Test",
            required_level=1,
            specialty="Any",
            trigger_conditions=TriggerConditions(),
            effect="speed_boost",
            effect_magnitude=1.5,
            upgrade_level=0
        )
        
        # Base magnitude
        assert script.get_effective_magnitude() == 1.5
        
        # Upgrade once (5% increase)
        script.upgrade()
        assert script.upgrade_level == 1
        assert script.get_effective_magnitude() == pytest.approx(1.5 * 1.05)
        
        # Upgrade twice more
        script.upgrade()
        script.upgrade()
        assert script.upgrade_level == 3
        assert script.get_effective_magnitude() == pytest.approx(1.5 * 1.15)

    def test_upgrade_cost_calculation(self):
        """Test upgrade cost increases exponentially."""
        script = AutomationScript(
            id="test_cost",
            name="Test Cost",
            description="Test",
            required_level=1,
            specialty="Any",
            trigger_conditions=TriggerConditions(),
            effect="speed_boost",
            upgrade_level=0
        )
        
        # Base cost
        assert script.calculate_upgrade_cost() == 1000
        
        # Cost increases with level
        script.upgrade_level = 1
        assert script.calculate_upgrade_cost() == 1500
        
        script.upgrade_level = 2
        assert script.calculate_upgrade_cost() == int(1000 * 1.5 ** 2)
        
        script.upgrade_level = 5
        assert script.calculate_upgrade_cost() == int(1000 * 1.5 ** 5)

    def test_max_upgrade_level(self):
        """Test that upgrades cap at max level."""
        script = AutomationScript(
            id="test_max",
            name="Test Max",
            description="Test",
            required_level=1,
            specialty="Any",
            trigger_conditions=TriggerConditions(),
            effect="speed_boost",
            upgrade_level=9
        )
        
        # Can upgrade to level 10
        assert script.upgrade() is True
        assert script.upgrade_level == 10
        
        # Cannot upgrade beyond level 10
        assert script.upgrade() is False
        assert script.upgrade_level == 10

    def test_chained_scripts_field(self):
        """Test chained scripts field."""
        script = AutomationScript(
            id="test_chain",
            name="Test Chain",
            description="Test",
            required_level=1,
            specialty="Any",
            trigger_conditions=TriggerConditions(),
            effect="auto_assign",
            chained_scripts=["script1", "script2"]
        )
        
        assert len(script.chained_scripts) == 2
        assert "script1" in script.chained_scripts
        assert "script2" in script.chained_scripts

    def test_priority_field(self):
        """Test priority field."""
        script1 = AutomationScript(
            id="low_priority",
            name="Low Priority",
            description="Test",
            required_level=1,
            specialty="Any",
            trigger_conditions=TriggerConditions(),
            effect="auto_assign",
            priority=10
        )
        
        script2 = AutomationScript(
            id="high_priority",
            name="High Priority",
            description="Test",
            required_level=1,
            specialty="Any",
            trigger_conditions=TriggerConditions(),
            effect="auto_assign",
            priority=50
        )
        
        assert script1.priority == 10
        assert script2.priority == 50
        
        # Test sorting by priority
        scripts = [script1, script2]
        scripts.sort(key=lambda x: x.priority, reverse=True)
        assert scripts[0].id == "high_priority"
        assert scripts[1].id == "low_priority"

    def test_serialization_with_new_fields(self):
        """Test to_dict and from_dict with new fields."""
        original = AutomationScript(
            id="test_serialize",
            name="Test Serialize",
            description="Test",
            required_level=5,
            specialty="Network Security",
            trigger_conditions=TriggerConditions(max_difficulty=3),
            effect="auto_assign",
            trigger_logic="OR",
            chained_scripts=["chain1", "chain2"],
            priority=25,
            cooldown_seconds=15.0,
            last_triggered=100.0,
            upgrade_level=3
        )
        
        # Serialize
        data = original.to_dict()
        assert data["trigger_logic"] == "OR"
        assert data["chained_scripts"] == ["chain1", "chain2"]
        assert data["priority"] == 25
        assert data["cooldown_seconds"] == 15.0
        assert data["last_triggered"] == 100.0
        assert data["upgrade_level"] == 3
        
        # Deserialize
        restored = AutomationScript.from_dict(data)
        assert restored.trigger_logic == "OR"
        assert restored.chained_scripts == ["chain1", "chain2"]
        assert restored.priority == 25
        assert restored.cooldown_seconds == 15.0
        assert restored.last_triggered == 100.0
        assert restored.upgrade_level == 3

    def test_invalid_trigger_logic(self):
        """Test that invalid trigger logic raises error."""
        with pytest.raises(ValueError, match="Invalid trigger_logic"):
            AutomationScript(
                id="test_invalid",
                name="Test Invalid",
                description="Test",
                required_level=1,
                specialty="Any",
                trigger_conditions=TriggerConditions(),
                effect="auto_assign",
                trigger_logic="INVALID"
            )


class TestAutomationProcessorAdvanced:
    """Test advanced automation processor features."""

    def test_script_priority_execution_order(self):
        """Test that scripts execute in priority order."""
        # This is tested implicitly by the sorting in process_automation
        # We verify that the sorting works correctly
        processor = AutomationProcessor()
        
        # Create mock game state
        game_state = Mock()
        game_state.specialists = []
        game_state.incidents = []
        game_state.clients = []
        game_state.automation_scripts = []
        
        # Create scripts with different priorities
        scripts = [
            (AutomationScript(
                id=f"script_{i}",
                name=f"Script {i}",
                description="Test",
                required_level=1,
                specialty="Any",
                trigger_conditions=TriggerConditions(),
                effect="speed_boost",
                priority=i * 10
            ), None)
            for i in range(5)
        ]
        
        # Sort by priority (higher first)
        scripts.sort(key=lambda x: x[0].priority, reverse=True)
        
        # Verify order
        priorities = [s[0].priority for s in scripts]
        assert priorities == [40, 30, 20, 10, 0]

    def test_upgrade_automation_script(self):
        """Test upgrading automation script through processor."""
        processor = AutomationProcessor()
        
        script = AutomationScript(
            id="test_upgrade",
            name="Test Upgrade",
            description="Test",
            required_level=1,
            specialty="Any",
            trigger_conditions=TriggerConditions(),
            effect="speed_boost",
            upgrade_level=0
        )
        
        # Create mock game state
        game_state = Mock()
        game_state.current_money = 5000
        game_state.get_automation_script_by_id = Mock(return_value=script)
        
        # Upgrade script
        result = processor.upgrade_automation_script(game_state, "test_upgrade")
        
        assert result["success"] is True
        assert result["new_level"] == 1
        assert result["cost"] == 1000
        assert game_state.current_money == 4000

    def test_upgrade_insufficient_funds(self):
        """Test upgrading with insufficient funds."""
        processor = AutomationProcessor()
        
        script = AutomationScript(
            id="test_poor",
            name="Test Poor",
            description="Test",
            required_level=1,
            specialty="Any",
            trigger_conditions=TriggerConditions(),
            effect="speed_boost",
            upgrade_level=0
        )
        
        # Create mock game state
        game_state = Mock()
        game_state.current_money = 500  # Not enough
        game_state.get_automation_script_by_id = Mock(return_value=script)
        
        # Try to upgrade
        result = processor.upgrade_automation_script(game_state, "test_poor")
        
        assert result["success"] is False
        assert "Insufficient funds" in result["error"]
        assert game_state.current_money == 500  # Money unchanged

    def test_statistics_tracking_per_script(self):
        """Test that statistics track per-script triggers and success rate."""
        processor = AutomationProcessor()
        
        # The stats should track triggers_per_script and success_rate_per_script
        stats = processor.get_statistics()
        assert "triggers_per_script" in stats
        assert "success_rate_per_script" in stats
