"""SOC Startup Client model for multi-client management system.

Clients represent cybersecurity service contracts with different industry threat profiles.
Each client has SLA requirements, satisfaction tracking, and contract renewal mechanics.
"""

from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum


class Industry(Enum):
    """Client industry types."""
    BANKING = "banking"
    ECOMMERCE = "ecommerce"
    HEALTHCARE = "healthcare"
    GOVERNMENT = "government"
    SAAS = "saas"
    TECHNOLOGY = "technology"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    EDUCATION = "education"
    ENERGY = "energy"
    TELECOM = "telecom"
    FINANCE = "finance"
    


@dataclass
class Client:
    """Represents a SOC client (cybersecurity service contract)."""
    
    # Identity
    client_id: str
    company_name: str
    industry: Industry
    
    # Contract Terms
    monthly_contract_value: float
    sla_response_time_seconds: int
    sla_resolution_time_seconds: int
    contract_start_month: int
    contract_end_month: int
    
    # Current Status
    satisfaction: float = 1.0  # 0.0 - 1.0
    is_active: bool = True
    
    # Threat Profile (varies by industry)
    avg_monthly_incidents: int = 5
    threat_landscape: List[str] = field(default_factory=list)
    
    # Severity distribution: {"critical": 0.1, "high": 0.3, "medium": 0.4, "low": 0.2}
    incident_severity_distribution: Dict[str, float] = field(default_factory=dict)
    
    # Tracking
    assigned_specialists: List[str] = field(default_factory=list)
    historical_sla_misses: int = 0
    months_active: int = 0
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "client_id": self.client_id,
            "company_name": self.company_name,
            "industry": self.industry.value,
            "monthly_contract_value": self.monthly_contract_value,
            "sla_response_time_seconds": self.sla_response_time_seconds,
            "sla_resolution_time_seconds": self.sla_resolution_time_seconds,
            "contract_start_month": self.contract_start_month,
            "contract_end_month": self.contract_end_month,
            "satisfaction": self.satisfaction,
            "is_active": self.is_active,
            "avg_monthly_incidents": self.avg_monthly_incidents,
            "threat_landscape": self.threat_landscape,
            "incident_severity_distribution": self.incident_severity_distribution,
            "assigned_specialists": self.assigned_specialists,
            "historical_sla_misses": self.historical_sla_misses,
            "months_active": self.months_active,
        }
    
    @staticmethod
    def from_dict(data: dict) -> "Client":
        """Create Client from JSON dict."""
        return Client(
            client_id=data["client_id"],
            company_name=data["company_name"],
            industry=Industry(data["industry"]),
            monthly_contract_value=data["monthly_contract_value"],
            sla_response_time_seconds=data["sla_response_time_seconds"],
            sla_resolution_time_seconds=data["sla_resolution_time_seconds"],
            contract_start_month=data["contract_start_month"],
            contract_end_month=data["contract_end_month"],
            satisfaction=data.get("satisfaction", 1.0),
            is_active=data.get("is_active", True),
            avg_monthly_incidents=data.get("avg_monthly_incidents", 5),
            threat_landscape=data.get("threat_landscape", []),
            incident_severity_distribution=data.get("incident_severity_distribution", {}),
            assigned_specialists=data.get("assigned_specialists", []),
            historical_sla_misses=data.get("historical_sla_misses", 0),
            months_active=data.get("months_active", 0),
        )
