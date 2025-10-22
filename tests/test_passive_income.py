"""Tests for passive income system (Task 20)."""

from unittest.mock import Mock
import time

import pytest

from src.core.passive_income_system import PassiveIncomeSystem
from src.models.client import Client, Industry


def create_test_client(client_id: str, company_name: str, is_active: bool = True, 
                       contract_value: float = 10000.0, satisfaction: float = 0.85,
                       industry: Industry = Industry.TECHNOLOGY) -> Client:
    """Helper to create a test client with standard fields."""
    return Client(
        client_id=client_id,
        company_name=company_name,
        industry=industry,
        monthly_contract_value=contract_value,
        sla_response_time_seconds=3600,
        sla_resolution_time_seconds=86400,
        contract_start_month=0,
        contract_end_month=12,
        satisfaction=satisfaction,
        is_active=is_active,
        avg_monthly_incidents=5
    )


class TestPassiveIncomeSystem:
    """Test passive income system features."""

    def test_initialization(self):
        """Test passive income system initialization."""
        config = {
            "passive_income": {
                "retainer_income_multiplier": 1.5,
                "investment_types": {
                    "low_risk": {"return_rate": 0.03, "risk": 0.0}
                }
            }
        }
        
        system = PassiveIncomeSystem(config)
        assert system._retainer_multiplier == 1.5
        assert "low_risk" in system._investment_types

    def test_retainer_income_calculation(self):
        """Test retainer income from active clients."""
        config = {}
        system = PassiveIncomeSystem(config)
        
        clients = [
            create_test_client("client1", "Test Client 1", contract_value=10000.0),
            create_test_client("client2", "Test Client 2", contract_value=15000.0, industry=Industry.FINANCE),
        ]
        
        # Calculate for 1 hour (3600 seconds)
        delta_time = 3600.0
        income = system.calculate_retainer_income(clients, delta_time)
        
        # Expected: (10000 + 15000) * 0.001 * 1 hour = 25
        assert income > 0
        assert income == pytest.approx(25.0, rel=0.01)

    def test_retainer_income_inactive_clients(self):
        """Test that inactive clients don't generate retainer income."""
        config = {}
        system = PassiveIncomeSystem(config)
        
        clients = [
            create_test_client("client1", "Inactive Client", is_active=False),
        ]
        
        delta_time = 3600.0
        income = system.calculate_retainer_income(clients, delta_time)
        
        assert income == 0.0

    def test_investment_returns_low_risk(self):
        """Test low-risk investment returns."""
        config = {}
        system = PassiveIncomeSystem(config)
        
        investments = {
            "low_risk": 10000.0
        }
        
        # Calculate for 1 year (simplified)
        seconds_per_year = 365 * 24 * 3600
        delta_time = seconds_per_year
        
        returns = system.calculate_investment_returns(investments, delta_time)
        
        # Expected: 10000 * 0.02 = 200
        assert returns > 0
        assert returns == pytest.approx(200.0, rel=0.01)

    def test_investment_returns_empty(self):
        """Test investment returns with no investments."""
        config = {}
        system = PassiveIncomeSystem(config)
        
        investments = {}
        returns = system.calculate_investment_returns(investments, 3600.0)
        
        assert returns == 0.0

    def test_reputation_bonus_calculation(self):
        """Test reputation bonus multiplier calculation."""
        config = {}
        system = PassiveIncomeSystem(config)
        
        # High reputation clients
        clients = [
            Client(
                id="client1",
                name="High Rep Client",
                industry="Technology",
                incident_rate_per_minute=0.5,
                sla_multiplier=1.0,
                reputation=100,
                contract_value=10000,
                active=True
            )
        ]
        
        multiplier = system.calculate_reputation_bonus(clients)
        
        # Expected: 1.0 + (100/100 * 0.5) = 1.5
        assert multiplier == pytest.approx(1.5, rel=0.01)
        
        # Low reputation clients
        clients[0].reputation = 0
        multiplier = system.calculate_reputation_bonus(clients)
        
        # Expected: 1.0 + (0/100 * 0.5) = 1.0
        assert multiplier == pytest.approx(1.0, rel=0.01)
        
        # Medium reputation
        clients[0].reputation = 50
        multiplier = system.calculate_reputation_bonus(clients)
        
        # Expected: 1.0 + (50/100 * 0.5) = 1.25
        assert multiplier == pytest.approx(1.25, rel=0.01)

    def test_reputation_bonus_no_clients(self):
        """Test reputation bonus with no clients."""
        config = {}
        system = PassiveIncomeSystem(config)
        
        multiplier = system.calculate_reputation_bonus([])
        assert multiplier == 1.0

    def test_apply_passive_income(self):
        """Test full passive income application to game state."""
        config = {}
        system = PassiveIncomeSystem(config)
        
        # Mock game state
        game_state = Mock()
        game_state.current_money = 1000.0
        game_state.total_money_earned = 0.0
        game_state.investments = {"low_risk": 10000.0}
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
        
        delta_time = 3600.0  # 1 hour
        result = system.apply_passive_income(game_state, delta_time)
        
        assert "retainer_income" in result
        assert "investment_return" in result
        assert "reputation_multiplier" in result
        assert "total_income" in result
        
        # Money should have increased
        assert game_state.current_money > 1000.0
        assert game_state.total_money_earned > 0

    def test_invest_success(self):
        """Test making a successful investment."""
        config = {}
        system = PassiveIncomeSystem(config)
        
        game_state = Mock()
        game_state.current_money = 5000.0
        game_state.investments = {}
        
        result = system.invest(game_state, "low_risk", 1000.0)
        
        assert result["success"] is True
        assert result["investment_type"] == "low_risk"
        assert result["amount"] == 1000.0
        assert game_state.current_money == 4000.0
        assert game_state.investments["low_risk"] == 1000.0

    def test_invest_insufficient_funds(self):
        """Test investment with insufficient funds."""
        config = {}
        system = PassiveIncomeSystem(config)
        
        game_state = Mock()
        game_state.current_money = 500.0
        game_state.investments = {}
        
        result = system.invest(game_state, "low_risk", 1000.0)
        
        assert result["success"] is False
        assert "Insufficient funds" in result["error"]
        assert game_state.current_money == 500.0

    def test_invest_invalid_type(self):
        """Test investment with invalid type."""
        config = {}
        system = PassiveIncomeSystem(config)
        
        game_state = Mock()
        game_state.current_money = 5000.0
        game_state.investments = {}
        
        result = system.invest(game_state, "invalid_type", 1000.0)
        
        assert result["success"] is False
        assert "Invalid investment type" in result["error"]

    def test_invest_negative_amount(self):
        """Test investment with negative amount."""
        config = {}
        system = PassiveIncomeSystem(config)
        
        game_state = Mock()
        game_state.current_money = 5000.0
        game_state.investments = {}
        
        result = system.invest(game_state, "low_risk", -100.0)
        
        assert result["success"] is False
        assert "must be positive" in result["error"]

    def test_withdraw_success(self):
        """Test successful withdrawal from investment."""
        config = {}
        system = PassiveIncomeSystem(config)
        
        game_state = Mock()
        game_state.current_money = 1000.0
        game_state.investments = {"low_risk": 5000.0}
        
        result = system.withdraw(game_state, "low_risk", 2000.0)
        
        assert result["success"] is True
        assert result["amount"] == 2000.0
        assert game_state.current_money == 3000.0
        assert game_state.investments["low_risk"] == 3000.0

    def test_withdraw_insufficient_balance(self):
        """Test withdrawal with insufficient investment balance."""
        config = {}
        system = PassiveIncomeSystem(config)
        
        game_state = Mock()
        game_state.current_money = 1000.0
        game_state.investments = {"low_risk": 500.0}
        
        result = system.withdraw(game_state, "low_risk", 1000.0)
        
        assert result["success"] is False
        assert "Insufficient investment balance" in result["error"]

    def test_withdraw_no_investments(self):
        """Test withdrawal with no investments."""
        config = {}
        system = PassiveIncomeSystem(config)
        
        # Create a mock without investments attribute
        game_state = type('GameState', (), {})()
        game_state.current_money = 1000.0
        
        result = system.withdraw(game_state, "low_risk", 1000.0)
        
        assert result["success"] is False
        assert "No investments found" in result["error"]

    def test_statistics_tracking(self):
        """Test that statistics are tracked correctly."""
        config = {}
        system = PassiveIncomeSystem(config)
        
        game_state = Mock()
        game_state.current_money = 1000.0
        game_state.total_money_earned = 0.0
        game_state.investments = {}
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
        
        # Generate some income
        system.apply_passive_income(game_state, 3600.0)
        
        stats = system.get_statistics()
        assert "total_retainer_income" in stats
        assert "total_investment_income" in stats
        assert "total_investment_losses" in stats
        assert "total_reputation_bonus" in stats
        
        # Stats should have values
        assert stats["total_retainer_income"] > 0

    def test_reset_statistics(self):
        """Test statistics reset."""
        config = {}
        system = PassiveIncomeSystem(config)
        
        # Generate some stats
        system._stats["total_retainer_income"] = 100.0
        system._stats["total_investment_income"] = 50.0
        
        system.reset_statistics()
        
        stats = system.get_statistics()
        assert stats["total_retainer_income"] == 0.0
        assert stats["total_investment_income"] == 0.0

    def test_multiple_investment_types(self):
        """Test handling multiple investment types."""
        config = {}
        system = PassiveIncomeSystem(config)
        
        game_state = Mock()
        game_state.current_money = 10000.0
        game_state.investments = {}
        
        # Invest in multiple types
        system.invest(game_state, "low_risk", 3000.0)
        system.invest(game_state, "medium_risk", 2000.0)
        system.invest(game_state, "high_risk", 1000.0)
        
        assert len(game_state.investments) == 3
        assert game_state.investments["low_risk"] == 3000.0
        assert game_state.investments["medium_risk"] == 2000.0
        assert game_state.investments["high_risk"] == 1000.0
        assert game_state.current_money == 4000.0
