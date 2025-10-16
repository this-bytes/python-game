"""Prestige and Prestige Upgrade models for the rebirth system.

This module defines the prestige upgrade system that provides permanent bonuses
after resetting the game.
"""

from dataclasses import dataclass
from typing import Dict
from enum import Enum


class PrestigeEffectType(Enum):
    """Enum for prestige upgrade effect types."""
    XP_MULTIPLIER = "xp_multiplier"
    MONEY_MULTIPLIER = "money_multiplier"
    AUTOMATION_EFFICIENCY = "automation_efficiency"
    STARTING_SPECIALISTS = "starting_specialists"
    INCIDENT_REWARD_BOOST = "incident_reward_boost"
    PASSIVE_INCOME_BOOST = "passive_income_boost"
    AUTOMATION_COOLDOWN_REDUCTION = "automation_cooldown_reduction"
    CLIENT_REPUTATION_BOOST = "client_reputation_boost"
    SLA_TIME_EXTENSION = "sla_time_extension"
    SPECIALIST_STAT_BOOST = "specialist_stat_boost"


@dataclass
class PrestigeUpgrade:
    """Represents a prestige upgrade that can be purchased with prestige points."""
    
    id: str
    name: str
    description: str
    cost_prestige_points: int
    effect_type: str
    effect_magnitude: float
    max_level: int
    
    def __post_init__(self):
        """Validate effect type."""
        if self.effect_type not in [e.value for e in PrestigeEffectType]:
            raise ValueError(f"Invalid prestige effect type: {self.effect_type}")
    
    def calculate_cost(self, current_level: int) -> int:
        """Calculate cost for next level.
        
        Args:
            current_level: Current level of the upgrade
            
        Returns:
            Cost in prestige points
        """
        if current_level >= self.max_level:
            return -1  # Max level reached
        
        # Exponential cost scaling
        return int(self.cost_prestige_points * (1.5 ** current_level))
    
    def calculate_total_effect(self, level: int) -> float:
        """Calculate total effect magnitude at given level.
        
        Args:
            level: Upgrade level
            
        Returns:
            Total effect magnitude
        """
        return self.effect_magnitude * level
    
    def to_dict(self) -> Dict:
        """Convert prestige upgrade to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "cost_prestige_points": self.cost_prestige_points,
            "effect_type": self.effect_type,
            "effect_magnitude": self.effect_magnitude,
            "max_level": self.max_level
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PrestigeUpgrade':
        """Create PrestigeUpgrade from dictionary.
        
        Args:
            data: Dictionary containing upgrade data
            
        Returns:
            New PrestigeUpgrade instance
        """
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            cost_prestige_points=data["cost_prestige_points"],
            effect_type=data["effect_type"],
            effect_magnitude=data["effect_magnitude"],
            max_level=data["max_level"]
        )
    
    def __repr__(self) -> str:
        """String representation of prestige upgrade."""
        return (f"PrestigeUpgrade(id='{self.id}', name='{self.name}', "
                f"effect={self.effect_type}, magnitude={self.effect_magnitude})")
