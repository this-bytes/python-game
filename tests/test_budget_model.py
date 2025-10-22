"""Tests for the Budget model."""

import pytest
from src.models.budget import Budget


class TestBudget:
    """Test suite for Budget dataclass."""
    
    def test_create_budget(self):
        """Verify Budget can be created with all required fields."""
        budget = Budget(
            total_reserves=10000.0,
            monthly_revenue=5000.0,
            monthly_expenses=3000.0,
            specialist_salary_per_month=3000.0,
            infrastructure_cost_per_client=500.0,
            fixed_overhead=1500.0,
        )
        
        # Verify basic fields
        assert budget.total_reserves == 10000.0
        assert budget.monthly_revenue == 5000.0
        assert budget.monthly_expenses == 3000.0
        assert budget.specialist_salary_per_month == 3000.0
        assert budget.infrastructure_cost_per_client == 500.0
        assert budget.fixed_overhead == 1500.0
    
    def test_get_monthly_profit(self):
        """Verify monthly profit calculation."""
        budget = Budget(
            total_reserves=10000.0,
            monthly_revenue=5000.0,
            monthly_expenses=3000.0,
        )
        
        profit = budget.get_monthly_profit()
        
        assert profit == 2000.0, f"Expected 2000.0, got {profit}"
    
    def test_get_monthly_profit_negative(self):
        """Verify monthly loss calculation."""
        budget = Budget(
            total_reserves=10000.0,
            monthly_revenue=2000.0,
            monthly_expenses=5000.0,
        )
        
        profit = budget.get_monthly_profit()
        
        assert profit == -3000.0, f"Expected -3000.0, got {profit}"
    
    def test_get_months_runway_profitable(self):
        """Verify runway is infinite when profitable."""
        budget = Budget(
            total_reserves=10000.0,
            monthly_revenue=5000.0,
            monthly_expenses=3000.0,
        )
        
        runway = budget.get_months_runway()
        
        assert runway == float('inf'), "Expected infinite runway when profitable"
    
    def test_get_months_runway_losing_money(self):
        """Verify runway calculation when losing money."""
        budget = Budget(
            total_reserves=10000.0,
            monthly_revenue=1000.0,
            monthly_expenses=3000.0,
        )
        
        runway = budget.get_months_runway()
        
        # monthly_loss = 3000 - 1000 = 2000
        # runway = 10000 / 2000 = 5 months
        assert runway == 5.0, f"Expected 5.0 months, got {runway}"
    
    def test_get_months_runway_critical(self):
        """Verify runway is low when near bankruptcy."""
        budget = Budget(
            total_reserves=1500.0,
            monthly_revenue=100.0,
            monthly_expenses=1000.0,
        )
        
        runway = budget.get_months_runway()
        
        # monthly_loss = 900
        # runway = 1500 / 900 ≈ 1.67 months
        assert 1.5 < runway < 2.0, f"Expected ~1.67 months, got {runway}"
    
    def test_is_bankrupt_no(self):
        """Verify company is not bankrupt with positive reserves."""
        budget = Budget(total_reserves=5000.0)
        
        assert budget.is_bankrupt() is False
    
    def test_is_bankrupt_yes(self):
        """Verify company is bankrupt with negative reserves."""
        budget = Budget(total_reserves=-1000.0)
        
        assert budget.is_bankrupt() is True
    
    def test_is_bankrupt_zero(self):
        """Verify company is not bankrupt at exactly zero reserves."""
        budget = Budget(total_reserves=0.0)
        
        assert budget.is_bankrupt() is False
    
    def test_is_in_critical_condition_yes(self):
        """Verify critical condition detected when < 1 month runway."""
        budget = Budget(
            total_reserves=1500.0,
            monthly_revenue=100.0,
            monthly_expenses=2000.0,
        )
        
        assert budget.is_in_critical_condition() is True
    
    def test_is_in_critical_condition_no(self):
        """Verify not in critical condition when profitable."""
        budget = Budget(
            total_reserves=10000.0,
            monthly_revenue=5000.0,
            monthly_expenses=3000.0,
        )
        
        assert budget.is_in_critical_condition() is False
    
    def test_is_in_critical_condition_no_bankruptcy(self):
        """Verify critical condition is False if already bankrupt."""
        budget = Budget(
            total_reserves=-1000.0,
            monthly_revenue=100.0,
            monthly_expenses=2000.0,
        )
        
        assert budget.is_in_critical_condition() is False
    
    def test_budget_to_dict(self):
        """Verify Budget.to_dict() serializes correctly."""
        budget = Budget(
            total_reserves=10000.0,
            monthly_revenue=5000.0,
            monthly_expenses=3000.0,
            revenue_history=[5000.0],
            expense_history=[3000.0],
        )
        
        budget_dict = budget.to_dict()
        
        # Verify serialization
        assert budget_dict["total_reserves"] == 10000.0
        assert budget_dict["monthly_revenue"] == 5000.0
        assert budget_dict["monthly_expenses"] == 3000.0
        assert budget_dict["revenue_history"] == [5000.0]
        assert isinstance(budget_dict, dict)
    
    def test_budget_from_dict(self):
        """Verify Budget.from_dict() deserializes correctly."""
        data = {
            "total_reserves": 10000.0,
            "monthly_revenue": 5000.0,
            "monthly_expenses": 3000.0,
            "revenue_history": [5000.0],
            "expense_history": [3000.0],
            "specialist_salary_per_month": 3000.0,
            "infrastructure_cost_per_client": 500.0,
            "fixed_overhead": 1500.0,
        }
        
        budget = Budget.from_dict(data)
        
        assert budget.total_reserves == 10000.0
        assert budget.monthly_revenue == 5000.0
        assert budget.monthly_expenses == 3000.0
        assert budget.revenue_history == [5000.0]
        assert budget.specialist_salary_per_month == 3000.0
