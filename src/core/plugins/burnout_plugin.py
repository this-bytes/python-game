"""BurnoutPlugin - Specialist Psychological Management System.

Plugin wrapper for BurnoutSystem providing specialist burnout tracking and recovery.
Integrates with game events to automatically track incident assignments and completions.

Features:
- Burnout accumulates: 5% per incident (additional 5% per difficulty level 2+)
- Performance penalty: -2% per burnout level (0-100%)
- Recovery: Rest day = -30%, Vacation = -50-80%, Therapy = clears trauma
- Thresholds: Warn at 60%, critical at 80%, force rest at 95%
"""

from typing import Dict, Any, List
from src.core.game_system import GameSystem
from src.core.burnout_system import BurnoutSystem, SpecialistBurnout
from src.core.event_bus import get_event_bus, Event


class BurnoutPlugin(GameSystem):
    """Plugin wrapper for BurnoutSystem with GameSystem integration."""

    def __init__(self):
        """Initialize burnout plugin."""
        super().__init__()
        self._burnout_system = BurnoutSystem()
        self._event_bus = get_event_bus()
        self._subscription_ids: List[str] = []

    def get_name(self) -> str:
        """Get plugin name."""
        return "BurnoutPlugin"

    def get_feature_id(self) -> str:
        """Get feature flag ID for burnout system."""
        return "burnout_system"

    def initialize(self, game_state) -> None:
        """Initialize burnout plugin.

        Args:
            game_state: Current game state
        """
        # Subscribe to relevant events
        self._subscription_ids = [
            self._event_bus.subscribe("incident_assigned", self._on_incident_assigned),
            self._event_bus.subscribe("incident_completed", self._on_incident_completed),
            self._event_bus.subscribe("specialist_hired", self._on_specialist_hired),
            self._event_bus.subscribe("specialist_rested", self._on_specialist_rested),
            self._event_bus.subscribe("specialist_vacation", self._on_specialist_vacation),
            self._event_bus.subscribe("specialist_therapy", self._on_specialist_therapy),
        ]

    def update(self, game_state, delta_time: float) -> None:
        """Update burnout plugin.

        Args:
            game_state: Current game state
            delta_time: Time elapsed since last update
        """
        # Burnout system is event-driven, no continuous updates needed
        pass

    def shutdown(self, game_state) -> None:
        """Shutdown burnout plugin.

        Args:
            game_state: Current game state
        """
        # Unsubscribe from all events
        for subscription_id in self._subscription_ids:
            self._event_bus.unsubscribe(subscription_id)
        self._subscription_ids.clear()

    def save_state(self, game_state) -> Dict[str, Any]:
        """Save burnout plugin state.

        Args:
            game_state: Current game state

        Returns:
            State data to save
        """
        # Convert burnout system state to serializable format
        state_data = {}
        for specialist_id, burnout in self._burnout_system.specialists.items():
            state_data[specialist_id] = {
                "burnout_level": burnout.burnout_level,
                "failed_incidents": burnout.failed_incidents,
                "last_rest_time": burnout.last_rest_time,
            }
        return state_data

    def load_state(self, game_state, state_data: Dict[str, Any]) -> None:
        """Load burnout plugin state.

        Args:
            game_state: Current game state
            state_data: Previously saved state data
        """
        # Restore burnout system state
        for specialist_id, burnout_data in state_data.items():
            burnout = self._burnout_system.register_specialist(specialist_id)
            burnout.burnout_level = burnout_data.get("burnout_level", 0.0)
            burnout.failed_incidents = burnout_data.get("failed_incidents", 0)
            burnout.last_rest_time = burnout_data.get("last_rest_time", 0.0)

    def _on_incident_assigned(self, event: Event) -> None:
        """Handle incident assignment event.

        Args:
            event: Incident assignment event
        """
        specialist_id = event.data.get("specialist_id")
        incident_difficulty = event.data.get("incident_difficulty", 1)

        if specialist_id:
            allowed, message = self._burnout_system.assign_incident(
                specialist_id, incident_difficulty
            )

            # Publish burnout update event
            self._event_bus.publish("burnout_updated", {
                "specialist_id": specialist_id,
                "burnout_level": self._burnout_system.get_specialist_status(specialist_id)["burnout_level"],
                "message": message,
                "allowed": allowed,
            })

    def _on_incident_completed(self, event: Event) -> None:
        """Handle incident completion event.

        Args:
            event: Incident completion event
        """
        specialist_id = event.data.get("specialist_id")
        success = event.data.get("success", True)

        if specialist_id:
            self._burnout_system.complete_incident(specialist_id, success)

            # Publish burnout update event
            self._event_bus.publish("burnout_updated", {
                "specialist_id": specialist_id,
                "burnout_level": self._burnout_system.get_specialist_status(specialist_id)["burnout_level"],
            })

    def _on_specialist_hired(self, event: Event) -> None:
        """Handle specialist hired event.

        Args:
            event: Specialist hired event
        """
        specialist_id = event.data.get("specialist_id")
        if specialist_id:
            self._burnout_system.register_specialist(specialist_id)

    def _on_specialist_rested(self, event: Event) -> None:
        """Handle specialist rest event.

        Args:
            event: Specialist rest event
        """
        specialist_id = event.data.get("specialist_id")
        if specialist_id:
            success, message = self._burnout_system.take_rest_day(specialist_id)

            # Publish burnout update event
            self._event_bus.publish("burnout_updated", {
                "specialist_id": specialist_id,
                "burnout_level": self._burnout_system.get_specialist_status(specialist_id)["burnout_level"],
                "message": message,
                "action": "rest",
            })

    def _on_specialist_vacation(self, event: Event) -> None:
        """Handle specialist vacation event.

        Args:
            event: Specialist vacation event
        """
        specialist_id = event.data.get("specialist_id")
        days = event.data.get("days", 1)
        cost_per_day = event.data.get("cost_per_day", 100)

        if specialist_id:
            success, message = self._burnout_system.take_vacation(
                specialist_id, days, cost_per_day
            )

            # Publish burnout update event
            self._event_bus.publish("burnout_updated", {
                "specialist_id": specialist_id,
                "burnout_level": self._burnout_system.get_specialist_status(specialist_id)["burnout_level"],
                "message": message,
                "action": "vacation",
                "days": days,
            })

    def _on_specialist_therapy(self, event: Event) -> None:
        """Handle specialist therapy event.

        Args:
            event: Specialist therapy event
        """
        specialist_id = event.data.get("specialist_id")
        cost = event.data.get("cost", 500)

        if specialist_id:
            success, message = self._burnout_system.attend_therapy(specialist_id, cost)

            # Publish burnout update event
            self._event_bus.publish("burnout_updated", {
                "specialist_id": specialist_id,
                "burnout_level": self._burnout_system.get_specialist_status(specialist_id)["burnout_level"],
                "message": message,
                "action": "therapy",
                "success": success,
            })

    # Public API methods for external access
    def get_specialist_status(self, specialist_id: str) -> Dict[str, Any]:
        """Get specialist burnout status.

        Args:
            specialist_id: Specialist ID

        Returns:
            Burnout status dictionary
        """
        return self._burnout_system.get_specialist_status(specialist_id)

    def get_team_status(self) -> Dict[str, Any]:
        """Get team-wide burnout statistics.

        Returns:
            Team burnout statistics
        """
        return self._burnout_system.get_team_status()

    def take_rest_day(self, specialist_id: str) -> tuple[bool, str]:
        """Force specialist to take rest day.

        Args:
            specialist_id: Specialist ID

        Returns:
            (success, message)
        """
        return self._burnout_system.take_rest_day(specialist_id)

    def take_vacation(self, specialist_id: str, days: int, cost_per_day: int) -> tuple[bool, str]:
        """Send specialist on vacation.

        Args:
            specialist_id: Specialist ID
            days: Vacation duration
            cost_per_day: Cost per day

        Returns:
            (success, message)
        """
        return self._burnout_system.take_vacation(specialist_id, days, cost_per_day)

    def attend_therapy(self, specialist_id: str, cost: int) -> tuple[bool, str]:
        """Send specialist to therapy.

        Args:
            specialist_id: Specialist ID
            cost: Therapy cost

        Returns:
            (success, message)
        """
        return self._burnout_system.attend_therapy(specialist_id, cost)