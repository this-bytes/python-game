"""Tests for the SLATracker model."""

import pytest
from src.models.sla_tracker import SLATracker


class TestSLATracker:
    """Test suite for SLATracker dataclass."""
    
    def test_create_sla_tracker(self):
        """Verify SLATracker can be created with all required fields."""
        tracker = SLATracker(
            tracker_id="sla_001",
            client_id="client_001",
            month=1,
            total_incidents=10,
            response_sla_met=9,
            response_sla_missed=1,
            resolution_sla_met=8,
            resolution_sla_missed=2,
        )
        
        # Verify basic fields
        assert tracker.tracker_id == "sla_001"
        assert tracker.client_id == "client_001"
        assert tracker.month == 1
        assert tracker.total_incidents == 10
        assert tracker.response_sla_met == 9
        assert tracker.response_sla_missed == 1
        assert tracker.resolution_sla_met == 8
        assert tracker.resolution_sla_missed == 2
    
    def test_get_response_compliance(self):
        """Verify response compliance calculation."""
        tracker = SLATracker(
            tracker_id="sla_001",
            client_id="client_001",
            month=1,
            response_sla_met=8,
            response_sla_missed=2,
        )
        
        compliance = tracker.get_response_compliance()
        
        assert compliance == 0.8, f"Expected 0.8, got {compliance}"
    
    def test_get_response_compliance_perfect(self):
        """Verify response compliance is 1.0 when all met."""
        tracker = SLATracker(
            tracker_id="sla_001",
            client_id="client_001",
            month=1,
            response_sla_met=10,
            response_sla_missed=0,
        )
        
        compliance = tracker.get_response_compliance()
        
        assert compliance == 1.0
    
    def test_get_response_compliance_zero_incidents(self):
        """Verify response compliance defaults to 1.0 with no incidents."""
        tracker = SLATracker(
            tracker_id="sla_001",
            client_id="client_001",
            month=1,
            response_sla_met=0,
            response_sla_missed=0,
        )
        
        compliance = tracker.get_response_compliance()
        
        assert compliance == 1.0
    
    def test_get_resolution_compliance(self):
        """Verify resolution compliance calculation."""
        tracker = SLATracker(
            tracker_id="sla_001",
            client_id="client_001",
            month=1,
            resolution_sla_met=7,
            resolution_sla_missed=3,
        )
        
        compliance = tracker.get_resolution_compliance()
        
        assert compliance == 0.7, f"Expected 0.7, got {compliance}"
    
    def test_get_overall_compliance(self):
        """Verify overall compliance averages response and resolution."""
        tracker = SLATracker(
            tracker_id="sla_001",
            client_id="client_001",
            month=1,
            response_sla_met=8,
            response_sla_missed=2,
            resolution_sla_met=6,
            resolution_sla_missed=4,
        )
        
        overall = tracker.get_overall_compliance()
        
        response_comp = 0.8
        resolution_comp = 0.6
        expected = (response_comp + resolution_comp) / 2.0
        
        assert overall == expected, f"Expected {expected}, got {overall}"
    
    def test_sla_tracker_to_dict(self):
        """Verify SLATracker.to_dict() serializes correctly."""
        tracker = SLATracker(
            tracker_id="sla_002",
            client_id="client_002",
            month=2,
            total_incidents=15,
            response_sla_met=12,
            response_sla_missed=3,
            resolution_sla_met=10,
            resolution_sla_missed=5,
        )
        
        tracker_dict = tracker.to_dict()
        
        # Verify serialization
        assert tracker_dict["tracker_id"] == "sla_002"
        assert tracker_dict["client_id"] == "client_002"
        assert tracker_dict["month"] == 2
        assert tracker_dict["total_incidents"] == 15
        assert tracker_dict["response_sla_met"] == 12
        assert isinstance(tracker_dict, dict)
    
    def test_sla_tracker_from_dict(self):
        """Verify SLATracker.from_dict() deserializes correctly."""
        data = {
            "tracker_id": "sla_003",
            "client_id": "client_003",
            "month": 3,
            "total_incidents": 20,
            "response_sla_met": 18,
            "response_sla_missed": 2,
            "resolution_sla_met": 15,
            "resolution_sla_missed": 5,
        }
        
        tracker = SLATracker.from_dict(data)
        
        assert tracker.tracker_id == "sla_003"
        assert tracker.client_id == "client_003"
        assert tracker.month == 3
        assert tracker.response_sla_met == 18
        assert tracker.resolution_sla_met == 15
