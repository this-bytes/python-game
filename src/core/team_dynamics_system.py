"""Team dynamics system for specialist relationships and synergies.

This module manages specialist relationships, morale, and team synergy bonuses
that affect overall team performance in incident resolution.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from src.models.specialist import Specialist
from src.utils.json_loader import JSONLoader

logger = logging.getLogger(__name__)


class RelationshipType(Enum):
    """Types of relationships between specialists."""
    FRIENDSHIP = "friendship"
    RIVALRY = "rivalry"
    MENTORSHIP = "mentorship"
    NEUTRAL = "neutral"


@dataclass
class Relationship:
    """Represents a relationship between two specialists."""
    specialist_a: str
    specialist_b: str
    relationship_type: RelationshipType
    strength: float  # 0.0 to 1.0
    last_interaction: float  # timestamp


@dataclass
class TeamMorale:
    """Represents the morale state of a specialist."""
    specialist_id: str
    current_morale: float
    base_morale: float
    relationship_impact: float
    workload_impact: float
    success_impact: float


@dataclass
class SynergyBonus:
    """Represents synergy bonuses for a team."""
    team_synergy: float
    relationship_bonuses: Dict[str, float]
    morale_bonuses: Dict[str, float]
    total_bonus: float


class TeamDynamicsSystem:
    """Manages specialist relationships, morale, and team synergies."""

    def __init__(self):
        """Initialize the team dynamics system."""
        self._json_loader = JSONLoader()
        self._config = {}
        self._relationships: Dict[Tuple[str, str], Relationship] = {}
        self._morale_states: Dict[str, TeamMorale] = {}
        self._relationship_types: Dict[str, Dict] = {}

        self._load_config()
        logger.info("Team dynamics system initialized")

    def _load_config(self) -> None:
        """Load team dynamics configuration."""
        try:
            config_data = self._json_loader.load_data("team_dynamics.json")
            self._config = config_data
            self._relationship_types = config_data.get("relationships", {})
            self._load_relationships()
            logger.info("Team dynamics configuration loaded")
        except Exception as e:
            logger.error(f"Failed to load team dynamics config: {e}")
            # Use default config
            self._config = {
                "relationships": {
                    "friendship": {"synergy_bonus": 0.15, "morale_boost": 5},
                    "rivalry": {"synergy_bonus": -0.10, "morale_boost": -3},
                    "mentorship": {"synergy_bonus": 0.20, "morale_boost": 8},
                    "neutral": {"synergy_bonus": 0.0, "morale_boost": 0}
                }
            }

    def _load_relationships(self) -> None:
        """Load predefined specialist relationships."""
        specialist_relationships = self._config.get("specialist_relationships", {})
        for spec_a, relationships in specialist_relationships.items():
            for spec_b, rel_type in relationships.items():
                if rel_type in self._relationship_types:
                    # Create bidirectional relationship
                    key_ab = (min(spec_a, spec_b), max(spec_a, spec_b))
                    relationship = Relationship(
                        specialist_a=min(spec_a, spec_b),
                        specialist_b=max(spec_a, spec_b),
                        relationship_type=RelationshipType(rel_type),
                        strength=1.0,
                        last_interaction=0.0
                    )
                    self._relationships[key_ab] = relationship

    def get_relationship(self, specialist_a: str, specialist_b: str) -> Optional[Relationship]:
        """Get the relationship between two specialists.

        Args:
            specialist_a: ID of first specialist
            specialist_b: ID of second specialist

        Returns:
            Relationship object if one exists, None otherwise
        """
        key = (min(specialist_a, specialist_b), max(specialist_a, specialist_b))
        return self._relationships.get(key)

    def update_morale(self, specialist: Specialist, team_members: List[Specialist],
                     current_time: float) -> None:
        """Update morale for a specialist based on team dynamics.

        Args:
            specialist: The specialist to update
            team_members: Other team members
            current_time: Current game time
        """
        if specialist.id not in self._morale_states:
            morale_config = self._config.get("morale_config", {})
            base_morale = float(morale_config.get("base_morale", 50) or 50)  # type: ignore
            self._morale_states[specialist.id] = TeamMorale(
                specialist_id=specialist.id,
                current_morale=base_morale,
                base_morale=base_morale,
                relationship_impact=0.0,
                workload_impact=0.0,
                success_impact=0.0
            )

        morale_state = self._morale_states[specialist.id]
        morale_config = self._config.get("morale_config", {})

        # Calculate relationship impact
        relationship_impact = 0.0
        for team_member in team_members:
            if team_member.id != specialist.id:
                relationship = self.get_relationship(specialist.id, team_member.id)
                if relationship:
                    rel_config = self._relationship_types.get(relationship.relationship_type.value, {})
                    relationship_impact += rel_config.get("morale_boost", 0) * relationship.strength

        morale_state.relationship_impact = relationship_impact

        # Calculate workload impact (simplified - based on active incidents)
        workload_impact = 0.0
        # This would be calculated based on current workload

        morale_state.workload_impact = workload_impact

        # Update current morale
        total_impact = (
            morale_state.relationship_impact * float(morale_config.get("relationship_impact_weight", 0.3)) +  # type: ignore
            morale_state.workload_impact * float(morale_config.get("workload_impact_weight", 0.4)) +  # type: ignore
            morale_state.success_impact * float(morale_config.get("success_impact_weight", 0.3))  # type: ignore
        )

        morale_state.current_morale = max(
            float(morale_config.get("min_morale", 0)),  # type: ignore
            min(
                float(morale_config.get("max_morale", 100)),  # type: ignore
                morale_state.base_morale + total_impact
            )
        )

        # Apply decay
        decay_rate = float(morale_config.get("morale_decay_rate", 0.1))  # type: ignore
        morale_state.current_morale *= (1.0 - decay_rate)

    def calculate_team_synergy(self, team_members: List[Specialist]) -> SynergyBonus:
        """Calculate synergy bonuses for a team.

        Args:
            team_members: List of specialists in the team

        Returns:
            SynergyBonus object with calculated bonuses
        """
        synergy_config = self._config.get("synergy_config", {})
        relationship_bonuses = {}
        morale_bonuses = {}
        total_synergy = 0.0

        # Calculate relationship-based synergy
        for i, specialist_a in enumerate(team_members):
            for specialist_b in team_members[i+1:]:
                relationship = self.get_relationship(specialist_a.id, specialist_b.id)
                if relationship:
                    rel_config = self._relationship_types.get(relationship.relationship_type.value, {})
                    synergy_bonus = rel_config.get("synergy_bonus", 0.0) * relationship.strength

                    relationship_bonuses[f"{specialist_a.id}_{specialist_b.id}"] = synergy_bonus
                    total_synergy += synergy_bonus

        # Calculate morale-based synergy
        for specialist in team_members:
            if specialist.id in self._morale_states:
                morale_state = self._morale_states[specialist.id]
                morale_config = self._config.get("morale_config", {})
                morale_thresholds = morale_config.get("morale_thresholds", {})

                morale_bonus = 0.0
                if morale_state.current_morale >= morale_thresholds.get("high", 75):
                    morale_bonus = 0.1
                elif morale_state.current_morale >= morale_thresholds.get("medium", 50):
                    morale_bonus = 0.05
                elif morale_state.current_morale <= morale_thresholds.get("low", 25):
                    morale_bonus = -0.05

                morale_bonuses[specialist.id] = morale_bonus
                total_synergy += morale_bonus

        # Apply team size bonus
        team_size_bonus = len(team_members) * float(synergy_config.get("team_size_bonus_multiplier", 0.05))  # type: ignore
        total_synergy += team_size_bonus

        # Clamp synergy
        total_synergy = max(
            float(synergy_config.get("min_synergy_penalty", -0.3)),  # type: ignore
            min(float(synergy_config.get("max_synergy_bonus", 0.5)), total_synergy)  # type: ignore
        )

        return SynergyBonus(
            team_synergy=total_synergy,
            relationship_bonuses=relationship_bonuses,
            morale_bonuses=morale_bonuses,
            total_bonus=total_synergy
        )

    def get_morale_state(self, specialist_id: str) -> Optional[TeamMorale]:
        """Get the morale state for a specialist.

        Args:
            specialist_id: ID of the specialist

        Returns:
            TeamMorale object if found, None otherwise
        """
        return self._morale_states.get(specialist_id)

    def get_all_relationships(self) -> List[Relationship]:
        """Get all relationships in the system.

        Returns:
            List of all Relationship objects
        """
        return list(self._relationships.values())

    def get_relationship_types(self) -> Dict[str, Dict]:
        """Get all relationship type configurations.

        Returns:
            Dictionary of relationship type configurations
        """
        return self._relationship_types.copy()