"""Budget plugin for managing company finances.

Integrates budget calculations into the plugin system and game loop,
handling monthly revenue/expense processing, bankruptcy detection,
and forced downsizing.
"""

import json
import logging
from typing import Dict, Any

from src.core.game_system import GameSystem
from src.core.budget_system import (
    calculate_monthly_revenue,
    calculate_monthly_expenses,
    process_monthly_budget,
    check_game_over,
)
from src.core.event_bus import get_event_bus

logger = logging.getLogger(__name__)


class BudgetPlugin(GameSystem):
    """Plugin for managing company budget and financial state.
    
    Responsibilities:
        - Calculate monthly revenue from active clients
        - Calculate monthly operating expenses
        - Apply monthly profit/loss to company reserves
        - Detect bankruptcy and critical conditions
        - Force downsizing if necessary
        - Trigger game over if required
    """
    
    def __init__(self):
        """Initialize budget plugin."""
        super().__init__()
        self._event_bus = get_event_bus()
        self._budget_config = {}
        self._last_month_processed = -1
    
    def get_name(self) -> str:
        """Get plugin name."""
        return "BudgetPlugin"
    
    def get_feature_id(self) -> str:
        """Get feature flag ID."""
        return "budget_system"
    
    def initialize(self, game_state) -> None:
        """Initialize budget plugin with game state.
        
        Loads budget configuration from JSON and sets up initial state.
        
        Args:
            game_state: Current game state
        """
        logger.info("[BUDGET_PLUGIN] Initializing budget system")
        
        # Load budget configuration
        try:
            with open("data/game_config.json", 'r') as f:
                config = json.load(f)
                self._budget_config = config.get("budget", {})
                logger.info(f"[BUDGET_PLUGIN] Loaded budget config: {self._budget_config}")
        except FileNotFoundError:
            logger.warning("[BUDGET_PLUGIN] game_config.json not found, using defaults")
            self._budget_config = self._get_default_config()
        
        # Initialize month tracking
        self._last_month_processed = -1
        
        # Subscribe to events
        self._event_bus.subscribe("month_ended", self._on_month_ended)
        logger.info("[BUDGET_PLUGIN] Initialization complete")
    
    def update(self, game_state, delta_time: float) -> None:
        """Update budget plugin.
        
        This is called every frame, but we only process on month boundaries.
        
        Args:
            game_state: Current game state
            delta_time: Time elapsed since last frame
        """
        # Check if we're at a new month boundary
        # This would typically be triggered by event, but having this as backup
        pass
    
    def shutdown(self, game_state) -> None:
        """Shutdown budget plugin and cleanup resources.
        
        Args:
            game_state: Current game state
        """
        logger.info("[BUDGET_PLUGIN] Shutting down")
        self._event_bus.unsubscribe("month_ended")
    
    def save_state(self, game_state) -> Dict[str, Any]:
        """Save budget plugin state for persistence.
        
        Args:
            game_state: Current game state
            
        Returns:
            Dictionary containing budget state to save
        """
        return {
            "total_reserves": game_state.budget.total_reserves,
            "monthly_revenue": game_state.budget.monthly_revenue,
            "monthly_expenses": game_state.budget.monthly_expenses,
            "revenue_history": game_state.budget.revenue_history,
            "expense_history": game_state.budget.expense_history,
            "profit_history": game_state.budget.profit_history,
            "last_month_processed": self._last_month_processed,
        }
    
    def load_state(self, game_state, state_data: Dict[str, Any]) -> None:
        """Load budget plugin state from saved data.
        
        Args:
            game_state: Current game state
            state_data: Previously saved state data
        """
        logger.info("[BUDGET_PLUGIN] Loading saved budget state")
        
        game_state.budget.total_reserves = state_data.get("total_reserves", 50000.0)
        game_state.budget.monthly_revenue = state_data.get("monthly_revenue", 0.0)
        game_state.budget.monthly_expenses = state_data.get("monthly_expenses", 0.0)
        game_state.budget.revenue_history = state_data.get("revenue_history", [])
        game_state.budget.expense_history = state_data.get("expense_history", [])
        game_state.budget.profit_history = state_data.get("profit_history", [])
        self._last_month_processed = state_data.get("last_month_processed", -1)
    
    def _on_month_ended(self, event: Any) -> None:
        """Handle month_ended event.
        
        Triggered when a game month ends. This is the hook to process
        monthly budget calculations.
        
        Args:
            event: Event data containing game_state
        """
        game_state = event.data.get("game_state")
        
        if game_state is None:
            logger.error("[BUDGET_PLUGIN] month_ended event missing game_state")
            return
        
        # Avoid double-processing the same month
        current_month = getattr(game_state, 'current_month', 0)
        if current_month == self._last_month_processed:
            logger.debug(f"[BUDGET_PLUGIN] Already processed month {current_month}, skipping")
            return
        
        logger.info(f"[BUDGET_PLUGIN] Processing end-of-month budget for month {current_month}")
        
        # Process monthly budget
        budget_result = process_monthly_budget(
            game_state,
            game_state.specialists,
            game_state.clients,
            self._budget_config
        )
        
        self._last_month_processed = current_month
        
        # Emit budget_updated event
        self._event_bus.publish("budget_updated", {
            "game_state": game_state,
            "budget_result": budget_result,
        })
        
        # Check for game over conditions
        is_game_over, reason = check_game_over(game_state)
        
        if is_game_over:
            logger.error(f"[BUDGET_PLUGIN] GAME OVER - Reason: {reason}")
            game_state.game_over = True
            game_state.game_over_reason = reason
            
            self._event_bus.publish("game_over", {
                "game_state": game_state,
                "reason": reason,
                "month": current_month,
                "final_reserves": game_state.budget.total_reserves,
            })
        elif budget_result["is_critical"]:
            logger.warning(
                f"[BUDGET_PLUGIN] CRITICAL CONDITION - "
                f"Reserves: ${budget_result['reserves']:.0f}, "
                f"Runway: {budget_result['months_runway']:.1f} months"
            )
            
            self._event_bus.publish("budget_critical", {
                "game_state": game_state,
                "months_runway": budget_result["months_runway"],
            })
        else:
            logger.info(
                f"[BUDGET_PLUGIN] Month {current_month} complete - "
                f"Reserves: ${budget_result['reserves']:.0f}, "
                f"Profit: ${budget_result['profit']:+.0f}"
            )
    
    def _get_default_config(self) -> Dict[str, float]:
        """Get default budget configuration.
        
        Returns:
            Dictionary with default budget parameters
        """
        return {
            "specialist_salary_per_month": 3000.0,
            "infrastructure_base": 2000.0,
            "infrastructure_cost_per_client": 500.0,
            "software_license_base": 1000.0,
            "software_license_per_specialist": 200.0,
            "fixed_overhead": 1500.0,
        }
