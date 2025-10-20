"""Economy system for managing market events, pricing dynamics, and financial management."""

import random
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from src.core.event_bus import get_event_bus, Event
from src.models.game_state import GameState


@dataclass
class MarketEvent:
    """Represents an active market event affecting the economy."""
    event_id: str
    name: str
    description: str
    event_type: str
    start_time: float
    duration: float
    effects: Dict[str, float]
    active: bool = True

    def is_expired(self, current_time: float) -> bool:
        """Check if the market event has expired."""
        return current_time >= self.start_time + self.duration

    def get_remaining_time(self, current_time: float) -> float:
        """Get remaining time for this event."""
        return max(0, self.start_time + self.duration - current_time)


@dataclass
class Investment:
    """Represents an investment made by the player."""
    investment_id: str
    investment_type: str
    amount_invested: float
    investment_time: float
    expected_return_rate: float
    volatility: float
    current_value: float = field(init=False)

    def __post_init__(self):
        self.current_value = self.amount_invested

    def update_value(self, time_elapsed: float, market_multiplier: float = 1.0):
        """Update investment value based on time and market conditions."""
        # Simple compound growth with volatility
        growth_rate = self.expected_return_rate * market_multiplier
        volatility_factor = random.gauss(1.0, self.volatility)

        time_factor = time_elapsed / (365 * 24 * 3600)  # Annualized
        self.current_value *= (1 + growth_rate * time_factor) * volatility_factor

    def calculate_profit_loss(self) -> float:
        """Calculate profit or loss on this investment."""
        return self.current_value - self.amount_invested


class EconomySystem:
    """Manages economic aspects of the game including market events, pricing, and investments."""

    def __init__(self, economy_config: Dict[str, Any]):
        """Initialize economy system with configuration."""
        self.config = economy_config
        self.event_bus = get_event_bus()

        # Market state
        self.active_events: List[MarketEvent] = []
        self.event_cooldowns: Dict[str, float] = {}
        self.market_multiplier = 1.0

        # Financial state
        self.investments: List[Investment] = []
        self.last_update_time = time.time()

        # Economic indicators
        self.inflation_rate = self.config["economy_config"]["inflation_rate"]
        self.market_volatility = self.config["economy_config"]["market_volatility"]

        # Subscribe to events
        self.event_bus.subscribe("incident_completed", self._on_incident_completed)
        self.event_bus.subscribe("specialist_hired", self._on_specialist_hired)
        self.event_bus.subscribe("contract_signed", self._on_contract_signed)

    def update(self, game_state: GameState, delta_time: float) -> None:
        """Update economy system state."""
        current_time = time.time()

        # Update market events
        self._update_market_events(current_time)

        # Update investments
        self._update_investments(delta_time)

        # Potentially trigger new market events
        self._check_for_new_events(game_state, current_time)

        # Update market multiplier based on active events
        self._calculate_market_multiplier()

        self.last_update_time = current_time

    def calculate_specialist_hiring_cost(self, specialist_level: int, reputation: float) -> float:
        """Calculate cost to hire a specialist."""
        pricing = self.config["pricing_dynamics"]["specialist_hiring"]

        base_cost = pricing["base_cost"]
        level_multiplier = pricing["level_multiplier"] ** (specialist_level - 1)
        reputation_discount = pricing["reputation_discount"] * reputation
        market_premium = pricing["market_premium"] * self.market_multiplier

        cost = base_cost * level_multiplier * (1 - reputation_discount) * (1 + market_premium)
        return max(base_cost, cost)  # Minimum cost

    def calculate_equipment_cost(self, base_cost: float, rarity: str) -> float:
        """Calculate cost of equipment with market fluctuations."""
        pricing = self.config["pricing_dynamics"]["equipment_costs"]

        rarity_multiplier = pricing["rarity_premium"].get(rarity, 1.0)
        market_fluctuation = random.gauss(1.0, pricing["market_fluctuation"])

        cost = base_cost * rarity_multiplier * market_fluctuation * self.market_multiplier
        return max(base_cost, cost)

    def calculate_contract_value(self, contract_type: str, negotiation_skill: float = 0.0) -> float:
        """Calculate value of a contract with negotiation."""
        pricing = self.config["pricing_dynamics"]["contract_pricing"]

        base_rate = pricing["base_rates"].get(contract_type, 1000)
        negotiation_range = pricing["negotiation_range"]

        # Negotiation affects final price within range
        negotiation_multiplier = negotiation_range["min_multiplier"] + (
            negotiation_range["max_multiplier"] - negotiation_range["min_multiplier"]
        ) * negotiation_skill

        final_value = base_rate * negotiation_multiplier * self.market_multiplier
        return final_value

    def make_investment(self, investment_type: str, amount: float) -> Optional[Investment]:
        """Make a new investment."""
        investment_config = None
        for inv in self.config["investment_system"]["investment_options"]:
            if inv["id"] == investment_type:
                investment_config = inv
                break

        if not investment_config or amount < investment_config["min_investment"]:
            return None

        investment = Investment(
            investment_id=f"inv_{investment_type}_{int(time.time())}",
            investment_type=investment_type,
            amount_invested=amount,
            investment_time=time.time(),
            expected_return_rate=investment_config["base_return_rate"],
            volatility=investment_config["volatility"]
        )

        self.investments.append(investment)
        return investment

    def get_total_investment_value(self) -> float:
        """Get total current value of all investments."""
        return sum(inv.current_value for inv in self.investments)

    def get_active_events(self) -> List[MarketEvent]:
        """Get list of currently active market events."""
        return [event for event in self.active_events if event.active]

    def get_market_summary(self) -> Dict[str, Any]:
        """Get summary of current market conditions."""
        return {
            "market_multiplier": self.market_multiplier,
            "active_events": len(self.get_active_events()),
            "total_investments": len(self.investments),
            "investment_value": self.get_total_investment_value(),
            "inflation_rate": self.inflation_rate
        }

    def _update_market_events(self, current_time: float) -> None:
        """Update active market events and remove expired ones."""
        expired_events = []
        for event in self.active_events:
            if event.is_expired(current_time):
                event.active = False
                expired_events.append(event)

        # Remove expired events
        for event in expired_events:
            self.active_events.remove(event)
            self.event_bus.publish("market_event_ended", {
                "event_id": event.event_id,
                "name": event.name
            })

    def _update_investments(self, delta_time: float) -> None:
        """Update investment values."""
        for investment in self.investments:
            investment.update_value(delta_time, self.market_multiplier)

    def _check_for_new_events(self, game_state: GameState, current_time: float) -> None:
        """Check if new market events should be triggered."""
        # Check cooldowns
        for event_type, cooldown_end in list(self.event_cooldowns.items()):
            if current_time >= cooldown_end:
                del self.event_cooldowns[event_type]

        # Random chance to trigger event
        if random.random() < 0.001:  # 0.1% chance per update
            self._trigger_random_event(current_time)

    def _trigger_random_event(self, current_time: float) -> None:
        """Trigger a random market event."""
        event_categories = self.config["market_events"]["event_categories"]
        weights = self.config["market_events"]["event_probability_weights"]

        # Select event type
        event_types = list(weights.keys())
        probabilities = [weights[et] for et in event_types]
        selected_type = random.choices(event_types, weights=probabilities)[0]

        if selected_type == "random_event":
            return  # Skip random events for now

        # Find matching category
        category = None
        for cat in event_categories:
            if cat["id"] == selected_type:
                category = cat
                break

        if not category:
            return

        # Check cooldown
        if selected_type in self.event_cooldowns:
            return

        # Create event
        duration = random.uniform(category["duration_range"][0], category["duration_range"][1])

        event = MarketEvent(
            event_id=f"event_{selected_type}_{int(current_time)}",
            name=category["name"],
            description=category.get("description", ""),
            event_type=selected_type,
            start_time=current_time,
            duration=duration,
            effects=category["effects"]
        )

        self.active_events.append(event)

        # Set cooldown
        cooldown_config = self.config["market_events"]["cooldown_periods"]
        base_cooldown = cooldown_config["event_type_cooldowns"].get(selected_type, 3600)
        self.event_cooldowns[selected_type] = current_time + base_cooldown

        # Publish event
        self.event_bus.publish("market_event_started", {
            "event_id": event.event_id,
            "name": event.name,
            "description": event.description,
            "effects": event.effects,
            "duration": event.duration
        })

    def _calculate_market_multiplier(self) -> None:
        """Calculate current market multiplier based on active events."""
        base_multiplier = 1.0

        for event in self.get_active_events():
            for effect_key, effect_value in event.effects.items():
                if "multiplier" in effect_key:
                    base_multiplier *= effect_value

        self.market_multiplier = base_multiplier

    def _on_incident_completed(self, event: Event) -> None:
        """Handle incident completion for economic effects."""
        # Could affect market based on incident outcomes
        pass

    def _on_specialist_hired(self, event: Event) -> None:
        """Handle specialist hiring for economic effects."""
        # Could affect supply/demand
        pass

    def _on_contract_signed(self, event: Event) -> None:
        """Handle contract signing for economic effects."""
        # Could affect market confidence
        pass