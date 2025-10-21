"""Tests for the new SOC Startup Client model."""

import pytest
from src.models.client import Client, Industry


class TestClientModel:
    """Test suite for Client dataclass."""
    
    def test_create_client(self):
        """Verify Client can be created with all required fields."""
        client = Client(
            client_id="client_001",
            company_name="TechCorp",
            industry=Industry.BANKING,
            monthly_contract_value=5000.0,
            sla_response_time_seconds=300,
            sla_resolution_time_seconds=3600,
            contract_start_month=1,
            contract_end_month=12,
            avg_monthly_incidents=8,
            threat_landscape=["credential_theft", "malware"],
            incident_severity_distribution={
                "critical": 0.1,
                "high": 0.3,
                "medium": 0.4,
                "low": 0.2
            }
        )
        
        # Verify basic fields
        assert client.client_id == "client_001"
        assert client.company_name == "TechCorp"
        assert client.industry == Industry.BANKING
        assert client.monthly_contract_value == 5000.0
        assert client.sla_response_time_seconds == 300
        assert client.sla_resolution_time_seconds == 3600
        
        # Verify defaults
        assert client.satisfaction == 1.0
        assert client.is_active is True
        assert client.assigned_specialists == []
        assert client.historical_sla_misses == 0
        assert client.months_active == 0
    
    def test_client_to_dict(self):
        """Verify Client.to_dict() serializes correctly."""
        client = Client(
            client_id="client_002",
            company_name="FinanceInc",
            industry=Industry.ECOMMERCE,
            monthly_contract_value=3000.0,
            sla_response_time_seconds=600,
            sla_resolution_time_seconds=7200,
            contract_start_month=2,
            contract_end_month=13,
            satisfaction=0.85,
            avg_monthly_incidents=12
        )
        
        client_dict = client.to_dict()
        
        # Verify serialization
        assert client_dict["client_id"] == "client_002"
        assert client_dict["company_name"] == "FinanceInc"
        assert client_dict["industry"] == "ecommerce"  # Enum value
        assert client_dict["monthly_contract_value"] == 3000.0
        assert client_dict["satisfaction"] == 0.85
        assert isinstance(client_dict, dict)
    
    def test_client_from_dict(self):
        """Verify Client.from_dict() deserializes correctly."""
        data = {
            "client_id": "client_003",
            "company_name": "HealthSystem",
            "industry": "healthcare",
            "monthly_contract_value": 8000.0,
            "sla_response_time_seconds": 180,
            "sla_resolution_time_seconds": 1800,
            "contract_start_month": 3,
            "contract_end_month": 14,
            "satisfaction": 0.95,
            "is_active": True,
            "avg_monthly_incidents": 15,
            "threat_landscape": ["ransomware", "phishing"],
            "incident_severity_distribution": {
                "critical": 0.2,
                "high": 0.3,
                "medium": 0.3,
                "low": 0.2
            },
            "assigned_specialists": ["spec_001", "spec_002"],
            "historical_sla_misses": 2,
            "months_active": 6
        }
        
        client = Client.from_dict(data)
        
        # Verify deserialization
        assert client.client_id == "client_003"
        assert client.company_name == "HealthSystem"
        assert client.industry == Industry.HEALTHCARE
        assert client.monthly_contract_value == 8000.0
        assert client.satisfaction == 0.95
        assert client.assigned_specialists == ["spec_001", "spec_002"]
        assert client.historical_sla_misses == 2
        assert client.months_active == 6
        
        # Verify round-trip
        assert client.to_dict() == data
