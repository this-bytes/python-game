"""Tests for Equipment System."""

import pytest
from src.core.equipment_system import EquipmentSystem
from src.models.equipment import Equipment
from src.models.specialist import Specialist, SpecialistStats


class TestEquipment:
    """Test Equipment model."""
    
    def test_to_dict(self):
        """Test converting equipment to dictionary."""
        equipment = Equipment(
            id="test_equipment",
            name="Test Equipment",
            description="A test item",
            equipment_type="tool",
            rarity="rare",
            stat_bonuses={"speed": 10, "accuracy": 5},
            unlock_level=5,
            cost=2000
        )
        
        data = equipment.to_dict()
        
        assert data["id"] == "test_equipment"
        assert data["name"] == "Test Equipment"
        assert data["equipment_type"] == "tool"
        assert data["rarity"] == "rare"
        assert data["stat_bonuses"]["speed"] == 10
    
    def test_from_dict(self):
        """Test creating equipment from dictionary."""
        data = {
            "id": "test_equipment",
            "name": "Test Equipment",
            "description": "A test item",
            "equipment_type": "badge",
            "rarity": "epic",
            "stat_bonuses": {"accuracy": 15, "xp_bonus": 0.1},
            "unlock_level": 10,
            "cost": 5000
        }
        
        equipment = Equipment.from_dict(data)
        
        assert equipment.id == "test_equipment"
        assert equipment.equipment_type == "badge"
        assert equipment.rarity == "epic"
        assert equipment.stat_bonuses["accuracy"] == 15


class TestEquipmentSystem:
    """Test EquipmentSystem class."""
    
    @pytest.fixture
    def equipment_config(self):
        """Sample equipment configuration."""
        return {
            "equipment": [
                {
                    "id": "basic_laptop",
                    "name": "Basic Laptop",
                    "description": "Standard laptop",
                    "equipment_type": "tool",
                    "rarity": "common",
                    "stat_bonuses": {"speed": 5, "accuracy": 2},
                    "unlock_level": 1,
                    "cost": 500
                },
                {
                    "id": "advanced_workstation",
                    "name": "Advanced Workstation",
                    "description": "High-end workstation",
                    "equipment_type": "tool",
                    "rarity": "rare",
                    "stat_bonuses": {"speed": 10, "accuracy": 5},
                    "unlock_level": 5,
                    "cost": 2000
                },
                {
                    "id": "gold_badge",
                    "name": "Gold Badge",
                    "description": "Premium badge",
                    "equipment_type": "badge",
                    "rarity": "epic",
                    "stat_bonuses": {"accuracy": 15, "xp_bonus": 0.1},
                    "unlock_level": 10,
                    "cost": 5000
                },
                {
                    "id": "neural_interface",
                    "name": "Neural Interface",
                    "description": "Brain-computer interface",
                    "equipment_type": "peripheral",
                    "rarity": "legendary",
                    "stat_bonuses": {"speed": 25, "accuracy": 20, "xp_bonus": 0.2},
                    "unlock_level": 20,
                    "cost": 20000
                }
            ]
        }
    
    @pytest.fixture
    def equipment_system(self, equipment_config):
        """Create an equipment system for testing."""
        return EquipmentSystem(equipment_config)
    
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
        specialist.inventory = ["basic_laptop", "gold_badge"]
        return specialist
    
    def test_initialization(self, equipment_system):
        """Test equipment system initialization."""
        assert len(equipment_system.equipment_catalog) == 4
        assert "basic_laptop" in equipment_system.equipment_catalog
        assert "neural_interface" in equipment_system.equipment_catalog
    
    def test_equip_item_success(self, equipment_system, test_specialist):
        """Test successful equipment."""
        equipment = equipment_system.get_equipment("basic_laptop")
        
        success = equipment_system.equip_item(test_specialist, equipment)
        
        assert success is True
        assert test_specialist.equipped_items["tool"] == "basic_laptop"
    
    def test_equip_item_not_in_inventory(self, equipment_system, test_specialist):
        """Test equipping item not in inventory."""
        equipment = equipment_system.get_equipment("neural_interface")
        
        success = equipment_system.equip_item(test_specialist, equipment)
        
        assert success is False
    
    def test_equip_item_replaces_existing(self, equipment_system, test_specialist):
        """Test that equipping replaces existing item in slot."""
        # Add another tool to inventory
        test_specialist.inventory.append("advanced_workstation")
        
        # Equip first tool
        equipment1 = equipment_system.get_equipment("basic_laptop")
        equipment_system.equip_item(test_specialist, equipment1)
        
        # Equip second tool (should replace first)
        equipment2 = equipment_system.get_equipment("advanced_workstation")
        equipment_system.equip_item(test_specialist, equipment2)
        
        assert test_specialist.equipped_items["tool"] == "advanced_workstation"
    
    def test_unequip_item_success(self, equipment_system, test_specialist):
        """Test successful unequipping."""
        equipment = equipment_system.get_equipment("basic_laptop")
        equipment_system.equip_item(test_specialist, equipment)
        
        unequipped = equipment_system.unequip_item(test_specialist, "tool")
        
        assert unequipped is not None
        assert unequipped.id == "basic_laptop"
        assert "tool" not in test_specialist.equipped_items
    
    def test_unequip_empty_slot(self, equipment_system, test_specialist):
        """Test unequipping from empty slot."""
        unequipped = equipment_system.unequip_item(test_specialist, "peripheral")
        
        assert unequipped is None
    
    def test_calculate_total_stats_no_equipment(self, equipment_system, test_specialist):
        """Test stat calculation with no equipment."""
        total_stats = equipment_system.calculate_total_stats(test_specialist)
        
        assert total_stats.speed == test_specialist.stats.speed
        assert total_stats.accuracy == test_specialist.stats.accuracy
    
    def test_calculate_total_stats_with_equipment(self, equipment_system, test_specialist):
        """Test stat calculation with equipped items."""
        # Equip basic laptop (+5 speed, +2 accuracy)
        equipment = equipment_system.get_equipment("basic_laptop")
        equipment_system.equip_item(test_specialist, equipment)
        
        total_stats = equipment_system.calculate_total_stats(test_specialist)
        
        assert total_stats.speed == 55.0  # 50 + 5
        assert total_stats.accuracy == 52.0  # 50 + 2
    
    def test_calculate_total_stats_multiple_items(self, equipment_system, test_specialist):
        """Test stat calculation with multiple equipped items."""
        # Equip basic laptop (+5 speed, +2 accuracy)
        equipment1 = equipment_system.get_equipment("basic_laptop")
        equipment_system.equip_item(test_specialist, equipment1)
        
        # Equip gold badge (+15 accuracy, +0.1 xp_bonus)
        equipment2 = equipment_system.get_equipment("gold_badge")
        equipment_system.equip_item(test_specialist, equipment2)
        
        total_stats = equipment_system.calculate_total_stats(test_specialist)
        
        assert total_stats.speed == 55.0  # 50 + 5
        assert total_stats.accuracy == 67.0  # 50 + 2 + 15
        assert total_stats.experience_bonus == 1.1  # 1.0 + 0.1
    
    def test_get_equipped_items(self, equipment_system, test_specialist):
        """Test getting all equipped items."""
        equipment1 = equipment_system.get_equipment("basic_laptop")
        equipment_system.equip_item(test_specialist, equipment1)
        
        equipment2 = equipment_system.get_equipment("gold_badge")
        equipment_system.equip_item(test_specialist, equipment2)
        
        equipped = equipment_system.get_equipped_items(test_specialist)
        
        assert len(equipped) == 2
        assert "tool" in equipped
        assert "badge" in equipped
        assert equipped["tool"].id == "basic_laptop"
    
    def test_add_to_inventory(self, equipment_system, test_specialist):
        """Test adding equipment to inventory."""
        equipment = equipment_system.get_equipment("neural_interface")
        
        success = equipment_system.add_to_inventory(test_specialist, equipment)
        
        assert success is True
        assert "neural_interface" in test_specialist.inventory
    
    def test_add_to_inventory_duplicate(self, equipment_system, test_specialist):
        """Test adding duplicate equipment to inventory."""
        equipment = equipment_system.get_equipment("basic_laptop")
        
        success = equipment_system.add_to_inventory(test_specialist, equipment)
        
        assert success is False  # Already in inventory
    
    def test_remove_from_inventory(self, equipment_system, test_specialist):
        """Test removing equipment from inventory."""
        success = equipment_system.remove_from_inventory(test_specialist, "basic_laptop")
        
        assert success is True
        assert "basic_laptop" not in test_specialist.inventory
    
    def test_remove_from_inventory_not_present(self, equipment_system, test_specialist):
        """Test removing equipment not in inventory."""
        success = equipment_system.remove_from_inventory(test_specialist, "neural_interface")
        
        assert success is False
    
    def test_remove_from_inventory_equipped(self, equipment_system, test_specialist):
        """Test that equipped items cannot be removed from inventory."""
        equipment = equipment_system.get_equipment("basic_laptop")
        equipment_system.equip_item(test_specialist, equipment)
        
        success = equipment_system.remove_from_inventory(test_specialist, "basic_laptop")
        
        assert success is False
        assert "basic_laptop" in test_specialist.inventory
    
    def test_get_equipment(self, equipment_system):
        """Test getting equipment by ID."""
        equipment = equipment_system.get_equipment("gold_badge")
        
        assert equipment is not None
        assert equipment.name == "Gold Badge"
        
        # Non-existent equipment
        assert equipment_system.get_equipment("nonexistent") is None
    
    def test_generate_equipment_drop_difficulty_affects_chance(self, equipment_system):
        """Test that higher difficulty increases drop chance."""
        # This is probabilistic, so we run multiple times
        drops_low = sum(1 for _ in range(100) 
                       if equipment_system.generate_equipment_drop(1) is not None)
        drops_high = sum(1 for _ in range(100) 
                        if equipment_system.generate_equipment_drop(5) is not None)
        
        # Higher difficulty should have more drops
        assert drops_high > drops_low
    
    def test_generate_equipment_drop_rarity_boost(self, equipment_system):
        """Test that rarity boost affects drop quality."""
        # Generate multiple drops with high boost
        drops_with_boost = []
        for _ in range(50):
            drop = equipment_system.generate_equipment_drop(5, rarity_boost=0.3)
            if drop:
                drops_with_boost.append(drop.rarity)
        
        # Should have some rare/epic/legendary drops
        if drops_with_boost:
            rare_count = sum(1 for r in drops_with_boost if r in ["rare", "epic", "legendary"])
            assert rare_count > 0
    
    def test_stat_bonuses_accuracy_capped(self, equipment_system, test_specialist):
        """Test that accuracy is capped at 100."""
        # Set accuracy close to cap
        test_specialist.stats.accuracy = 85.0
        
        # Equip gold badge (+15 accuracy)
        equipment = equipment_system.get_equipment("gold_badge")
        equipment_system.equip_item(test_specialist, equipment)
        
        total_stats = equipment_system.calculate_total_stats(test_specialist)
        
        # Should be capped at 100
        assert total_stats.accuracy == 100.0
