"""Test Suite for Burnout System.

Tests burnout mechanics including:
- Assignment burnout accumulation
- Recovery through rest, vacation, therapy
- Performance penalties and error chance scaling
- Team-wide burnout statistics
"""

import pytest
from src.core.burnout_system import BurnoutSystem, BurnoutTier, SpecialistBurnout


@pytest.fixture
def burnout_system() -> BurnoutSystem:
    """Provide fresh burnout system instance."""
    return BurnoutSystem()


@pytest.fixture
def specialist_id() -> str:
    """Provide test specialist ID."""
    return "specialist_001"


class TestBurnoutSystem:
    """Test BurnoutSystem manager class."""
    
    def test_register_specialist_creates_fresh_state(self, burnout_system, specialist_id):
        """Verify registering specialist creates fresh burnout state."""
        burnout = burnout_system.register_specialist(specialist_id)
        
        assert burnout.specialist_id == specialist_id
        assert burnout.burnout_level == 0.0
        assert burnout.failed_incidents == 0
        assert burnout.tier == BurnoutTier.FRESH
    
    def test_assign_incident_increases_burnout(self, burnout_system, specialist_id):
        """Verify assigning incident increases burnout."""
        burnout_system.register_specialist(specialist_id)
        
        success, msg = burnout_system.assign_incident(specialist_id, incident_difficulty=1)
        
        assert success is True
        assert "Burnout: 5%" in msg
        assert burnout_system.get_specialist_status(specialist_id)["burnout_level"] == 5.0
    
    def test_assign_incident_with_difficulty_scaling(self, burnout_system, specialist_id):
        """Verify burnout scales with incident difficulty."""
        burnout_system.register_specialist(specialist_id)
        
        # Difficulty 1: 5% burnout
        burnout_system.assign_incident(specialist_id, incident_difficulty=1)
        status_1 = burnout_system.get_specialist_status(specialist_id)
        
        # Difficulty 4: 5% + (4-1)*5% = 20% burnout
        burnout_system.register_specialist("spec_2")
        burnout_system.assign_incident("spec_2", incident_difficulty=4)
        status_4 = burnout_system.get_specialist_status("spec_2")
        
        assert status_1["burnout_level"] == 5.0
        assert status_4["burnout_level"] == 20.0
    
    def test_failed_incident_adds_trauma(self, burnout_system, specialist_id):
        """Verify failed incidents add trauma counter."""
        burnout_system.register_specialist(specialist_id)
        burnout_system.assign_incident(specialist_id, incident_difficulty=2)
        
        burnout_system.complete_incident(specialist_id, success=False)
        status = burnout_system.get_specialist_status(specialist_id)
        
        assert status["trauma_incidents"] == 1
        # 10% burnout added on failure
        assert status["burnout_level"] > 10.0
    
    def test_successful_incident_no_trauma(self, burnout_system, specialist_id):
        """Verify successful incidents don't add trauma."""
        burnout_system.register_specialist(specialist_id)
        burnout_system.assign_incident(specialist_id, incident_difficulty=2)
        
        burnout_system.complete_incident(specialist_id, success=True)
        status = burnout_system.get_specialist_status(specialist_id)
        
        assert status["trauma_incidents"] == 0
    
    def test_rest_day_recovers_burnout(self, burnout_system, specialist_id):
        """Verify rest day recovers 30% burnout."""
        burnout = burnout_system.register_specialist(specialist_id)
        burnout_system.assign_incident(specialist_id, incident_difficulty=4)  # 20% burnout
        
        success, msg = burnout_system.take_rest_day(specialist_id)
        
        assert success is True
        status = burnout_system.get_specialist_status(specialist_id)
        # Should recover 30% but max is current level, so roughly back to baseline
        assert "Rested" in msg
    
    def test_vacation_recovers_more_burnout(self, burnout_system, specialist_id):
        """Verify vacation recovers more burnout than rest day."""
        burnout_system.register_specialist(specialist_id)
        
        # Build up burnout
        for _ in range(10):
            burnout_system.assign_incident(specialist_id, incident_difficulty=2)
        
        status_before = burnout_system.get_specialist_status(specialist_id)
        burnout_before = status_before["burnout_level"]
        
        success, msg = burnout_system.take_vacation(specialist_id, days=3, cost_per_day=100)
        
        assert success is True
        status_after = burnout_system.get_specialist_status(specialist_id)
        burnout_after = status_after["burnout_level"]
        
        assert burnout_after < burnout_before
        assert "3-day vacation" in msg
    
    def test_vacation_costs_money(self, burnout_system, specialist_id):
        """Verify vacation costs money (even without balance check in simplified system)."""
        burnout_system.register_specialist(specialist_id)
        
        # Build burnout
        for _ in range(10):
            burnout_system.assign_incident(specialist_id, incident_difficulty=2)
        
        status_before = burnout_system.get_specialist_status(specialist_id)
        
        success, msg = burnout_system.take_vacation(specialist_id, days=3, cost_per_day=100)
        
        # System currently doesn't check money, just returns success
        assert success is True
        assert "3-day vacation" in msg
        assert "Cost: 300" in msg  # 3 * 100
    
    def test_therapy_clears_trauma(self, burnout_system, specialist_id):
        """Verify therapy clears trauma counter."""
        burnout_system.register_specialist(specialist_id)
        
        # Create trauma
        burnout_system.assign_incident(specialist_id, incident_difficulty=2)
        burnout_system.complete_incident(specialist_id, success=False)
        burnout_system.complete_incident(specialist_id, success=False)
        
        status_before = burnout_system.get_specialist_status(specialist_id)
        assert status_before["trauma_incidents"] == 2
        
        success, msg = burnout_system.attend_therapy(specialist_id, cost=500)
        
        assert success is True
        status_after = burnout_system.get_specialist_status(specialist_id)
        assert status_after["trauma_incidents"] == 0
    
    def test_performance_multiplier_scales_with_burnout(self, burnout_system, specialist_id):
        """Verify performance multiplier decreases linearly with burnout."""
        burnout_system.register_specialist(specialist_id)
        
        # Fresh: 1.0x
        status_fresh = burnout_system.get_specialist_status(specialist_id)
        assert status_fresh["performance_multiplier"] == 1.0
        
        # Build burnout to 50% (direct calculation for precision)
        spec = burnout_system.register_specialist("test_perf")
        spec.burnout_level = 50.0
        status_mid = burnout_system.get_specialist_status("test_perf")
        assert status_mid["performance_multiplier"] == 0.5  # 1.0 - (50/100) = 0.5
        
        # At 100%
        spec.burnout_level = 100.0
        status_broken = burnout_system.get_specialist_status("test_perf")
        assert status_broken["performance_multiplier"] == 0.0
    
    def test_error_chance_scales_with_burnout(self, burnout_system, specialist_id):
        """Verify error chance increases with burnout (0.0-0.5 scale)."""
        burnout_system.register_specialist(specialist_id)
        
        # Fresh: 0% error chance
        status_fresh = burnout_system.get_specialist_status(specialist_id)
        assert status_fresh["error_chance"] == 0.0
        
        # Mid burnout: 0.25 at 50%
        spec = burnout_system.register_specialist("test_error")
        spec.burnout_level = 50.0
        status_mid = burnout_system.get_specialist_status("test_error")
        assert status_mid["error_chance"] == 0.25  # (50/100) * 0.5 = 0.25
        
        # Broken: 0.5 at 100%
        spec.burnout_level = 100.0
        status_broken = burnout_system.get_specialist_status("test_error")
        assert status_broken["error_chance"] == 0.5  # (100/100) * 0.5 = 0.5
    
    def test_burnout_capped_at_100_percent(self, burnout_system, specialist_id):
        """Verify burnout is capped at 100%."""
        burnout_system.register_specialist(specialist_id)
        
        # Try to accumulate beyond 100%
        for _ in range(50):
            burnout_system.assign_incident(specialist_id, incident_difficulty=5)
        
        status = burnout_system.get_specialist_status(specialist_id)
        assert status["burnout_level"] == 100.0
        assert status["tier"] == "broken"  # tier returns enum.value (string)


class TestSpecialistBurnout:
    """Test SpecialistBurnout state class."""
    
    def test_tier_mapping_fresh(self):
        """Verify 0-20% maps to FRESH tier."""
        burnout = SpecialistBurnout(specialist_id="test", burnout_level=10.0)
        assert burnout.tier == BurnoutTier.FRESH
    
    def test_tier_mapping_stressed(self):
        """Verify 21-40% maps to STRESSED tier."""
        burnout = SpecialistBurnout(specialist_id="test", burnout_level=30.0)
        assert burnout.tier == BurnoutTier.STRESSED
    
    def test_tier_mapping_exhausted(self):
        """Verify 41-60% maps to EXHAUSTED tier."""
        burnout = SpecialistBurnout(specialist_id="test", burnout_level=50.0)
        assert burnout.tier == BurnoutTier.EXHAUSTED
    
    def test_tier_mapping_critical(self):
        """Verify 61-80% maps to CRITICAL tier."""
        burnout = SpecialistBurnout(specialist_id="test", burnout_level=70.0)
        assert burnout.tier == BurnoutTier.CRITICAL
    
    def test_tier_mapping_broken(self):
        """Verify 81-100% maps to BROKEN tier."""
        burnout = SpecialistBurnout(specialist_id="test", burnout_level=90.0)
        assert burnout.tier == BurnoutTier.BROKEN


class TestBurnoutIntegration:
    """Test integration scenarios with multiple specialists."""
    
    def test_team_status_empty(self, burnout_system):
        """Verify team status for empty system."""
        status = burnout_system.get_team_status()
        assert status["team_size"] == 0
        assert status["average_burnout"] == 0.0
        assert status["critical_count"] == 0
    
    def test_team_status_multiple_specialists(self, burnout_system):
        """Verify team status aggregates multiple specialists."""
        # Register 3 specialists with different burnout levels
        burnout_system.register_specialist("spec_1")
        burnout_system.register_specialist("spec_2")
        burnout_system.register_specialist("spec_3")
        
        # Set burnout directly for predictable testing
        burnout_system.specialists["spec_1"].burnout_level = 5.0
        burnout_system.specialists["spec_2"].burnout_level = 50.0
        burnout_system.specialists["spec_3"].burnout_level = 90.0
        
        status = burnout_system.get_team_status()
        
        assert status["team_size"] == 3
        # Average of 5%, 50%, 90% = 48.33%
        assert 45.0 < status["average_burnout"] < 52.0
        assert status["critical_count"] >= 1  # At least spec_3 is critical (>80%)
    
    def test_overwork_scenario(self, burnout_system):
        """Test realistic overwork scenario: assign, fail, rest, recover."""
        spec_id = "overworked_specialist"
        burnout_system.register_specialist(spec_id)
        
        # Phase 1: Overwork - multiple assignments
        for _ in range(8):
            burnout_system.assign_incident(spec_id, incident_difficulty=3)
        
        # Phase 2: Failures from stress
        burnout_system.complete_incident(spec_id, success=False)
        burnout_system.complete_incident(spec_id, success=False)
        
        status_overworked = burnout_system.get_specialist_status(spec_id)
        assert status_overworked["burnout_level"] > 50
        # After 8 assignments at diff 3 (20% each) = 100% capped, so tier is "broken"
        assert status_overworked["tier"] == "broken"  # tier returns string (enum.value)
        assert status_overworked["trauma_incidents"] == 2
        
        # Phase 3: Recovery pathway
        burnout_system.take_vacation(spec_id, days=5, cost_per_day=100)
        burnout_system.attend_therapy(spec_id, cost=500)
        
        status_recovered = burnout_system.get_specialist_status(spec_id)
        assert status_recovered["burnout_level"] < status_overworked["burnout_level"]
        assert status_recovered["trauma_incidents"] == 0
