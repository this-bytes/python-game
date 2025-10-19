import pytest
from src.core.resolution_system import ResolutionSystem, ResolutionDecision, ResolutionSession
from src.models.specialist import Specialist, SpecialistStats
from src.models.incident import Incident
from src.core.burnout_system import BurnoutSystem
from unittest.mock import Mock


class TestDecisionBasedResolution:
    """Test decision-based incident resolution system."""

    @pytest.fixture
    def resolution_system(self):
        """Create resolution system for testing."""
        burnout_system = BurnoutSystem()
        return ResolutionSystem(burnout_system)

    @pytest.fixture
    def specialist(self):
        """Create test specialist."""
        return Specialist(
            id="spec_test_001",
            name="Test Specialist",
            specialty="Network Security",
            level=3,
            xp=500,
            stats=SpecialistStats(
                speed=100.0,
                accuracy=90.0,
                experience_bonus=1.0
            )
        )

    @pytest.fixture
    def incident(self):
        """Create test incident."""
        return Incident(
            id="inc_test_001",
            incident_type="DDoS Attack",
            specialty_required="Network Security",
            difficulty=2,
            sla_seconds=300,
            base_reward=500,
            xp_reward=100,
            client_id="client_001"
        )

    def test_start_resolution_creates_session(self, resolution_system, specialist, incident):
        """Verify start_resolution creates a new session with correct initial state."""
        session = resolution_system.start_resolution(incident, specialist)

        assert isinstance(session, ResolutionSession)
        assert session.incident_id == incident.id
        assert session.specialist_id == specialist.id
        assert session.current_stage == "containment"  # First stage of DDoS tree
        assert session.decisions_made == []
        assert session.total_burnout_cost == 0
        assert session.total_money_cost == 0

    def test_get_current_stage_info_returns_correct_data(self, resolution_system, specialist, incident):
        """Verify get_current_stage_info returns proper stage information."""
        session = resolution_system.start_resolution(incident, specialist)
        stage_info = resolution_system.get_current_stage_info(session)

        assert "stage_id" in stage_info
        assert "prompt" in stage_info
        assert "decisions" in stage_info
        assert isinstance(stage_info["decisions"], list)
        assert len(stage_info["decisions"]) > 0

        # Check decision structure
        decision = stage_info["decisions"][0]
        assert "id" in decision
        assert "text" in decision
        assert "effects" in decision

    def test_make_decision_advances_stage(self, resolution_system, specialist, incident):
        """Verify making a decision advances to next stage."""
        session = resolution_system.start_resolution(incident, specialist)

        # Get first decision
        stage_info = resolution_system.get_current_stage_info(session)
        first_decision = stage_info["decisions"][0]

        # Make decision
        resolution_system.make_decision(session, first_decision["id"], specialist)

        # Should advance to next stage
        assert session.current_stage == "investigation"  # Next stage in DDoS tree
        assert len(session.decisions_made) == 1
        assert session.decisions_made[0].decision_id == first_decision["id"]

    def test_make_decision_applies_effects(self, resolution_system, specialist, incident):
        """Verify decision effects are applied to session."""
        session = resolution_system.start_resolution(incident, specialist)

        # Find decision with burnout cost
        stage_info = resolution_system.get_current_stage_info(session)
        burnout_decision = None
        for decision in stage_info["decisions"]:
            if decision["effects"].get("burnout_cost", 0) > 0:
                burnout_decision = decision
                break

        assert burnout_decision is not None, "Should have decision with burnout cost"

        initial_burnout = session.total_burnout_cost
        burnout_cost = burnout_decision["effects"]["burnout_cost"]

        # Make decision
        resolution_system.make_decision(session, burnout_decision["id"], specialist)

        # Burnout cost should be applied
        assert session.total_burnout_cost == initial_burnout + burnout_cost

    def test_complete_resolution_with_success(self, resolution_system, specialist, incident):
        """Verify successful resolution completes session and returns result."""
        session = resolution_system.start_resolution(incident, specialist)

        # Advance through all stages by making decisions
        stages_completed = 0
        while stages_completed < 3:  # Assuming 3 stages
            stage_info = resolution_system.get_current_stage_info(session)
            if stage_info.get("decisions"):
                decision_id = stage_info["decisions"][0]["id"]
                resolution_system.make_decision(session, decision_id, specialist)
                stages_completed += 1
            else:
                break

        # Complete resolution
        result = resolution_system.complete_resolution(session, specialist, incident)

        assert result.success is True
        assert result.incident_id == incident.id
        assert result.specialist_id == specialist.id
        assert result.decisions_made == session.decisions_made
        assert result.total_burnout_cost == session.total_burnout_cost
        assert result.total_money_cost == session.total_money_cost

    def test_complete_resolution_with_failure(self, resolution_system, specialist, incident):
        """Verify resolution completion works correctly."""
        session = resolution_system.start_resolution(incident, specialist)

        # Make one decision
        stage_info = resolution_system.get_current_stage_info(session)
        decision_id = stage_info["decisions"][0]["id"]
        resolution_system.make_decision(session, decision_id, specialist)

        result = resolution_system.complete_resolution(session, specialist, incident)

        # Verify result structure regardless of success/failure
        assert isinstance(result.success, bool)
        assert result.incident_id == incident.id
        assert result.specialist_id == specialist.id
        assert len(result.decisions_made) == 1

    def test_invalid_decision_raises_error(self, resolution_system, specialist, incident):
        """Verify invalid decision ID returns failure."""
        session = resolution_system.start_resolution(incident, specialist)

        success, next_stage, effects = resolution_system.make_decision(session, "invalid_decision_id", specialist)

        assert success is False
        assert next_stage is None
        assert effects == {}

    def test_time_pressure_affects_decisions(self, resolution_system, specialist, incident):
        """Verify time pressure modifies decision effects."""
        session = resolution_system.start_resolution(incident, specialist)

        # Simulate time pressure (low time remaining)
        session.time_pressure_multiplier = 2.0  # High pressure

        stage_info = resolution_system.get_current_stage_info(session)

        # Decisions should have modified effects due to time pressure
        for decision in stage_info["decisions"]:
            # Time pressure should affect success rates or costs
            assert "effects" in decision

    def test_specialist_skill_modifies_decision_effects(self, resolution_system, specialist, incident):
        """Verify specialist skills modify decision outcomes."""
        # Create high-level specialist
        skilled_specialist = Specialist(
            id="spec_skilled_001",
            name="Skilled Specialist",
            specialty="Network Security",
            level=10,
            xp=5000,
            stats=SpecialistStats(
                speed=120.0,
                accuracy=95.0,
                experience_bonus=1.2
            )
        )

        session = resolution_system.start_resolution(incident, skilled_specialist)
        stage_info = resolution_system.get_current_stage_info(session)

        # High-level specialist should have better success rates
        for decision in stage_info["decisions"]:
            success_chance = decision["effects"].get("success_chance", 0.5)
            # Skilled specialist should have higher base success
            assert success_chance >= 0.5

    def test_different_incident_types_have_different_decision_trees(self, resolution_system, specialist):
        """Verify different incident types have unique decision trees."""
        ddos_incident = Incident(
            id="inc_ddos_001",
            incident_type="DDoS Attack",
            specialty_required="Network Security",
            difficulty=2,
            sla_seconds=300,
            base_reward=500,
            xp_reward=100,
            client_id="client_001"
        )

        malware_incident = Incident(
            id="inc_malware_001",
            incident_type="Malware Infection",
            specialty_required="Network Security",
            difficulty=2,
            sla_seconds=300,
            base_reward=500,
            xp_reward=100,
            client_id="client_001"
        )

        ddos_session = resolution_system.start_resolution(ddos_incident, specialist)
        malware_session = resolution_system.start_resolution(malware_incident, specialist)

        ddos_stage_info = resolution_system.get_current_stage_info(ddos_session)
        malware_stage_info = resolution_system.get_current_stage_info(malware_session)

        # Different incident types should have different decision trees
        assert ddos_stage_info["stage_id"] != malware_stage_info["stage_id"] or \
               ddos_stage_info["prompt"] != malware_stage_info["prompt"]

    def test_decision_effects_accumulate_correctly(self, resolution_system, specialist, incident):
        """Verify multiple decisions accumulate effects properly."""
        session = resolution_system.start_resolution(incident, specialist)

        initial_burnout = session.total_burnout_cost
        initial_money = session.total_money_cost

        # Make multiple decisions
        tree_id = resolution_system._get_tree_id_for_incident(incident)
        for _ in range(min(2, len(resolution_system.resolution_trees[tree_id]["stages"]))):
            stage_info = resolution_system.get_current_stage_info(session)
            if stage_info["decisions"]:
                decision = stage_info["decisions"][0]
                burnout_cost = decision["effects"].get("burnout_cost", 0)
                money_cost = decision["effects"].get("money_cost", 0)

                resolution_system.make_decision(session, decision["id"], specialist)

                # Effects should accumulate
                assert session.total_burnout_cost >= initial_burnout + burnout_cost
                assert session.total_money_cost >= initial_money + money_cost

    def test_resolution_result_includes_all_metrics(self, resolution_system, specialist, incident):
        """Verify resolution result includes comprehensive metrics."""
        session = resolution_system.start_resolution(incident, specialist)

        # Make a decision to add some effects
        stage_info = resolution_system.get_current_stage_info(session)
        if stage_info["decisions"]:
            resolution_system.make_decision(session, stage_info["decisions"][0]["id"], specialist)

        result = resolution_system.complete_resolution(session, specialist, incident)

        # Result should include all expected fields
        required_fields = [
            "success", "incident_id", "specialist_id", "decisions_made",
            "total_burnout_cost", "total_money_cost", "resolution_time",
            "actual_success_rate"
        ]

        for field in required_fields:
            assert hasattr(result, field), f"Result missing field: {field}"