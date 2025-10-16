"""Specialist Progression System.

Handles XP calculation, level-ups, stat increases, and skill point allocation.
"""

from typing import Dict, Optional
from src.utils.logger import GameLogger


class ProgressionSystem:
    """Manages specialist leveling and progression mechanics."""
    
    def __init__(self, config: Dict):
        """Initialize the progression system.
        
        Args:
            config: Game configuration dictionary containing xp_curve and level_stat_increases
        """
        self._logger = GameLogger("progression_system")
        
        # Load XP curve configuration
        xp_config = config.get("xp_curve", {})
        self.base_xp = xp_config.get("base_xp", 100)
        self.exponent = xp_config.get("exponent", 1.5)
        self.level_cap = xp_config.get("level_cap", 50)
        
        # Load stat increase configuration
        self.level_stat_increases = config.get("level_stat_increases", {
            "speed": 2,
            "accuracy": 1,
            "xp_bonus": 0.05
        })
        
        # Load skill points per level
        self.skill_points_per_level = config.get("skill_points_per_level", 1)
        
        self._logger.logger.info(
            f"[PROGRESSION] Initialized: base_xp={self.base_xp}, "
            f"exponent={self.exponent}, level_cap={self.level_cap}"
        )
    
    def calculate_xp_for_level(self, level: int) -> int:
        """Calculate total XP needed to reach a specific level.
        
        Args:
            level: Target level to calculate XP for
            
        Returns:
            Total XP required to reach the target level
        """
        if level <= 1:
            return 0
        
        total_xp = 0
        for lvl in range(1, level):
            total_xp += int(self.base_xp * (lvl ** self.exponent))
        
        return total_xp
    
    def calculate_level_from_xp(self, xp: int) -> int:
        """Determine current level from total XP.
        
        Args:
            xp: Total XP accumulated
            
        Returns:
            Current level based on XP
        """
        level = 1
        while level < self.level_cap:
            xp_for_next_level = self.calculate_xp_for_level(level + 1)
            if xp < xp_for_next_level:
                break
            level += 1
        
        return level
    
    def get_stat_increases_for_level(self, level: int) -> Dict[str, float]:
        """Get stat bonuses awarded at a specific level.
        
        Args:
            level: Level to get stat increases for
            
        Returns:
            Dictionary of stat increases (e.g., {"speed": 2, "accuracy": 1})
        """
        return self.level_stat_increases.copy()
    
    def process_level_up(self, specialist) -> Dict:
        """Handle level-up logic and award rewards.
        
        Args:
            specialist: The specialist who is leveling up
            
        Returns:
            Dictionary containing level-up rewards and information:
            {
                "new_level": int,
                "stat_increases": Dict[str, float],
                "skill_points_awarded": int,
                "unlocked_abilities": List[str]
            }
        """
        new_level = specialist.level
        stat_increases = self.get_stat_increases_for_level(new_level)
        
        # Apply stat increases
        specialist.stats.speed += stat_increases.get("speed", 0)
        specialist.stats.accuracy = min(100.0, specialist.stats.accuracy + stat_increases.get("accuracy", 0))
        specialist.stats.experience_bonus += stat_increases.get("xp_bonus", 0.0)
        
        # Award skill points
        specialist.skill_points += self.skill_points_per_level
        
        # Check for ability unlocks (to be implemented with ability system)
        unlocked_abilities = []
        
        self._logger.logger.info(
            f"[PROGRESSION] Specialist {specialist.id} leveled up to {new_level}: "
            f"stats={stat_increases}, skill_points=+{self.skill_points_per_level}"
        )
        
        return {
            "new_level": new_level,
            "stat_increases": stat_increases,
            "skill_points_awarded": self.skill_points_per_level,
            "unlocked_abilities": unlocked_abilities
        }
