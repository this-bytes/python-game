"""Tests for Progression System."""

import pytest
from src.core.progression_system import ProgressionSystem
from src.models.specialist import Specialist, SpecialistStats


class TestProgressionSystem:
    """Test ProgressionSystem class."""
    
    @pytest.fixture
    def progression_config(self):
        """Sample progression configuration."""
        return {
            "xp_curve": {
                "base_xp": 100,
                "exponent": 1.5,
                "level_cap": 50
            },
            "level_stat_increases": {
                "speed": 2,
                "accuracy": 1,
                "xp_bonus": 0.05
            },
            "skill_points_per_level": 1
        }
    
    @pytest.fixture
    def progression_system(self, progression_config):
        """Create a progression system for testing."""
        return ProgressionSystem(progression_config)
    
    @pytest.fixture
    def test_specialist(self):
        """Create a test specialist."""
        return Specialist(
            id="test_spec",
            name="Test Specialist",
            specialty="Network Security",
            level=1,
            xp=0,
            stats=SpecialistStats(speed=50.0, accuracy=50.0, experience_bonus=1.0)
        )
    
    def test_initialization(self, progression_system):
        """Test progression system initialization."""
        assert progression_system.base_xp == 100
        assert progression_system.exponent == 1.5
        assert progression_system.level_cap == 50
        assert progression_system.skill_points_per_level == 1
    
    def test_calculate_xp_for_level_1(self, progression_system):
        """Test XP calculation for level 1."""
        xp = progression_system.calculate_xp_for_level(1)
        assert xp == 0
    
    def test_calculate_xp_for_level_2(self, progression_system):
        """Test XP calculation for level 2."""
        xp = progression_system.calculate_xp_for_level(2)
        assert xp == 100  # base_xp * (1 ** 1.5)
    
    def test_calculate_xp_for_level_3(self, progression_system):
        """Test XP calculation for level 3."""
        xp = progression_system.calculate_xp_for_level(3)
        # Level 2: 100, Level 3: 100 + 282 = 382
        # But the formula is cumulative: base_xp * (1**1.5) + base_xp * (2**1.5)
        assert xp == 100 + int(100 * (2 ** 1.5))  # 100 + 282 = 382
    
    def test_calculate_level_from_xp_level_1(self, progression_system):
        """Test level calculation from XP - level 1."""
        level = progression_system.calculate_level_from_xp(0)
        assert level == 1
    
    def test_calculate_level_from_xp_level_2(self, progression_system):
        """Test level calculation from XP - level 2."""
        level = progression_system.calculate_level_from_xp(100)
        assert level == 2
    
    def test_calculate_level_from_xp_level_3(self, progression_system):
        """Test level calculation from XP - level 3."""
        xp_for_level_3 = progression_system.calculate_xp_for_level(3)
        level = progression_system.calculate_level_from_xp(xp_for_level_3)
        assert level == 3
    
    def test_calculate_level_from_xp_between_levels(self, progression_system):
        """Test level calculation when XP is between levels."""
        level = progression_system.calculate_level_from_xp(200)
        # 200 XP is between level 2 (100) and level 3 (382)
        assert level == 2
    
    def test_get_stat_increases_for_level(self, progression_system):
        """Test getting stat increases for a level."""
        stat_increases = progression_system.get_stat_increases_for_level(5)
        assert stat_increases["speed"] == 2
        assert stat_increases["accuracy"] == 1
        assert stat_increases["xp_bonus"] == 0.05
    
    def test_process_level_up(self, progression_system, test_specialist):
        """Test processing level up."""
        test_specialist.level = 2
        initial_speed = test_specialist.stats.speed
        initial_accuracy = test_specialist.stats.accuracy
        initial_xp_bonus = test_specialist.stats.experience_bonus
        initial_skill_points = test_specialist.skill_points
        
        rewards = progression_system.process_level_up(test_specialist)
        
        # Check stat increases
        assert test_specialist.stats.speed == initial_speed + 2
        assert test_specialist.stats.accuracy == initial_accuracy + 1
        assert test_specialist.stats.experience_bonus == initial_xp_bonus + 0.05
        
        # Check skill points awarded
        assert test_specialist.skill_points == initial_skill_points + 1
        
        # Check rewards dictionary
        assert rewards["new_level"] == 2
        assert rewards["stat_increases"]["speed"] == 2
        assert rewards["skill_points_awarded"] == 1
    
    def test_process_level_up_accuracy_cap(self, progression_system, test_specialist):
        """Test that accuracy is capped at 100."""
        test_specialist.stats.accuracy = 99.5
        test_specialist.level = 2
        
        progression_system.process_level_up(test_specialist)
        
        # Accuracy should be capped at 100
        assert test_specialist.stats.accuracy == 100.0


class TestSpecialistProgression:
    """Test specialist progression methods."""
    
    @pytest.fixture
    def test_specialist(self):
        """Create a test specialist."""
        return Specialist(
            id="test_spec",
            name="Test Specialist",
            specialty="Network Security",
            level=1,
            xp=0,
            stats=SpecialistStats(speed=50.0, accuracy=50.0, experience_bonus=1.0)
        )
    
    def test_gain_xp_applies_bonus(self, test_specialist):
        """Test that gain_xp applies experience bonus."""
        test_specialist.stats.experience_bonus = 1.5
        test_specialist.gain_xp(100)
        
        # Should gain 100 * 1.5 = 150 XP
        assert test_specialist.xp == 150
    
    def test_gain_xp_triggers_level_up(self, test_specialist):
        """Test that gaining XP can trigger level up."""
        test_specialist.xp = 90
        leveled_up = test_specialist.gain_xp(10)
        
        # Should reach 100 XP and level up to 2
        assert leveled_up is True
        assert test_specialist.level == 2
    
    def test_allocate_skill_point_speed(self, test_specialist):
        """Test allocating skill point to speed."""
        test_specialist.skill_points = 1
        initial_speed = test_specialist.stats.speed
        
        success = test_specialist.allocate_skill_point("speed")
        
        assert success is True
        assert test_specialist.stats.speed == initial_speed + 5.0
        assert test_specialist.skill_points == 0
    
    def test_allocate_skill_point_accuracy(self, test_specialist):
        """Test allocating skill point to accuracy."""
        test_specialist.skill_points = 1
        initial_accuracy = test_specialist.stats.accuracy
        
        success = test_specialist.allocate_skill_point("accuracy")
        
        assert success is True
        assert test_specialist.stats.accuracy == initial_accuracy + 2.0
        assert test_specialist.skill_points == 0
    
    def test_allocate_skill_point_xp_bonus(self, test_specialist):
        """Test allocating skill point to experience bonus."""
        test_specialist.skill_points = 1
        initial_xp_bonus = test_specialist.stats.experience_bonus
        
        success = test_specialist.allocate_skill_point("experience_bonus")
        
        assert success is True
        assert test_specialist.stats.experience_bonus == initial_xp_bonus + 0.1
        assert test_specialist.skill_points == 0
    
    def test_allocate_skill_point_no_points(self, test_specialist):
        """Test that allocation fails when no skill points."""
        test_specialist.skill_points = 0
        
        success = test_specialist.allocate_skill_point("speed")
        
        assert success is False
    
    def test_allocate_skill_point_invalid_stat(self, test_specialist):
        """Test that allocation fails for invalid stat."""
        test_specialist.skill_points = 1
        
        success = test_specialist.allocate_skill_point("invalid_stat")
        
        assert success is False
        assert test_specialist.skill_points == 1  # Points not consumed
    
    def test_allocate_skill_point_accuracy_capped(self, test_specialist):
        """Test that accuracy is capped at 100."""
        test_specialist.skill_points = 1
        test_specialist.stats.accuracy = 99.0
        
        test_specialist.allocate_skill_point("accuracy")
        
        assert test_specialist.stats.accuracy == 100.0
    
    def test_serialization_with_new_fields(self, test_specialist):
        """Test that new fields are properly serialized."""
        test_specialist.skill_points = 5
        test_specialist.abilities = ["ability_1", "ability_2"]
        test_specialist.ability_cooldowns = {"ability_1": 30.0}
        test_specialist.active_effects = [{"type": "speed_boost", "duration": 10.0}]
        test_specialist.equipped_items = {"tool": "laptop_001"}
        test_specialist.inventory = ["item_001", "item_002"]
        
        data = test_specialist.to_dict()
        
        assert data["skill_points"] == 5
        assert data["abilities"] == ["ability_1", "ability_2"]
        assert data["ability_cooldowns"]["ability_1"] == 30.0
        assert len(data["active_effects"]) == 1
        assert data["equipped_items"]["tool"] == "laptop_001"
        assert len(data["inventory"]) == 2
    
    def test_deserialization_with_new_fields(self):
        """Test that specialists can be created from dict with new fields."""
        data = {
            "id": "test_spec",
            "name": "Test Specialist",
            "specialty": "Network Security",
            "level": 5,
            "xp": 1000,
            "stats": {"speed": 60.0, "accuracy": 70.0, "experience_bonus": 1.3},
            "skill_points": 3,
            "abilities": ["ability_1"],
            "ability_cooldowns": {"ability_1": 10.0},
            "active_effects": [],
            "equipped_items": {"tool": "laptop_001"},
            "inventory": ["item_001"]
        }
        
        specialist = Specialist.from_dict(data)
        
        assert specialist.skill_points == 3
        assert specialist.abilities == ["ability_1"]
        assert specialist.ability_cooldowns["ability_1"] == 10.0
        assert specialist.equipped_items["tool"] == "laptop_001"
        assert specialist.inventory == ["item_001"]
