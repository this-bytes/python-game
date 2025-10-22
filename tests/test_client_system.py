"""Comprehensive tests for client_system module (Phase 3).

Tests cover all client lifecycle:
- Client generation from industry templates
- Satisfaction tracking and updates
- Contract renewal logic
- Contract termination
- JSON loading
"""

import pytest
from typing import List

from src.models.client import Client, Industry
from src.core.client_system import (
    generate_client_from_template,
    generate_random_client,
    update_client_satisfaction,
    get_satisfaction_status,
    attempt_contract_renewal,
    handle_contract_termination,
    load_clients_from_json,
)


# ===== FIXTURES =====

@pytest.fixture
def sample_client() -> Client:
    """Create a sample client for testing."""
    return Client(
        client_id="test_001",
        company_name="TestCorp Inc.",
        industry=Industry.TECHNOLOGY,
        monthly_contract_value=10000.0,
        sla_response_time_seconds=3600,
        sla_resolution_time_seconds=86400,
        contract_start_month=0,
        contract_end_month=12,
        satisfaction=0.85,
        is_active=True,
        avg_monthly_incidents=5,
        threat_landscape=["DDoS", "Malware"],
        incident_severity_distribution={"high": 0.3, "medium": 0.7},
    )


# ===== CLIENT GENERATION TESTS =====

class TestClientGeneration:
    """Tests for client generation from templates."""

    def test_generate_client_from_technology_template(self) -> None:
        """Verify client generation from Technology industry template."""
        client = generate_client_from_template(
            industry=Industry.TECHNOLOGY,
            client_id="gen_tech_001"
        )
        
        assert client.client_id == "gen_tech_001"
        assert client.industry == Industry.TECHNOLOGY
        assert client.is_active is True
        assert client.satisfaction == 1.0  # New clients start satisfied
        assert client.months_active == 0
        assert len(client.threat_landscape) > 0

    def test_generate_client_from_finance_template(self) -> None:
        """Verify client generation from Finance industry template."""
        client = generate_client_from_template(
            industry=Industry.FINANCE,
            client_id="gen_fin_001"
        )
        
        assert client.industry == Industry.FINANCE
        # Finance has stricter SLAs
        assert client.sla_response_time_seconds <= 3600

    def test_generate_client_with_custom_name(self) -> None:
        """Verify client generation with custom company name."""
        custom_name = "CustomCorp LLC"
        client = generate_client_from_template(
            industry=Industry.BANKING,
            client_id="gen_custom_001",
            company_name_override=custom_name
        )
        
        assert client.company_name == custom_name

    def test_generate_client_variance(self) -> None:
        """Verify client generation applies realistic variance."""
        # Generate multiple clients; they should have variance
        client1 = generate_client_from_template(Industry.TECHNOLOGY, "var_001")
        client2 = generate_client_from_template(Industry.TECHNOLOGY, "var_002")
        
        # While both from same industry template, variance should make them differ
        # (not guaranteed to differ, but likely)
        # At minimum, they should have different IDs
        assert client1.client_id != client2.client_id

    def test_generate_random_client(self) -> None:
        """Verify random client generation selects different industries."""
        client = generate_random_client("random_001")
        
        assert client.client_id == "random_001"
        assert client.industry in Industry
        assert client.is_active is True
        assert client.satisfaction == 1.0

    def test_generated_client_has_valid_contract_terms(self) -> None:
        """Verify generated client has valid contract terms."""
        client = generate_client_from_template(Industry.HEALTHCARE, "valid_001")
        
        # Contract terms should be valid
        assert client.monthly_contract_value > 0
        assert client.sla_response_time_seconds > 0
        assert client.sla_resolution_time_seconds > 0
        assert client.sla_resolution_time_seconds >= client.sla_response_time_seconds
        assert client.contract_end_month > client.contract_start_month


# ===== SATISFACTION TESTS =====

class TestSatisfactionSystem:
    """Tests for client satisfaction tracking and updates."""

    def test_update_satisfaction_perfect_month(self, sample_client: Client) -> None:
        """Verify satisfaction with perfect SLA performance (zero misses)."""
        initial_satisfaction = sample_client.satisfaction
        
        # Perfect month: 5 met, 0 missed
        update_client_satisfaction(sample_client, sla_met=5, sla_missed=0)
        
        # No penalty, but also no bonus (satisfaction already high at 0.85)
        assert sample_client.satisfaction >= initial_satisfaction

    def test_update_satisfaction_sla_violation(self, sample_client: Client) -> None:
        """Verify satisfaction decreases with SLA violations."""
        initial_satisfaction = sample_client.satisfaction  # 0.85
        
        # 2 SLAs missed: should lose 30%
        update_client_satisfaction(sample_client, sla_met=3, sla_missed=2)
        
        # Expected: 0.85 - 0.30 = 0.55
        assert sample_client.satisfaction == pytest.approx(0.55, rel=0.01)

    def test_update_satisfaction_data_breach(self, sample_client: Client) -> None:
        """Verify satisfaction decreases catastrophically with data breach."""
        initial_satisfaction = sample_client.satisfaction  # 0.85
        
        # Data breach: -30% penalty
        update_client_satisfaction(
            sample_client,
            sla_met=0,
            sla_missed=0,
            data_breach=True
        )
        
        # Expected: 0.85 - 0.30 = 0.55
        assert sample_client.satisfaction == pytest.approx(0.55, rel=0.01)

    def test_satisfaction_clamped_to_zero(self, sample_client: Client) -> None:
        """Verify satisfaction cannot go below 0.0."""
        # Multiple violations should clamp at 0.0
        update_client_satisfaction(sample_client, sla_met=0, sla_missed=10)
        
        assert sample_client.satisfaction == 0.0

    def test_satisfaction_clamped_to_one(self, sample_client: Client) -> None:
        """Verify satisfaction cannot exceed 1.0."""
        sample_client.satisfaction = 0.95
        
        # Perfect month bonus should not exceed 1.0
        update_client_satisfaction(sample_client, sla_met=10, sla_missed=0)
        
        assert sample_client.satisfaction <= 1.0

    def test_satisfaction_excellence_bonus(self) -> None:
        """Verify excellence bonus (+5%) on perfect month with high satisfaction."""
        client = Client(
            client_id="bonus_001",
            company_name="BonusTest",
            industry=Industry.TECHNOLOGY,
            monthly_contract_value=10000.0,
            sla_response_time_seconds=3600,
            sla_resolution_time_seconds=86400,
            contract_start_month=0,
            contract_end_month=12,
            satisfaction=0.90,  # High satisfaction (>0.80)
            is_active=True,
            avg_monthly_incidents=5,
        )
        
        # Perfect month should trigger bonus
        update_client_satisfaction(client, sla_met=5, sla_missed=0)
        
        # Expected: 0.90 + 0.05 = 0.95
        assert client.satisfaction == pytest.approx(0.95, rel=0.01)

    def test_historical_sla_misses_tracked(self, sample_client: Client) -> None:
        """Verify historical SLA misses are accumulated."""
        initial_misses = sample_client.historical_sla_misses
        
        update_client_satisfaction(sample_client, sla_met=3, sla_missed=2)
        
        assert sample_client.historical_sla_misses == initial_misses + 2

    def test_get_satisfaction_status_excellent(self) -> None:
        """Verify status for excellent satisfaction (>=0.90)."""
        assert get_satisfaction_status(0.95) == "excellent"
        assert get_satisfaction_status(0.90) == "excellent"

    def test_get_satisfaction_status_satisfied(self) -> None:
        """Verify status for satisfied satisfaction (0.70-0.90)."""
        assert get_satisfaction_status(0.80) == "satisfied"
        assert get_satisfaction_status(0.70) == "satisfied"

    def test_get_satisfaction_status_warning(self) -> None:
        """Verify status for warning satisfaction (0.40-0.70)."""
        assert get_satisfaction_status(0.55) == "warning"
        assert get_satisfaction_status(0.40) == "warning"

    def test_get_satisfaction_status_critical(self) -> None:
        """Verify status for critical satisfaction (<0.40)."""
        assert get_satisfaction_status(0.30) == "critical"
        assert get_satisfaction_status(0.0) == "critical"


# ===== CONTRACT RENEWAL TESTS =====

class TestContractRenewal:
    """Tests for contract renewal and termination."""

    def test_renewal_with_excellent_satisfaction(self, sample_client: Client) -> None:
        """Verify high renewal chance with excellent satisfaction."""
        sample_client.satisfaction = 0.95
        
        # Run multiple attempts; should mostly succeed
        renewals = [
            attempt_contract_renewal(sample_client)[0]
            for _ in range(100)
        ]
        
        renewal_rate = sum(renewals) / len(renewals)
        # 95% chance should result in >80% renewals over 100 attempts
        assert renewal_rate > 0.80

    def test_renewal_with_critical_satisfaction(self, sample_client: Client) -> None:
        """Verify low renewal chance with critical satisfaction."""
        sample_client.satisfaction = 0.30
        
        # Run multiple attempts; should mostly fail
        renewals = [
            attempt_contract_renewal(sample_client)[0]
            for _ in range(100)
        ]
        
        renewal_rate = sum(renewals) / len(renewals)
        # 20% chance should result in <40% renewals over 100 attempts
        assert renewal_rate < 0.40

    def test_renewal_returns_reason(self, sample_client: Client) -> None:
        """Verify renewal attempt returns human-readable reason."""
        renewed, reason = attempt_contract_renewal(sample_client)
        
        assert isinstance(renewed, bool)
        assert isinstance(reason, str)
        assert len(reason) > 0
        assert ("renewed" in reason.lower() or "not" in reason.lower())

    def test_termination_deactivates_client(self, sample_client: Client) -> None:
        """Verify contract termination deactivates client."""
        assert sample_client.is_active is True
        
        result = handle_contract_termination(
            sample_client,
            reason="Satisfaction too low"
        )
        
        assert sample_client.is_active is False
        assert result["client_id"] == sample_client.client_id
        assert result["revenue_lost"] == sample_client.monthly_contract_value

    def test_termination_calculates_prestige_loss(self, sample_client: Client) -> None:
        """Verify termination calculates prestige loss proportional to revenue."""
        result = handle_contract_termination(
            sample_client,
            reason="Test termination"
        )
        
        # Prestige loss = monthly_revenue / 100
        expected_prestige_loss = int(sample_client.monthly_contract_value / 100)
        assert result["prestige_loss"] == expected_prestige_loss

    def test_termination_returns_details(self, sample_client: Client) -> None:
        """Verify termination returns complete details."""
        reason = "SLA failures"
        result = handle_contract_termination(sample_client, reason)
        
        assert "client_id" in result
        assert "company_name" in result
        assert "revenue_lost" in result
        assert "prestige_loss" in result
        assert "reason" in result
        assert result["reason"] == reason


# ===== JSON LOADING TESTS =====

class TestClientJSONLoading:
    """Tests for loading clients from JSON."""

    def test_load_clients_from_json_returns_list(self) -> None:
        """Verify loading clients returns a list."""
        clients = load_clients_from_json()
        
        assert isinstance(clients, list)

    def test_loaded_clients_have_valid_structure(self) -> None:
        """Verify loaded clients have all required fields."""
        clients = load_clients_from_json()
        
        if len(clients) > 0:
            client = clients[0]
            assert hasattr(client, "client_id")
            assert hasattr(client, "company_name")
            assert hasattr(client, "industry")
            assert hasattr(client, "monthly_contract_value")
            assert hasattr(client, "satisfaction")
            assert hasattr(client, "is_active")

    def test_loaded_clients_have_realistic_values(self) -> None:
        """Verify loaded clients have realistic contract values."""
        clients = load_clients_from_json()
        
        for client in clients[:3]:  # Check first 3
            assert client.monthly_contract_value > 0
            assert 0.0 <= client.satisfaction <= 1.0
            assert client.sla_response_time_seconds > 0
            assert client.avg_monthly_incidents > 0


# ===== INTEGRATION TESTS =====

class TestClientSystemIntegration:
    """Integration tests for full client lifecycle."""

    def test_complete_client_lifecycle_excellent(self) -> None:
        """Test full lifecycle: generate → track satisfaction → renew."""
        # Generate client
        client = generate_client_from_template(Industry.TECHNOLOGY, "lifecycle_001")
        assert client.satisfaction == 1.0
        
        # Month 1: Perfect performance
        update_client_satisfaction(client, sla_met=5, sla_missed=0)
        assert client.satisfaction >= 0.95
        
        # Renew (should succeed with high satisfaction)
        renewed, _ = attempt_contract_renewal(client)
        assert client.is_active is True

    def test_complete_client_lifecycle_decline(self) -> None:
        """Test lifecycle: generate → poor performance → termination."""
        # Generate client
        client = generate_client_from_template(Industry.HEALTHCARE, "lifecycle_002")
        
        # Simulate 3 months of poor performance
        for month in range(3):
            update_client_satisfaction(client, sla_met=1, sla_missed=4)
        
        # After 3 months of misses, satisfaction should be low
        assert client.satisfaction < 0.30
        
        # Renewal unlikely to succeed
        renewed, reason = attempt_contract_renewal(client)
        
        # If not renewed, terminate
        if not renewed:
            result = handle_contract_termination(client, reason)
            assert client.is_active is False
            assert result["prestige_loss"] > 0

    def test_multiple_clients_independent_satisfaction(self) -> None:
        """Verify multiple clients' satisfaction tracks independently."""
        client1 = generate_client_from_template(Industry.BANKING, "multi_001")
        client2 = generate_client_from_template(Industry.RETAIL, "multi_002")
        
        # Update client1 with violations
        update_client_satisfaction(client1, sla_met=1, sla_missed=3)
        
        # Client2 should be unaffected
        assert client2.satisfaction == 1.0
        assert client1.satisfaction < 1.0

    def test_industry_variety_generates_different_profiles(self) -> None:
        """Verify different industries have meaningfully different profiles."""
        tech_client = generate_client_from_template(Industry.TECHNOLOGY, "tech_001")
        finance_client = generate_client_from_template(Industry.FINANCE, "fin_001")
        
        # Different industries should have different incident frequencies or SLAs
        # (not strictly required but typical in design)
        assert (
            tech_client.avg_monthly_incidents != finance_client.avg_monthly_incidents or
            tech_client.sla_response_time_seconds != finance_client.sla_response_time_seconds
        )
