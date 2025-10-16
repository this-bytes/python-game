"""Equipment model.

Represents equipment items that specialists can equip for stat bonuses.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class Equipment:
    """Represents an equipment item that can be equipped by specialists."""
    
    id: str
    name: str
    description: str
    equipment_type: str  # TOOL, BADGE, PERIPHERAL
    rarity: str  # COMMON, RARE, EPIC, LEGENDARY
    stat_bonuses: Dict[str, float]  # {"speed": 5, "accuracy": 3}
    unlock_level: int
    cost: int  # Purchase cost (if in shop)
    
    def to_dict(self) -> Dict:
        """Convert equipment to dictionary for serialization.
        
        Returns:
            Dictionary representation of the equipment
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "equipment_type": self.equipment_type,
            "rarity": self.rarity,
            "stat_bonuses": self.stat_bonuses.copy(),
            "unlock_level": self.unlock_level,
            "cost": self.cost
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Equipment':
        """Create Equipment from dictionary.
        
        Args:
            data: Dictionary containing equipment data
            
        Returns:
            New Equipment instance
        """
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            equipment_type=data["equipment_type"],
            rarity=data["rarity"],
            stat_bonuses=data["stat_bonuses"].copy(),
            unlock_level=data["unlock_level"],
            cost=data["cost"]
        )
