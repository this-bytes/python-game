"""Tests for ClientManager class."""

import pytest
from src.models.client import Client
from src.models.incident import Incident
from src.core.client_manager import ClientManager


@pytest.fixture
def client_manager():
    """Create a ClientManager instance for testing."""
    return ClientManager()


@pytest.fixture
def sample_client():
    """Create a sample client for testing."""
    return Client(
        id="client_test_001",
        name="Test Corp",
        industry="Technology",
        incident_rate_per_minute=0.5,
        sla_multiplier=1.0,
        reputation=80,
        contract_value=10000,
        active=True,
    )


@pytest.fixture
def sample_incident():
    """Create a sample incident for testing."""
    return Incident(
        id="inc_test_001",
        incident_type="DDoS Attack",
        specialty_required="Network Security",
        difficulty=3,
        sla_seconds=300,
        base_reward=500,
        xp_reward=100,
        client_id="client_test_001",
        status="resolved",
    )


class TestClientManager:
    """Test suite for ClientManager."""

    def test_update_reputation_success_sla_met(
        self, client_manager, sample_client, sample_incident
    ):
        """Test reputation update for successful resolution with SLA met."""
        initial_reputation = sample_client.reputation
        new_reputation = client_manager.update_reputation(
            sample_client, sample_incident, success=True, sla_met=True
        )

        assert new_reputation == initial_reputation + 2
        assert sample_client.reputation == new_reputation
        assert len(sample_client.satisfaction_history) == 1
        assert sample_client.satisfaction_history[0] == 100.0
        assert sample_client.total_incidents_resolved == 1
        assert sample_client.total_sla_failures == 0

    def test_update_reputation_success_sla_missed(
        self, client_manager, sample_client, sample_incident
    ):
        """Test reputation update for successful resolution with SLA missed."""
        initial_reputation = sample_client.reputation
        new_reputation = client_manager.update_reputation(
            sample_client, sample_incident, success=True, sla_met=False
        )

        assert new_reputation == initial_reputation - 1
        assert sample_client.reputation == new_reputation
        assert len(sample_client.satisfaction_history) == 1
        assert sample_client.satisfaction_history[0] == 60.0
        assert sample_client.total_incidents_resolved == 1
        assert sample_client.total_sla_failures == 1

    def test_update_reputation_failure(
        self, client_manager, sample_client, sample_incident
    ):
        """Test reputation update for failed resolution."""
        initial_reputation = sample_client.reputation
        new_reputation = client_manager.update_reputation(
            sample_client, sample_incident, success=False, sla_met=False
        )

        assert new_reputation == initial_reputation - 5
        assert sample_client.reputation == new_reputation
        assert len(sample_client.satisfaction_history) == 1
        assert sample_client.satisfaction_history[0] == 0.0
        assert sample_client.total_incidents_resolved == 0
        assert sample_client.total_sla_failures == 1

    def test_update_reputation_clamping(
        self, client_manager, sample_client, sample_incident
    ):
        """Test that reputation is clamped to 0-100 range."""
        # Test upper bound
        sample_client.reputation = 99
        new_reputation = client_manager.update_reputation(
            sample_client, sample_incident, success=True, sla_met=True
        )
        assert new_reputation == 100  # Clamped at 100

        # Test lower bound
        sample_client.reputation = 3
        new_reputation = client_manager.update_reputation(
            sample_client, sample_incident, success=False, sla_met=False
        )
        assert new_reputation == 0  # Clamped at 0

    def test_satisfaction_history_limit(
        self, client_manager, sample_client, sample_incident
    ):
        """Test that satisfaction history is limited to 10 entries."""
        # Add 15 incidents
        for i in range(15):
            client_manager.update_reputation(
                sample_client, sample_incident, success=True, sla_met=True
            )

        # Should only keep last 10
        assert len(sample_client.satisfaction_history) == 10
        # All should be 100.0 (successful with SLA)
        assert all(s == 100.0 for s in sample_client.satisfaction_history)

    def test_calculate_satisfaction_no_history(self, client_manager, sample_client):
        """Test satisfaction calculation with no history."""
        sample_client.satisfaction_history = []
        satisfaction = client_manager.calculate_satisfaction(sample_client)
        assert satisfaction == 100.0  # Default to perfect

    def test_calculate_satisfaction_with_history(self, client_manager, sample_client):
        """Test satisfaction calculation with history."""
        sample_client.satisfaction_history = [100.0, 60.0, 100.0, 0.0, 100.0]
        satisfaction = client_manager.calculate_satisfaction(sample_client)
        assert satisfaction == 72.0  # Average of the values

    def test_determine_tier(self, client_manager, sample_client):
        """Test tier determination based on reputation."""
        # Tier 5: 80-100
        sample_client.reputation = 85
        assert client_manager.determine_tier(sample_client) == 5

        # Tier 4: 60-80
        sample_client.reputation = 70
        assert client_manager.determine_tier(sample_client) == 4

        # Tier 3: 40-60
        sample_client.reputation = 50
        assert client_manager.determine_tier(sample_client) == 3

        # Tier 2: 20-40
        sample_client.reputation = 30
        assert client_manager.determine_tier(sample_client) == 2

        # Tier 1: 0-20
        sample_client.reputation = 10
        assert client_manager.determine_tier(sample_client) == 1

    def test_determine_tier_boundaries(self, client_manager, sample_client):
        """Test tier determination at exact boundaries."""
        assert client_manager.determine_tier(sample_client) == 5  # 80
        sample_client.reputation = 79
        assert client_manager.determine_tier(sample_client) == 4

        sample_client.reputation = 60
        assert client_manager.determine_tier(sample_client) == 4
        sample_client.reputation = 59
        assert client_manager.determine_tier(sample_client) == 3

        sample_client.reputation = 40
        assert client_manager.determine_tier(sample_client) == 3
        sample_client.reputation = 39
        assert client_manager.determine_tier(sample_client) == 2

        sample_client.reputation = 20
        assert client_manager.determine_tier(sample_client) == 2
        sample_client.reputation = 19
        assert client_manager.determine_tier(sample_client) == 1

    def test_apply_reputation_effects_high(self, client_manager, sample_client):
        """Test reputation effects for high reputation client."""
        sample_client.reputation = 85
        effects = client_manager.apply_reputation_effects(sample_client)

        assert effects["reward_multiplier"] == 1.2
        assert effects["difficulty_modifier"] == -0.1

    def test_apply_reputation_effects_medium(self, client_manager, sample_client):
        """Test reputation effects for medium reputation client."""
        sample_client.reputation = 50
        effects = client_manager.apply_reputation_effects(sample_client)

        assert effects["reward_multiplier"] == 1.0
        assert effects["difficulty_modifier"] == 0.0

    def test_apply_reputation_effects_low(self, client_manager, sample_client):
        """Test reputation effects for low reputation client."""
        sample_client.reputation = 30
        effects = client_manager.apply_reputation_effects(sample_client)

        assert effects["reward_multiplier"] == 0.8
        assert effects["difficulty_modifier"] == 0.1

    def test_check_contract_renewal_safe(self, client_manager, sample_client):
        """Test contract renewal for client with good reputation."""
        sample_client.reputation = 50
        will_renew = client_manager.check_contract_renewal(sample_client, None)
        assert will_renew is True

    def test_check_contract_renewal_at_risk(self, client_manager, sample_client):
        """Test contract renewal for client with poor reputation."""
        sample_client.reputation = 25
        will_renew = client_manager.check_contract_renewal(sample_client, None)
        assert will_renew is False

    def test_check_contract_renewal_boundary(self, client_manager, sample_client):
        """Test contract renewal at reputation boundary."""
        sample_client.reputation = 30
        will_renew = client_manager.check_contract_renewal(sample_client, None)
        assert will_renew is True

        sample_client.reputation = 29
        will_renew = client_manager.check_contract_renewal(sample_client, None)
        assert will_renew is False

    def test_get_reputation_tier_name(self, client_manager):
        """Test getting tier names."""
        assert client_manager.get_reputation_tier_name(5) == "Excellent"
        assert client_manager.get_reputation_tier_name(4) == "Good"
        assert client_manager.get_reputation_tier_name(3) == "Fair"
        assert client_manager.get_reputation_tier_name(2) == "Poor"
        assert client_manager.get_reputation_tier_name(1) == "At Risk"
        assert client_manager.get_reputation_tier_name(99) == "Unknown"

    def test_get_client_summary(
        self, client_manager, sample_client, sample_incident
    ):
        """Test getting comprehensive client summary."""
        # Add some history
        sample_client.total_incidents_assigned = 10
        sample_client.total_incidents_resolved = 8
        sample_client.total_sla_failures = 2
        sample_client.satisfaction_history = [100.0, 60.0, 100.0, 100.0, 60.0]
        sample_client.reputation = 80
        sample_client.tier = client_manager.determine_tier(sample_client)  # Calculate tier

        summary = client_manager.get_client_summary(sample_client)

        assert summary["client_id"] == sample_client.id
        assert summary["name"] == sample_client.name
        assert summary["reputation"] == 80
        assert summary["tier"] == 5
        assert summary["tier_name"] == "Excellent"
        assert summary["satisfaction"] == 84.0  # Average of satisfaction_history
        assert summary["total_incidents_assigned"] == 10
        assert summary["total_incidents_resolved"] == 8
        assert summary["total_sla_failures"] == 2
        assert summary["success_rate"] == 80.0
        assert summary["sla_compliance_rate"] == 80.0
        assert summary["reward_multiplier"] == 1.2
        assert summary["difficulty_modifier"] == -0.1
        assert summary["will_renew_contract"] is True
        assert summary["at_risk"] is False

    def test_get_client_summary_no_incidents(self, client_manager, sample_client):
        """Test client summary with no incident history."""
        sample_client.total_incidents_assigned = 0
        summary = client_manager.get_client_summary(sample_client)

        assert summary["success_rate"] == 0.0
        assert summary["sla_compliance_rate"] == 100.0  # Perfect when no data

    def test_tier_updates_with_reputation(
        self, client_manager, sample_client, sample_incident
    ):
        """Test that tier updates automatically when reputation changes."""
        sample_client.reputation = 85
        sample_client.tier = 5

        # Drop reputation significantly
        for i in range(10):
            client_manager.update_reputation(
                sample_client, sample_incident, success=False, sla_met=False
            )

        # Tier should have dropped
        assert sample_client.tier < 5
        assert sample_client.reputation < 40
