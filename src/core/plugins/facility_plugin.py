"""FacilityPlugin - Facility Management System.

Plugin wrapper for FacilitySystem providing facility upgrade management and bonus calculations.
Integrates with game events to handle facility upgrades and apply facility effects to gameplay.

Features:
- Facility upgrade management with cost validation
- Aggregate bonus calculations from all facilities
- Facility effect application to game state
- Facility information and upgrade summaries
- Event-driven upgrade notifications
"""

from typing import Dict, Any, List, Optional
from src.core.game_system import GameSystem
from src.core.facility_system import FacilitySystem
from src.core.event_bus import get_event_bus, Event


class FacilityPlugin(GameSystem):
    """Plugin wrapper for FacilitySystem with GameSystem integration."""

    def __init__(self):
        """Initialize facility plugin."""
        super().__init__()
        self._facility_system = FacilitySystem()
        self._event_bus = get_event_bus()
        self._subscription_ids: List[str] = []

    def get_name(self) -> str:
        """Get plugin name."""
        return "FacilityPlugin"

    def get_feature_id(self) -> str:
        """Get feature flag ID for facility system."""
        return "facility_system"

    def initialize(self, game_state) -> None:
        """Initialize facility plugin.

        Args:
            game_state: Current game state
        """
        # Subscribe to relevant events
        self._subscription_ids = [
            self._event_bus.subscribe("facility_upgrade", self._on_facility_upgrade),
            self._event_bus.subscribe("facility_effects_apply", self._on_apply_facility_effects),
        ]

    def update(self, game_state, delta_time: float) -> None:
        """Update facility plugin.

        Args:
            game_state: Current game state
            delta_time: Time elapsed since last update
        """
        # Apply facility effects periodically (every 300 seconds / 5 minutes)
        current_time = getattr(game_state, 'game_time', 0.0)
        if hasattr(self, '_last_effects_time'):
            if current_time - self._last_effects_time >= 300.0:
                self._apply_facility_effects(game_state)
                self._last_effects_time = current_time
        else:
            self._last_effects_time = current_time
            self._apply_facility_effects(game_state)

    def shutdown(self, game_state) -> None:
        """Shutdown facility plugin.

        Args:
            game_state: Current game state
        """
        # Unsubscribe from all events
        for subscription_id in self._subscription_ids:
            self._event_bus.unsubscribe(subscription_id)
        self._subscription_ids.clear()

    def save_state(self, game_state) -> Dict[str, Any]:
        """Save facility plugin state.

        Args:
            game_state: Current game state

        Returns:
            State data to save
        """
        state_data = {
            "last_effects_time": getattr(self, '_last_effects_time', 0.0),
        }

        return state_data

    def load_state(self, game_state, state_data: Dict[str, Any]) -> None:
        """Load facility plugin state.

        Args:
            game_state: Current game state
            state_data: Previously saved state data
        """
        self._last_effects_time = state_data.get("last_effects_time", 0.0)

    def _apply_facility_effects(self, game_state) -> None:
        """Apply facility effects to game state.

        Args:
            game_state: Current game state
        """
        effects = self._facility_system.apply_facility_effects(game_state)

        # Publish facility effects applied event
        self._event_bus.publish("facility_effects_applied", {
            "effects": effects,
            "timestamp": getattr(game_state, 'game_time', 0.0),
        })

    def _on_facility_upgrade(self, event: Event) -> None:
        """Handle facility upgrade event.

        Args:
            event: Facility upgrade event
        """
        game_state = event.data.get("game_state")
        facility_id = event.data.get("facility_id")

        if game_state and facility_id:
            facilities = getattr(game_state, "facilities", [])
            facility = self._facility_system.get_facility_by_id(facilities, facility_id)

            if facility:
                success = self._facility_system.upgrade_facility(facility, game_state)

                # Publish upgrade result event
                self._event_bus.publish("facility_upgrade_result", {
                    "facility_id": facility_id,
                    "success": success,
                    "new_level": facility.level if success else facility.level,
                    "upgrade_cost": facility.calculate_upgrade_cost() if success else 0,
                })

    def _on_apply_facility_effects(self, event: Event) -> None:
        """Handle apply facility effects event.

        Args:
            event: Apply facility effects event
        """
        game_state = event.data.get("game_state")

        if game_state:
            self._apply_facility_effects(game_state)

    # Public API methods for external access
    def upgrade_facility(self, facility, game_state) -> bool:
        """Upgrade a facility if player can afford it.

        Args:
            facility: The facility to upgrade
            game_state: Current game state

        Returns:
            True if upgrade successful, False otherwise
        """
        return self._facility_system.upgrade_facility(facility, game_state)

    def calculate_facility_bonuses(self, facilities: List) -> Dict[str, float]:
        """Aggregate all facility bonuses into a single dictionary.

        Args:
            facilities: List of all facilities

        Returns:
            Dictionary mapping bonus types to total bonus values
        """
        return self._facility_system.calculate_facility_bonuses(facilities)

    def apply_facility_effects(self, game_state) -> Dict[str, float]:
        """Calculate and return facility effects on game state.

        Args:
            game_state: Current game state

        Returns:
            Dictionary of facility effects to apply
        """
        return self._facility_system.apply_facility_effects(game_state)

    def get_facility_by_id(self, facilities: List, facility_id: str):
        """Get facility by ID.

        Args:
            facilities: List of all facilities
            facility_id: ID of facility to find

        Returns:
            Facility instance or None if not found
        """
        return self._facility_system.get_facility_by_id(facilities, facility_id)

    def get_upgradeable_facilities(self, facilities: List) -> List:
        """Get list of facilities that can be upgraded.

        Args:
            facilities: List of all facilities

        Returns:
            List of facilities below max level
        """
        return self._facility_system.get_upgradeable_facilities(facilities)

    def get_total_upgrade_cost(self, facilities: List) -> int:
        """Calculate total cost to upgrade all upgradeable facilities once.

        Args:
            facilities: List of all facilities

        Returns:
            Total upgrade cost
        """
        return self._facility_system.get_total_upgrade_cost(facilities)

    def get_max_level_facilities(self, facilities: List) -> List:
        """Get list of facilities at max level.

        Args:
            facilities: List of all facilities

        Returns:
            List of max level facilities
        """
        return self._facility_system.get_max_level_facilities(facilities)

    def get_facility_summary(self, facility) -> Dict:
        """Get comprehensive summary of facility status.

        Args:
            facility: The facility to summarize

        Returns:
            Dictionary with facility information
        """
        return self._facility_system.get_facility_summary(facility)

    def get_all_facilities_summary(self, facilities: List) -> Dict:
        """Get summary of all facilities and aggregate bonuses.

        Args:
            facilities: List of all facilities

        Returns:
            Dictionary with aggregate information
        """
        return self._facility_system.get_all_facilities_summary(facilities)