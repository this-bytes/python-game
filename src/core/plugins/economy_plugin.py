"""Economy plugin for managing market events, pricing dynamics, and financial management."""

import json
from typing import Dict, Any

from src.core.game_system import GameSystem
from src.core.economy_system import EconomySystem


class EconomyPlugin(GameSystem):
    """Plugin wrapper for the economy system."""

    def __init__(self):
        """Initialize economy plugin."""
        super().__init__()
        self.economy_system: EconomySystem | None = None

    def get_name(self) -> str:
        """Get plugin name."""
        return "EconomyPlugin"

    def get_feature_id(self) -> str:
        """Get feature flag ID."""
        return "economy_system"

    def initialize(self, game_state) -> None:
        """Initialize economy plugin with game state."""
        # Load economy configuration
        try:
            with open("data/economy.json", 'r') as f:
                economy_config = json.load(f)
        except FileNotFoundError:
            # Fallback to basic config if file doesn't exist
            economy_config = self._get_default_config()

        self.economy_system = EconomySystem(economy_config)

        # Subscribe to events if needed
        # self._event_bus.subscribe("game_update", self._on_game_update)

    def update(self, game_state, delta_time: float) -> None:
        """Update economy plugin."""
        if self.economy_system:
            self.economy_system.update(game_state, delta_time)

    def shutdown(self, game_state) -> None:
        """Shutdown economy plugin and cleanup resources."""
        # Unsubscribe from events if needed
        # self._event_bus.unsubscribe("game_update", self._on_game_update)
        pass

    def save_state(self, game_state) -> Dict[str, Any]:
        """Save economy plugin state."""
        if not self.economy_system:
            return {}

        return {
            "active_events": [
                {
                    "event_id": event.event_id,
                    "name": event.name,
                    "description": event.description,
                    "event_type": event.event_type,
                    "start_time": event.start_time,
                    "duration": event.duration,
                    "effects": event.effects,
                    "active": event.active
                }
                for event in self.economy_system.active_events
            ],
            "event_cooldowns": self.economy_system.event_cooldowns,
            "investments": [
                {
                    "investment_id": inv.investment_id,
                    "investment_type": inv.investment_type,
                    "amount_invested": inv.amount_invested,
                    "investment_time": inv.investment_time,
                    "expected_return_rate": inv.expected_return_rate,
                    "volatility": inv.volatility,
                    "current_value": inv.current_value
                }
                for inv in self.economy_system.investments
            ],
            "market_multiplier": self.economy_system.market_multiplier,
            "last_update_time": self.economy_system.last_update_time
        }

    def load_state(self, game_state, state_data: Dict[str, Any]) -> None:
        """Load economy plugin state."""
        if not self.economy_system:
            return

        # Load active events
        from src.core.economy_system import MarketEvent
        self.economy_system.active_events = [
            MarketEvent(**event_data)
            for event_data in state_data.get("active_events", [])
        ]

        # Load cooldowns
        self.economy_system.event_cooldowns = state_data.get("event_cooldowns", {})

        # Load investments
        from src.core.economy_system import Investment
        self.economy_system.investments = [
            Investment(**inv_data)
            for inv_data in state_data.get("investments", [])
        ]

        # Load other state
        self.economy_system.market_multiplier = state_data.get("market_multiplier", 1.0)
        self.economy_system.last_update_time = state_data.get("last_update_time", 0.0)

    def get_economy_system(self) -> EconomySystem | None:
        """Get the underlying economy system for external access."""
        return self.economy_system

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default economy configuration if file doesn't exist."""
        return {
            "economy_config": {
                "base_currency": "credits",
                "starting_balance": 5000,
                "inflation_rate": 0.001,
                "market_volatility": 0.1
            },
            "pricing_dynamics": {
                "specialist_hiring": {
                    "base_cost": 2000,
                    "level_multiplier": 1.5,
                    "reputation_discount": 0.02,
                    "market_premium": 0.1
                }
            },
            "market_events": {
                "event_categories": [],
                "event_probability_weights": {},
                "cooldown_periods": {
                    "min_cooldown": 1800,
                    "max_cooldown": 7200
                }
            },
            "financial_management": {
                "income_sources": {},
                "expenses": {},
                "taxes_and_fees": {}
            },
            "investment_system": {
                "investment_options": [],
                "investment_mechanics": {}
            }
        }