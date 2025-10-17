"""Tests for resolution system with burnout integration."""

import pytest
from src.core.resolution_system import ResolutionSystem
from src.core.burnout_system import BurnoutSystem
from src.models.specialist import Specialist, SpecialistStats
from src.models.incident import Incident


@pytest.fixture
def burnout_system():
    return BurnoutSystem()


@pytest.fixture
def resolution_system(burnout_system):
    return ResolutionSystem(burnout_system)


@pytest.fixture
def specialist():
    return Specialist(
        id="test_001",
        name="Test",
        specialty="Network Security",
        level=5,
        xp=0,
        stats=SpecialistStats(100, 85, 1.0)
    )


@pytest.fixture
def incident():
    return Incident(
        id="inc_001",
        incident_type="DDoS Attack",
        specialty_required="Network Security",
        difficulty=2,
        sla_seconds=300,
        base_reward=500,
        xp_reward=100,
        client_id="client_001"
    )


class TestResolutionTiming:
    """Test resolution time calculations with burnout."""

    def test_fresh_specialist_no_slowdown(self, resolution_system, specialist, incident):
        """Specialist with 0% burnout resolves at normal speed."""
        specialist.burnout_level = 0.0
        time, mult = resolution_system.calculate_resolution_time(
            specialist, incident, 100.0
        )
        assert time == 100.0
        assert mult == 1.0

    def test_stressed_specialist_10_percent_slowdown(self, resolution_system, specialist, incident):
        """Specialist at 30% burnout (STRESSED) is ~30% slower."""
        specialist.burnout_level = 30.0
        time, mult = resolution_system.calculate_resolution_time(
            specialist, incident, 100.0
        )
        assert mult == pytest.approx(0.7, abs=0.01)
        assert time == pytest.approx(142.8, abs=1.0)

    def test_exhausted_specialist_50_percent_slowdown(self, resolution_system, specialist, incident):
        """Specialist at 50% burnout (EXHAUSTED) is ~50% slower."""
        specialist.burnout_level = 50.0
        time, mult = resolution_system.calculate_resolution_time(
            specialist, incident, 100.0
        )
        assert mult == pytest.approx(0.5, abs=0.01)
        assert time == pytest.approx(200.0, abs=1.0)

    def test_critical_specialist_75_percent_slowdown(self, resolution_system, specialist, incident):
        """Specialist at 70% burnout (CRITICAL) is ~3.3x slower."""
        specialist.burnout_level = 70.0
        time, mult = resolution_system.calculate_resolution_time(
            specialist, incident, 100.0
        )
        assert mult == pytest.approx(0.30, abs=0.01)
        assert time == pytest.approx(333.3, abs=1.0)

    def test_broken_specialist_cannot_resolve(self, resolution_system, specialist, incident):
        """Specialist at 100% burnout (BROKEN) cannot resolve."""
        specialist.burnout_level = 100.0
        time, mult = resolution_system.calculate_resolution_time(
            specialist, incident, 100.0
        )
        assert mult == 0.0
        assert time == float('inf')


class TestSuccessRate:
    """Test success rate calculations with error chance."""

    def test_fresh_specialist_full_success_rate(self, resolution_system, specialist, incident):
        """Specialist with 0% burnout has full success rate."""
        specialist.burnout_level = 0.0
        rate = resolution_system.calculate_success_rate(
            specialist, incident, base_success_rate=0.9
        )
        assert rate == pytest.approx(0.9, abs=0.01)

    def test_stressed_specialist_error_chance(self, resolution_system, specialist, incident):
        """Specialist at 30% burnout has 15% error chance."""
        specialist.burnout_level = 30.0
        rate = resolution_system.calculate_success_rate(
            specialist, incident, base_success_rate=0.9
        )
        expected = 0.9 * (1.0 - 0.15)
        assert rate == pytest.approx(expected, abs=0.01)

    def test_exhausted_specialist_error_chance(self, resolution_system, specialist, incident):
        """Specialist at 50% burnout (EXHAUSTED) has 25% error chance."""
        specialist.burnout_level = 50.0
        rate = resolution_system.calculate_success_rate(
            specialist, incident, base_success_rate=0.9
        )
        expected = 0.9 * (1.0 - 0.25)
        assert rate == pytest.approx(expected, abs=0.01)

    def test_broken_specialist_half_success_rate(self, resolution_system, specialist, incident):
        """Specialist at 100% burnout (BROKEN) has 50% error chance."""
        specialist.burnout_level = 100.0
        rate = resolution_system.calculate_success_rate(
            specialist, incident, base_success_rate=0.9
        )
        expected = 0.9 * (1.0 - 0.5)
        assert rate == pytest.approx(expected, abs=0.01)


class TestAttemptResolution:
    """Test full resolution attempts."""

    def test_fresh_specialist_likely_succeeds(self, resolution_system, specialist, incident):
        """Fresh specialist has high success rate."""
        specialist.burnout_level = 0.0
        successes = 0
        for _ in range(100):
            result = resolution_system.attempt_resolution(
                specialist, incident, base_time=100, base_success_rate=0.9
            )
            if result.success:
                successes += 1
        assert successes > 70  # Should be ~90 successes

    def test_result_has_metrics(self, resolution_system, specialist, incident):
        """Resolution result includes all metrics."""
        specialist.burnout_level = 50.0
        result = resolution_system.attempt_resolution(specialist, incident)

        assert result.specialist_id == specialist.id
        assert result.incident_id == incident.id
        assert result.base_time == 100.0
        assert result.burnout_multiplier == pytest.approx(0.5, abs=0.01)
        assert result.resolution_time == pytest.approx(200.0, abs=1.0)
        assert result.error_chance > 0.0


class TestCompleteIncident:
    """Test incident completion with burnout tracking."""

    def test_successful_completion_updates_burnout(
        self, resolution_system, burnout_system, specialist, incident
    ):
        """Successful completion updates burnout system."""
        burnout_system.register_specialist(specialist.id)
        burnout_system.assign_incident(specialist.id, incident_difficulty=2)

        result = resolution_system.complete_incident(
            specialist, incident, success=True
        )

        assert result['success'] is True
        assert result['specialist_id'] == specialist.id
        assert result['incident_id'] == incident.id
        assert 'burnout_level' in result
        assert 'burnout_tier' in result

    def test_failed_completion_adds_trauma(
        self, resolution_system, burnout_system, specialist, incident
    ):
        """Failed completion adds trauma (extra burnout)."""
        burnout_system.register_specialist(specialist.id)
        burnout_system.assign_incident(specialist.id, incident_difficulty=2)
        
        # Get the specialist from burnout system to see state
        burnout_spec = burnout_system.specialists[specialist.id]
        initial_burnout = burnout_spec.burnout_level

        resolution_system.complete_incident(
            specialist, incident, success=False
        )

        assert burnout_spec.burnout_level > initial_burnout  # Should be +10%

    def test_incident_marked_resolved(
        self, resolution_system, burnout_system, specialist, incident
    ):
        """Incident is marked as resolved."""
        burnout_system.register_specialist(specialist.id)
        assert incident.status != "resolved"

        resolution_system.complete_incident(
            specialist, incident, success=True
        )

        assert incident.is_resolved()
