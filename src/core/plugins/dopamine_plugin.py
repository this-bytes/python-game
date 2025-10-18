"""DopaminePlugin - Addictive Gameplay Mechanics System.

Plugin wrapper for DopamineSystem providing combo chains, risk/reward contracts,
and instant gratification feedback to transform clicking into strategic, rewarding gameplay.

Features:
- Combo multipliers for consecutive actions
- Risk/reward contracts for high-stakes incidents
- Perfect completion bonuses
- Visual/audio feedback tiers
- Session statistics tracking
"""

from typing import Dict, Any, List, Optional
from src.core.game_system import GameSystem
from src.core.dopamine_system import DopamineSystem, RiskRewardContract
from src.core.event_bus import get_event_bus, Event


class DopaminePlugin(GameSystem):
    """Plugin wrapper for DopamineSystem with GameSystem integration."""

    def __init__(self):
        """Initialize dopamine plugin."""
        super().__init__()
        self._dopamine_system = DopamineSystem()
        self._event_bus = get_event_bus()
        self._subscription_ids: List[str] = []

    def get_name(self) -> str:
        """Get plugin name."""
        return "DopaminePlugin"

    def get_feature_id(self) -> str:
        """Get feature flag ID for dopamine system."""
        return "dopamine_system"

    def initialize(self, game_state) -> None:
        """Initialize dopamine plugin.

        Args:
            game_state: Current game state
        """
        # Subscribe to relevant events
        self._subscription_ids = [
            self._event_bus.subscribe("incident_assigned", self._on_incident_assigned),
            self._event_bus.subscribe("incident_completed", self._on_incident_completed),
            self._event_bus.subscribe("dopamine_offer_risk_contract", self._on_offer_risk_contract),
            self._event_bus.subscribe("dopamine_apply_risk_contract", self._on_apply_risk_contract),
        ]

    def update(self, game_state, delta_time: float) -> None:
        """Update dopamine plugin.

        Args:
            game_state: Current game state
            delta_time: Time elapsed since last update
        """
        # Update combo timer for expiration
        self._dopamine_system.update(delta_time)

    def shutdown(self, game_state) -> None:
        """Shutdown dopamine plugin.

        Args:
            game_state: Current game state
        """
        # Unsubscribe from all events
        for subscription_id in self._subscription_ids:
            self._event_bus.unsubscribe(subscription_id)
        self._subscription_ids.clear()

    def save_state(self, game_state) -> Dict[str, Any]:
        """Save dopamine plugin state.

        Args:
            game_state: Current game state

        Returns:
            State data to save
        """
        # Convert dopamine system state to serializable format
        return {
            "combo_state": {
                "current_combo": self._dopamine_system.combo_state.current_combo,
                "max_combo": self._dopamine_system.combo_state.max_combo,
                "combo_timer": self._dopamine_system.combo_state.combo_timer,
                "last_action_time": self._dopamine_system.combo_state.last_action_time,
            },
            "session_stats": self._dopamine_system.session_stats.copy(),
        }

    def load_state(self, game_state, state_data: Dict[str, Any]) -> None:
        """Load dopamine plugin state.

        Args:
            game_state: Current game state
            state_data: Previously saved state data
        """
        # Restore dopamine system state
        combo_data = state_data.get("combo_state", {})
        self._dopamine_system.combo_state.current_combo = combo_data.get("current_combo", 0)
        self._dopamine_system.combo_state.max_combo = combo_data.get("max_combo", 0)
        self._dopamine_system.combo_state.combo_timer = combo_data.get("combo_timer", 0.0)
        self._dopamine_system.combo_state.last_action_time = combo_data.get("last_action_time", 0.0)

        session_stats = state_data.get("session_stats", {})
        self._dopamine_system.session_stats.update(session_stats)

    def _on_incident_assigned(self, event: Event) -> None:
        """Handle incident assignment event.

        Args:
            event: Incident assignment event
        """
        incident = event.data.get("incident")
        specialist = event.data.get("specialist")

        if incident and specialist:
            feedback = self._dopamine_system.register_incident_assignment(incident, specialist)

            # Publish combo feedback event
            self._event_bus.publish("combo_feedback", {
                "combo_count": feedback["combo_count"],
                "multiplier": feedback["multiplier"],
                "is_milestone": feedback["is_milestone"],
                "reward_tier": feedback["reward_tier"].value,
                "message": feedback["message"],
            })

    def _on_incident_completed(self, event: Event) -> None:
        """Handle incident completion event.

        Args:
            event: Incident completion event
        """
        incident = event.data.get("incident")
        specialist = event.data.get("specialist")
        success = event.data.get("success", True)
        is_sla_met = event.data.get("is_sla_met", True)

        if incident and specialist:
            feedback = self._dopamine_system.register_incident_completion(
                incident, specialist, success, is_sla_met
            )

            # Publish completion feedback event
            self._event_bus.publish("completion_feedback", {
                "final_reward": feedback["final_reward"],
                "final_xp": feedback["final_xp"],
                "multiplier": feedback["multiplier"],
                "is_perfect": feedback["is_perfect"],
                "reward_tier": feedback["reward_tier"].value,
                "message": feedback["message"],
                "combo_count": feedback["combo_count"],
                "combo_broken": feedback.get("combo_broken", False),
            })

    def _on_offer_risk_contract(self, event: Event) -> None:
        """Handle offer risk contract event.

        Args:
            event: Offer risk contract event
        """
        incident = event.data.get("incident")
        difficulty = event.data.get("difficulty", 1)

        if incident:
            contract = self._dopamine_system.offer_risk_contract(incident, difficulty)

            # Publish contract offer event
            if contract:
                self._event_bus.publish("risk_contract_offered", {
                    "incident_id": getattr(incident, 'id', None),
                    "contract_type": contract.contract_type,
                    "reward_multiplier": contract.reward_multiplier,
                    "failure_penalty": contract.failure_penalty,
                    "description": contract.description,
                    "icon": contract.icon,
                })

    def _on_apply_risk_contract(self, event: Event) -> None:
        """Handle apply risk contract event.

        Args:
            event: Apply risk contract event
        """
        incident = event.data.get("incident")
        contract_type = event.data.get("contract_type")

        if incident and contract_type and contract_type in self._dopamine_system.risk_contracts:
            contract = self._dopamine_system.risk_contracts[contract_type]
            self._dopamine_system.apply_risk_contract(incident, contract)

            # Publish contract applied event
            self._event_bus.publish("risk_contract_applied", {
                "incident_id": getattr(incident, 'id', None),
                "contract_type": contract.contract_type,
                "reward_multiplier": contract.reward_multiplier,
                "failure_penalty": contract.failure_penalty,
            })

    # Public API methods for external access
    def get_combo_multiplier(self) -> float:
        """Get current combo multiplier.

        Returns:
            Current combo multiplier (1.0+)
        """
        return self._dopamine_system.combo_state.get_multiplier()

    def get_combo_count(self) -> int:
        """Get current combo count.

        Returns:
            Current combo count
        """
        return self._dopamine_system.combo_state.current_combo

    def get_max_combo(self) -> int:
        """Get max combo achieved.

        Returns:
            Maximum combo achieved in session
        """
        return self._dopamine_system.combo_state.max_combo

    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics.

        Returns:
            Dictionary of session stats
        """
        return self._dopamine_system.session_stats.copy()

    def offer_risk_contract(self, incident, difficulty: int) -> Optional[RiskRewardContract]:
        """Offer a risk/reward contract for an incident.

        Args:
            incident: Incident object
            difficulty: Incident difficulty (1-5)

        Returns:
            RiskRewardContract if offered, None otherwise
        """
        return self._dopamine_system.offer_risk_contract(incident, difficulty)

    def apply_risk_contract(self, incident, contract: RiskRewardContract) -> None:
        """Apply risk contract modifiers to an incident.

        Args:
            incident: Incident to modify
            contract: Risk contract to apply
        """
        self._dopamine_system.apply_risk_contract(incident, contract)

    def calculate_risk_reward(self, incident, success: bool, is_sla_met: bool) -> int:
        """Calculate final reward for risk contract.

        Args:
            incident: Incident with risk contract
            success: Whether incident was completed successfully
            is_sla_met: Whether SLA was met

        Returns:
            Final reward (positive) or penalty (negative)
        """
        return self._dopamine_system.calculate_risk_reward(incident, success, is_sla_met)

    def get_combo_display_color(self, combo: int) -> tuple[int, int, int]:
        """Get color for combo counter display.

        Args:
            combo: Combo count

        Returns:
            RGB color tuple
        """
        return self._dopamine_system.get_combo_display_color(combo)

    def break_combo(self) -> None:
        """Break the current combo chain."""
        self._dopamine_system.combo_state.break_combo()