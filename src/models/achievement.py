"""Achievement model.

Represents achievements that players can unlock for completing various tasks.
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Achievement:
    """Represents an achievement that can be unlocked."""
    
    id: str
    name: str
    description: str
    category: str  # PROGRESSION, EFFICIENCY, SPECIALTY_MASTERY, WEALTH, SPEED
    condition_type: str  # INCIDENTS_RESOLVED, TOTAL_XP, SPECIALIST_LEVEL, MONEY_EARNED, SLA_PERFECTION, etc.
    condition_value: int
    reward_money: int
    reward_xp: int
    reward_equipment: Optional[str] = None  # Equipment ID
    hidden: bool = False  # Secret achievements
    
    def to_dict(self) -> Dict:
        """Convert achievement to dictionary for serialization.
        
        Returns:
            Dictionary representation of the achievement
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "condition_type": self.condition_type,
            "condition_value": self.condition_value,
            "reward_money": self.reward_money,
            "reward_xp": self.reward_xp,
            "reward_equipment": self.reward_equipment,
            "hidden": self.hidden
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Achievement':
        """Create Achievement from dictionary.
        
        Args:
            data: Dictionary containing achievement data
            
        Returns:
            New Achievement instance
        """
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            category=data["category"],
            condition_type=data["condition_type"],
            condition_value=data["condition_value"],
            reward_money=data["reward_money"],
            reward_xp=data["reward_xp"],
            reward_equipment=data.get("reward_equipment"),
            hidden=data.get("hidden", False)
        )
