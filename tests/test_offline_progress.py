"""Tests for offline progress system (Task 21)."""

from unittest.mock import Mock
import time

import pytest

from src.core.offline_progress import OfflineProgressSystem
from src.models.client import Client
from src.models.specialist import Specialist, SpecialistStats


class TestOfflineProgressSystem:
    """Test offline progress system features."""

    def test_initialization(self):
        """Test offline progress system initialization."""
        config = {
            "game_settings": {
                "offline_progress_cap_hours": 48
            }
        }
        
        system = OfflineProgressSystem(config)
        assert system._max_offline_hours == 48

    def test_calculate_offline_progress_with_cap(self):
        """Test that offline progress is capped at max hours."""
        config = {
            "game_settings": {
                "offline_progress_cap_hours": 24
            }
        }
        system = OfflineProgressSystem(config)
        
        game_state = Mock()
        game_state.specialists = []
        game_state.clients = []
        game_state.investments = {}
        game_state.current_money = 1000.0
        game_state.total_money_earned = 0.0
        game_state._passive_income_system = None
        
        # 48 hours elapsed, should be capped at 24
        time_elapsed = 48 * 3600
        
        result = system.calculate_offline_progress(game_state, time_elapsed)
        
        assert result["time_elapsed"] == time_elapsed
        assert result["time_simulated"] == 24 * 3600
        assert result["was_capped"] is True

    def test_calculate_offline_progress_no_cap(self):
        """Test offline progress without hitting cap."""
        config = {}
        system = OfflineProgressSystem(config)
        
        game_state = Mock()
        game_state.specialists = []
        game_state.clients = []
        game_state.investments = {}
        game_state.current_money = 1000.0
        game_state.total_money_earned = 0.0
        game_state._passive_income_system = None
        
        # 12 hours elapsed, under 24 hour cap
        time_elapsed = 12 * 3600
        
        result = system.calculate_offline_progress(game_state, time_elapsed)
        
        assert result["time_elapsed"] == time_elapsed
        assert result["time_simulated"] == time_elapsed
        assert result["was_capped"] is False

    def test_simulate_offline_incidents(self):
        """Test simulation of incidents during offline period."""
        config = {}
        system = OfflineProgressSystem(config)
        
        game_state = Mock()
        game_state.clients = [
            Client(
                id="client1",
                name="Test Client",
                industry="Technology",
                incident_rate_per_minute=0.5,  # 0.5 incidents/minute
                sla_multiplier=1.0,
                reputation=80,
                contract_value=10000,
                active=True
            )
        ]
        
        # 1 hour offline
        time_elapsed = 3600.0
        
        incidents = system.simulate_offline_incidents(game_state, time_elapsed)
        
        # With 0.5 incidents/min * 0.5 multiplier = 0.25/min
        # 0.25 * 60 min = 15 incidents expected (approximately)
        assert len(incidents) > 0
        assert len(incidents) < 30  # Some variability

    def test_simulate_offline_incidents_inactive_client(self):
        """Test that inactive clients don't generate incidents."""
        config = {}
        system = OfflineProgressSystem(config)
        
        game_state = Mock()
        game_state.clients = [
            Client(
                id="client1",
                name="Inactive Client",
                industry="Technology",
                incident_rate_per_minute=0.5,
                sla_multiplier=1.0,
                reputation=80,
                contract_value=10000,
                active=False  # Inactive
            )
        ]
        
        time_elapsed = 3600.0
        incidents = system.simulate_offline_incidents(game_state, time_elapsed)
        
        assert len(incidents) == 0

    def test_simulate_offline_automation_no_specialists(self):
        """Test automation simulation with no automated specialists."""
        config = {}
        system = OfflineProgressSystem(config)
        
        game_state = Mock()
        game_state.specialists = []
        game_state.clients = [
            Client(
                id="client1",
                name="Test Client",
                industry="Technology",
                incident_rate_per_minute=0.5,
                sla_multiplier=1.0,
                reputation=80,
                contract_value=10000,
                active=True
            )
        ]
        
        time_elapsed = 3600.0
        
        result = system.simulate_offline_automation(game_state, time_elapsed)
        
        # Without automation, all incidents fail
        assert result["incidents_handled"] == 0
        assert result["incidents_failed"] > 0
        assert result["automation_success_rate"] == 0.0

    def test_simulate_offline_automation_with_specialists(self):
        """Test automation simulation with automated specialists."""
        config = {}
        system = OfflineProgressSystem(config)
        
        specialist = Specialist(
            id="spec1",
            name="Test Specialist",
            specialty="Network Security",
            level=5,
            xp=1000,
            stats=SpecialistStats(speed=85, accuracy=90, experience_bonus=1.2),
            status="available",
            automation_scripts=["auto_assign_network_low"]
        )
        
        game_state = Mock()
        game_state.specialists = [specialist]
        game_state.clients = [
            Client(
                id="client1",
                name="Test Client",
                industry="Technology",
                incident_rate_per_minute=0.1,  # Lower rate for predictable test
                sla_multiplier=1.0,
                reputation=80,
                contract_value=10000,
                active=True
            )
        ]
        
        time_elapsed = 3600.0
        
        result = system.simulate_offline_automation(game_state, time_elapsed)
        
        # With automation, some incidents should be handled
        total_incidents = result["incidents_handled"] + result["incidents_failed"]
        assert total_incidents > 0
        assert result["incidents_handled"] > 0  # Some should succeed
        assert result["automation_success_rate"] > 0.0

    def test_calculate_automation_success_rate(self):
        """Test automation success rate calculation."""
        config = {}
        system = OfflineProgressSystem(config)
        
        # High accuracy specialist
        specialist1 = Mock()
        specialist1.stats = Mock()
        specialist1.stats.accuracy = 90
        
        rate = system._calculate_automation_success_rate([specialist1])
        assert rate == pytest.approx(0.9, rel=0.01)
        
        # Multiple specialists get bonus
        specialist2 = Mock()
        specialist2.stats = Mock()
        specialist2.stats.accuracy = 85
        
        rate = system._calculate_automation_success_rate([specialist1, specialist2])
        # Average accuracy = 87.5, plus 10% bonus = 0.975, capped at 0.95
        assert rate == pytest.approx(0.95, rel=0.01)

    def test_calculate_offline_income(self):
        """Test offline income calculation."""
        config = {}
        system = OfflineProgressSystem(config)
        
        game_state = Mock()
        game_state.clients = [
            Client(
                id="client1",
                name="Test Client",
                industry="Technology",
                incident_rate_per_minute=0.5,
                sla_multiplier=1.0,
                reputation=80,
                contract_value=10000,
                active=True
            )
        ]
        game_state._passive_income_system = None
        
        # 1 hour
        time_elapsed = 3600.0
        
        result = system.calculate_offline_income(game_state, time_elapsed)
        
        assert "retainer_income" in result
        assert "total_income" in result
        assert result["total_income"] > 0

    def test_statistics_tracking(self):
        """Test statistics tracking."""
        config = {}
        system = OfflineProgressSystem(config)
        
        game_state = Mock()
        game_state.specialists = []
        game_state.clients = []
        game_state.investments = {}
        game_state.current_money = 1000.0
        game_state.total_money_earned = 0.0
        game_state._passive_income_system = None
        
        time_elapsed = 3600.0
        system.calculate_offline_progress(game_state, time_elapsed)
        
        stats = system.get_statistics()
        assert stats["last_offline_duration"] == time_elapsed
        assert stats["total_offline_time"] == time_elapsed
        assert stats["total_offline_sessions"] == 1

    def test_reset_statistics(self):
        """Test statistics reset."""
        config = {}
        system = OfflineProgressSystem(config)
        
        # Set some stats
        system._stats["total_offline_time"] = 10000.0
        system._stats["total_offline_sessions"] = 5
        
        system.reset_statistics()
        
        stats = system.get_statistics()
        assert stats["total_offline_time"] == 0.0
        assert stats["total_offline_sessions"] == 0

    def test_select_random_specialty(self):
        """Test random specialty selection."""
        config = {}
        system = OfflineProgressSystem(config)
        
        specialty = system._select_random_specialty()
        
        assert specialty in [
            "Network Security",
            "Malware Analysis",
            "Digital Forensics",
            "Application Security",
            "Cloud Security",
            "Incident Response"
        ]

    def test_select_random_difficulty(self):
        """Test random difficulty selection."""
        config = {}
        system = OfflineProgressSystem(config)
        
        difficulty = system._select_random_difficulty()
        
        assert 1 <= difficulty <= 5

    def test_offline_progress_report_structure(self):
        """Test that offline progress report has expected structure."""
        config = {}
        system = OfflineProgressSystem(config)
        
        game_state = Mock()
        game_state.specialists = []
        game_state.clients = []
        game_state.investments = {}
        game_state.current_money = 1000.0
        game_state.total_money_earned = 0.0
        game_state._passive_income_system = None
        
        result = system.calculate_offline_progress(game_state, 3600.0)
        
        # Check report structure
        assert "time_elapsed" in result
        assert "time_simulated" in result
        assert "was_capped" in result
        assert "incidents" in result
        assert "automation" in result
        assert "income" in result
        assert "summary" in result
        
        # Check summary structure
        summary = result["summary"]
        assert "total_income" in summary
        assert "total_xp" in summary
        assert "incidents_handled" in summary
        assert "incidents_failed" in summary
