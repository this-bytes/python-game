"""Client model representing a company with a cybersecurity contract.

Clients generate incidents at configured rates and have SLA requirements.
Reputation with clients affects contract renewals and bonuses.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List
from enum import Enum


class ClientIndustry(Enum):
    """Enum for client industry sectors."""
    TECHNOLOGY = "Technology"
    FINANCE = "Finance"
    HEALTHCARE = "Healthcare"
    RETAIL = "Retail"
    MANUFACTURING = "Manufacturing"
    GOVERNMENT = "Government"
    EDUCATION = "Education"
    ENERGY = "Energy"


@dataclass
class Client:
    """Represents a client company with a cybersecurity service contract."""
    
    id: str
    name: str
    industry: str
    incident_rate_per_minute: float  # Average incidents generated per minute
    sla_multiplier: float  # Multiplier applied to base SLA times
    reputation: int  # Reputation score (0-100)
    contract_value: int  # Monthly contract value in dollars
    active: bool = True
    
    # Tycoon system fields
    satisfaction_history: List[float] = field(default_factory=list)  # Last 10 incidents
    tier: int = 1  # 1-5 (calculated from reputation)
    contracts: List[str] = field(default_factory=list)  # Contract IDs
    total_incidents_assigned: int = 0
    total_incidents_resolved: int = 0
    total_sla_failures: int = 0
    
    def __post_init__(self):
        """Validate data after initialization."""
        self.reputation = max(0, min(100, self.reputation))  # Clamp 0-100
        if self.incident_rate_per_minute < 0:
            self.incident_rate_per_minute = 0.0
    
    def is_active(self) -> bool:
        """Check if client contract is active.
        
        Returns:
            True if contract is active, False otherwise
        """
        return self.active
    
    def get_incident_rate(self) -> float:
        """Get the incident generation rate for this client.
        
        Returns:
            Incidents per minute
        """
        if not self.active:
            return 0.0
        
        return self.incident_rate_per_minute
    
    def calculate_sla_time(self, base_sla_seconds: int) -> int:
        """Calculate actual SLA time for an incident from this client.
        
        Args:
            base_sla_seconds: Base SLA time from incident type
            
        Returns:
            Actual SLA time in seconds
        """
        return int(base_sla_seconds * self.sla_multiplier)
    
    def adjust_reputation(self, change: int) -> int:
        """Adjust client reputation.
        
        Args:
            change: Amount to change reputation (positive or negative)
            
        Returns:
            New reputation value
        """
        old_reputation = self.reputation
        self.reputation = max(0, min(100, self.reputation + change))
        return self.reputation
    
    def increase_reputation(self, amount: int = 1) -> int:
        """Increase client reputation (successful incident resolution).
        
        Args:
            amount: Amount to increase reputation
            
        Returns:
            New reputation value
        """
        return self.adjust_reputation(amount)
    
    def decrease_reputation(self, amount: int = 3) -> int:
        """Decrease client reputation (SLA failure or poor service).
        
        Args:
            amount: Amount to decrease reputation
            
        Returns:
            New reputation value
        """
        return self.adjust_reputation(-amount)
    
    def get_reputation_level(self) -> str:
        """Get reputation level description.
        
        Returns:
            Reputation level: 'Excellent', 'Good', 'Fair', 'Poor', or 'Critical'
        """
        if self.reputation >= 90:
            return "Excellent"
        elif self.reputation >= 70:
            return "Good"
        elif self.reputation >= 50:
            return "Fair"
        elif self.reputation >= 30:
            return "Poor"
        else:
            return "Critical"
    
    def is_at_risk(self) -> bool:
        """Check if client relationship is at risk (low reputation).
        
        Returns:
            True if reputation < 50, False otherwise
        """
        return self.reputation < 50
    
    def calculate_contract_bonus(self) -> float:
        """Calculate contract value bonus based on reputation.
        
        Returns:
            Bonus multiplier (1.0 = no bonus, 1.5 = 50% bonus)
        """
        # Bonus for high reputation (90+: 25% bonus, 80+: 15% bonus, 70+: 5% bonus)
        if self.reputation >= 90:
            return 1.25
        elif self.reputation >= 80:
            return 1.15
        elif self.reputation >= 70:
            return 1.05
        else:
            return 1.0
    
    def calculate_monthly_revenue(self) -> int:
        """Calculate monthly revenue from this client including reputation bonus.
        
        Returns:
            Monthly revenue in dollars
        """
        if not self.active:
            return 0
        
        base_revenue = self.contract_value
        bonus_multiplier = self.calculate_contract_bonus()
        return int(base_revenue * bonus_multiplier)
    
    def suspend_contract(self) -> bool:
        """Suspend the client contract (deactivate).
        
        Returns:
            True if suspended, False if already inactive
        """
        if not self.active:
            return False
        
        self.active = False
        return True
    
    def resume_contract(self) -> bool:
        """Resume a suspended client contract.
        
        Returns:
            True if resumed, False if already active
        """
        if self.active:
            return False
        
        self.active = True
        return True
    
    def should_renew_contract(self, min_reputation: int = 30) -> bool:
        """Determine if contract should be renewed based on reputation.
        
        Args:
            min_reputation: Minimum reputation required for renewal
            
        Returns:
            True if reputation is sufficient for renewal, False otherwise
        """
        return self.reputation >= min_reputation
    
    def get_incident_rate_description(self) -> str:
        """Get description of incident generation rate.
        
        Returns:
            Description: 'Very High', 'High', 'Medium', 'Low', or 'Very Low'
        """
        rate = self.incident_rate_per_minute
        
        if rate >= 1.0:
            return "Very High"
        elif rate >= 0.6:
            return "High"
        elif rate >= 0.3:
            return "Medium"
        elif rate >= 0.1:
            return "Low"
        else:
            return "Very Low"
    
    def get_sla_strictness(self) -> str:
        """Get description of SLA strictness.
        
        Returns:
            Description: 'Very Strict', 'Strict', 'Standard', 'Relaxed', or 'Very Relaxed'
        """
        if self.sla_multiplier <= 0.7:
            return "Very Strict"
        elif self.sla_multiplier <= 0.9:
            return "Strict"
        elif self.sla_multiplier <= 1.1:
            return "Standard"
        elif self.sla_multiplier <= 1.3:
            return "Relaxed"
        else:
            return "Very Relaxed"
    
    def to_dict(self) -> Dict:
        """Convert client to dictionary for serialization.
        
        Returns:
            Dictionary representation of the client
        """
        return {
            "id": self.id,
            "name": self.name,
            "industry": self.industry,
            "incident_rate_per_minute": self.incident_rate_per_minute,
            "sla_multiplier": self.sla_multiplier,
            "reputation": self.reputation,
            "contract_value": self.contract_value,
            "active": self.active,
            "satisfaction_history": self.satisfaction_history.copy(),
            "tier": self.tier,
            "contracts": self.contracts.copy(),
            "total_incidents_assigned": self.total_incidents_assigned,
            "total_incidents_resolved": self.total_incidents_resolved,
            "total_sla_failures": self.total_sla_failures
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Client':
        """Create Client from dictionary.
        
        Args:
            data: Dictionary containing client data
            
        Returns:
            New Client instance
        """
        return cls(
            id=data["id"],
            name=data["name"],
            industry=data["industry"],
            incident_rate_per_minute=data["incident_rate_per_minute"],
            sla_multiplier=data["sla_multiplier"],
            reputation=data["reputation"],
            contract_value=data["contract_value"],
            active=data.get("active", True),
            satisfaction_history=data.get("satisfaction_history", []).copy(),
            tier=data.get("tier", 1),
            contracts=data.get("contracts", []).copy(),
            total_incidents_assigned=data.get("total_incidents_assigned", 0),
            total_incidents_resolved=data.get("total_incidents_resolved", 0),
            total_sla_failures=data.get("total_sla_failures", 0)
        )
    
    def __repr__(self) -> str:
        """String representation of client."""
        return (f"Client(id='{self.id}', name='{self.name}', "
                f"industry='{self.industry}', reputation={self.reputation}, "
                f"active={self.active})")
