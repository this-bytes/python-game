"""Prestige System - Restart with Permanent Upgrades

The prestige system lets players reset their progress in exchange for
permanent bonuses that make future runs faster and more profitable.

Prestige Mechanic:
- Unlock at $100k revenue milestone
- Exchange current progress for Prestige Points (PP)
- PP based on total revenue generated (logarithmic curve)
- Spend PP on permanent upgrades
- Keep prestige upgrades across resets

Prestige Upgrades:
- XP multipliers (faster specialist leveling)
- Money multipliers (more profitable contracts)
- Starting specialists (begin with more staff)
- Starting money (skip early grind)
- Auto-assignment unlocks (better automation)
- SLA time extensions (more breathing room)
- Incident quality (better rewards per incident)

Strategy:
- Early prestige = fewer PP but faster iteration
- Late prestige = more PP but slower single run
- Finding optimal prestige timing is the meta-game
"""

from typing import Dict, Any, List
import logging
import math

from src.core.plugin_system import GameSystem

logger = logging.getLogger(__name__)


class PrestigeSystem(GameSystem):
    """Prestige system for strategic resets and permanent progression."""
    
    # Prestige unlock threshold
    UNLOCK_REVENUE = 100_000  # $100k total revenue
    
    # PP calculation: PP = floor(log10(revenue / 10000))
    # Examples: $100k -> 1 PP, $1M -> 2 PP, $10M -> 3 PP
    PP_BASE_DIVISOR = 10_000
    
    def __init__(self, event_bus):
        super().__init__(event_bus, "prestige_system")
        
        # Prestige state
        self.total_prestige_count = 0
        self.total_prestige_points = 0
        self.available_prestige_points = 0
        
        # Purchased upgrades (persists across prestige)
        self.upgrades = {
            # XP multipliers
            "xp_multiplier_1": 0,  # +10% XP per level (max 10 = +100%)
            "xp_multiplier_2": 0,  # +25% XP per level (max 5 = +125%)
            
            # Money multipliers
            "money_multiplier_1": 0,  # +10% money per level (max 10 = +100%)
            "money_multiplier_2": 0,  # +25% money per level (max 5 = +125%)
            
            # Starting bonuses
            "starting_specialists": 0,  # +1 specialist per level (max 5)
            "starting_money": 0,  # +$5k per level (max 10 = +$50k)
            
            # Quality of life
            "auto_assign_speed": 0,  # Auto-assign higher difficulty (max 5)
            "sla_extension": 0,  # +10% SLA time per level (max 5 = +50%)
            
            # Advanced
            "incident_quality": 0,  # Better incident rewards (max 5)
            "synergy_power": 0,  # Stronger synergy bonuses (max 5)
        }
        
        # Upgrade costs (in PP)
        self.upgrade_costs = {
            "xp_multiplier_1": 1,
            "xp_multiplier_2": 3,
            "money_multiplier_1": 1,
            "money_multiplier_2": 3,
            "starting_specialists": 2,
            "starting_money": 1,
            "auto_assign_speed": 2,
            "sla_extension": 2,
            "incident_quality": 3,
            "synergy_power": 4,
        }
        
        # Upgrade max levels
        self.upgrade_max_levels = {
            "xp_multiplier_1": 10,
            "xp_multiplier_2": 5,
            "money_multiplier_1": 10,
            "money_multiplier_2": 5,
            "starting_specialists": 5,
            "starting_money": 10,
            "auto_assign_speed": 5,
            "sla_extension": 5,
            "incident_quality": 5,
            "synergy_power": 5,
        }
        
        # Current run statistics
        self.current_run_revenue = 0
        self.prestige_unlocked = False
    
    def initialize(self) -> None:
        """Initialize prestige system."""
        logger.info("Initializing Prestige System...")
        
        # Subscribe to money events to track revenue
        self.event_bus.subscribe("money_earned", self._on_money_earned)
        
        # Subscribe to prestige trigger
        self.event_bus.subscribe("prestige_triggered", self._on_prestige)
        
        logger.info("Prestige System initialized")
    
    def update(self, dt: float) -> None:
        """Update prestige system."""
        # Check if prestige should be unlocked
        if not self.prestige_unlocked and self.current_run_revenue >= self.UNLOCK_REVENUE:
            self.prestige_unlocked = True
            self.event_bus.emit("prestige_unlocked", {
                "current_revenue": self.current_run_revenue,
                "potential_pp": self._calculate_prestige_points(self.current_run_revenue)
            })
            logger.info(f"Prestige unlocked at ${self.current_run_revenue:,}")
    
    def shutdown(self) -> None:
        """Shutdown prestige system."""
        logger.info("Shutting down Prestige System...")
        self.event_bus.unsubscribe("money_earned", self._on_money_earned)
        self.event_bus.unsubscribe("prestige_triggered", self._on_prestige)
    
    def get_state(self) -> Dict[str, Any]:
        """Get prestige state for saving."""
        return {
            "total_prestige_count": self.total_prestige_count,
            "total_prestige_points": self.total_prestige_points,
            "available_prestige_points": self.available_prestige_points,
            "upgrades": self.upgrades.copy(),
            "current_run_revenue": self.current_run_revenue,
            "prestige_unlocked": self.prestige_unlocked
        }
    
    def set_state(self, state: Dict[str, Any]) -> None:
        """Restore prestige state."""
        self.total_prestige_count = state.get("total_prestige_count", 0)
        self.total_prestige_points = state.get("total_prestige_points", 0)
        self.available_prestige_points = state.get("available_prestige_points", 0)
        self.upgrades.update(state.get("upgrades", {}))
        self.current_run_revenue = state.get("current_run_revenue", 0)
        self.prestige_unlocked = state.get("prestige_unlocked", False)
    
    def _on_money_earned(self, event_data: Dict[str, Any]) -> None:
        """Track money earned for prestige calculation."""
        amount = event_data.get("amount", 0)
        self.current_run_revenue += amount
    
    def _on_prestige(self, event_data: Dict[str, Any]) -> None:
        """Handle prestige trigger."""
        if not self.prestige_unlocked:
            logger.warning("Prestige triggered but not unlocked yet")
            return
        
        # Calculate PP earned
        pp_earned = self._calculate_prestige_points(self.current_run_revenue)
        
        if pp_earned <= 0:
            logger.warning("Prestige would earn 0 PP, not proceeding")
            return
        
        logger.info(f"Prestiging! Revenue: ${self.current_run_revenue:,}, PP earned: {pp_earned}")
        
        # Award PP
        self.total_prestige_points += pp_earned
        self.available_prestige_points += pp_earned
        self.total_prestige_count += 1
        
        # Reset current run stats
        self.current_run_revenue = 0
        self.prestige_unlocked = False
        
        # Emit prestige complete event
        self.event_bus.emit("prestige_completed", {
            "pp_earned": pp_earned,
            "total_pp": self.total_prestige_points,
            "available_pp": self.available_prestige_points,
            "prestige_count": self.total_prestige_count
        })
        
        # Emit game reset event (other systems handle their own reset)
        self.event_bus.emit("game_reset_requested", {
            "reason": "prestige",
            "prestige_count": self.total_prestige_count
        })
    
    def _calculate_prestige_points(self, revenue: float) -> int:
        """Calculate prestige points based on revenue.
        
        Formula: PP = floor(log10(revenue / 10000))
        This gives logarithmic scaling:
        - $100k -> 1 PP
        - $1M -> 2 PP
        - $10M -> 3 PP
        - $100M -> 4 PP
        
        Args:
            revenue: Total revenue generated
            
        Returns:
            Prestige points earned
        """
        if revenue < self.UNLOCK_REVENUE:
            return 0
        
        return int(math.floor(math.log10(revenue / self.PP_BASE_DIVISOR)))
    
    def purchase_upgrade(self, upgrade_id: str) -> bool:
        """Purchase a prestige upgrade.
        
        Args:
            upgrade_id: ID of upgrade to purchase
            
        Returns:
            True if purchase successful, False otherwise
        """
        if upgrade_id not in self.upgrades:
            logger.error(f"Unknown upgrade: {upgrade_id}")
            return False
        
        # Check if at max level
        current_level = self.upgrades[upgrade_id]
        max_level = self.upgrade_max_levels[upgrade_id]
        if current_level >= max_level:
            logger.warning(f"Upgrade {upgrade_id} already at max level {max_level}")
            return False
        
        # Check if enough PP
        cost = self.upgrade_costs[upgrade_id]
        if self.available_prestige_points < cost:
            logger.warning(f"Not enough PP for {upgrade_id} (have {self.available_prestige_points}, need {cost})")
            return False
        
        # Purchase upgrade
        self.upgrades[upgrade_id] += 1
        self.available_prestige_points -= cost
        
        logger.info(f"Purchased upgrade {upgrade_id} level {self.upgrades[upgrade_id]} for {cost} PP")
        
        # Emit upgrade event
        self.event_bus.emit("prestige_upgrade_purchased", {
            "upgrade_id": upgrade_id,
            "level": self.upgrades[upgrade_id],
            "cost": cost,
            "remaining_pp": self.available_prestige_points
        })
        
        return True
    
    def get_active_bonuses(self) -> Dict[str, float]:
        """Get all active prestige bonuses.
        
        Returns:
            Dictionary of bonus type -> multiplier/value
        """
        bonuses = {}
        
        # XP multipliers
        xp_bonus = (
            self.upgrades["xp_multiplier_1"] * 0.10 +
            self.upgrades["xp_multiplier_2"] * 0.25
        )
        if xp_bonus > 0:
            bonuses["xp_multiplier"] = 1.0 + xp_bonus
        
        # Money multipliers
        money_bonus = (
            self.upgrades["money_multiplier_1"] * 0.10 +
            self.upgrades["money_multiplier_2"] * 0.25
        )
        if money_bonus > 0:
            bonuses["money_multiplier"] = 1.0 + money_bonus
        
        # Starting bonuses
        if self.upgrades["starting_specialists"] > 0:
            bonuses["starting_specialists"] = self.upgrades["starting_specialists"]
        
        if self.upgrades["starting_money"] > 0:
            bonuses["starting_money"] = self.upgrades["starting_money"] * 5000
        
        # Auto-assign difficulty threshold
        if self.upgrades["auto_assign_speed"] > 0:
            bonuses["auto_assign_difficulty"] = 5 + self.upgrades["auto_assign_speed"]
        
        # SLA extension
        sla_bonus = self.upgrades["sla_extension"] * 0.10
        if sla_bonus > 0:
            bonuses["sla_multiplier"] = 1.0 + sla_bonus
        
        # Incident quality
        quality_bonus = self.upgrades["incident_quality"] * 0.10
        if quality_bonus > 0:
            bonuses["incident_quality_multiplier"] = 1.0 + quality_bonus
        
        # Synergy power
        synergy_bonus = self.upgrades["synergy_power"] * 0.10
        if synergy_bonus > 0:
            bonuses["synergy_power_multiplier"] = 1.0 + synergy_bonus
        
        return bonuses
