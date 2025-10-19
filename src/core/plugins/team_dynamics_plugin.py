"""Team dynamics plugin for managing specialist relationships and morale.

This plugin integrates the team dynamics system into the game, providing
relationship tracking, morale management, and synergy bonuses.
"""

import logging
from typing import Any, Dict, Optional

from src.core.game_system import GameSystem
from src.core.team_dynamics_system import TeamDynamicsSystem
from src.models.game_state import GameState

logger = logging.getLogger(__name__)


class TeamDynamicsPlugin(GameSystem):
    """Plugin for team dynamics system integration."""

    def __init__(self):
        """Initialize the team dynamics plugin."""
        super().__init__()

    def get_name(self) -> str:
        """Get the plugin name.

        Returns:
            Plugin name string
        """
        return "team_dynamics"
        self._team_dynamics_system: Optional[TeamDynamicsSystem] = None
        self._game_state: Optional[GameState] = None

    def initialize(self, game_state: GameState) -> None:
        """Initialize the team dynamics system.

        Args:
            game_state: Current game state
        """
        self._game_state = game_state
        self._team_dynamics_system = TeamDynamicsSystem()

        logger.info("Team dynamics plugin initialized")

    def update(self, game_state: GameState, delta_time: float) -> None:
        """Update the team dynamics system.

        Args:
            game_state: Current game state
            delta_time: Time elapsed since last update
        """
        if not self._team_dynamics_system or not self._game_state:
            return

        # Update morale for all specialists
        for specialist in self._game_state.specialists:
            # For now, consider all specialists as "team members"
            team_members = [s for s in self._game_state.specialists if s.id != specialist.id]
            self._team_dynamics_system.update_morale(specialist, team_members, 0.0)  # TODO: pass actual time

    def shutdown(self, game_state: GameState) -> None:
        """Shutdown the team dynamics system.

        Args:
            game_state: Current game state
        """
        self._team_dynamics_system = None
        self._game_state = None
        logger.info("Team dynamics plugin shut down")

    def save_state(self) -> Dict[str, Any]:
        """Save team dynamics state.

        Returns:
            State data dictionary
        """
        if not self._team_dynamics_system:
            return {}

        # Save morale states
        morale_states = {}
        for specialist_id, morale_state in self._team_dynamics_system._morale_states.items():
            morale_states[specialist_id] = {
                "current_morale": morale_state.current_morale,
                "base_morale": morale_state.base_morale,
                "relationship_impact": morale_state.relationship_impact,
                "workload_impact": morale_state.workload_impact,
                "success_impact": morale_state.success_impact,
            }

        return {
            "morale_states": morale_states,
            "relationships": [
                {
                    "specialist_a": rel.specialist_a,
                    "specialist_b": rel.specialist_b,
                    "relationship_type": rel.relationship_type.value,
                    "strength": rel.strength,
                    "last_interaction": rel.last_interaction,
                }
                for rel in self._team_dynamics_system.get_all_relationships()
            ]
        }

    def load_state(self, state_data: Dict[str, Any]) -> None:
        """Load team dynamics state.

        Args:
            state_data: State data dictionary
        """
        if not self._team_dynamics_system:
            return

        # Load morale states
        morale_states = state_data.get("morale_states", {})
        for specialist_id, morale_data in morale_states.items():
            from src.core.team_dynamics_system import TeamMorale
            morale_state = TeamMorale(
                specialist_id=specialist_id,
                current_morale=morale_data["current_morale"],
                base_morale=morale_data["base_morale"],
                relationship_impact=morale_data["relationship_impact"],
                workload_impact=morale_data["workload_impact"],
                success_impact=morale_data["success_impact"],
            )
            self._team_dynamics_system._morale_states[specialist_id] = morale_state

        # Load relationships
        relationships_data = state_data.get("relationships", [])
        for rel_data in relationships_data:
            from src.core.team_dynamics_system import Relationship, RelationshipType
            relationship = Relationship(
                specialist_a=rel_data["specialist_a"],
                specialist_b=rel_data["specialist_b"],
                relationship_type=RelationshipType(rel_data["relationship_type"]),
                strength=rel_data["strength"],
                last_interaction=rel_data["last_interaction"],
            )
            key = (min(relationship.specialist_a, relationship.specialist_b),
                   max(relationship.specialist_a, relationship.specialist_b))
            self._team_dynamics_system._relationships[key] = relationship

        logger.info("Team dynamics state loaded")

    def get_team_synergy(self, team_members: list) -> Optional[Any]:
        """Get synergy bonus for a team.

        Args:
            team_members: List of specialists in the team

        Returns:
            SynergyBonus object or None if system not initialized
        """
        if not self._team_dynamics_system:
            return None

        return self._team_dynamics_system.calculate_team_synergy(team_members)

    def get_morale_state(self, specialist_id: str) -> Optional[Any]:
        """Get morale state for a specialist.

        Args:
            specialist_id: ID of the specialist

        Returns:
            TeamMorale object or None if not found
        """
        if not self._team_dynamics_system:
            return None

        return self._team_dynamics_system.get_morale_state(specialist_id)

    def get_relationships(self) -> list:
        """Get all relationships in the system.

        Returns:
            List of Relationship objects
        """
        if not self._team_dynamics_system:
            return []

        return self._team_dynamics_system.get_all_relationships()