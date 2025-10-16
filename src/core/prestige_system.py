"""Prestige System for managing game resets with permanent bonuses.

This module handles the prestige/rebirth mechanic where players reset their game
progress in exchange for prestige points and permanent upgrade bonuses.
"""

from typing import Dict, List, Any, Optional, TYPE_CHECKING
import copy

from src.models.prestige import PrestigeUpgrade, PrestigeEffectType
from src.utils.logger import GameLogger

if TYPE_CHECKING:
    from src.models.game_state import GameState


class PrestigeSystem:
    """Manages prestige mechanics and permanent upgrades.
    
    This system calculates prestige points based on player progression,
    handles game resets, and applies prestige upgrade bonuses.
    """

    def __init__(self, prestige_upgrades: List[PrestigeUpgrade], logger: Optional[GameLogger] = None):
        """Initialize the prestige system.
        
        Args:
            prestige_upgrades: List of available prestige upgrades
            logger: Optional logger for prestige events
        """
        self._logger = logger or GameLogger("prestige_system")
        self._upgrades = {upgrade.id: upgrade for upgrade in prestige_upgrades}
        
        # Statistics
        self._stats = {
            "total_prestiges": 0,
            "total_prestige_points_earned": 0,
            "total_prestige_points_spent": 0
        }

    def calculate_prestige_points(self, game_state: 'GameState') -> int:
        """Calculate prestige points based on current game progression.
        
        Args:
            game_state: Current game state
            
        Returns:
            Number of prestige points that would be awarded
        """
        points = 0
        
        # Points from total XP
        total_xp = sum(s.xp for s in game_state.specialists)
        xp_points = total_xp // 10000  # 1 point per 10,000 XP
        points += xp_points
        
        # Points from total money earned
        money_points = int(game_state.total_money_earned // 100000)  # 1 point per 100,000 money
        points += money_points
        
        # Points from specialist levels
        total_levels = sum(s.level for s in game_state.specialists)
        level_points = total_levels // 10  # 1 point per 10 levels
        points += level_points
        
        # Points from incidents handled
        incident_points = game_state.metrics.total_incidents_handled // 100  # 1 point per 100 incidents
        points += incident_points
        
        # Bonus points from high SLA compliance
        if game_state.metrics.sla_compliance_rate >= 90:
            points += 5
        if game_state.metrics.sla_compliance_rate >= 95:
            points += 5
        
        # Minimum 1 point for performing prestige
        points = max(1, points)
        
        self._logger.logger.debug(
            f"[PRESTIGE] Calculated prestige points: {points} "
            f"(XP: {xp_points}, Money: {money_points}, Levels: {level_points}, Incidents: {incident_points})"
        )
        
        return points

    def perform_prestige(self, game_state: 'GameState') -> 'GameState':
        """Perform prestige reset on game state.
        
        Args:
            game_state: Current game state to reset
            
        Returns:
            New game state with prestige bonuses applied
        """
        # Calculate prestige points earned
        points_earned = self.calculate_prestige_points(game_state)
        
        # Store prestige data before reset
        old_prestige_points = getattr(game_state, 'prestige_points', 0)
        old_prestige_upgrades = getattr(game_state, 'prestige_upgrades', {}).copy()
        old_total_prestiges = getattr(game_state, 'total_prestiges', 0)
        old_clients = copy.deepcopy(game_state.clients)
        
        # Create new game state (this will reset most things via __post_init__)
        from src.models.game_state import GameState
        new_state = GameState()
        
        # Restore prestige-related data
        new_state.prestige_points = old_prestige_points + points_earned
        new_state.prestige_upgrades = old_prestige_upgrades
        new_state.total_prestiges = old_total_prestiges + 1
        
        # Keep clients (but reset reputation to a base level)
        for client in old_clients:
            client.reputation = max(50, client.reputation // 2)  # Half reputation, min 50
        new_state.clients = old_clients
        
        # Apply prestige bonuses to new state
        self._apply_prestige_bonuses(new_state)
        
        # Update statistics
        self._stats["total_prestiges"] += 1
        self._stats["total_prestige_points_earned"] += points_earned
        
        self._logger.logger.info(
            f"[PRESTIGE] Prestige performed! Earned {points_earned} points, "
            f"total: {new_state.prestige_points} points, prestige #{new_state.total_prestiges}"
        )
        
        return new_state

    def purchase_prestige_upgrade(self, upgrade_id: str, game_state: 'GameState') -> Dict[str, Any]:
        """Purchase a prestige upgrade.
        
        Args:
            upgrade_id: ID of the upgrade to purchase
            game_state: Current game state
            
        Returns:
            Dictionary containing purchase result
        """
        if upgrade_id not in self._upgrades:
            return {
                "success": False,
                "error": f"Unknown prestige upgrade: {upgrade_id}"
            }
        
        upgrade = self._upgrades[upgrade_id]
        
        # Get current level
        if not hasattr(game_state, 'prestige_upgrades'):
            game_state.prestige_upgrades = {}
        
        current_level = game_state.prestige_upgrades.get(upgrade_id, 0)
        
        # Check if at max level
        if current_level >= upgrade.max_level:
            return {
                "success": False,
                "error": "Upgrade already at max level"
            }
        
        # Calculate cost
        cost = upgrade.calculate_cost(current_level)
        
        # Check if can afford
        prestige_points = getattr(game_state, 'prestige_points', 0)
        if prestige_points < cost:
            return {
                "success": False,
                "error": "Insufficient prestige points",
                "cost": cost,
                "available": prestige_points
            }
        
        # Purchase upgrade
        game_state.prestige_points -= cost
        game_state.prestige_upgrades[upgrade_id] = current_level + 1
        
        # Apply new bonuses
        self._apply_prestige_bonuses(game_state)
        
        # Update statistics
        self._stats["total_prestige_points_spent"] += cost
        
        self._logger.logger.info(
            f"[PRESTIGE] Purchased {upgrade.name} level {current_level + 1} for {cost} points"
        )
        
        return {
            "success": True,
            "upgrade_id": upgrade_id,
            "new_level": current_level + 1,
            "cost": cost,
            "remaining_points": game_state.prestige_points
        }

    def apply_prestige_bonuses(self, game_state: 'GameState') -> Dict[str, float]:
        """Apply all prestige bonuses to game state.
        
        Args:
            game_state: Game state to apply bonuses to
            
        Returns:
            Dictionary of total bonuses by effect type
        """
        return self._apply_prestige_bonuses(game_state)

    def _apply_prestige_bonuses(self, game_state: 'GameState') -> Dict[str, float]:
        """Internal method to apply prestige bonuses.
        
        Args:
            game_state: Game state to apply bonuses to
            
        Returns:
            Dictionary of total bonuses by effect type
        """
        bonuses = {}
        
        if not hasattr(game_state, 'prestige_upgrades'):
            return bonuses
        
        for upgrade_id, level in game_state.prestige_upgrades.items():
            if upgrade_id not in self._upgrades:
                continue
            
            upgrade = self._upgrades[upgrade_id]
            total_effect = upgrade.calculate_total_effect(level)
            
            effect_type = upgrade.effect_type
            if effect_type not in bonuses:
                bonuses[effect_type] = 0.0
            
            bonuses[effect_type] += total_effect
        
        # Apply specific bonuses
        if PrestigeEffectType.STARTING_SPECIALISTS.value in bonuses:
            # This would need to be handled during game initialization
            pass
        
        self._logger.logger.debug(f"[PRESTIGE] Applied bonuses: {bonuses}")
        
        return bonuses

    def get_prestige_multiplier(self, game_state: 'GameState', effect_type: str) -> float:
        """Get the total multiplier for a specific effect type.
        
        Args:
            game_state: Current game state
            effect_type: Effect type to get multiplier for
            
        Returns:
            Total multiplier (1.0 = no bonus)
        """
        bonuses = self._apply_prestige_bonuses(game_state)
        return 1.0 + bonuses.get(effect_type, 0.0)

    def get_available_upgrades(self, game_state: 'GameState') -> List[Dict[str, Any]]:
        """Get list of available upgrades with their current status.
        
        Args:
            game_state: Current game state
            
        Returns:
            List of upgrade information dictionaries
        """
        upgrades_list = []
        prestige_points = getattr(game_state, 'prestige_points', 0)
        prestige_upgrades = getattr(game_state, 'prestige_upgrades', {})
        
        for upgrade_id, upgrade in self._upgrades.items():
            current_level = prestige_upgrades.get(upgrade_id, 0)
            cost = upgrade.calculate_cost(current_level)
            can_afford = prestige_points >= cost if cost > 0 else False
            at_max = current_level >= upgrade.max_level
            
            upgrades_list.append({
                "id": upgrade_id,
                "name": upgrade.name,
                "description": upgrade.description,
                "effect_type": upgrade.effect_type,
                "effect_magnitude": upgrade.effect_magnitude,
                "current_level": current_level,
                "max_level": upgrade.max_level,
                "cost": cost if not at_max else None,
                "can_afford": can_afford,
                "at_max_level": at_max,
                "total_effect": upgrade.calculate_total_effect(current_level)
            })
        
        return upgrades_list

    def get_statistics(self) -> Dict[str, Any]:
        """Get prestige system statistics.
        
        Returns:
            Dictionary containing statistics
        """
        return self._stats.copy()

    def reset_statistics(self) -> None:
        """Reset prestige system statistics."""
        self._stats = {
            "total_prestiges": 0,
            "total_prestige_points_earned": 0,
            "total_prestige_points_spent": 0
        }
