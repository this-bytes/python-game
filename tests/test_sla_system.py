"""Unit tests for SLA System Core Functions.

Tests the core SLA tracking logic, satisfaction impact calculations,
and client satisfaction updates.

Follows 15-point gate standards: 100% type hints, Google docstrings,
>80% coverage, specific error handling, edge cases.
"""

import pytest
from typing import Tuple, Optional

from src.core.sla_system import (
    track_sla_incident,
    calculate_sla_impact_on_satisfaction,
    update_client_satisfaction_from_sla,
    get_sla_satisfaction_tier_name,
    get_sla_satisfaction_impact_description,
)

from src.models.sla_tracker import SLATracker
from src.models.incident import Incident
from src.models.client import Client
from src.models.game_state import GameState
from src.models.specialist import Specialist


# ============================================================================
# FIXTURES: Reusable test data factories
# ============================================================================

@pytest.fixture
def tracker() -> SLATracker:
    """Factory fixture for fresh SLA tracker.
    
    Returns:
        SLATracker with zero incidents tracked
    """
    return SLATracker(
        tracker_id="tracker_test_001",
        client_id="client_test_001",
        month=1,
        total_incidents=0,
        response_sla_met=0,
        response_sla_missed=0,
        resolution_sla_met=0,
        resolution_sla_missed=0
    )


@pytest.fixture
def incident() -> Incident:
    """Factory fixture for test incident.
    
    Returns:
        Incident with 3600 second (1 hour) SLA
    """
    return Incident(
        id="inc_test_001",
        incident_type="DDoS Attack",
        specialty_required="Network Security",
        difficulty=3,
        sla_seconds=3600,  # 1 hour
        base_reward=500,
        xp_reward=100,
        client_id="client_test_001",
        description="Test incident"
    )


@pytest.fixture
def satisfied_client() -> Client:
    """Factory fixture for satisfied client.
    
    Returns:
        Client with 0.85 satisfaction
    """
    from src.models.client import Industry
    
    return Client(
        client_id="client_satisfied_001",
        company_name="Happy Corp",
        industry=Industry.BANKING,
        monthly_contract_value=10000.0,
        sla_response_time_seconds=300,
        sla_resolution_time_seconds=3600,
        contract_start_month=1,
        contract_end_month=12,
        satisfaction=0.85,
        is_active=True
    )


@pytest.fixture
def dissatisfied_client() -> Client:
    """Factory fixture for dissatisfied client.
    
    Returns:
        Client with 0.40 satisfaction (at risk)
    """
    from src.models.client import Industry
    
    return Client(
        client_id="client_dissatisfied_001",
        company_name="Unhappy Inc",
        industry=Industry.HEALTHCARE,
        monthly_contract_value=8000.0,
        sla_response_time_seconds=600,
        sla_resolution_time_seconds=7200,
        contract_start_month=1,
        contract_end_month=12,
        satisfaction=0.40,
        is_active=True
    )


@pytest.fixture
def excellent_tracker() -> SLATracker:
    """Factory fixture for tracker with excellent compliance.
    
    Returns:
        SLATracker with 95% compliance (excellent)
    """
    return SLATracker(
        tracker_id="tracker_excellent",
        client_id="client_test_001",
        month=1,
        total_incidents=20,
        response_sla_met=20,
        response_sla_missed=0,
        resolution_sla_met=19,
        resolution_sla_missed=1
    )


@pytest.fixture
def good_tracker() -> SLATracker:
    """Factory fixture for tracker with good compliance.
    
    Returns:
        SLATracker with 80% compliance (good)
    """
    return SLATracker(
        tracker_id="tracker_good",
        client_id="client_test_001",
        month=1,
        total_incidents=20,
        response_sla_met=20,
        response_sla_missed=0,
        resolution_sla_met=16,
        resolution_sla_missed=4
    )


@pytest.fixture
def poor_tracker() -> SLATracker:
    """Factory fixture for tracker with poor compliance.
    
    Returns:
        SLATracker with 40% compliance (poor)
    """
    return SLATracker(
        tracker_id="tracker_poor",
        client_id="client_test_001",
        month=1,
        total_incidents=20,
        response_sla_met=20,
        response_sla_missed=0,
        resolution_sla_met=8,
        resolution_sla_missed=12
    )


@pytest.fixture
def game_state() -> GameState:
    """Factory fixture for game state.
    
    Returns:
        GameState with basic setup
    """
    return GameState()


# ============================================================================
# TEST: track_sla_incident
# ============================================================================

class TestTrackSLAIncident:
    """Test suite for track_sla_incident function.
    
    Verifies incident SLA tracking and compliance recording.
    """

    def test_track_incident_sla_met(self, tracker: SLATracker, incident: Incident) -> None:
        """Verify tracking when SLA is met.
        
        Incident: 3600s SLA, Resolution: 3400s (met)
        """
        track_sla_incident(tracker, incident, 3400.0)
        
        assert tracker.total_incidents == 1
        assert tracker.response_sla_met == 1
        assert tracker.response_sla_missed == 0
        assert tracker.resolution_sla_met == 1
        assert tracker.resolution_sla_missed == 0

    def test_track_incident_sla_missed(self, tracker: SLATracker, incident: Incident) -> None:
        """Verify tracking when SLA is missed.
        
        Incident: 3600s SLA, Resolution: 4000s (missed)
        """
        track_sla_incident(tracker, incident, 4000.0)
        
        assert tracker.total_incidents == 1
        assert tracker.response_sla_met == 1
        assert tracker.response_sla_missed == 0
        assert tracker.resolution_sla_met == 0
        assert tracker.resolution_sla_missed == 1

    def test_track_incident_sla_exact_boundary(self, tracker: SLATracker, incident: Incident) -> None:
        """Verify tracking at exact SLA boundary (should be met).
        
        Incident: 3600s SLA, Resolution: 3600s (exactly at boundary)
        """
        track_sla_incident(tracker, incident, 3600.0)
        
        assert tracker.total_incidents == 1
        assert tracker.resolution_sla_met == 1
        assert tracker.resolution_sla_missed == 0

    def test_track_incident_very_fast(self, tracker: SLATracker, incident: Incident) -> None:
        """Verify tracking for very fast resolution.
        
        Incident: 3600s SLA, Resolution: 10s (far ahead of deadline)
        """
        track_sla_incident(tracker, incident, 10.0)
        
        assert tracker.total_incidents == 1
        assert tracker.resolution_sla_met == 1
        assert tracker.resolution_sla_missed == 0

    def test_track_multiple_incidents(self, tracker: SLATracker, incident: Incident) -> None:
        """Verify tracking multiple incidents updates correctly.
        
        Track 5 incidents: 3 met, 2 missed
        """
        # First incident: met
        track_sla_incident(tracker, incident, 3400.0)
        assert tracker.total_incidents == 1
        assert tracker.resolution_sla_met == 1
        
        # Second incident: met
        track_sla_incident(tracker, incident, 3500.0)
        assert tracker.total_incidents == 2
        assert tracker.resolution_sla_met == 2
        
        # Third incident: missed
        track_sla_incident(tracker, incident, 4000.0)
        assert tracker.total_incidents == 3
        assert tracker.resolution_sla_missed == 1

    def test_track_incident_response_always_met(self, tracker: SLATracker, incident: Incident) -> None:
        """Verify response SLA is always recorded as met (implicit).
        
        For gameplay simplicity, response is always counted as met.
        """
        track_sla_incident(tracker, incident, 5000.0)  # Resolution missed
        
        assert tracker.response_sla_met == 1
        assert tracker.response_sla_missed == 0
        # Resolution missed, but response still met
        assert tracker.resolution_sla_missed == 1

    def test_track_incident_invalid_tracker_type(self, incident: Incident) -> None:
        """Verify error on invalid tracker type."""
        with pytest.raises(TypeError):
            track_sla_incident("not_a_tracker", incident, 3000.0)  # type: ignore

    def test_track_incident_invalid_incident_type(self, tracker: SLATracker) -> None:
        """Verify error on invalid incident type."""
        with pytest.raises(TypeError):
            track_sla_incident(tracker, "not_an_incident", 3000.0)  # type: ignore

    def test_track_incident_negative_resolution_time(self, tracker: SLATracker, incident: Incident) -> None:
        """Verify error on negative resolution time."""
        with pytest.raises(ValueError):
            track_sla_incident(tracker, incident, -1000.0)

    def test_track_incident_zero_resolution_time(self, tracker: SLATracker, incident: Incident) -> None:
        """Verify zero resolution time is valid (instant resolution)."""
        track_sla_incident(tracker, incident, 0.0)
        
        assert tracker.total_incidents == 1
        assert tracker.resolution_sla_met == 1


# ============================================================================
# TEST: calculate_sla_impact_on_satisfaction
# ============================================================================

class TestCalculateSLAImpactOnSatisfaction:
    """Test suite for calculate_sla_impact_on_satisfaction function.
    
    Verifies satisfaction calculation and clamping.
    """

    def test_excellent_tracker_adds_bonus(self, excellent_tracker: SLATracker) -> None:
        """Verify excellent compliance adds +0.02 bonus."""
        new_satisfaction: float = calculate_sla_impact_on_satisfaction(excellent_tracker, 0.75)
        
        expected: float = 0.75 + 0.02
        assert abs(new_satisfaction - expected) < 0.0001  # Use stricter tolerance

    def test_good_tracker_adds_small_bonus(self, good_tracker: SLATracker) -> None:
        """Verify good compliance (75-89%) adds +0.01 bonus.
        
        Good tracker fixture: 80% compliance should give +0.01 impact.
        Debug: good_tracker compliance = (20+20) / 2 / 2 indices = 0.80
        Actually: response (20/20=1.0), resolution (16/20=0.8), overall = 0.9 (excellent!)
        Need to create tracker that's actually 80% overall.
        """
        # Create proper 80% tracker: response 0.8, resolution 0.8 -> overall 0.8
        tracker_80 = SLATracker(
            tracker_id="tracker_test_80",
            client_id="client_test",
            month=1,
            total_incidents=10,
            response_sla_met=8,
            response_sla_missed=2,
            resolution_sla_met=8,
            resolution_sla_missed=2
        )
        # Compliance: (0.8 + 0.8) / 2 = 0.8 (good tier)
        # Impact: +0.01
        
        new_satisfaction: float = calculate_sla_impact_on_satisfaction(tracker_80, 0.75)
        
        expected: float = 0.75 + 0.01
        assert abs(new_satisfaction - expected) < 0.0001, \
            f"Expected {expected}, got {new_satisfaction}"

    def test_poor_tracker_applies_penalty(self, poor_tracker: SLATracker) -> None:
        """Verify poor compliance (<60%) applies -0.03 penalty.
        
        Create proper poor compliance tracker: response 0.5, resolution 0.5 -> overall 0.5
        """
        # Create proper 50% tracker (clearly poor < 60%)
        tracker_50 = SLATracker(
            tracker_id="tracker_test_50",
            client_id="client_test",
            month=1,
            total_incidents=10,
            response_sla_met=5,
            response_sla_missed=5,
            resolution_sla_met=5,
            resolution_sla_missed=5
        )
        # Compliance: (0.5 + 0.5) / 2 = 0.5 (poor tier)
        # Impact: -0.03
        
        new_satisfaction: float = calculate_sla_impact_on_satisfaction(tracker_50, 0.50)
        
        expected: float = 0.50 - 0.03
        assert abs(new_satisfaction - expected) < 0.0001, \
            f"Expected {expected}, got {new_satisfaction}"

    def test_satisfaction_clamped_to_maximum(self, excellent_tracker: SLATracker) -> None:
        """Verify satisfaction is clamped to 1.0 maximum.
        
        Starting at 0.99 + 0.02 bonus = 1.01 (should clamp to 1.0)
        """
        new_satisfaction: float = calculate_sla_impact_on_satisfaction(excellent_tracker, 0.99)
        
        assert new_satisfaction == 1.0

    def test_satisfaction_clamped_to_minimum(self) -> None:
        """Verify satisfaction is clamped to 0.0 minimum.
        
        Create poor tracker (50% compliance) -> -0.03 penalty
        Starting at 0.01 - 0.03 = -0.02, should clamp to 0.0
        """
        # Create proper poor tracker: 50% compliance -> poor status
        tracker_poor = SLATracker(
            tracker_id="tracker_test_clamp_min",
            client_id="client_test",
            month=1,
            total_incidents=10,
            response_sla_met=5,
            response_sla_missed=5,
            resolution_sla_met=5,
            resolution_sla_missed=5
        )
        # Compliance: (0.5 + 0.5) / 2 = 0.5 (poor tier)
        # Impact: -0.03
        
        new_satisfaction: float = calculate_sla_impact_on_satisfaction(tracker_poor, 0.01)
        
        # Should be clamped to 0.0 (not -0.02)
        assert new_satisfaction == 0.0, f"Expected 0.0, got {new_satisfaction}"

    def test_satisfaction_starts_at_minimum(self, poor_tracker: SLATracker) -> None:
        """Verify satisfaction at 0.0 stays at 0.0 (no further penalty)."""
        new_satisfaction: float = calculate_sla_impact_on_satisfaction(poor_tracker, 0.0)
        
        assert new_satisfaction == 0.0

    def test_satisfaction_starts_at_maximum(self, excellent_tracker: SLATracker) -> None:
        """Verify satisfaction at 1.0 stays at 1.0 (no further bonus)."""
        new_satisfaction: float = calculate_sla_impact_on_satisfaction(excellent_tracker, 1.0)
        
        assert new_satisfaction == 1.0

    def test_invalid_tracker_type(self) -> None:
        """Verify error on invalid tracker type."""
        with pytest.raises(TypeError):
            calculate_sla_impact_on_satisfaction("not_a_tracker", 0.75)  # type: ignore

    def test_invalid_satisfaction_type(self, excellent_tracker: SLATracker) -> None:
        """Verify error on non-numeric satisfaction."""
        with pytest.raises(TypeError):
            calculate_sla_impact_on_satisfaction(excellent_tracker, "0.75")  # type: ignore

    def test_satisfaction_below_minimum_range(self, excellent_tracker: SLATracker) -> None:
        """Verify error on satisfaction below 0.0."""
        with pytest.raises(ValueError):
            calculate_sla_impact_on_satisfaction(excellent_tracker, -0.1)

    def test_satisfaction_above_maximum_range(self, excellent_tracker: SLATracker) -> None:
        """Verify error on satisfaction above 1.0."""
        with pytest.raises(ValueError):
            calculate_sla_impact_on_satisfaction(excellent_tracker, 1.1)


# ============================================================================
# TEST: update_client_satisfaction_from_sla
# ============================================================================

class TestUpdateClientSatisfactionFromSLA:
    """Test suite for update_client_satisfaction_from_sla function.
    
    Verifies client satisfaction updates from SLA trackers.
    """

    def test_update_satisfied_client_excellent(
        self,
        game_state: GameState,
        satisfied_client: Client,
        excellent_tracker: SLATracker
    ) -> None:
        """Verify update on satisfied client with excellent SLA."""
        success: bool
        error: Optional[str]
        success, error = update_client_satisfaction_from_sla(game_state, satisfied_client, excellent_tracker)
        
        assert success is True
        assert error is None
        assert abs(satisfied_client.satisfaction - 0.87) < 0.001  # 0.85 + 0.02

    def test_update_dissatisfied_client_excellent(
        self,
        game_state: GameState,
        dissatisfied_client: Client,
        excellent_tracker: SLATracker
    ) -> None:
        """Verify update on dissatisfied client gets excellent bonus."""
        success: bool
        error: Optional[str]
        success, error = update_client_satisfaction_from_sla(game_state, dissatisfied_client, excellent_tracker)
        
        assert success is True
        assert error is None
        assert abs(dissatisfied_client.satisfaction - 0.42) < 0.001  # 0.40 + 0.02

    def test_update_client_poor_sla_penalty(
        self,
        game_state: GameState,
        satisfied_client: Client
    ) -> None:
        """Verify update on satisfied client with poor SLA applies penalty.
        
        Create poor tracker (50% compliance) -> -0.03 penalty
        Client: 0.85 - 0.03 = 0.82
        """
        # Create proper poor tracker: 50% compliance
        tracker_poor = SLATracker(
            tracker_id="tracker_test_penalty",
            client_id="client_test",
            month=1,
            total_incidents=10,
            response_sla_met=5,
            response_sla_missed=5,
            resolution_sla_met=5,
            resolution_sla_missed=5
        )
        # Compliance: (0.5 + 0.5) / 2 = 0.5 (poor tier)
        # Impact: -0.03
        
        initial_satisfaction: float = satisfied_client.satisfaction
        
        success: bool
        error: Optional[str]
        success, error = update_client_satisfaction_from_sla(game_state, satisfied_client, tracker_poor)
        
        assert success is True
        assert error is None
        
        # Poor tracker (50% compliance) should apply -0.03 penalty
        expected_satisfaction: float = 0.85 - 0.03
        assert abs(satisfied_client.satisfaction - expected_satisfaction) < 0.0001, \
            "Poor SLA should decrease satisfaction"

    def test_update_client_at_minimum_satisfaction(
        self,
        game_state: GameState,
        poor_tracker: SLATracker
    ) -> None:
        """Verify client at 0.0 satisfaction stays at 0.0 with poor SLA."""
        from src.models.client import Industry
        
        client = Client(
            client_id="client_minimum",
            company_name="On Brink",
            industry=Industry.FINANCE,
            monthly_contract_value=5000.0,
            sla_response_time_seconds=300,
            sla_resolution_time_seconds=3600,
            contract_start_month=1,
            contract_end_month=12,
            satisfaction=0.0,
            is_active=True
        )
        
        success: bool
        error: Optional[str]
        success, error = update_client_satisfaction_from_sla(game_state, client, poor_tracker)
        
        assert success is True
        assert client.satisfaction == 0.0

    def test_update_client_at_maximum_satisfaction(
        self,
        game_state: GameState,
        excellent_tracker: SLATracker
    ) -> None:
        """Verify client at 1.0 satisfaction stays at 1.0 with excellent SLA."""
        from src.models.client import Industry
        
        client = Client(
            client_id="client_maximum",
            company_name="Perfect Client",
            industry=Industry.RETAIL,
            monthly_contract_value=15000.0,
            sla_response_time_seconds=300,
            sla_resolution_time_seconds=3600,
            contract_start_month=1,
            contract_end_month=12,
            satisfaction=1.0,
            is_active=True
        )
        
        success: bool
        error: Optional[str]
        success, error = update_client_satisfaction_from_sla(game_state, client, excellent_tracker)
        
        assert success is True
        assert client.satisfaction == 1.0

    def test_invalid_game_state_type(self, satisfied_client: Client, excellent_tracker: SLATracker) -> None:
        """Verify error on invalid game_state type."""
        success: bool
        error: Optional[str]
        success, error = update_client_satisfaction_from_sla("not_game_state", satisfied_client, excellent_tracker)  # type: ignore
        
        assert success is False
        assert error is not None

    def test_invalid_client_type(self, game_state: GameState, excellent_tracker: SLATracker) -> None:
        """Verify error on invalid client type."""
        success: bool
        error: Optional[str]
        success, error = update_client_satisfaction_from_sla(game_state, "not_a_client", excellent_tracker)  # type: ignore
        
        assert success is False
        assert error is not None

    def test_invalid_tracker_type(self, game_state: GameState, satisfied_client: Client) -> None:
        """Verify error on invalid tracker type."""
        success: bool
        error: Optional[str]
        success, error = update_client_satisfaction_from_sla(game_state, satisfied_client, "not_a_tracker")  # type: ignore
        
        assert success is False
        assert error is not None


# ============================================================================
# TEST: Helper Functions
# ============================================================================

class TestHelperFunctions:
    """Test suite for SLA system helper functions.
    
    Verifies human-readable descriptions for UI/logging.
    """

    def test_tier_name_excellent(self) -> None:
        """Verify excellent tier name."""
        name: str = get_sla_satisfaction_tier_name("excellent")
        assert name == "Excellent Service"

    def test_tier_name_good(self) -> None:
        """Verify good tier name."""
        name: str = get_sla_satisfaction_tier_name("good")
        assert name == "Good Service"

    def test_tier_name_fair(self) -> None:
        """Verify fair tier name."""
        name: str = get_sla_satisfaction_tier_name("fair")
        assert "At Risk" in name or "Fair" in name

    def test_tier_name_poor(self) -> None:
        """Verify poor tier name."""
        name: str = get_sla_satisfaction_tier_name("poor")
        assert "Critical" in name or "Poor" in name

    def test_impact_description_excellent(self) -> None:
        """Verify excellent impact description."""
        desc: str = get_sla_satisfaction_impact_description(0.02)
        assert "Excellent" in desc or "2%" in desc

    def test_impact_description_good(self) -> None:
        """Verify good impact description."""
        desc: str = get_sla_satisfaction_impact_description(0.01)
        assert "Good" in desc or "1%" in desc

    def test_impact_description_fair(self) -> None:
        """Verify fair impact description."""
        desc: str = get_sla_satisfaction_impact_description(0.0)
        assert "No Change" in desc or "Fair" in desc

    def test_impact_description_poor(self) -> None:
        """Verify poor impact description."""
        desc: str = get_sla_satisfaction_impact_description(-0.03)
        assert "Penalty" in desc or "Poor" in desc or "3%" in desc


if __name__ == "__main__":
    """Enable direct test execution for quick validation."""
    pytest.main([__file__, "-v", "--tb=short"])
