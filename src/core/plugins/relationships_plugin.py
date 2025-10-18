"""RelationshipsPlugin - Specialist Relationships and Team Synergy System.

Plugin wrapper for RelationshipsSystem providing specialist relationship tracking and team synergy.
Integrates with game events to automatically evolve relationships based on team assignments.

Features:
- Friendships boost team performance multipliers
- Rivalries create conflict penalties
- Dynamic relationship evolution based on assignments
- Team synergy calculations for optimal team composition
"""

from typing import Dict, Any, List
from src.core.game_system import GameSystem
from src.core.relationships_system import RelationshipsSystem
from src.core.event_bus import get_event_bus, Event


class RelationshipsPlugin(GameSystem):
    """Plugin wrapper for RelationshipsSystem with GameSystem integration."""

    def __init__(self):
        """Initialize relationships plugin."""
        super().__init__()
        self._relationships_system = None  # Will be initialized with game config
        self._event_bus = get_event_bus()
        self._subscription_ids: List[str] = []

    def get_name(self) -> str:
        """Get plugin name."""
        return "RelationshipsPlugin"

    def get_feature_id(self) -> str:
        """Get feature flag ID for relationships system."""
        return "relationships_system"

    def initialize(self, game_state) -> None:
        """Initialize relationships plugin.

        Args:
            game_state: Current game state
        """
        # Initialize relationships system with game config
        game_config = getattr(game_state, 'config', {})
        self._relationships_system = RelationshipsSystem(game_config)

        # Subscribe to relevant events
        self._subscription_ids = [
            self._event_bus.subscribe("incident_assigned", self._on_incident_assigned),
            self._event_bus.subscribe("specialist_hired", self._on_specialist_hired),
            self._event_bus.subscribe("relationships_create_rivalry", self._on_create_rivalry),
            self._event_bus.subscribe("relationships_create_friendship", self._on_create_friendship),
        ]

    def update(self, game_state, delta_time: float) -> None:
        """Update relationships plugin.

        Args:
            game_state: Current game state
            delta_time: Time elapsed since last update
        """
        # Relationships system is event-driven, no continuous updates needed
        pass

    def shutdown(self, game_state) -> None:
        """Shutdown relationships plugin.

        Args:
            game_state: Current game state
        """
        # Unsubscribe from all events
        for subscription_id in self._subscription_ids:
            self._event_bus.unsubscribe(subscription_id)
        self._subscription_ids.clear()

    def save_state(self, game_state) -> Dict[str, Any]:
        """Save relationships plugin state.

        Args:
            game_state: Current game state

        Returns:
            State data to save
        """
        if self._relationships_system:
            return self._relationships_system.to_dict()
        return {"relationships": []}

    def load_state(self, game_state, state_data: Dict[str, Any]) -> None:
        """Load relationships plugin state.

        Args:
            game_state: Current game state
            state_data: Previously saved state data
        """
        if self._relationships_system:
            self._relationships_system.from_dict(state_data)

    def _on_incident_assigned(self, event: Event) -> None:
        """Handle incident assignment event.

        Args:
            event: Incident assignment event
        """
        specialist_id = event.data.get("specialist_id")
        team_specialist_ids = event.data.get("team_specialist_ids", [])
        time_elapsed = event.data.get("time_elapsed", 0.0)

        if specialist_id and self._relationships_system:
            self._relationships_system.record_assignment(
                specialist_id, team_specialist_ids, time_elapsed
            )

            # Calculate and publish team synergy
            if team_specialist_ids:
                synergy = self._relationships_system.get_team_synergy_multiplier(team_specialist_ids)
                self._event_bus.publish("team_synergy_calculated", {
                    "team_specialist_ids": team_specialist_ids,
                    "synergy_multiplier": synergy,
                })

    def _on_specialist_hired(self, event: Event) -> None:
        """Handle specialist hired event.

        Args:
            event: Specialist hired event
        """
        specialist_id = event.data.get("specialist_id")
        if specialist_id and self._relationships_system:
            self._relationships_system.register_specialist(specialist_id)

    def _on_create_rivalry(self, event: Event) -> None:
        """Handle create rivalry event.

        Args:
            event: Create rivalry event
        """
        specialist_a_id = event.data.get("specialist_a_id")
        specialist_b_id = event.data.get("specialist_b_id")
        intensity = event.data.get("intensity", -75.0)

        if specialist_a_id and specialist_b_id and self._relationships_system:
            self._relationships_system.create_rivalry(
                specialist_a_id, specialist_b_id, intensity
            )

            # Publish rivalry created event
            self._event_bus.publish("rivalry_created", {
                "specialist_a_id": specialist_a_id,
                "specialist_b_id": specialist_b_id,
                "intensity": intensity,
            })

    def _on_create_friendship(self, event: Event) -> None:
        """Handle create friendship event.

        Args:
            event: Create friendship event
        """
        specialist_a_id = event.data.get("specialist_a_id")
        specialist_b_id = event.data.get("specialist_b_id")
        intensity = event.data.get("intensity", 75.0)

        if specialist_a_id and specialist_b_id and self._relationships_system:
            self._relationships_system.create_friendship(
                specialist_a_id, specialist_b_id, intensity
            )

            # Publish friendship created event
            self._event_bus.publish("friendship_created", {
                "specialist_a_id": specialist_a_id,
                "specialist_b_id": specialist_b_id,
                "intensity": intensity,
            })

    # Public API methods for external access
    def get_team_synergy_multiplier(self, team_specialist_ids: List[str]) -> float:
        """Calculate overall synergy multiplier for a team.

        Args:
            team_specialist_ids: List of specialist IDs on team

        Returns:
            Average synergy multiplier (0.8 to 1.2 typical range)
        """
        if self._relationships_system:
            return self._relationships_system.get_team_synergy_multiplier(team_specialist_ids)
        return 1.0

    def get_specialist_relationships_summary(self, specialist_id: str) -> Dict[str, Any]:
        """Get summary of a specialist's relationships.

        Args:
            specialist_id: Specialist to query

        Returns:
            Dict with friend count, rival count, average intensity
        """
        if self._relationships_system:
            return self._relationships_system.get_specialist_relationships_summary(specialist_id)
        return {"friends": 0, "rivals": 0, "average_intensity": 0.0, "total_relationships": 0}

    def create_rivalry(self, specialist_a_id: str, specialist_b_id: str, intensity: float = -75.0) -> None:
        """Manually create a rivalry between two specialists.

        Args:
            specialist_a_id: First specialist ID
            specialist_b_id: Second specialist ID
            intensity: Rivalry intensity (-100 to -50)
        """
        if self._relationships_system:
            self._relationships_system.create_rivalry(specialist_a_id, specialist_b_id, intensity)

    def create_friendship(self, specialist_a_id: str, specialist_b_id: str, intensity: float = 75.0) -> None:
        """Manually create a friendship between two specialists.

        Args:
            specialist_a_id: First specialist ID
            specialist_b_id: Second specialist ID
            intensity: Friendship intensity (50 to 100)
        """
        if self._relationships_system:
            self._relationships_system.create_friendship(specialist_a_id, specialist_b_id, intensity)

    def clear_cache(self) -> None:
        """Clear synergy calculation cache."""
        if self._relationships_system:
            self._relationships_system.clear_cache()