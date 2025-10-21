"""Specialist relationships system: rivalries, friendships, and team synergy.

Relationships between specialists create emergent gameplay:
- Friendships boost team performance multipliers
- Rivalries create conflict penalties
- Dynamic relationship evolution based on assignments
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict
from src.utils.logger import GameLogger


class RelationshipType(Enum):
    """Types of relationships between specialists."""
    NEUTRAL = 0.0
    RIVAL = -1.0
    FRIENDLY = 1.0


@dataclass
class Relationship:
    """Tracks relationship between two specialists."""
    specialist_a_id: str
    specialist_b_id: str
    relationship_type: RelationshipType
    intensity: float  # -100 (bitter rival) to +100 (best friends)
    incidents_together: int = 0
    last_updated_at: float = 0.0

    def is_rival(self) -> bool:
        """Check if relationship is rivalry."""
        return self.intensity < -50

    def is_friendship(self) -> bool:
        """Check if relationship is friendship."""
        return self.intensity > 50

    def get_synergy_multiplier(self) -> float:
        """Get performance multiplier from this relationship.
        
        Returns:
            1.0 (neutral), 0.85-0.95 (rivalry penalty), 1.05-1.15 (friendship bonus)
        """
        if self.is_rival():
            return max(0.85, 1.0 - (abs(self.intensity) * 0.001))
        if self.is_friendship():
            return min(1.15, 1.0 + (self.intensity * 0.001))
        return 1.0


@dataclass
class SpecialistRelationships:
    """Manages all relationships for a specialist."""
    specialist_id: str
    relationships: Dict[str, Relationship] = field(default_factory=dict)

    def add_relationship(self, other_id: str, rel: Relationship) -> None:
        """Add or update relationship with another specialist."""
        self.relationships[other_id] = rel

    def get_relationship(self, other_id: str) -> Optional[Relationship]:
        """Get relationship with another specialist."""
        return self.relationships.get(other_id)

    def get_average_synergy_with_team(self, team_specialist_ids: list[str]) -> float:
        """Calculate average synergy multiplier with a team.
        
        Args:
            team_specialist_ids: List of specialist IDs on the team
            
        Returns:
            Average synergy multiplier across all team relationships
        """
        if not team_specialist_ids:
            return 1.0

        total_multiplier = 0.0
        for other_id in team_specialist_ids:
            if other_id == self.specialist_id:
                continue
            rel = self.get_relationship(other_id)
            multiplier = rel.get_synergy_multiplier() if rel else 1.0
            total_multiplier += multiplier

        team_size = len([s for s in team_specialist_ids if s != self.specialist_id])
        return total_multiplier / team_size if team_size > 0 else 1.0


class RelationshipsSystem:
    """Manages specialist relationships and team synergy mechanics."""

    def __init__(self, game_config: dict):
        """Initialize relationships system.
        
        Args:
            game_config: Game configuration with relationship parameters
        """
        self.logger = GameLogger("relationships_system")
        self.config = game_config.get("relationships", {})
        
        # Map of specialist_id -> SpecialistRelationships
        self.specialists_relationships: Dict[str, SpecialistRelationships] = {}
        
        # Cache for team synergy calculations
        self._synergy_cache: Dict[tuple, float] = {}

    def register_specialist(self, specialist_id: str) -> None:
        """Register a specialist in the relationships system.
        
        Args:
            specialist_id: ID of specialist to register
        """
        if specialist_id not in self.specialists_relationships:
            self.specialists_relationships[specialist_id] = SpecialistRelationships(specialist_id)
            self.logger.debug(f"Registered specialist {specialist_id} in relationships")

    def record_assignment(
        self,
        specialist_id: str,
        team_specialist_ids: list[str],
        time_elapsed: float
    ) -> None:
        """Record specialists working together (builds relationships).
        
        Args:
            specialist_id: Primary specialist on assignment
            team_specialist_ids: All specialists on team
            time_elapsed: Time elapsed for assignment
        """
        self.register_specialist(specialist_id)

        for teammate_id in team_specialist_ids:
            if teammate_id == specialist_id:
                continue

            self.register_specialist(teammate_id)

            # Get or create relationship
            rel = self.specialists_relationships[specialist_id].get_relationship(teammate_id)

            if rel is None:
                rel = Relationship(
                    specialist_a_id=specialist_id,
                    specialist_b_id=teammate_id,
                    relationship_type=RelationshipType.NEUTRAL,
                    intensity=0.0,
                    last_updated_at=time_elapsed
                )
                self.specialists_relationships[specialist_id].add_relationship(teammate_id, rel)

            # Increment shared incidents
            rel.incidents_together += 1

            # Evolve intensity based on shared experiences
            # Random chance to develop rivalry or friendship over multiple assignments
            if rel.incidents_together >= self.config.get("friendship_threshold", 3):
                if rel.intensity < 50:  # Not yet at friendship
                    rel.intensity += self.config.get("intensity_increase_per_incident", 5.0)
                    rel.relationship_type = RelationshipType.FRIENDLY

            self.logger.debug(
                f"Recorded assignment: {specialist_id} + {teammate_id}, "
                f"intensity={rel.intensity:.1f}"
            )

    def create_rivalry(
        self,
        specialist_a_id: str,
        specialist_b_id: str,
        intensity: float = -75.0
    ) -> None:
        """Manually create a rivalry between two specialists.
        
        Args:
            specialist_a_id: First specialist ID
            specialist_b_id: Second specialist ID
            intensity: Rivalry intensity (-100 to -50)
        """
        self.register_specialist(specialist_a_id)
        self.register_specialist(specialist_b_id)

        rel = Relationship(
            specialist_a_id=specialist_a_id,
            specialist_b_id=specialist_b_id,
            relationship_type=RelationshipType.RIVAL,
            intensity=min(-50.0, intensity),
            incidents_together=0
        )

        self.specialists_relationships[specialist_a_id].add_relationship(specialist_b_id, rel)
        self.logger.info(f"Created rivalry: {specialist_a_id} ↔ {specialist_b_id}")

    def create_friendship(
        self,
        specialist_a_id: str,
        specialist_b_id: str,
        intensity: float = 75.0
    ) -> None:
        """Manually create a friendship between two specialists.
        
        Args:
            specialist_a_id: First specialist ID
            specialist_b_id: Second specialist ID
            intensity: Friendship intensity (50 to 100)
        """
        self.register_specialist(specialist_a_id)
        self.register_specialist(specialist_b_id)

        rel = Relationship(
            specialist_a_id=specialist_a_id,
            specialist_b_id=specialist_b_id,
            relationship_type=RelationshipType.FRIENDLY,
            intensity=max(50.0, intensity),
            incidents_together=0
        )

        self.specialists_relationships[specialist_a_id].add_relationship(specialist_b_id, rel)
        self.logger.info(f"Created friendship: {specialist_a_id} ↔ {specialist_b_id}")

    def get_team_synergy_multiplier(self, team_specialist_ids: list[str]) -> float:
        """Calculate overall synergy multiplier for a team.
        
        Team synergy is the average of all pairwise relationships.
        This incentivizes building cohesive teams.
        
        Args:
            team_specialist_ids: List of specialist IDs on team
            
        Returns:
            Average synergy multiplier (0.8 to 1.2 typical range)
        """
        if len(team_specialist_ids) <= 1:
            return 1.0

        # Check cache
        cache_key = tuple(sorted(team_specialist_ids))
        if cache_key in self._synergy_cache:
            return self._synergy_cache[cache_key]

        total_multiplier = 0.0
        pair_count = 0

        for specialist_id in team_specialist_ids:
            team_without_self = [s for s in team_specialist_ids if s != specialist_id]
            avg_synergy = self.specialists_relationships[specialist_id].get_average_synergy_with_team(
                team_without_self
            )
            total_multiplier += avg_synergy
            pair_count += 1

        team_synergy = total_multiplier / pair_count if pair_count > 0 else 1.0

        # Cache for performance
        self._synergy_cache[cache_key] = team_synergy

        return team_synergy

    def get_specialist_relationships_summary(self, specialist_id: str) -> dict:
        """Get summary of a specialist's relationships.
        
        Args:
            specialist_id: Specialist to query
            
        Returns:
            Dict with friend count, rival count, average intensity
        """
        if specialist_id not in self.specialists_relationships:
            return {"friends": 0, "rivals": 0, "average_intensity": 0.0}

        spec_rels = self.specialists_relationships[specialist_id]
        rels = list(spec_rels.relationships.values())

        friends = [r for r in rels if r.is_friendship()]
        rivals = [r for r in rels if r.is_rival()]
        avg_intensity = sum(r.intensity for r in rels) / len(rels) if rels else 0.0

        return {
            "friends": len(friends),
            "rivals": len(rivals),
            "average_intensity": avg_intensity,
            "total_relationships": len(rels)
        }

    def clear_cache(self) -> None:
        """Clear synergy calculation cache (call after updates)."""
        self._synergy_cache.clear()

    def to_dict(self) -> dict:
        """Serialize relationships for saving.
        
        Returns:
            Dictionary with all relationships data
        """
        all_relationships = []
        for spec_id, spec_rels in self.specialists_relationships.items():
            for other_id, rel in spec_rels.relationships.items():
                all_relationships.append({
                    "specialist_a_id": rel.specialist_a_id,
                    "specialist_b_id": rel.specialist_b_id,
                    "relationship_type": rel.relationship_type.name,
                    "intensity": rel.intensity,
                    "incidents_together": rel.incidents_together,
                    "last_updated_at": rel.last_updated_at
                })

        return {"relationships": all_relationships}

    def from_dict(self, data: dict) -> None:
        """Load relationships from saved data.
        
        Args:
            data: Dictionary with relationships data
        """
        self.specialists_relationships.clear()
        self._synergy_cache.clear()

        for rel_data in data.get("relationships", []):
            spec_a = rel_data["specialist_a_id"]
            spec_b = rel_data["specialist_b_id"]

            self.register_specialist(spec_a)
            self.register_specialist(spec_b)

            rel = Relationship(
                specialist_a_id=spec_a,
                specialist_b_id=spec_b,
                relationship_type=RelationshipType[rel_data["relationship_type"]],
                intensity=rel_data["intensity"],
                incidents_together=rel_data["incidents_together"],
                last_updated_at=rel_data["last_updated_at"]
            )

            self.specialists_relationships[spec_a].add_relationship(spec_b, rel)

        self.logger.info(f"Loaded {len(data.get('relationships', []))} relationships")
