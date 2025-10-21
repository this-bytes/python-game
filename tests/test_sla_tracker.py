"""Unit tests for expanded SLA Tracker model.

Tests SLA compliance calculations, status categorization, and satisfaction
impact calculations that drive client satisfaction mechanics.

Follows 15-point gate standards: 100% type hints, Google docstrings,
>80% coverage, specific error handling, edge case validation.
"""

import pytest
from typing import Literal, Dict

from src.models.sla_tracker import SLATracker


# ============================================================================
# FIXTURES: Reusable test data factories
# ============================================================================

@pytest.fixture
def perfect_tracker() -> SLATracker:
    """Factory fixture for perfect compliance tracker.
    
    Returns:
        SLATracker with 100% compliance on all metrics
    """
    tracker = SLATracker(
        tracker_id="tracker_perfect_001",
        client_id="client_001",
        month=1,
        total_incidents=10,
        response_sla_met=10,
        response_sla_missed=0,
        resolution_sla_met=10,
        resolution_sla_missed=0
    )
    return tracker


@pytest.fixture
def excellent_tracker() -> SLATracker:
    """Factory fixture for excellent compliance tracker (95%).
    
    Returns:
        SLATracker with 95% compliance (excellent tier)
    """
    tracker = SLATracker(
        tracker_id="tracker_excellent_001",
        client_id="client_001",
        month=1,
        total_incidents=10,
        response_sla_met=9,
        response_sla_missed=1,
        resolution_sla_met=10,
        resolution_sla_missed=0
    )
    return tracker


@pytest.fixture
def good_tracker() -> SLATracker:
    """Factory fixture for good compliance tracker (80%).
    
    Returns:
        SLATracker with 80% compliance (good tier)
    """
    tracker = SLATracker(
        tracker_id="tracker_good_001",
        client_id="client_001",
        month=1,
        total_incidents=10,
        response_sla_met=8,
        response_sla_missed=2,
        resolution_sla_met=8,
        resolution_sla_missed=2
    )
    return tracker


@pytest.fixture
def fair_tracker() -> SLATracker:
    """Factory fixture for fair compliance tracker (65%).
    
    Returns:
        SLATracker with 65% compliance (fair tier)
    """
    tracker = SLATracker(
        tracker_id="tracker_fair_001",
        client_id="client_001",
        month=1,
        total_incidents=10,
        response_sla_met=7,
        response_sla_missed=3,
        resolution_sla_met=6,
        resolution_sla_missed=4
    )
    return tracker


@pytest.fixture
def poor_tracker() -> SLATracker:
    """Factory fixture for poor compliance tracker (40%).
    
    Returns:
        SLATracker with 40% compliance (poor tier - critical)
    """
    tracker = SLATracker(
        tracker_id="tracker_poor_001",
        client_id="client_001",
        month=1,
        total_incidents=10,
        response_sla_met=3,
        response_sla_missed=7,
        resolution_sla_met=5,
        resolution_sla_missed=5
    )
    return tracker


@pytest.fixture
def no_incidents_tracker() -> SLATracker:
    """Factory fixture for tracker with no incidents (edge case).
    
    Returns:
        SLATracker with zero incidents (should default to perfect compliance)
    """
    tracker = SLATracker(
        tracker_id="tracker_empty_001",
        client_id="client_001",
        month=1,
        total_incidents=0,
        response_sla_met=0,
        response_sla_missed=0,
        resolution_sla_met=0,
        resolution_sla_missed=0
    )
    return tracker


# ============================================================================
# TEST: COMPLIANCE RATE CALCULATIONS
# ============================================================================

class TestComplianceRateCalculations:
    """Test suite for compliance rate calculations.
    
    Compliance is calculated as:
    Overall = (Response Rate + Resolution Rate) / 2
    
    Where each rate = successes / (successes + failures)
    """

    def test_perfect_compliance(self, perfect_tracker: SLATracker) -> None:
        """Verify perfect compliance rate (100%).
        
        Expected: response_rate=100%, resolution_rate=100%, overall=100%
        """
        response_rate: float = perfect_tracker.get_response_compliance()
        resolution_rate: float = perfect_tracker.get_resolution_compliance()
        overall_rate: float = perfect_tracker.get_compliance_rate()
        
        assert abs(response_rate - 1.0) < 0.001, \
            f"Response rate should be 1.0, got {response_rate}"
        assert abs(resolution_rate - 1.0) < 0.001, \
            f"Resolution rate should be 1.0, got {resolution_rate}"
        assert abs(overall_rate - 1.0) < 0.001, \
            f"Overall rate should be 1.0, got {overall_rate}"

    def test_excellent_compliance(self, excellent_tracker: SLATracker) -> None:
        """Verify excellent compliance rate (95%).
        
        Response: 9/10 = 0.90, Resolution: 10/10 = 1.0
        Overall: (0.90 + 1.0) / 2 = 0.95
        """
        response_rate: float = excellent_tracker.get_response_compliance()
        resolution_rate: float = excellent_tracker.get_resolution_compliance()
        overall_rate: float = excellent_tracker.get_compliance_rate()
        
        assert abs(response_rate - 0.9) < 0.001, \
            f"Response rate should be 0.9, got {response_rate}"
        assert abs(resolution_rate - 1.0) < 0.001, \
            f"Resolution rate should be 1.0, got {resolution_rate}"
        assert abs(overall_rate - 0.95) < 0.001, \
            f"Overall rate should be 0.95, got {overall_rate}"

    def test_good_compliance(self, good_tracker: SLATracker) -> None:
        """Verify good compliance rate (80%).
        
        Response: 8/10 = 0.80, Resolution: 8/10 = 0.80
        Overall: (0.80 + 0.80) / 2 = 0.80
        """
        overall_rate: float = good_tracker.get_compliance_rate()
        
        assert abs(overall_rate - 0.80) < 0.001, \
            f"Overall rate should be 0.80, got {overall_rate}"

    def test_fair_compliance(self, fair_tracker: SLATracker) -> None:
        """Verify fair compliance rate (65%).
        
        Response: 7/10 = 0.70, Resolution: 6/10 = 0.60
        Overall: (0.70 + 0.60) / 2 = 0.65
        """
        overall_rate: float = fair_tracker.get_compliance_rate()
        
        assert abs(overall_rate - 0.65) < 0.001, \
            f"Overall rate should be 0.65, got {overall_rate}"

    def test_poor_compliance(self, poor_tracker: SLATracker) -> None:
        """Verify poor compliance rate (40%).
        
        Response: 3/10 = 0.30, Resolution: 5/10 = 0.50
        Overall: (0.30 + 0.50) / 2 = 0.40
        """
        overall_rate: float = poor_tracker.get_compliance_rate()
        
        assert abs(overall_rate - 0.40) < 0.001, \
            f"Overall rate should be 0.40, got {overall_rate}"

    def test_no_incidents_defaults_to_perfect(self, no_incidents_tracker: SLATracker) -> None:
        """Verify that zero incidents defaults to perfect compliance (1.0).
        
        Edge case: New client with no incidents tracked yet.
        Expected behavior: Default to perfect compliance until incidents exist.
        """
        response_rate: float = no_incidents_tracker.get_response_compliance()
        resolution_rate: float = no_incidents_tracker.get_resolution_compliance()
        overall_rate: float = no_incidents_tracker.get_compliance_rate()
        
        assert abs(response_rate - 1.0) < 0.001, \
            f"Zero incidents should default to 1.0, got {response_rate}"
        assert abs(resolution_rate - 1.0) < 0.001, \
            f"Zero incidents should default to 1.0, got {resolution_rate}"
        assert abs(overall_rate - 1.0) < 0.001, \
            f"Zero incidents should default to 1.0, got {overall_rate}"


# ============================================================================
# TEST: SLA STATUS CATEGORIZATION
# ============================================================================

class TestSLAStatusCategorization:
    """Test suite for SLA status tier categorization.
    
    Tiers:
    - Excellent: >= 90% (0.90)
    - Good: 75-89% (0.75-0.89)
    - Fair: 60-74% (0.60-0.74)
    - Poor: < 60% (< 0.60)
    """

    def test_status_perfect_is_excellent(self, perfect_tracker: SLATracker) -> None:
        """Verify 100% compliance maps to excellent status."""
        status: Literal["excellent", "good", "fair", "poor"] = perfect_tracker.get_sla_status()
        
        assert status == "excellent", f"Perfect compliance should be 'excellent', got '{status}'"

    def test_status_excellent_tier(self, excellent_tracker: SLATracker) -> None:
        """Verify 95% compliance maps to excellent status."""
        status: Literal["excellent", "good", "fair", "poor"] = excellent_tracker.get_sla_status()
        
        assert status == "excellent", f"95% should be 'excellent', got '{status}'"

    def test_status_excellent_boundary_exact(self) -> None:
        """Verify status at exact excellent boundary (90%).
        
        Edge case: Exactly at boundary should be classified as excellent, not good.
        """
        tracker = SLATracker(
            tracker_id="tracker_boundary_90",
            client_id="client_001",
            month=1,
            total_incidents=10,
            response_sla_met=9,
            response_sla_missed=1,
            resolution_sla_met=9,
            resolution_sla_missed=1
        )
        # Compliance: (0.9 + 0.9) / 2 = 0.90
        
        status: Literal["excellent", "good", "fair", "poor"] = tracker.get_sla_status()
        
        assert status == "excellent", f"90% should be 'excellent', got '{status}'"

    def test_status_good_tier(self, good_tracker: SLATracker) -> None:
        """Verify 80% compliance maps to good status."""
        status: Literal["excellent", "good", "fair", "poor"] = good_tracker.get_sla_status()
        
        assert status == "good", f"80% should be 'good', got '{status}'"

    def test_status_good_boundary_upper(self) -> None:
        """Verify status at upper good boundary (89%).
        
        Edge case: Just below excellent boundary.
        """
        tracker = SLATracker(
            tracker_id="tracker_boundary_89",
            client_id="client_001",
            month=1,
            response_sla_met=9,
            response_sla_missed=1,
            resolution_sla_met=8,
            resolution_sla_missed=2
        )
        # Compliance: (0.9 + 0.80) / 2 = 0.85
        
        status: Literal["excellent", "good", "fair", "poor"] = tracker.get_sla_status()
        
        assert status == "good", f"85% should be 'good', got '{status}'"

    def test_status_good_boundary_lower(self) -> None:
        """Verify status at lower good boundary (75%).
        
        Edge case: Exactly at boundary with fair.
        """
        tracker = SLATracker(
            tracker_id="tracker_boundary_75",
            client_id="client_001",
            month=1,
            response_sla_met=8,
            response_sla_missed=2,
            resolution_sla_met=7,
            resolution_sla_missed=3
        )
        # Compliance: (0.8 + 0.7) / 2 = 0.75
        
        status: Literal["excellent", "good", "fair", "poor"] = tracker.get_sla_status()
        
        assert status == "good", f"75% should be 'good', got '{status}'"

    def test_status_fair_tier(self, fair_tracker: SLATracker) -> None:
        """Verify 65% compliance maps to fair status."""
        status: Literal["excellent", "good", "fair", "poor"] = fair_tracker.get_sla_status()
        
        assert status == "fair", f"65% should be 'fair', got '{status}'"

    def test_status_fair_boundary_lower(self) -> None:
        """Verify status at lower fair boundary (60%).
        
        Edge case: Exactly at boundary with poor.
        """
        tracker = SLATracker(
            tracker_id="tracker_boundary_60",
            client_id="client_001",
            month=1,
            response_sla_met=6,
            response_sla_missed=4,
            resolution_sla_met=6,
            resolution_sla_missed=4
        )
        # Compliance: (0.6 + 0.6) / 2 = 0.60
        
        status: Literal["excellent", "good", "fair", "poor"] = tracker.get_sla_status()
        
        assert status == "fair", f"60% should be 'fair', got '{status}'"

    def test_status_poor_tier(self, poor_tracker: SLATracker) -> None:
        """Verify 40% compliance maps to poor status."""
        status: Literal["excellent", "good", "fair", "poor"] = poor_tracker.get_sla_status()
        
        assert status == "poor", f"40% should be 'poor', got '{status}'"

    def test_status_poor_boundary_upper(self) -> None:
        """Verify status just below fair boundary (59%).
        
        Edge case: Just below the 60% fair threshold.
        """
        tracker = SLATracker(
            tracker_id="tracker_boundary_59",
            client_id="client_001",
            month=1,
            response_sla_met=5,
            response_sla_missed=5,
            resolution_sla_met=6,
            resolution_sla_missed=4
        )
        # Compliance: (0.5 + 0.6) / 2 = 0.55
        
        status: Literal["excellent", "good", "fair", "poor"] = tracker.get_sla_status()
        
        assert status == "poor", f"55% should be 'poor', got '{status}'"

    def test_status_critical_poor(self) -> None:
        """Verify critical poor compliance (very low).
        
        Edge case: Extremely poor performance indicating serious issues.
        """
        tracker = SLATracker(
            tracker_id="tracker_critical",
            client_id="client_001",
            month=1,
            total_incidents=20,
            response_sla_met=2,
            response_sla_missed=18,
            resolution_sla_met=3,
            resolution_sla_missed=17
        )
        # Compliance: (0.1 + 0.15) / 2 = 0.125 (12.5%)
        
        status: Literal["excellent", "good", "fair", "poor"] = tracker.get_sla_status()
        
        assert status == "poor", f"12.5% should be 'poor', got '{status}'"


# ============================================================================
# TEST: SATISFACTION IMPACT CALCULATIONS
# ============================================================================

class TestSatisfactionImpactCalculations:
    """Test suite for satisfaction impact from SLA compliance.
    
    Impact multipliers:
    - Excellent (90-100%): +0.02 (customer very satisfied)
    - Good (75-89%): +0.01 (customer satisfied)
    - Fair (60-74%): 0.00 (meets minimum, no bonus or penalty)
    - Poor (<60%): -0.03 (customer very dissatisfied)
    """

    def test_impact_excellent_is_positive(self, excellent_tracker: SLATracker) -> None:
        """Verify excellent status yields +0.02 satisfaction bonus."""
        impact: float = excellent_tracker.get_satisfaction_impact()
        
        assert abs(impact - 0.02) < 0.001, \
            f"Excellent should yield +0.02, got {impact}"

    def test_impact_good_is_small_positive(self, good_tracker: SLATracker) -> None:
        """Verify good status yields +0.01 satisfaction bonus."""
        impact: float = good_tracker.get_satisfaction_impact()
        
        assert abs(impact - 0.01) < 0.001, \
            f"Good should yield +0.01, got {impact}"

    def test_impact_fair_is_neutral(self, fair_tracker: SLATracker) -> None:
        """Verify fair status yields 0.00 (no bonus/penalty)."""
        impact: float = fair_tracker.get_satisfaction_impact()
        
        assert abs(impact - 0.0) < 0.001, \
            f"Fair should yield 0.00, got {impact}"

    def test_impact_poor_is_negative(self, poor_tracker: SLATracker) -> None:
        """Verify poor status yields -0.03 satisfaction penalty."""
        impact: float = poor_tracker.get_satisfaction_impact()
        
        assert abs(impact - (-0.03)) < 0.001, \
            f"Poor should yield -0.03, got {impact}"

    def test_impact_perfect_is_excellent(self, perfect_tracker: SLATracker) -> None:
        """Verify 100% compliance yields excellent bonus."""
        impact: float = perfect_tracker.get_satisfaction_impact()
        
        assert abs(impact - 0.02) < 0.001, \
            f"Perfect should yield +0.02, got {impact}"

    def test_impact_critical_poor_is_penalty(self) -> None:
        """Verify critical poor performance yields maximum penalty."""
        tracker = SLATracker(
            tracker_id="tracker_critical",
            client_id="client_001",
            month=1,
            response_sla_met=1,
            response_sla_missed=9,
            resolution_sla_met=1,
            resolution_sla_missed=9
        )
        # Compliance: (0.1 + 0.1) / 2 = 0.1 (10% - critical)
        
        impact: float = tracker.get_satisfaction_impact()
        
        assert abs(impact - (-0.03)) < 0.001, \
            f"Critical poor should yield -0.03 penalty, got {impact}"


# ============================================================================
# TEST: SERIALIZATION (to_dict / from_dict)
# ============================================================================

class TestSLATrackerSerialization:
    """Test suite for SLA tracker serialization and deserialization.
    
    Ensures data persistence works correctly for save/load operations.
    """

    def test_to_dict_includes_all_fields(self, good_tracker: SLATracker) -> None:
        """Verify to_dict includes all necessary fields for persistence."""
        data: Dict = good_tracker.to_dict()
        
        required_fields: list[str] = [
            "tracker_id",
            "client_id",
            "month",
            "total_incidents",
            "response_sla_met",
            "response_sla_missed",
            "resolution_sla_met",
            "resolution_sla_missed",
            "compliance_rate",
            "sla_status",
            "satisfaction_impact",
        ]
        
        for field in required_fields:
            assert field in data, f"Missing field in to_dict: {field}"

    def test_to_dict_values_correct(self, good_tracker: SLATracker) -> None:
        """Verify to_dict values match tracker state."""
        data: Dict = good_tracker.to_dict()
        
        assert data["tracker_id"] == "tracker_good_001"
        assert data["client_id"] == "client_001"
        assert data["month"] == 1
        assert data["total_incidents"] == 10
        assert abs(data["compliance_rate"] - 0.80) < 0.001
        assert data["sla_status"] == "good"
        assert abs(data["satisfaction_impact"] - 0.01) < 0.001

    def test_from_dict_restores_correctly(self, good_tracker: SLATracker) -> None:
        """Verify from_dict reconstructs tracker from dict."""
        original_data: Dict = good_tracker.to_dict()
        restored_tracker: SLATracker = SLATracker.from_dict(original_data)
        
        assert restored_tracker.tracker_id == good_tracker.tracker_id
        assert restored_tracker.client_id == good_tracker.client_id
        assert restored_tracker.month == good_tracker.month
        assert restored_tracker.total_incidents == good_tracker.total_incidents
        assert restored_tracker.response_sla_met == good_tracker.response_sla_met
        assert restored_tracker.response_sla_missed == good_tracker.response_sla_missed
        assert restored_tracker.resolution_sla_met == good_tracker.resolution_sla_met
        assert restored_tracker.resolution_sla_missed == good_tracker.resolution_sla_missed

    def test_round_trip_serialization(self) -> None:
        """Verify tracker survives round-trip serialization (to_dict -> from_dict)."""
        original = SLATracker(
            tracker_id="test_roundtrip",
            client_id="client_roundtrip",
            month=3,
            total_incidents=15,
            response_sla_met=12,
            response_sla_missed=3,
            resolution_sla_met=13,
            resolution_sla_missed=2
        )
        
        # Serialize and deserialize
        data: Dict = original.to_dict()
        restored: SLATracker = SLATracker.from_dict(data)
        
        # Verify all compliance rates match
        assert abs(original.get_compliance_rate() - restored.get_compliance_rate()) < 0.001
        assert original.get_sla_status() == restored.get_sla_status()
        assert abs(original.get_satisfaction_impact() - restored.get_satisfaction_impact()) < 0.001

    def test_from_dict_with_missing_optional_fields(self) -> None:
        """Verify from_dict handles missing optional fields with defaults.
        
        Edge case: Loading old save data without new fields.
        """
        minimal_data: Dict = {
            "tracker_id": "minimal",
            "client_id": "client_minimal",
            "month": 1
        }
        
        tracker: SLATracker = SLATracker.from_dict(minimal_data)
        
        assert tracker.total_incidents == 0
        assert tracker.response_sla_met == 0
        assert tracker.response_sla_missed == 0
        assert tracker.resolution_sla_met == 0
        assert tracker.resolution_sla_missed == 0
        assert abs(tracker.get_compliance_rate() - 1.0) < 0.001


if __name__ == "__main__":
    """Enable direct test execution for quick validation."""
    pytest.main([__file__, "-v", "--tb=short"])
