"""SOC Startup Contract model for managing service agreements.

Contracts represent active service agreements with clients, including
terms, pricing, renewal status, and duration tracking.
"""

from dataclasses import dataclass
from typing import Dict
from enum import Enum


class ContractStatus(Enum):
    """Contract lifecycle status."""
    ACTIVE = "active"
    RENEWAL_PENDING = "renewal_pending"
    TERMINATED = "terminated"


@dataclass
class Contract:
    """Represents a service contract with a client."""
    
    # Identity
    contract_id: str
    client_id: str
    
    # Terms
    monthly_value: float
    start_month: int
    end_month: int
    
    # Status
    status: ContractStatus = ContractStatus.ACTIVE
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "contract_id": self.contract_id,
            "client_id": self.client_id,
            "monthly_value": self.monthly_value,
            "start_month": self.start_month,
            "end_month": self.end_month,
            "status": self.status.value,
        }
    
    @staticmethod
    def from_dict(data: dict) -> "Contract":
        """Create Contract from JSON dict."""
        return Contract(
            contract_id=data["contract_id"],
            client_id=data["client_id"],
            monthly_value=data["monthly_value"],
            start_month=data["start_month"],
            end_month=data["end_month"],
            status=ContractStatus(data.get("status", "active")),
        )
