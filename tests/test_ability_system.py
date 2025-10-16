"""Tests for Ability System."""

import pytest
import time
from src.core.ability_system import AbilitySystem
from src.models.specialist import Specialist, SpecialistStats
from src.models.specialist_ability import SpecialistAbility
from src.models.incident import Incident


class TestSpecialistAbility:
    """Test SpecialistAbility model."""
    
    def test_to_dict(self):
        """Test converting ability to dictionary."""
        ability = SpecialistAbility(
            id="test_ability",
            name="Test Ability",
            description="A test ability",
            ability_type="speed_burst",
            cooldown_seconds=120.0,
            duration_seconds=30.0,
            effect_magnitude=2.0,
            unlock_level=5,
            specialty="Any"
        )
        
        data = ability.to_dict()
        
        assert data["id"] == "test_ability"
        assert data["name"] == "Test Ability"
        assert data["ability_type"] == "speed_burst"
        assert data["cooldown_seconds"] == 120.0
        assert data["effect_magnitude"] == 2.0
    
    def test_from_dict(self):
        """Test creating ability from dictionary."""
        data = {
            "id": "test_ability",
            "name": "Test Ability",
            "description": "A test ability",
            "ability_type": "accuracy_boost",
            "cooldown_seconds": 180.0,
            "duration_seconds": 60.0,
            "effect_magnitude": 1.5,
            "unlock_level": 8,
            "specialty": "Network Security"
        }
        
        ability = SpecialistAbility.from_dict(data)
        
        assert ability.id == "test_ability"
        assert ability.ability_type == "accuracy_boost"
        assert ability.specialty == "Network Security"


class TestAbilitySystem:
    """Test AbilitySystem class."""
    
    @pytest.fixture
    def abilities_config(self):
        """Sample abilities configuration."""
        return {
            "abilities": [
                {
                    "id": "speed_burst",
                    "name": "Speed Burst",
                    "description": "Double resolution speed",
                    "ability_type": "speed_burst",
                    "cooldown_seconds": 120,
                    "duration_seconds": 30,
                    "effect_magnitude": 2.0,
                    "unlock_level": 5,
                    "specialty": "Any"
                },
                {
                    "id": "accuracy_boost",
                    "name": "Perfect Focus",
                    "description": "Boost accuracy",
                    "ability_type": "accuracy_boost",
                    "cooldown_seconds": 180,
                    "duration_seconds": 60,
                    "effect_magnitude": 1.5,
                    "unlock_level": 8,
                    "specialty": "Any"
                },
                {
                    "id": "network_specialist_ability",
                    "name": "Network Specialist Ability",
                    "description": "Network-only ability",
                    "ability_type": "speed_burst",
                    "cooldown_seconds": 100,
                    "duration_seconds": 20,
                    "effect_magnitude": 3.0,
                    "unlock_level": 7,
                    "specialty": "Network Security"
                }
            ]
        }
    
    @pytest.fixture
    def ability_system(self, abilities_config):
        """Create an ability system for testing."""
        return AbilitySystem(abilities_config)
    
    @pytest.fixture
    def test_specialist(self):
        """Create a test specialist."""
        specialist = Specialist(
            id="test_spec",
            name="Test Specialist",
            specialty="Network Security",
            level=10,
            xp=1000,
            stats=SpecialistStats(speed=50.0, accuracy=50.0, experience_bonus=1.0)
        )
        specialist.abilities = ["speed_burst", "accuracy_boost", "network_specialist_ability"]
        return specialist
    
    @pytest.fixture
    def test_incident(self):
        """Create a test incident."""
        return Incident(
            id="test_incident",
            incident_type="Test Incident",
            specialty_required="Network Security",
            difficulty=2,
            sla_seconds=300,
            base_reward=500,
            xp_reward=100,
            client_id="client_001"
        )
    
    def test_initialization(self, ability_system):
        """Test ability system initialization."""
        assert len(ability_system.abilities) == 3
        assert "speed_burst" in ability_system.abilities
        assert "accuracy_boost" in ability_system.abilities
    
    def test_activate_ability_success(self, ability_system, test_specialist):
        """Test successful ability activation."""
        result = ability_system.activate_ability(test_specialist, "speed_burst")
        
        assert result["success"] is True
        assert "Speed Burst" in result["message"]
        assert "effect_applied" in result
        assert test_specialist.ability_cooldowns["speed_burst"] == 120
    
    def test_activate_ability_not_found(self, ability_system, test_specialist):
        """Test activating non-existent ability."""
        result = ability_system.activate_ability(test_specialist, "nonexistent_ability")
        
        assert result["success"] is False
        assert "not found" in result["message"]
    
    def test_activate_ability_not_unlocked(self, ability_system, test_specialist):
        """Test activating an ability that's not unlocked."""
        test_specialist.abilities = []  # No abilities unlocked
        
        result = ability_system.activate_ability(test_specialist, "speed_burst")
        
        assert result["success"] is False
        assert "not unlocked" in result["message"]
    
    def test_activate_ability_on_cooldown(self, ability_system, test_specialist):
        """Test activating an ability that's on cooldown."""
        test_specialist.ability_cooldowns["speed_burst"] = 60.0
        
        result = ability_system.activate_ability(test_specialist, "speed_burst")
        
        assert result["success"] is False
        assert "cooldown" in result["message"]
    
    def test_activate_ability_wrong_specialty(self, ability_system, test_specialist):
        """Test activating a specialist-specific ability with wrong specialty."""
        test_specialist.specialty = "Malware Analysis"
        
        result = ability_system.activate_ability(test_specialist, "network_specialist_ability")
        
        assert result["success"] is False
        assert "specialty" in result["message"].lower()
    
    def test_update_cooldowns(self, ability_system, test_specialist):
        """Test cooldown updates."""
        test_specialist.ability_cooldowns = {
            "speed_burst": 10.0,
            "accuracy_boost": 5.0
        }
        
        ability_system.update_cooldowns(test_specialist, 3.0)
        
        assert test_specialist.ability_cooldowns["speed_burst"] == 7.0
        assert test_specialist.ability_cooldowns["accuracy_boost"] == 2.0
    
    def test_update_cooldowns_remove_finished(self, ability_system, test_specialist):
        """Test that finished cooldowns are removed."""
        test_specialist.ability_cooldowns = {
            "speed_burst": 2.0,
            "accuracy_boost": 10.0
        }
        
        ability_system.update_cooldowns(test_specialist, 3.0)
        
        assert "speed_burst" not in test_specialist.ability_cooldowns
        assert "accuracy_boost" in test_specialist.ability_cooldowns
    
    def test_get_available_abilities(self, ability_system, test_specialist):
        """Test getting available abilities."""
        test_specialist.ability_cooldowns = {
            "speed_burst": 10.0  # On cooldown
        }
        
        available = ability_system.get_available_abilities(test_specialist)
        
        assert "accuracy_boost" in available
        assert "network_specialist_ability" in available
        assert "speed_burst" not in available
    
    def test_apply_active_effects_speed(self, ability_system, test_specialist):
        """Test applying speed burst effect."""
        test_specialist.active_effects = [
            {
                "ability_id": "speed_burst",
                "ability_type": "speed_burst",
                "magnitude": 2.0,
                "duration": 30.0,
                "start_time": time.time(),
                "stat_affected": "speed"
            }
        ]
        
        modifiers = ability_system.apply_active_effects(test_specialist)
        
        assert modifiers["speed"] == 2.0
        assert modifiers["accuracy"] == 1.0
    
    def test_apply_active_effects_multiple(self, ability_system, test_specialist):
        """Test applying multiple active effects."""
        current_time = time.time()
        test_specialist.active_effects = [
            {
                "ability_id": "speed_burst",
                "ability_type": "speed_burst",
                "magnitude": 2.0,
                "duration": 30.0,
                "start_time": current_time,
                "stat_affected": "speed"
            },
            {
                "ability_id": "accuracy_boost",
                "ability_type": "accuracy_boost",
                "magnitude": 1.5,
                "duration": 60.0,
                "start_time": current_time,
                "stat_affected": "accuracy"
            }
        ]
        
        modifiers = ability_system.apply_active_effects(test_specialist)
        
        assert modifiers["speed"] == 2.0
        assert modifiers["accuracy"] == 1.5
    
    def test_update_active_effects_removes_expired(self, ability_system, test_specialist):
        """Test that expired effects are removed."""
        old_time = time.time() - 100  # 100 seconds ago
        test_specialist.active_effects = [
            {
                "ability_id": "speed_burst",
                "ability_type": "speed_burst",
                "magnitude": 2.0,
                "duration": 30.0,  # Expired
                "start_time": old_time,
                "stat_affected": "speed"
            },
            {
                "ability_id": "accuracy_boost",
                "ability_type": "accuracy_boost",
                "magnitude": 1.5,
                "duration": 120.0,  # Still active
                "start_time": time.time(),
                "stat_affected": "accuracy"
            }
        ]
        
        ability_system.update_active_effects(test_specialist, 1.0)
        
        assert len(test_specialist.active_effects) == 1
        assert test_specialist.active_effects[0]["ability_id"] == "accuracy_boost"
    
    def test_unlock_abilities_for_level(self, ability_system, test_specialist):
        """Test unlocking abilities when reaching a level."""
        test_specialist.level = 5
        test_specialist.abilities = []
        
        unlocked = ability_system.unlock_abilities_for_level(test_specialist, 5)
        
        assert "speed_burst" in unlocked
        assert "speed_burst" in test_specialist.abilities
    
    def test_unlock_abilities_specialty_specific(self, ability_system, test_specialist):
        """Test that specialty-specific abilities only unlock for correct specialty."""
        test_specialist.level = 7
        test_specialist.abilities = []
        
        unlocked = ability_system.unlock_abilities_for_level(test_specialist, 7)
        
        # Should unlock the network security ability since specialist has that specialty
        assert "network_specialist_ability" in unlocked
    
    def test_unlock_abilities_wrong_specialty(self, ability_system, test_specialist):
        """Test that specialty-specific abilities don't unlock for wrong specialty."""
        test_specialist.specialty = "Malware Analysis"
        test_specialist.level = 7
        test_specialist.abilities = []
        
        unlocked = ability_system.unlock_abilities_for_level(test_specialist, 7)
        
        # Should not unlock the network security ability
        assert "network_specialist_ability" not in unlocked
    
    def test_get_ability(self, ability_system):
        """Test getting an ability by ID."""
        ability = ability_system.get_ability("speed_burst")
        
        assert ability is not None
        assert ability.name == "Speed Burst"
        
        # Non-existent ability
        assert ability_system.get_ability("nonexistent") is None
    
    def test_ability_with_incident_target(self, ability_system, test_specialist, test_incident):
        """Test ability activation with incident target."""
        initial_sla = test_incident.sla_deadline
        
        # First unlock and add SLA extension ability
        test_specialist.abilities.append("sla_extension")
        ability_system.abilities["sla_extension"] = SpecialistAbility(
            id="sla_extension",
            name="Time Extension",
            description="Extend SLA",
            ability_type="sla_extension",
            cooldown_seconds=300,
            duration_seconds=0,
            effect_magnitude=1.5,
            unlock_level=10,
            specialty="Any"
        )
        
        result = ability_system.activate_ability(test_specialist, "sla_extension", test_incident)
        
        assert result["success"] is True
        # SLA should be extended
        assert test_incident.sla_deadline > initial_sla
