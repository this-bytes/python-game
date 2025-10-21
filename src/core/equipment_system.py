"""Equipment System.

Handles equipment drops, equipping, and stat calculations.
"""

from typing import Dict, Optional
import random
from src.models.equipment import Equipment
from src.models.specialist import SpecialistStats
from src.utils.logger import GameLogger


class EquipmentSystem:
    """Manages equipment items and their effects."""
    
    def __init__(self, equipment_config: Dict):
        """Initialize the equipment system.
        
        Args:
            equipment_config: Configuration dictionary containing equipment data
        """
        self._logger = GameLogger("equipment_system")
        self.equipment_catalog: Dict[str, Equipment] = {}
        
        # Load equipment from config
        if "equipment" in equipment_config:
            for equipment_data in equipment_config["equipment"]:
                equipment = Equipment.from_dict(equipment_data)
                self.equipment_catalog[equipment.id] = equipment
        
        # Rarity weights for drops
        self.rarity_weights = {
            "common": 0.60,    # 60%
            "rare": 0.25,      # 25%
            "epic": 0.12,      # 12%
            "legendary": 0.03  # 3%
        }
        
        logger_target = getattr(self._logger, "logger", self._logger)
        logger_target.info(
            f"[EQUIPMENT_SYSTEM] Initialized with {len(self.equipment_catalog)} equipment items"
        )
    
    def generate_equipment_drop(self, incident_difficulty: int, 
                                 rarity_boost: float = 0.0) -> Optional[Equipment]:
        """Generate a random equipment drop after incident resolution.
        
        Args:
            incident_difficulty: Difficulty of the resolved incident (1-5)
            rarity_boost: Additional boost to rarity chance (0.0-1.0)
            
        Returns:
            Equipment instance or None if no drop
        """
        # Drop chance increases with difficulty (20% to 60%)
        drop_chance = 0.20 + (incident_difficulty - 1) * 0.10
        
        if random.random() > drop_chance:
            return None
        
        # Adjust rarity weights based on difficulty and boost
        adjusted_weights = self.rarity_weights.copy()
        difficulty_boost = (incident_difficulty - 1) * 0.05
        total_boost = min(0.5, rarity_boost + difficulty_boost)
        
        # Shift probability from common to higher rarities
        adjusted_weights["common"] = max(0.1, adjusted_weights["common"] - total_boost)
        adjusted_weights["legendary"] = min(0.3, adjusted_weights["legendary"] + total_boost * 0.3)
        adjusted_weights["epic"] = min(0.4, adjusted_weights["epic"] + total_boost * 0.4)
        adjusted_weights["rare"] = min(0.5, adjusted_weights["rare"] + total_boost * 0.3)
        
        # Normalize weights
        total_weight = sum(adjusted_weights.values())
        adjusted_weights = {k: v / total_weight for k, v in adjusted_weights.items()}
        
        # Select rarity
        rand = random.random()
        cumulative = 0.0
        selected_rarity = "common"
        
        for rarity, weight in adjusted_weights.items():
            cumulative += weight
            if rand <= cumulative:
                selected_rarity = rarity
                break
        
        # Get equipment of selected rarity
        matching_equipment = [
            eq for eq in self.equipment_catalog.values()
            if eq.rarity.lower() == selected_rarity
        ]
        
        if not matching_equipment:
            return None
        
        # Random selection from matching equipment
        dropped_equipment = random.choice(matching_equipment)
        
        logger_target = getattr(self._logger, "logger", self._logger)
        logger_target.info(
            f"[EQUIPMENT_SYSTEM] Equipment drop: {dropped_equipment.name} ({dropped_equipment.rarity})"
        )
        
        return dropped_equipment
    
    def equip_item(self, specialist, equipment: Equipment) -> bool:
        """Equip an item to a specialist.
        
        Args:
            specialist: The specialist to equip the item to
            equipment: The equipment to equip
            
        Returns:
            True if successful, False otherwise
        """
        slot = equipment.equipment_type.lower()
        
        # Check if equipment is in inventory
        if equipment.id not in specialist.inventory:
            logger_target = getattr(self._logger, "logger", self._logger)
            logger_target.warning(
                f"[EQUIPMENT_SYSTEM] Equipment {equipment.id} not in inventory"
            )
            return False
        
        # Unequip existing item in slot if present
        if slot in specialist.equipped_items:
            old_equipment_id = specialist.equipped_items[slot]
            logger_target = getattr(self._logger, "logger", self._logger)
            logger_target.info(
                f"[EQUIPMENT_SYSTEM] Unequipping {old_equipment_id} from {slot}"
            )
        
        # Equip new item
        specialist.equipped_items[slot] = equipment.id
        
        logger_target = getattr(self._logger, "logger", self._logger)
        logger_target.info(
            f"[EQUIPMENT_SYSTEM] Specialist {specialist.id} equipped {equipment.name}"
        )
        
        return True
    
    def unequip_item(self, specialist, slot: str) -> Optional[Equipment]:
        """Unequip an item from a slot.
        
        Args:
            specialist: The specialist to unequip from
            slot: The equipment slot to unequip
            
        Returns:
            The unequipped Equipment or None if slot was empty
        """
        if slot not in specialist.equipped_items:
            return None
        
        equipment_id = specialist.equipped_items[slot]
        del specialist.equipped_items[slot]
        
        equipment = self.equipment_catalog.get(equipment_id)
        
        logger_target = getattr(self._logger, "logger", self._logger)
        logger_target.info(
            f"[EQUIPMENT_SYSTEM] Specialist {specialist.id} unequipped from {slot}"
        )
        
        return equipment
    
    def calculate_total_stats(self, specialist) -> SpecialistStats:
        """Calculate total stats including equipment bonuses.
        
        Args:
            specialist: The specialist to calculate stats for
            
        Returns:
            SpecialistStats with equipment bonuses applied
        """
        # Start with base stats
        total_stats = SpecialistStats(
            speed=specialist.stats.speed,
            accuracy=specialist.stats.accuracy,
            experience_bonus=specialist.stats.experience_bonus
        )
        
        # Add bonuses from equipped items
        for slot, equipment_id in specialist.equipped_items.items():
            equipment = self.equipment_catalog.get(equipment_id)
            if equipment:
                for stat, bonus in equipment.stat_bonuses.items():
                    if stat == "speed":
                        total_stats.speed += bonus
                    elif stat == "accuracy":
                        total_stats.accuracy = min(100.0, total_stats.accuracy + bonus)
                    elif stat == "xp_bonus" or stat == "experience_bonus":
                        total_stats.experience_bonus += bonus
        
        return total_stats
    
    def get_equipped_items(self, specialist) -> Dict[str, Equipment]:
        """Get all equipped equipment.
        
        Args:
            specialist: The specialist to get equipment for
            
        Returns:
            Dictionary mapping slot to Equipment instance
        """
        equipped = {}
        
        for slot, equipment_id in specialist.equipped_items.items():
            equipment = self.equipment_catalog.get(equipment_id)
            if equipment:
                equipped[slot] = equipment
        
        return equipped
    
    def add_to_inventory(self, specialist, equipment: Equipment) -> bool:
        """Add equipment to specialist's inventory.
        
        Args:
            specialist: The specialist to add equipment to
            equipment: The equipment to add
            
        Returns:
            True if added, False if already in inventory
        """
        if equipment.id in specialist.inventory:
            return False
        
        specialist.inventory.append(equipment.id)
        
        logger_target = getattr(self._logger, "logger", self._logger)
        logger_target.info(
            f"[EQUIPMENT_SYSTEM] Added {equipment.name} to {specialist.id}'s inventory"
        )
        
        return True
    
    def remove_from_inventory(self, specialist, equipment_id: str) -> bool:
        """Remove equipment from specialist's inventory.
        
        Args:
            specialist: The specialist to remove equipment from
            equipment_id: The equipment ID to remove
            
        Returns:
            True if removed, False if not in inventory
        """
        if equipment_id not in specialist.inventory:
            return False
        
        # Can't remove if equipped
        for slot, equipped_id in specialist.equipped_items.items():
            if equipped_id == equipment_id:
                logger_target = getattr(self._logger, "logger", self._logger)
                logger_target.warning(
                    f"[EQUIPMENT_SYSTEM] Cannot remove equipped item {equipment_id}"
                )
                return False
        
        specialist.inventory.remove(equipment_id)
        
        logger_target = getattr(self._logger, "logger", self._logger)
        logger_target.info(
            f"[EQUIPMENT_SYSTEM] Removed {equipment_id} from {specialist.id}'s inventory"
        )
        
        return True
    
    def get_equipment(self, equipment_id: str) -> Optional[Equipment]:
        """Get equipment by ID.
        
        Args:
            equipment_id: The equipment ID
            
        Returns:
            Equipment instance or None if not found
        """
        return self.equipment_catalog.get(equipment_id)
    
    def can_upgrade_equipment(self, equipment: Equipment) -> bool:
        """Check if equipment can be upgraded to a higher rarity.
        
        Args:
            equipment: The equipment to check
            
        Returns:
            True if equipment can be upgraded
        """
        rarity_hierarchy = ["common", "rare", "epic", "legendary"]
        current_rarity_index = rarity_hierarchy.index(equipment.rarity.lower())
        
        # Can't upgrade legendary equipment
        return current_rarity_index < len(rarity_hierarchy) - 1
    
    def get_upgrade_requirements(self, equipment: Equipment) -> Dict:
        """Get the requirements to upgrade equipment.
        
        Args:
            equipment: The equipment to upgrade
            
        Returns:
            Dictionary with upgrade requirements
        """
        rarity_hierarchy = ["common", "rare", "epic", "legendary"]
        current_rarity_index = rarity_hierarchy.index(equipment.rarity.lower())
        next_rarity = rarity_hierarchy[current_rarity_index + 1]
        
        # Upgrade requirements based on current rarity
        requirements = {
            "common": {"count": 2, "cost": 1000},
            "rare": {"count": 3, "cost": 5000},
            "epic": {"count": 3, "cost": 15000}
        }
        
        return {
            "equipment_type": equipment.equipment_type,
            "current_rarity": equipment.rarity,
            "target_rarity": next_rarity,
            "required_count": requirements[equipment.rarity.lower()]["count"],
            "upgrade_cost": requirements[equipment.rarity.lower()]["cost"]
        }
    
    def upgrade_equipment(self, equipment_ids: list[str]) -> Optional[Equipment]:
        """Upgrade equipment by combining multiple pieces.
        
        Args:
            equipment_ids: List of equipment IDs to combine (must be same type/rarity)
            
        Returns:
            New upgraded equipment or None if upgrade failed
        """
        if not equipment_ids or len(equipment_ids) < 2:
            return None
        
        # Get all equipment
        equipment_list = []
        for eq_id in equipment_ids:
            eq = self.get_equipment(eq_id)
            if not eq:
                return None
            equipment_list.append(eq)
        
        # Validate all equipment is the same type and rarity
        first_eq = equipment_list[0]
        for eq in equipment_list[1:]:
            if eq.equipment_type != first_eq.equipment_type or eq.rarity != first_eq.rarity:
                return None
        
        # Check upgrade requirements
        requirements = self.get_upgrade_requirements(first_eq)
        if len(equipment_list) != requirements["required_count"]:
            return None
        
        # Find target equipment (same type, next rarity)
        target_rarity = requirements["target_rarity"]
        target_equipment = None
        
        for eq in self.equipment_catalog.values():
            if (eq.equipment_type == first_eq.equipment_type and 
                eq.rarity.lower() == target_rarity.lower()):
                target_equipment = eq
                break
        
        if not target_equipment:
            logger_target = getattr(self._logger, "logger", self._logger)
            logger_target.warning(
                f"[EQUIPMENT_SYSTEM] No upgrade target found for {first_eq.equipment_type} {target_rarity}"
            )
            return None
        
        logger_target = getattr(self._logger, "logger", self._logger)
        logger_target.info(
            f"[EQUIPMENT_SYSTEM] Upgraded {len(equipment_list)}x {first_eq.rarity} {first_eq.equipment_type} "
            f"to {target_equipment.name}"
        )
        
        return target_equipment
