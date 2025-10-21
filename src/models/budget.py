"""Budget model for tracking company finances.

Manages revenue, expenses, reserves, and provides financial analysis
such as profitability, runway, and bankruptcy detection.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Budget:
    """Tracks company finances and budget state."""
    
    total_reserves: float
    monthly_revenue: float = 0.0
    monthly_expenses: float = 0.0
    
    revenue_history: List[float] = field(default_factory=list)
    expense_history: List[float] = field(default_factory=list)
    profit_history: List[float] = field(default_factory=list)
    
    specialist_salary_per_month: float = 3000.0
    infrastructure_cost_per_client: float = 500.0
    software_license_base: float = 1000.0
    software_license_per_specialist: float = 200.0
    infrastructure_base: float = 2000.0
    fixed_overhead: float = 1500.0
    
    def get_monthly_profit(self) -> float:
        """Return monthly profit: revenue - expenses.
        
        Returns:
            Positive if profitable, negative if losing money
        """
        return self.monthly_revenue - self.monthly_expenses
    
    def get_months_runway(self) -> float:
        """How many months can company survive at current burn rate?
        
        Returns:
            Number of months of runway, or infinity if profitable
        """
        if self.get_monthly_profit() >= 0:
            return float('inf')  # Profitable
        
        monthly_burn = abs(self.get_monthly_profit())
        if monthly_burn == 0:
            return float('inf')
        
        return self.total_reserves / monthly_burn
    
    def is_bankrupt(self) -> bool:
        """Check if company is bankrupt.
        
        Returns:
            True if reserves < 0
        """
        return self.total_reserves < 0
    
    def is_in_critical_condition(self) -> bool:
        """Check if company is in critical condition (near bankruptcy).
        
        Returns:
            True if running out of money (< 1 month runway) and not bankrupt
        """
        return self.get_months_runway() < 1.0 and not self.is_bankrupt()
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "total_reserves": self.total_reserves,
            "monthly_revenue": self.monthly_revenue,
            "monthly_expenses": self.monthly_expenses,
            "revenue_history": self.revenue_history,
            "expense_history": self.expense_history,
            "profit_history": self.profit_history,
            "specialist_salary_per_month": self.specialist_salary_per_month,
            "infrastructure_cost_per_client": self.infrastructure_cost_per_client,
            "software_license_base": self.software_license_base,
            "software_license_per_specialist": self.software_license_per_specialist,
            "infrastructure_base": self.infrastructure_base,
            "fixed_overhead": self.fixed_overhead,
        }
    
    @staticmethod
    def from_dict(data: dict) -> "Budget":
        """Create Budget from JSON dict."""
        return Budget(
            total_reserves=data["total_reserves"],
            monthly_revenue=data.get("monthly_revenue", 0.0),
            monthly_expenses=data.get("monthly_expenses", 0.0),
            revenue_history=data.get("revenue_history", []),
            expense_history=data.get("expense_history", []),
            profit_history=data.get("profit_history", []),
            specialist_salary_per_month=data.get("specialist_salary_per_month", 3000.0),
            infrastructure_cost_per_client=data.get("infrastructure_cost_per_client", 500.0),
            software_license_base=data.get("software_license_base", 1000.0),
            software_license_per_specialist=data.get("software_license_per_specialist", 200.0),
            infrastructure_base=data.get("infrastructure_base", 2000.0),
            fixed_overhead=data.get("fixed_overhead", 1500.0),
        )
