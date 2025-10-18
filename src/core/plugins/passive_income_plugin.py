"""PassiveIncomePlugin - Passive Income Management System.

Plugin wrapper for PassiveIncomeSystem providing passive income generation from retainers,
investments, and reputation bonuses. Integrates with game events to automatically apply
passive income and handle investment actions.

Features:
- Contract retainer income from active clients
- Investment returns with risk/reward mechanics
- Reputation-based income multipliers
- Investment management (invest/withdraw)
- Statistics tracking
"""

from typing import Dict, Any, List, Optional
from src.core.game_system import GameSystem
from src.core.passive_income_system import PassiveIncomeSystem
from src.core.event_bus import get_event_bus, Event


class PassiveIncomePlugin(GameSystem):
    """Plugin wrapper for PassiveIncomeSystem with GameSystem integration."""

    def __init__(self):
        """Initialize passive income plugin."""
        super().__init__()
        self._passive_income_system = None  # Will be initialized with game config
        self._event_bus = get_event_bus()
        self._subscription_ids: List[str] = []
        self._last_update_time = 0.0

    def get_name(self) -> str:
        """Get plugin name."""
        return "PassiveIncomePlugin"

    def get_feature_id(self) -> str:
        """Get feature flag ID for passive income system."""
        return "passive_income_system"

    def initialize(self, game_state) -> None:
        """Initialize passive income plugin.

        Args:
            game_state: Current game state
        """
        # Initialize passive income system with game config
        game_config = getattr(game_state, 'config', {})
        self._passive_income_system = PassiveIncomeSystem(game_config)

        # Subscribe to relevant events
        self._subscription_ids = [
            self._event_bus.subscribe("passive_income_apply", self._on_apply_passive_income),
            self._event_bus.subscribe("investment_make", self._on_make_investment),
            self._event_bus.subscribe("investment_withdraw", self._on_withdraw_investment),
        ]

    def update(self, game_state, delta_time: float) -> None:
        """Update passive income plugin.

        Args:
            game_state: Current game state
            delta_time: Time elapsed since last update
        """
        # Apply passive income periodically (every 60 seconds)
        current_time = getattr(game_state, 'game_time', 0.0)
        if current_time - self._last_update_time >= 60.0:
            self._apply_passive_income(game_state, current_time - self._last_update_time)
            self._last_update_time = current_time

    def shutdown(self, game_state) -> None:
        """Shutdown passive income plugin.

        Args:
            game_state: Current game state
        """
        # Unsubscribe from all events
        for subscription_id in self._subscription_ids:
            self._event_bus.unsubscribe(subscription_id)
        self._subscription_ids.clear()

    def save_state(self, game_state) -> Dict[str, Any]:
        """Save passive income plugin state.

        Args:
            game_state: Current game state

        Returns:
            State data to save
        """
        state_data = {
            "last_update_time": self._last_update_time,
        }

        # Include passive income statistics
        if self._passive_income_system:
            state_data["statistics"] = self._passive_income_system.get_statistics()

        return state_data

    def load_state(self, game_state, state_data: Dict[str, Any]) -> None:
        """Load passive income plugin state.

        Args:
            game_state: Current game state
            state_data: Previously saved state data
        """
        self._last_update_time = state_data.get("last_update_time", 0.0)

        # Restore statistics if available
        if self._passive_income_system and "statistics" in state_data:
            # Note: Statistics are stored in the system, but we don't restore them
            # as they represent historical data that should persist
            pass

    def _apply_passive_income(self, game_state, delta_time: float) -> None:
        """Apply passive income to game state.

        Args:
            game_state: Current game state
            delta_time: Time elapsed since last update
        """
        if self._passive_income_system:
            result = self._passive_income_system.apply_passive_income(game_state, delta_time)

            # Publish passive income applied event
            if result["total_income"] != 0:
                self._event_bus.publish("passive_income_applied", {
                    "retainer_income": result["retainer_income"],
                    "reputation_multiplier": result["reputation_multiplier"],
                    "reputation_bonus": result["reputation_bonus"],
                    "investment_return": result["investment_return"],
                    "total_income": result["total_income"],
                    "delta_time": delta_time,
                })

    def _on_apply_passive_income(self, event: Event) -> None:
        """Handle apply passive income event.

        Args:
            event: Apply passive income event
        """
        game_state = event.data.get("game_state")
        delta_time = event.data.get("delta_time", 60.0)

        if game_state:
            self._apply_passive_income(game_state, delta_time)

    def _on_make_investment(self, event: Event) -> None:
        """Handle make investment event.

        Args:
            event: Make investment event
        """
        game_state = event.data.get("game_state")
        investment_type = event.data.get("investment_type")
        amount = event.data.get("amount")

        if game_state and investment_type and amount and self._passive_income_system:
            result = self._passive_income_system.invest(game_state, investment_type, amount)

            # Publish investment made event
            self._event_bus.publish("investment_made", {
                "success": result.get("success", False),
                "investment_type": investment_type,
                "amount": amount,
                "error": result.get("error"),
                "total_invested": result.get("total_invested"),
                "return_rate": result.get("return_rate"),
                "risk": result.get("risk"),
            })

    def _on_withdraw_investment(self, event: Event) -> None:
        """Handle withdraw investment event.

        Args:
            event: Withdraw investment event
        """
        game_state = event.data.get("game_state")
        investment_type = event.data.get("investment_type")
        amount = event.data.get("amount")

        if game_state and investment_type and amount and self._passive_income_system:
            result = self._passive_income_system.withdraw(game_state, investment_type, amount)

            # Publish investment withdrawn event
            self._event_bus.publish("investment_withdrawn", {
                "success": result.get("success", False),
                "investment_type": investment_type,
                "amount": amount,
                "error": result.get("error"),
                "remaining": result.get("remaining"),
            })

    # Public API methods for external access
    def calculate_retainer_income(self, clients: List, delta_time: float) -> float:
        """Calculate retainer income from active client contracts.

        Args:
            clients: List of active clients
            delta_time: Time elapsed since last calculation (in seconds)

        Returns:
            Total retainer income for the time period
        """
        if self._passive_income_system:
            return self._passive_income_system.calculate_retainer_income(clients, delta_time)
        return 0.0

    def calculate_investment_returns(self, investments: Dict[str, float], delta_time: float) -> float:
        """Calculate returns (or losses) from investments.

        Args:
            investments: Dictionary mapping investment type to amount invested
            delta_time: Time elapsed since last calculation (in seconds)

        Returns:
            Net return (positive for gains, negative for losses)
        """
        if self._passive_income_system:
            return self._passive_income_system.calculate_investment_returns(investments, delta_time)
        return 0.0

    def calculate_reputation_bonus(self, clients: List) -> float:
        """Calculate passive income multiplier based on client reputation.

        Args:
            clients: List of clients

        Returns:
            Reputation bonus multiplier (e.g., 1.1 for 10% bonus)
        """
        if self._passive_income_system:
            return self._passive_income_system.calculate_reputation_bonus(clients)
        return 1.0

    def apply_passive_income(self, game_state, delta_time: float) -> Dict[str, Any]:
        """Apply all passive income sources to game state.

        Args:
            game_state: Current game state
            delta_time: Time elapsed since last update (in seconds)

        Returns:
            Dictionary containing breakdown of passive income
        """
        if self._passive_income_system:
            return self._passive_income_system.apply_passive_income(game_state, delta_time)
        return {"total_income": 0.0}

    def invest(self, game_state, investment_type: str, amount: float) -> Dict[str, Any]:
        """Make an investment.

        Args:
            game_state: Current game state
            investment_type: Type of investment (low_risk, medium_risk, high_risk)
            amount: Amount to invest

        Returns:
            Dictionary containing investment result
        """
        if self._passive_income_system:
            return self._passive_income_system.invest(game_state, investment_type, amount)
        return {"success": False, "error": "Passive income system not initialized"}

    def withdraw(self, game_state, investment_type: str, amount: float) -> Dict[str, Any]:
        """Withdraw from an investment.

        Args:
            game_state: Current game state
            investment_type: Type of investment
            amount: Amount to withdraw

        Returns:
            Dictionary containing withdrawal result
        """
        if self._passive_income_system:
            return self._passive_income_system.withdraw(game_state, investment_type, amount)
        return {"success": False, "error": "Passive income system not initialized"}

    def get_statistics(self) -> Dict[str, Any]:
        """Get passive income statistics.

        Returns:
            Dictionary containing statistics
        """
        if self._passive_income_system:
            return self._passive_income_system.get_statistics()
        return {}

    def reset_statistics(self) -> None:
        """Reset passive income statistics."""
        if self._passive_income_system:
            self._passive_income_system.reset_statistics()