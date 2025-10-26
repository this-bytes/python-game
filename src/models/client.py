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
    


@dataclass(init=False)
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
    # Contracts held by this client (list of contract ids)
    contracts: List[str] = field(default_factory=list)
    # Reputation and satisfaction history tracking (0-100 scale)
    reputation: int = 80
    satisfaction_history: List[float] = field(default_factory=list)
    total_incidents_resolved: int = 0
    total_sla_failures: int = 0
    # Convenience counters and tier
    total_incidents_assigned: int = 0
    tier: int = 5
    def __init__(
        self,
        client_id: str | None = None,
        company_name: str | None = None,
        industry: Industry | str | None = None,
        monthly_contract_value: float = 0.0,
        sla_response_time_seconds: int = 300,
        sla_resolution_time_seconds: int = 3600,
        contract_start_month: int = 1,
        contract_end_month: int = 12,
        satisfaction: float = 1.0,
        is_active: bool = True,
        avg_monthly_incidents: int = 5,
        threat_landscape: List[str] | None = None,
        incident_severity_distribution: Dict[str, float] | None = None,
        assigned_specialists: List[str] | None = None,
        historical_sla_misses: int = 0,
        months_active: int = 0,
        reputation: int = 80,
        satisfaction_history: List[float] | None = None,
        total_incidents_resolved: int = 0,
        total_sla_failures: int = 0,
        total_incidents_assigned: int = 0,
        tier: int = 5,
        **kwargs,
    ) -> None:
        """Flexible initializer accepting either 'id' or 'client_id', and 'name' or 'company_name'.

        This preserves backward compatibility with older tests/code that passed `id=` or
        `name=` while keeping the canonical attribute names `client_id` and `company_name`.
        """
        # Backwards-compatible aliases
        # Accept either 'id' or 'client_id'
        if client_id is None and 'id' in kwargs:
            client_id = kwargs.pop('id')

        # Accept either 'company_name' or 'name'
        if company_name is None and 'name' in kwargs:
            company_name = kwargs.pop('name')

        # Industry may be provided as string; accept case-insensitive names/values
        if isinstance(industry, str):
            try:
                industry = Industry(industry.lower())
            except Exception:
                try:
                    industry = Industry[industry.upper()]
                except Exception:
                    # fallback to TECHNOLOGY when unknown
                    industry = Industry.TECHNOLOGY

        # Assign defaults for optional collections
        self.client_id = client_id if client_id is not None else kwargs.get('client_id', '')
        self.company_name = company_name if company_name is not None else kwargs.get('company_name', '')
        self.industry = industry if industry is not None else Industry.TECHNOLOGY
        self.monthly_contract_value = monthly_contract_value
        self.sla_response_time_seconds = sla_response_time_seconds
        self.sla_resolution_time_seconds = sla_resolution_time_seconds
        self.contract_start_month = contract_start_month
        self.contract_end_month = contract_end_month
        self.satisfaction = satisfaction
        self.is_active = is_active
        self.avg_monthly_incidents = avg_monthly_incidents
        self.threat_landscape = threat_landscape or []
        self.incident_severity_distribution = incident_severity_distribution or {}
        self.assigned_specialists = assigned_specialists or []
        self.historical_sla_misses = historical_sla_misses
        self.months_active = months_active
        self.reputation = reputation
        self.satisfaction_history = satisfaction_history or []
        self.total_incidents_resolved = total_incidents_resolved
        self.total_sla_failures = total_sla_failures
        self.total_incidents_assigned = total_incidents_assigned
        self.tier = tier
        # Backwards-compatible contracts list (may be used by ContractManager/tests)
        self.contracts = kwargs.get('contracts', [])

    @property
    def id(self) -> str:
        """Compatibility alias for client_id expected by other systems/tests."""
        return self.client_id

    @property
    def name(self) -> str:
        """Compatibility alias for company_name expected by other systems/tests."""
        return self.company_name
    
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
            "reputation": self.reputation,
            "satisfaction_history": self.satisfaction_history,
            "total_incidents_resolved": self.total_incidents_resolved,
            "total_sla_failures": self.total_sla_failures,
            "total_incidents_assigned": self.total_incidents_assigned,
            "tier": self.tier,
        }
    
    @staticmethod
    def from_dict(data: dict) -> "Client":
        """Create Client from JSON dict."""
        # Backwards-compatible key mapping: accept old keys like 'id', 'name', 'contract_value',
        # and new canonical keys
        client_id = data.get("client_id") or data.get("id")
        company_name = data.get("company_name") or data.get("name")
        industry_val = data.get("industry", "technology")
        # SLA and contract keys may be present under different names in older data
        monthly_contract_value = data.get("monthly_contract_value") or data.get("contract_value", 0.0)
        sla_response = data.get("sla_response_time_seconds") or data.get("sla_response") or 300
        sla_resolution = data.get("sla_resolution_time_seconds") or data.get("sla_resolution") or 3600

        return Client(
            client_id=client_id,
            company_name=company_name,
            # Accept case-insensitive industry names/values
            industry=Industry(industry_val.lower()) if isinstance(industry_val, str) else industry_val,
            monthly_contract_value=monthly_contract_value,
            sla_response_time_seconds=sla_response,
            sla_resolution_time_seconds=sla_resolution,
            contract_start_month=data.get("contract_start_month", 1),
            contract_end_month=data.get("contract_end_month", 12),
            satisfaction=data.get("satisfaction", 1.0),
            is_active=data.get("is_active", True),
            avg_monthly_incidents=data.get("avg_monthly_incidents", 5),
            threat_landscape=data.get("threat_landscape", []),
            incident_severity_distribution=data.get("incident_severity_distribution", {}),
            assigned_specialists=data.get("assigned_specialists", []),
            historical_sla_misses=data.get("historical_sla_misses", 0),
            months_active=data.get("months_active", 0),
            reputation=data.get("reputation", 80),
            satisfaction_history=data.get("satisfaction_history", []),
            total_incidents_resolved=data.get("total_incidents_resolved", 0),
            total_sla_failures=data.get("total_sla_failures", 0),
            total_incidents_assigned=data.get("total_incidents_assigned", 0),
            tier=data.get("tier", 5),
        )
