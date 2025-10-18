"""Test suite for specialist relationships system.

Coverage:
- Relationship creation and intensity tracking
- Synergy multiplier calculations
- Team synergy aggregation
- Rivalry and friendship mechanics
- Serialization/deserialization
"""

import pytest
from src.core.relationships_system import (
    RelationshipsSystem,
    Relationship,
    RelationshipType,
    SpecialistRelationships,
)


@pytest.fixture
def relationships_system() -> RelationshipsSystem:
    """Provide initialized relationships system."""
    config = {
        "relationships": {
            "friendship_threshold": 3,
            "intensity_increase_per_incident": 5.0
        }
    }
    return RelationshipsSystem(config)


@pytest.fixture
def three_specialists() -> list[str]:
    """Provide three specialist IDs."""
    return ["spec_001", "spec_002", "spec_003"]


class TestRelationshipIntensity:
    """Test relationship intensity calculations."""

    def test_neutral_relationship_has_zero_intensity(self, relationships_system):
        """Verify neutral relationship starts at intensity 0."""
        relationships_system.register_specialist("spec_001")
        relationships_system.register_specialist("spec_002")

        rel = Relationship(
            specialist_a_id="spec_001",
            specialist_b_id="spec_002",
            relationship_type=RelationshipType.NEUTRAL,
            intensity=0.0
        )
        relationships_system.specialists_relationships["spec_001"].add_relationship("spec_002", rel)

        retrieved = relationships_system.specialists_relationships["spec_001"].get_relationship("spec_002")
        assert retrieved.intensity == 0.0

    def test_rivalry_relationship_negative_intensity(self, relationships_system):
        """Verify rivalry has negative intensity."""
        relationships_system.create_rivalry("spec_001", "spec_002", intensity=-80.0)

        rel = relationships_system.specialists_relationships["spec_001"].get_relationship("spec_002")
        assert rel.intensity == -80.0
        assert rel.is_rival()

    def test_friendship_relationship_positive_intensity(self, relationships_system):
        """Verify friendship has positive intensity."""
        relationships_system.create_friendship("spec_001", "spec_002", intensity=80.0)

        rel = relationships_system.specialists_relationships["spec_001"].get_relationship("spec_002")
        assert rel.intensity == 80.0
        assert rel.is_friendship()

    def test_intensity_increases_with_shared_incidents(self, relationships_system):
        """Verify intensity grows as specialists work together."""
        relationships_system.record_assignment("spec_001", ["spec_002"], 0.0)
        rel_after_1 = relationships_system.specialists_relationships["spec_001"].get_relationship("spec_002")
        incidents_1 = rel_after_1.incidents_together

        relationships_system.record_assignment("spec_001", ["spec_002"], 1.0)
        rel_after_2 = relationships_system.specialists_relationships["spec_001"].get_relationship("spec_002")
        incidents_2 = rel_after_2.incidents_together

        assert incidents_2 > incidents_1
        assert rel_after_2.intensity >= rel_after_1.intensity


class TestSynergyMultipliers:
    """Test synergy multiplier calculations."""

    def test_neutral_relationship_multiplier_is_one(self, relationships_system):
        """Verify neutral relationship gives 1.0x multiplier."""
        rel = Relationship(
            specialist_a_id="spec_001",
            specialist_b_id="spec_002",
            relationship_type=RelationshipType.NEUTRAL,
            intensity=0.0
        )
        assert rel.get_synergy_multiplier() == 1.0

    def test_rivalry_applies_penalty_multiplier(self, relationships_system):
        """Verify rivalry reduces team performance."""
        rel = Relationship(
            specialist_a_id="spec_001",
            specialist_b_id="spec_002",
            relationship_type=RelationshipType.RIVAL,
            intensity=-75.0
        )
        multiplier = rel.get_synergy_multiplier()
        assert 0.85 <= multiplier < 1.0

    def test_friendship_applies_bonus_multiplier(self, relationships_system):
        """Verify friendship boosts team performance."""
        rel = Relationship(
            specialist_a_id="spec_001",
            specialist_b_id="spec_002",
            relationship_type=RelationshipType.FRIENDLY,
            intensity=75.0
        )
        multiplier = rel.get_synergy_multiplier()
        assert 1.0 < multiplier <= 1.15

    def test_stronger_rivalry_larger_penalty(self, relationships_system):
        """Verify more intense rivalry has larger penalty."""
        rel_weak = Relationship(
            specialist_a_id="spec_001",
            specialist_b_id="spec_002",
            relationship_type=RelationshipType.RIVAL,
            intensity=-60.0
        )
        rel_strong = Relationship(
            specialist_a_id="spec_001",
            specialist_b_id="spec_002",
            relationship_type=RelationshipType.RIVAL,
            intensity=-90.0
        )
        
        mult_weak = rel_weak.get_synergy_multiplier()
        mult_strong = rel_strong.get_synergy_multiplier()
        
        assert mult_strong < mult_weak

    def test_stronger_friendship_larger_bonus(self, relationships_system):
        """Verify more intense friendship has larger bonus."""
        rel_weak = Relationship(
            specialist_a_id="spec_001",
            specialist_b_id="spec_002",
            relationship_type=RelationshipType.FRIENDLY,
            intensity=60.0
        )
        rel_strong = Relationship(
            specialist_a_id="spec_001",
            specialist_b_id="spec_002",
            relationship_type=RelationshipType.FRIENDLY,
            intensity=90.0
        )
        
        mult_weak = rel_weak.get_synergy_multiplier()
        mult_strong = rel_strong.get_synergy_multiplier()
        
        assert mult_strong > mult_weak


class TestTeamSynergy:
    """Test team-wide synergy calculations."""

    def test_single_specialist_team_has_neutral_synergy(self, relationships_system):
        """Verify solo specialist team gives 1.0x synergy."""
        multiplier = relationships_system.get_team_synergy_multiplier(["spec_001"])
        assert multiplier == 1.0

    def test_empty_team_has_neutral_synergy(self, relationships_system):
        """Verify empty team gives 1.0x synergy."""
        multiplier = relationships_system.get_team_synergy_multiplier([])
        assert multiplier == 1.0

    def test_team_with_all_friends_boosted(self, relationships_system, three_specialists):
        """Verify team of friends has synergy bonus."""
        # Create friendships between all pairs
        relationships_system.create_friendship("spec_001", "spec_002")
        relationships_system.create_friendship("spec_001", "spec_003")
        relationships_system.create_friendship("spec_002", "spec_003")

        multiplier = relationships_system.get_team_synergy_multiplier(three_specialists)
        assert multiplier > 1.0

    def test_team_with_all_rivals_penalized(self, relationships_system, three_specialists):
        """Verify team of rivals has synergy penalty."""
        # Create rivalries between all pairs
        relationships_system.create_rivalry("spec_001", "spec_002")
        relationships_system.create_rivalry("spec_001", "spec_003")
        relationships_system.create_rivalry("spec_002", "spec_003")

        multiplier = relationships_system.get_team_synergy_multiplier(three_specialists)
        assert multiplier < 1.0

    def test_mixed_team_synergy_blended(self, relationships_system, three_specialists):
        """Verify mixed team has blended synergy."""
        # Create one friendship, one rivalry
        relationships_system.create_friendship("spec_001", "spec_002")
        relationships_system.create_rivalry("spec_001", "spec_003")

        multiplier = relationships_system.get_team_synergy_multiplier(three_specialists)
        # Should be between rival and friend multipliers
        assert 0.9 < multiplier < 1.1


class TestAssignmentTracking:
    """Test tracking of specialist assignments."""

    def test_record_assignment_creates_relationship(self, relationships_system):
        """Verify assignment creates relationship if none exists."""
        relationships_system.record_assignment("spec_001", ["spec_002"], 0.0)

        rel = relationships_system.specialists_relationships["spec_001"].get_relationship("spec_002")
        assert rel is not None
        assert rel.incidents_together == 1

    def test_record_assignment_increments_incidents(self, relationships_system):
        """Verify multiple assignments increment incident counter."""
        relationships_system.record_assignment("spec_001", ["spec_002"], 0.0)
        relationships_system.record_assignment("spec_001", ["spec_002"], 1.0)
        relationships_system.record_assignment("spec_001", ["spec_002"], 2.0)

        rel = relationships_system.specialists_relationships["spec_001"].get_relationship("spec_002")
        assert rel.incidents_together == 3

    def test_record_assignment_handles_multiple_team_members(self, relationships_system):
        """Verify assignment with multiple team members creates all relationships."""
        relationships_system.record_assignment("spec_001", ["spec_002", "spec_003"], 0.0)

        rel_2 = relationships_system.specialists_relationships["spec_001"].get_relationship("spec_002")
        rel_3 = relationships_system.specialists_relationships["spec_001"].get_relationship("spec_003")

        assert rel_2 is not None
        assert rel_3 is not None

    def test_record_assignment_skips_self(self, relationships_system):
        """Verify assignment doesn't create self-relationships."""
        relationships_system.record_assignment("spec_001", ["spec_001", "spec_002"], 0.0)

        # Should only have relationship with spec_002, not spec_001
        spec_rels = relationships_system.specialists_relationships["spec_001"].relationships
        assert len(spec_rels) == 1
        assert "spec_002" in spec_rels


class TestRelationshipIntegration:
    """Test integration of relationships into team performance."""

    def test_specialist_average_synergy_with_team(self, relationships_system):
        """Verify specialist's average synergy with team."""
        relationships_system.create_friendship("spec_001", "spec_002", intensity=80.0)
        relationships_system.create_rivalry("spec_001", "spec_003", intensity=-80.0)

        avg_synergy = relationships_system.specialists_relationships["spec_001"].get_average_synergy_with_team(
            ["spec_002", "spec_003"]
        )

        # Should be average of friend bonus and rival penalty
        assert 0.95 < avg_synergy < 1.05

    def test_relationships_summary(self, relationships_system):
        """Verify relationship summary counts friends and rivals."""
        relationships_system.create_friendship("spec_001", "spec_002")
        relationships_system.create_friendship("spec_001", "spec_003")
        relationships_system.create_rivalry("spec_001", "spec_004")

        summary = relationships_system.get_specialist_relationships_summary("spec_001")

        assert summary["friends"] == 2
        assert summary["rivals"] == 1
        assert summary["total_relationships"] == 3

    def test_no_relationships_summary(self, relationships_system):
        """Verify unregistered specialist returns empty summary."""
        summary = relationships_system.get_specialist_relationships_summary("spec_unknown")

        assert summary["friends"] == 0
        assert summary["rivals"] == 0
        assert summary["average_intensity"] == 0.0


class TestSerialization:
    """Test saving and loading relationships."""

    def test_serialize_relationships(self, relationships_system):
        """Verify relationships serialize to dict."""
        relationships_system.create_friendship("spec_001", "spec_002")
        relationships_system.create_rivalry("spec_001", "spec_003")

        data = relationships_system.to_dict()

        assert "relationships" in data
        assert len(data["relationships"]) == 2

    def test_deserialize_relationships(self, relationships_system):
        """Verify relationships deserialize from dict."""
        relationships_system.create_friendship("spec_001", "spec_002", intensity=85.0)
        relationships_system.create_rivalry("spec_001", "spec_003", intensity=-85.0)

        original_data = relationships_system.to_dict()

        # Create new system and load
        new_system = RelationshipsSystem({"relationships": {}})
        new_system.from_dict(original_data)

        # Verify friendships
        rel_friend = new_system.specialists_relationships["spec_001"].get_relationship("spec_002")
        assert rel_friend.intensity == 85.0
        assert rel_friend.is_friendship()

        # Verify rivalries
        rel_rival = new_system.specialists_relationships["spec_001"].get_relationship("spec_003")
        assert rel_rival.intensity == -85.0
        assert rel_rival.is_rival()

    def test_deserialize_preserves_all_fields(self, relationships_system):
        """Verify all fields preserved in serialization."""
        relationships_system.record_assignment("spec_001", ["spec_002"], 0.0)
        relationships_system.record_assignment("spec_001", ["spec_002"], 1.0)

        rel_before = relationships_system.specialists_relationships["spec_001"].get_relationship("spec_002")

        original_data = relationships_system.to_dict()
        new_system = RelationshipsSystem({"relationships": {}})
        new_system.from_dict(original_data)

        rel_after = new_system.specialists_relationships["spec_001"].get_relationship("spec_002")

        assert rel_after.incidents_together == rel_before.incidents_together
        assert rel_after.intensity == rel_before.intensity


class TestCaching:
    """Test synergy calculation caching."""

    def test_team_synergy_caches_result(self, relationships_system, three_specialists):
        """Verify team synergy result is cached."""
        # Register all specialists first
        for spec_id in three_specialists:
            relationships_system.register_specialist(spec_id)
        
        relationships_system.create_friendship("spec_001", "spec_002")

        mult_1 = relationships_system.get_team_synergy_multiplier(three_specialists)
        mult_2 = relationships_system.get_team_synergy_multiplier(three_specialists)

        assert mult_1 == mult_2
        assert len(relationships_system._synergy_cache) > 0

    def test_cache_cleared_on_update(self, relationships_system, three_specialists):
        """Verify cache clears when relationships updated."""
        # Register all specialists first
        for spec_id in three_specialists:
            relationships_system.register_specialist(spec_id)
        
        relationships_system.create_friendship("spec_001", "spec_002")
        relationships_system.get_team_synergy_multiplier(three_specialists)

        cache_size = len(relationships_system._synergy_cache)
        assert cache_size > 0

        relationships_system.clear_cache()
        assert len(relationships_system._synergy_cache) == 0

    def test_cache_key_order_independent(self, relationships_system):
        """Verify cache treats team order as same (sorted keys)."""
        team_1 = ["spec_001", "spec_002", "spec_003"]
        team_2 = ["spec_003", "spec_001", "spec_002"]

        # Register all specialists first
        for spec_id in team_1:
            relationships_system.register_specialist(spec_id)

        relationships_system.create_friendship("spec_001", "spec_002")

        mult_1 = relationships_system.get_team_synergy_multiplier(team_1)
        mult_2 = relationships_system.get_team_synergy_multiplier(team_2)

        assert mult_1 == mult_2


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_same_specialist_not_registered_twice(self, relationships_system):
        """Verify registering same specialist twice is idempotent."""
        relationships_system.register_specialist("spec_001")
        relationships_system.register_specialist("spec_001")

        assert len(relationships_system.specialists_relationships) == 1

    def test_rivalry_intensity_clamped_to_minimum(self, relationships_system):
        """Verify rivalry intensity clamped to -50."""
        relationships_system.create_rivalry("spec_001", "spec_002", intensity=-200.0)

        rel = relationships_system.specialists_relationships["spec_001"].get_relationship("spec_002")
        assert rel.intensity <= -50.0

    def test_friendship_intensity_clamped_to_minimum(self, relationships_system):
        """Verify friendship intensity clamped to 50."""
        relationships_system.create_friendship("spec_001", "spec_002", intensity=10.0)

        rel = relationships_system.specialists_relationships["spec_001"].get_relationship("spec_002")
        assert rel.intensity >= 50.0

    def test_relationship_type_enum_values(self):
        """Verify relationship type enum has correct values."""
        assert RelationshipType.NEUTRAL.value == 0.0
        assert RelationshipType.RIVAL.value == -1.0
        assert RelationshipType.FRIENDLY.value == 1.0
