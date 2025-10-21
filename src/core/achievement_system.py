"""Achievement System.

Handles achievement tracking, unlocking, and reward distribution.
"""

from typing import Dict, List, Optional
from src.models.achievement import Achievement
from src.utils.logger import GameLogger


class AchievementSystem:
    """Manages achievements and progress tracking."""
    
    def __init__(self, achievements_config: Dict):
        """Initialize the achievement system.
        
        Args:
            achievements_config: Configuration dictionary containing achievements data
        """
        self._logger = GameLogger("achievement_system")
        self.achievements: Dict[str, Achievement] = {}
        
        # Load achievements from config
        if "achievements" in achievements_config:
            for achievement_data in achievements_config["achievements"]:
                achievement = Achievement.from_dict(achievement_data)
                self.achievements[achievement.id] = achievement
        
        self._logger.info(
            f"[ACHIEVEMENT_SYSTEM] Initialized with {len(self.achievements)} achievements"
        )
    
    def check_achievements(self, game_state) -> List[Achievement]:
        """Check all achievements and return newly unlocked ones.
        
        Args:
            game_state: The current game state
            
        Returns:
            List of newly unlocked achievements
        """
        newly_unlocked = []
        
        for achievement_id, achievement in self.achievements.items():
            # Skip if already unlocked
            if achievement_id in game_state.unlocked_achievements:
                continue
            
            # Check if achievement condition is met
            if self._check_achievement_condition(achievement, game_state):
                newly_unlocked.append(achievement)
                game_state.unlocked_achievements.append(achievement_id)
                
                # Award rewards
                self.award_achievement(achievement, game_state)
                
                self._logger.info(
                    f"[ACHIEVEMENT_SYSTEM] Achievement unlocked: {achievement.name}"
                )
        
        return newly_unlocked
    
    def _check_achievement_condition(self, achievement: Achievement, game_state) -> bool:
        """Check if an achievement's condition is met.
        
        Args:
            achievement: The achievement to check
            game_state: The current game state
            
        Returns:
            True if condition is met, False otherwise
        """
        condition_type = achievement.condition_type
        condition_value = achievement.condition_value
        
        if condition_type == "incidents_resolved":
            return game_state.metrics.total_incidents_handled >= condition_value
        
        elif condition_type == "total_xp":
            # Sum XP from all specialists
            total_xp = sum(s.xp for s in game_state.specialists)
            return total_xp >= condition_value
        
        elif condition_type == "specialist_level":
            # Check if any specialist has reached the level
            max_level = max((s.level for s in game_state.specialists), default=0)
            return max_level >= condition_value
        
        elif condition_type == "money_earned":
            return game_state.total_money_earned >= condition_value
        
        elif condition_type == "current_money":
            return game_state.current_money >= condition_value
        
        elif condition_type == "sla_perfection":
            # Check if we have resolved enough incidents with perfect SLA
            # This is tracked via total_incidents_handled vs failed
            if game_state.metrics.total_incidents_handled < condition_value:
                return False
            # Check SLA compliance rate
            return game_state.metrics.sla_compliance_rate >= 100.0
        
        elif condition_type == "specialty_incidents_resolved":
            # Count incidents resolved by specialty
            # This would need additional tracking in game_state
            # For now, we'll use a simplified check
            return False  # Not yet implemented
        
        elif condition_type == "specialists_hired":
            return len(game_state.specialists) >= condition_value
        
        elif condition_type == "total_clients":
            return len(game_state.clients) >= condition_value
        
        elif condition_type == "prestige_count":
            return game_state.total_prestiges >= condition_value
        
        elif condition_type == "equipment_collected":
            # Count unique equipment across all specialists
            all_equipment = set()
            for specialist in game_state.specialists:
                all_equipment.update(specialist.inventory)
                all_equipment.update(specialist.equipped_items.values())
            return len(all_equipment) >= condition_value
        
        elif condition_type == "abilities_unlocked":
            # Count unlocked abilities across all specialists
            all_abilities = set()
            for specialist in game_state.specialists:
                all_abilities.update(specialist.abilities)
            return len(all_abilities) >= condition_value
        
        return False
    
    def award_achievement(self, achievement: Achievement, game_state):
        """Award achievement rewards to the player.
        
        Args:
            achievement: The achievement to award
            game_state: The current game state
        """
        # Award money
        if achievement.reward_money > 0:
            game_state.current_money += achievement.reward_money
            game_state.total_money_earned += achievement.reward_money
        
        # Award XP to all specialists
        if achievement.reward_xp > 0:
            for specialist in game_state.specialists:
                specialist.gain_xp(achievement.reward_xp)
        
        # Award equipment
        if achievement.reward_equipment:
            # Add equipment to first available specialist's inventory
            if game_state.specialists:
                game_state.specialists[0].inventory.append(achievement.reward_equipment)
        
        self._logger.info(
            f"[ACHIEVEMENT_SYSTEM] Awarded: ${achievement.reward_money}, "
            f"{achievement.reward_xp} XP, equipment: {achievement.reward_equipment}"
        )
    
    def get_progress(self, achievement: Achievement, game_state) -> float:
        """Get progress toward an achievement (0.0-1.0).
        
        Args:
            achievement: The achievement to check progress for
            game_state: The current game state
            
        Returns:
            Progress value between 0.0 and 1.0
        """
        if achievement.id in game_state.unlocked_achievements:
            return 1.0
        
        condition_type = achievement.condition_type
        condition_value = achievement.condition_value
        
        if condition_value == 0:
            return 0.0
        
        current_value = 0
        
        if condition_type == "incidents_resolved":
            current_value = game_state.metrics.total_incidents_handled
        
        elif condition_type == "total_xp":
            current_value = sum(s.xp for s in game_state.specialists)
        
        elif condition_type == "specialist_level":
            current_value = max((s.level for s in game_state.specialists), default=0)
        
        elif condition_type == "money_earned":
            current_value = game_state.total_money_earned
        
        elif condition_type == "current_money":
            current_value = game_state.current_money
        
        elif condition_type == "sla_perfection":
            current_value = game_state.metrics.total_incidents_handled
        
        elif condition_type == "specialists_hired":
            current_value = len(game_state.specialists)
        
        elif condition_type == "total_clients":
            current_value = len(game_state.clients)
        
        elif condition_type == "prestige_count":
            current_value = game_state.total_prestiges
        
        elif condition_type == "equipment_collected":
            all_equipment = set()
            for specialist in game_state.specialists:
                all_equipment.update(specialist.inventory)
                all_equipment.update(specialist.equipped_items.values())
            current_value = len(all_equipment)
        
        elif condition_type == "abilities_unlocked":
            all_abilities = set()
            for specialist in game_state.specialists:
                all_abilities.update(specialist.abilities)
            current_value = len(all_abilities)
        
        # Calculate progress
        progress = min(1.0, current_value / condition_value)
        
        # Store progress in game state
        game_state.achievement_progress[achievement.id] = progress
        
        return progress
    
    def get_achievement(self, achievement_id: str) -> Optional[Achievement]:
        """Get an achievement by ID.
        
        Args:
            achievement_id: The achievement ID
            
        Returns:
            Achievement instance or None if not found
        """
        return self.achievements.get(achievement_id)
    
    def get_all_achievements(self, include_hidden: bool = False) -> List[Achievement]:
        """Get all achievements.
        
        Args:
            include_hidden: Whether to include hidden achievements
            
        Returns:
            List of all achievements
        """
        if include_hidden:
            return list(self.achievements.values())
        else:
            return [a for a in self.achievements.values() if not a.hidden]
    
    def get_achievements_by_category(self, category: str) -> List[Achievement]:
        """Get achievements in a specific category.
        
        Args:
            category: The category to filter by
            
        Returns:
            List of achievements in the category
        """
        return [a for a in self.achievements.values() if a.category.lower() == category.lower()]
