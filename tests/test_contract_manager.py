"""Tests for Contract model and ContractManager."""

import pytest
import time
from src.models.contract import Contract
from src.models.client import Client
from src.models.incident import Incident
from src.core.contract_manager import ContractManager
from src.models.game_state import GameState


@pytest.fixture
def sample_contract():
    """Create a sample contract for testing."""
    return Contract(
        id="contract_001",
        client_id="client_001",
        contract_type="retainer",
        base_rate=1000.0,
        sla_terms={"max_response_time": 300},
        duration_days=30,
        penalties={"sla_failure": 0.5},
        bonuses={"perfect_month": 1.5},
        start_time=time.time(),
        end_time=0,  # Will be calculated
        status="ACTIVE",
    )


@pytest.fixture
def sample_client():
    """Create a sample client for testing."""
    return Client(
        id="client_001",
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
        id="inc_001",
        incident_type="DDoS Attack",
        specialty_required="Network Security",
        difficulty=3,
        sla_seconds=300,
        base_reward=500,
        xp_reward=100,
        client_id="client_001",
    )


@pytest.fixture
def contract_manager():
    """Create a ContractManager instance."""
    manager = ContractManager()
    # Load sample templates
    templates = [
        {
            "id": "retainer_basic",
            "name": "Basic Retainer",
            "contract_type": "retainer",
            "base_rate": 1000,
            "sla_terms": {"max_response_time": 300},
            "duration_days": 30,
            "penalties": {"sla_failure": 0.5},
            "bonuses": {"perfect_month": 1.5},
        },
        {
            "id": "per_incident_standard",
            "name": "Standard Per-Incident",
            "contract_type": "per_incident",
            "base_rate": 500,
            "sla_terms": {"max_response_time": 240},
            "duration_days": 45,
            "penalties": {"sla_failure": 0.4},
            "bonuses": {"fast_resolution": 1.2},
        },
    ]
    manager.load_templates(templates)
    return manager


class TestContract:
    """Test suite for Contract model."""

    def test_initialization(self, sample_contract):
        """Test contract initialization."""
        assert sample_contract.id == "contract_001"
        assert sample_contract.client_id == "client_001"
        assert sample_contract.contract_type == "retainer"
        assert sample_contract.base_rate == 1000.0
        assert sample_contract.status == "ACTIVE"
        assert sample_contract.end_time > 0  # Should be calculated

    def test_end_time_calculation(self, sample_contract):
        """Test that end_time is calculated from duration."""
        expected_end = sample_contract.start_time + (30 * 86400)
        assert abs(sample_contract.end_time - expected_end) < 1

    def test_is_active(self, sample_contract):
        """Test active status check."""
        assert sample_contract.is_active() is True

        # Test terminated contract
        sample_contract.status = "TERMINATED"
        assert sample_contract.is_active() is False

    def test_is_expired(self, sample_contract):
        """Test expiration check."""
        assert sample_contract.is_expired() is False

        # Make contract expired
        sample_contract.end_time = time.time() - 100
        assert sample_contract.is_expired() is True

    def test_get_time_remaining(self, sample_contract):
        """Test time remaining calculation."""
        time_remaining = sample_contract.get_time_remaining()
        expected = 30 * 86400  # 30 days in seconds
        assert abs(time_remaining - expected) < 2  # Allow 2 second variance

    def test_get_days_remaining(self, sample_contract):
        """Test days remaining calculation."""
        days = sample_contract.get_days_remaining()
        assert days == 29 or days == 30  # Could be 29 due to rounding

        # Test expired contract
        sample_contract.end_time = time.time() - 100
        assert sample_contract.get_days_remaining() == 0

    def test_update_sla_compliance(self, sample_contract):
        """Test SLA compliance rate updates."""
        assert sample_contract.sla_compliance_rate == 100.0

        # First incident - SLA met
        sample_contract.update_sla_compliance(True)
        assert sample_contract.sla_compliance_rate == 100.0
        assert sample_contract.incidents_handled == 1

        # Second incident - SLA failed
        sample_contract.update_sla_compliance(False)
        assert sample_contract.sla_compliance_rate == 50.0
        assert sample_contract.incidents_handled == 2

        # Third incident - SLA met
        sample_contract.update_sla_compliance(True)
        assert abs(sample_contract.sla_compliance_rate - 66.67) < 0.1
        assert sample_contract.incidents_handled == 3

    def test_calculate_penalty(self, sample_contract):
        """Test penalty calculation."""
        penalty = sample_contract.calculate_penalty(1000.0)
        assert penalty == 500.0  # 50% penalty

    def test_calculate_bonus(self, sample_contract):
        """Test bonus calculation."""
        bonus = sample_contract.calculate_bonus(1000.0, "perfect_month")
        assert bonus == 1500.0  # 150% bonus

    def test_terminate(self, sample_contract):
        """Test contract termination."""
        sample_contract.terminate("client_termination")
        assert sample_contract.status == "TERMINATED"

    def test_expire(self, sample_contract):
        """Test contract expiration."""
        sample_contract.expire()
        assert sample_contract.status == "EXPIRED"

    def test_renew(self, sample_contract):
        """Test contract renewal."""
        old_start = sample_contract.start_time
        sample_contract.renew(60, {"base_rate": 1500.0})

        assert sample_contract.duration_days == 60
        assert sample_contract.base_rate == 1500.0
        assert sample_contract.status == "ACTIVE"
        assert sample_contract.start_time > old_start
        assert sample_contract.incidents_handled == 0
        assert sample_contract.sla_compliance_rate == 100.0

    def test_to_dict(self, sample_contract):
        """Test contract serialization."""
        data = sample_contract.to_dict()
        assert data["id"] == "contract_001"
        assert data["client_id"] == "client_001"
        assert data["contract_type"] == "retainer"
        assert data["status"] == "ACTIVE"

    def test_from_dict(self):
        """Test contract deserialization."""
        data = {
            "id": "contract_002",
            "client_id": "client_002",
            "contract_type": "per_incident",
            "base_rate": 500.0,
            "sla_terms": {"max_response_time": 240},
            "duration_days": 45,
            "penalties": {"sla_failure": 0.4},
            "bonuses": {"fast_resolution": 1.2},
            "start_time": time.time(),
            "end_time": time.time() + 3888000,
            "status": "ACTIVE",
        }
        contract = Contract.from_dict(data)
        assert contract.id == "contract_002"
        assert contract.contract_type == "per_incident"


class TestContractManager:
    """Test suite for ContractManager."""

    def test_load_templates(self, contract_manager):
        """Test template loading."""
        assert "retainer_basic" in contract_manager.contract_templates
        assert "per_incident_standard" in contract_manager.contract_templates

    def test_negotiate_contract_success(self, contract_manager, sample_client):
        """Test successful contract negotiation."""
        # Create a minimal game state
        game_state = GameState(
            specialists=[],
            incidents=[],
            clients=[sample_client],
            automation_scripts=[],
        )

        contract = contract_manager.negotiate_contract(
            sample_client,
            "retainer_basic",
            {"base_rate": 1200, "duration_days": 30},
            game_state,
        )

        assert contract is not None
        assert contract.client_id == sample_client.id
        assert contract.base_rate == 1200
        assert contract.status == "ACTIVE"
        assert contract.id in sample_client.contracts

    def test_negotiate_contract_low_reputation(
        self, contract_manager, sample_client
    ):
        """Test contract negotiation fails with low reputation."""
        sample_client.reputation = 20
        game_state = GameState(
            specialists=[],
            incidents=[],
            clients=[sample_client],
            automation_scripts=[],
        )

        contract = contract_manager.negotiate_contract(
            sample_client, "retainer_basic", {}, game_state
        )

        assert contract is None

    def test_negotiate_contract_invalid_template(
        self, contract_manager, sample_client
    ):
        """Test negotiation with invalid template."""
        game_state = GameState(
            specialists=[],
            incidents=[],
            clients=[sample_client],
            automation_scripts=[],
        )

        contract = contract_manager.negotiate_contract(
            sample_client, "nonexistent_template", {}, game_state
        )

        assert contract is None

    def test_renew_contract(self, contract_manager, sample_contract, sample_client):
        """Test contract renewal with improved terms."""
        game_state = GameState(
            specialists=[],
            incidents=[],
            clients=[sample_client],
            automation_scripts=[],
        )

        old_rate = sample_contract.base_rate
        sample_client.reputation = 85  # High reputation

        renewed = contract_manager.renew_contract(sample_contract, game_state)

        assert renewed.base_rate > old_rate
        assert renewed.status == "ACTIVE"

    def test_terminate_contract_by_client(
        self, contract_manager, sample_contract
    ):
        """Test contract termination by client (no penalty)."""
        game_state = GameState(
            specialists=[],
            incidents=[],
            clients=[],
            automation_scripts=[],
        )

        penalty = contract_manager.terminate_contract(
            sample_contract, "client_termination", game_state
        )

        assert penalty == 0.0
        assert sample_contract.status == "TERMINATED"

    def test_terminate_contract_by_firm(self, contract_manager, sample_contract):
        """Test contract termination by firm (with penalty)."""
        game_state = GameState(
            specialists=[],
            incidents=[],
            clients=[],
            automation_scripts=[],
        )

        penalty = contract_manager.terminate_contract(
            sample_contract, "firm_termination", game_state
        )

        assert penalty > 0
        assert sample_contract.status == "TERMINATED"

    def test_apply_penalties(
        self, contract_manager, sample_contract, sample_incident
    ):
        """Test penalty application."""
        penalty = contract_manager.apply_penalties(
            sample_contract, sample_incident
        )

        expected = sample_incident.base_reward * 0.5
        assert penalty == expected

    def test_apply_bonuses(
        self, contract_manager, sample_contract, sample_incident
    ):
        """Test bonus application."""
        bonus = contract_manager.apply_bonuses(
            sample_contract, sample_incident, "perfect_month"
        )

        expected = sample_incident.base_reward * 1.5
        assert bonus == expected

    def test_calculate_retainer_income(self, contract_manager, sample_contract):
        """Test passive retainer income calculation."""
        contracts = [sample_contract]
        delta_time = 3600  # 1 hour

        income = contract_manager.calculate_retainer_income(contracts, delta_time)

        # Should be a fraction of daily rate
        daily_rate = sample_contract.base_rate / sample_contract.duration_days
        expected_income = (daily_rate / 86400) * 3600
        assert abs(income - expected_income) < 0.01

    def test_calculate_retainer_income_inactive(
        self, contract_manager, sample_contract
    ):
        """Test no income from inactive contracts."""
        sample_contract.status = "EXPIRED"
        contracts = [sample_contract]

        income = contract_manager.calculate_retainer_income(contracts, 3600)
        assert income == 0.0

    def test_check_expirations(self, contract_manager, sample_contract):
        """Test expiration checking."""
        # Make contract expired
        sample_contract.end_time = time.time() - 100
        contracts = [sample_contract]

        expired = contract_manager.check_expirations(contracts)

        assert len(expired) == 1
        assert sample_contract.status == "EXPIRED"

    def test_get_contract_summary(self, contract_manager, sample_contract):
        """Test contract summary generation."""
        summary = contract_manager.get_contract_summary(sample_contract)

        assert summary["id"] == sample_contract.id
        assert summary["client_id"] == sample_contract.client_id
        assert summary["contract_type"] == "retainer"
        assert summary["is_active"] is True
        assert "days_remaining" in summary

    def test_get_active_contracts_count(self, contract_manager, sample_contract):
        """Test active contract counting."""
        contract2 = Contract(
            id="contract_002",
            client_id="client_002",
            contract_type="per_incident",
            base_rate=500.0,
            sla_terms={},
            duration_days=30,
            penalties={},
            bonuses={},
            start_time=time.time(),
            end_time=0,
            status="EXPIRED",
        )

        contracts = [sample_contract, contract2]
        count = contract_manager.get_active_contracts_count(contracts)

        assert count == 1

    def test_get_total_retainer_value(self, contract_manager, sample_contract):
        """Test total retainer value calculation."""
        contract2 = Contract(
            id="contract_002",
            client_id="client_002",
            contract_type="retainer",
            base_rate=2000.0,
            sla_terms={},
            duration_days=30,
            penalties={},
            bonuses={},
            start_time=time.time(),
            end_time=0,
            status="ACTIVE",
        )

        contracts = [sample_contract, contract2]
        total = contract_manager.get_total_retainer_value(contracts)

        assert total == 3000.0
