"""Specialist Ability model.

Represents special abilities that specialists can activate with cooldowns.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class SpecialistAbility:
    """Represents a specialist ability that can be activated."""
    
    id: str
    name: str
    description: str
    ability_type: str  # SPEED_BURST, ACCURACY_BOOST, SLA_EXTENSION, REWARD_MULTIPLIER, AUTO_COMPLETE
    cooldown_seconds: float
    duration_seconds: float  # 0 for instant effects
    effect_magnitude: float
    unlock_level: int
    specialty: str = "Any"  # "Any" or specific specialty
    
    def to_dict(self) -> Dict:
        """Convert ability to dictionary for serialization.
        
        Returns:
            Dictionary representation of the ability
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "ability_type": self.ability_type,
            "cooldown_seconds": self.cooldown_seconds,
            "duration_seconds": self.duration_seconds,
            "effect_magnitude": self.effect_magnitude,
            "unlock_level": self.unlock_level,
            "specialty": self.specialty
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SpecialistAbility':
        """Create SpecialistAbility from dictionary.
        
        Args:
            data: Dictionary containing ability data
            
        Returns:
            New SpecialistAbility instance
        """
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            ability_type=data["ability_type"],
            cooldown_seconds=data["cooldown_seconds"],
            duration_seconds=data["duration_seconds"],
            effect_magnitude=data["effect_magnitude"],
            unlock_level=data["unlock_level"],
            specialty=data.get("specialty", "Any")
        )
