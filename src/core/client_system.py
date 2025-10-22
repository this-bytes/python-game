"""Client management system for SOC Startup.

Handles client acquisition, satisfaction tracking, and contract renewal.
This is Phase 3 of the core game systems.

Key features:
- Generate clients from industry profiles
- Acquire clients for the company
- Track and update client satisfaction
- Handle contract renewals based on satisfaction
- SLA performance affects retention
"""

import random
import json
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from src.models.client import Client, Industry
from src.utils.logger import GameLogger
from src.utils.json_loader import JSONLoader


logger = GameLogger("client_system")


# ===== CLIENT GENERATION =====

def generate_client_from_template(
    industry: Industry,
    client_id: str,
    company_name_override: Optional[str] = None
) -> Client:
    """Create a new client from an industry profile template.
    
    Each industry has different:
    - Incident frequency and severity distribution
    - SLA strictness
    - Contract value
    - Threat landscape
    
    Args:
        industry: Industry enum value
        client_id: Unique client ID
        company_name_override: Optional custom name; otherwise generated
        
    Returns:
        New Client instance
        
    Raises:
        ValueError: If industry not found or invalid
    """
    # Load industry profiles from JSON
    try:
        with open("data/clients.json", "r") as f:
            data = json.load(f)
    except Exception as e:
        logger.error("Failed to load clients.json", exception=e)
        raise ValueError(f"Cannot load client templates: {e}")
    
    # Get industry template from existing client data (simplified approach)
    # In full implementation, we'd have separate industry_templates.json
    industry_profiles = _build_industry_profiles(data.get("clients", []))
    
    if industry.value not in industry_profiles:
        logger.warning(f"Industry profile not found: {industry.value}")
        profile = _get_default_profile()
    else:
        profile = industry_profiles[industry.value]
    
    # Generate company name if not provided
    if company_name_override is None:
        company_name = _generate_company_name(industry)
    else:
        company_name = company_name_override
    
    # Create client with slight variance from template
    client = Client(
        client_id=client_id,
        company_name=company_name,
        industry=industry,
        monthly_contract_value=_apply_variance(
            profile["monthly_contract_value"],
            variance_pct=0.1  # ±10% variance
        ),
        sla_response_time_seconds=profile["sla_response_time_seconds"],
        sla_resolution_time_seconds=profile["sla_resolution_time_seconds"],
        contract_start_month=0,  # Starts at current month
        contract_end_month=12,   # 12 month contracts
        satisfaction=1.0,        # New clients start satisfied
        is_active=True,
        avg_monthly_incidents=int(_apply_variance(
            profile["avg_monthly_incidents"],
            variance_pct=0.15
        )),
        threat_landscape=profile.get("threat_landscape", []),
        incident_severity_distribution=profile.get(
            "incident_severity_distribution", {}
        ),
        months_active=0,
    )
    
    logger.info(
        f"Generated client: {client.company_name} ({industry.value})",
        contract_value=client.monthly_contract_value,
        incidents_per_month=client.avg_monthly_incidents,
    )
    
    return client


def generate_random_client(client_id: str) -> Client:
    """Generate client with random industry.
    
    Args:
        client_id: Unique client ID
        
    Returns:
        New Client with random industry
    """
    industries = [ind for ind in Industry]
    random_industry = random.choice(industries)
    return generate_client_from_template(random_industry, client_id)


# ===== SATISFACTION SYSTEM =====

def update_client_satisfaction(
    client: Client,
    sla_met: int,
    sla_missed: int,
    data_breach: bool = False
) -> None:
    """Update client satisfaction based on monthly SLA performance.
    
    Satisfaction formula:
    - Base: No change if SLA met
    - SLA Violation: -0.15 per missed SLA
    - Data Breach: -0.30 (catastrophic)
    - Excellence Bonus: +0.05 if zero misses + sustained high satisfaction
    
    Satisfaction bounds: [0.0, 1.0]
    
    Args:
        client: Client to update
        sla_met: Number of SLAs met this month
        sla_missed: Number of SLAs missed this month
        data_breach: If true, apply catastrophic penalty
        
    Raises:
        ValueError: If sla_met/sla_missed are negative
    """
    if sla_met < 0 or sla_missed < 0:
        raise ValueError("SLA counts cannot be negative")
    
    old_satisfaction = client.satisfaction
    
    # Calculate satisfaction change
    satisfaction_change = 0.0
    
    # SLA violations: -15% per miss
    satisfaction_change -= sla_missed * 0.15
    
    # Data breach is catastrophic: -30%
    if data_breach:
        satisfaction_change -= 0.30
        logger.warning(
            f"Data breach for {client.company_name}: satisfaction -= 30%"
        )
    # Excellence bonus: +5% if perfect month and satisfaction > 0.8 and no breach
    elif sla_missed == 0 and client.satisfaction > 0.80:
        satisfaction_change += 0.05
        logger.debug(f"{client.company_name}: Excellence bonus +5%")
    
    # Apply change and clamp to [0.0, 1.0]
    new_satisfaction = max(0.0, min(1.0, old_satisfaction + satisfaction_change))
    client.satisfaction = new_satisfaction
    
    # Track SLA misses
    client.historical_sla_misses += sla_missed
    
    logger.info(
        f"Satisfaction updated: {client.company_name}",
        old=f"{old_satisfaction:.2%}",
        new=f"{new_satisfaction:.2%}",
        change=f"{satisfaction_change:+.2%}",
        sla_met=sla_met,
        sla_missed=sla_missed,
    )


def get_satisfaction_status(satisfaction: float) -> str:
    """Get human-readable satisfaction status.
    
    Args:
        satisfaction: Client satisfaction (0.0-1.0)
        
    Returns:
        Status string: "excellent", "satisfied", "warning", "critical"
    """
    if satisfaction >= 0.90:
        return "excellent"
    elif satisfaction >= 0.70:
        return "satisfied"
    elif satisfaction >= 0.40:
        return "warning"
    else:
        return "critical"


# ===== CONTRACT RENEWAL =====

def attempt_contract_renewal(client: Client) -> Tuple[bool, str]:
    """Determine if client renews contract at month end.
    
    Renewal probability based on satisfaction:
    - Excellent (>=0.90): 95% renewal
    - Satisfied (0.70-0.90): 80% renewal
    - Warning (0.40-0.70): 50% renewal
    - Critical (<0.40): 20% renewal
    
    Args:
        client: Client attempting renewal
        
    Returns:
        Tuple of (renewed: bool, reason: str)
    """
    satisfaction = client.satisfaction
    status = get_satisfaction_status(satisfaction)
    
    # Determine renewal probability based on status
    renewal_probabilities = {
        "excellent": 0.95,
        "satisfied": 0.80,
        "warning": 0.50,
        "critical": 0.20,
    }
    
    renewal_chance = renewal_probabilities.get(status, 0.5)
    renewed = random.random() < renewal_chance
    
    # Build reason message
    if renewed:
        reason = f"Contract renewed ({status} - {satisfaction:.0%} satisfaction)"
    else:
        reason = f"Contract NOT renewed ({status} - {satisfaction:.0%} satisfaction)"
    
    logger.info(
        f"{client.company_name}: {reason}",
        satisfaction=f"{satisfaction:.0%}",
        renewal_chance=f"{renewal_chance:.0%}",
    )
    
    return renewed, reason


def handle_contract_termination(client: Client, reason: str) -> Dict:
    """Process client contract termination.
    
    When client cancels:
    - Mark as inactive
    - Remove from active roster
    - Calculate prestige loss
    - Log reason
    
    Args:
        client: Client being terminated
        reason: Reason for termination
        
    Returns:
        Dict with termination details:
        {
            "client_id": str,
            "company_name": str,
            "revenue_lost": float,
            "prestige_loss": int,
            "reason": str
        }
    """
    client.is_active = False
    
    # Prestige loss scales with monthly revenue (bigger clients = bigger loss)
    prestige_loss = int(client.monthly_contract_value / 100)  # $1 revenue = 1 prestige loss
    
    result = {
        "client_id": client.client_id,
        "company_name": client.company_name,
        "revenue_lost": client.monthly_contract_value,
        "prestige_loss": prestige_loss,
        "reason": reason,
    }
    
    logger.warning(
        f"Client terminated: {client.company_name}",
        reason=reason,
        revenue_lost=client.monthly_contract_value,
        prestige_loss=prestige_loss,
    )
    
    return result


# ===== HELPER FUNCTIONS =====

def _build_industry_profiles(clients_data: List[Dict]) -> Dict[str, Dict]:
    """Build industry profile templates from sample client data.
    
    Aggregates similar clients by industry to create templates.
    """
    profiles = {}
    
    for client in clients_data:
        industry = client.get("industry", "technology")
        
        if industry not in profiles:
            profiles[industry] = {
                "monthly_contract_value": client.get("monthly_contract_value", 10000),
                "sla_response_time_seconds": client.get("sla_response_time_seconds", 3600),
                "sla_resolution_time_seconds": client.get("sla_resolution_time_seconds", 86400),
                "avg_monthly_incidents": client.get("avg_monthly_incidents", 5),
                "threat_landscape": client.get("threat_landscape", []),
                "incident_severity_distribution": client.get("incident_severity_distribution", {}),
            }
    
    return profiles


def _get_default_profile() -> Dict:
    """Get default industry profile for unknown industries."""
    return {
        "monthly_contract_value": 10000.0,
        "sla_response_time_seconds": 3600,
        "sla_resolution_time_seconds": 86400,
        "avg_monthly_incidents": 5,
        "threat_landscape": ["DDoS", "Malware", "Phishing"],
        "incident_severity_distribution": {
            "critical": 0.10,
            "high": 0.25,
            "medium": 0.45,
            "low": 0.20,
        },
    }


def _generate_company_name(industry: Industry) -> str:
    """Generate a realistic company name for an industry.
    
    Args:
        industry: Industry type
        
    Returns:
        Generated company name
    """
    prefixes = {
        "banking": ["SecureBank", "TrustFinance", "VaultTrust"],
        "healthcare": ["HealthPlus", "MedSecure", "CareGuard"],
        "government": ["CivicShield", "PublicSecure", "StateGuard"],
        "technology": ["TechCorp", "CloudSecure", "DevShield"],
        "finance": ["FinanceVault", "AssetSecure", "TrustGuard"],
        "retail": ["RetailSecure", "StoreSafe", "ShopShield"],
        "ecommerce": ["OrderSecure", "CheckoutGuard", "CartShield"],
        "manufacturing": ["FactorySecure", "ProductShield", "MfgGuard"],
        "education": ["EduSecure", "CampusShield", "SchoolGuard"],
        "energy": ["EnergyShield", "PowerSecure", "GridGuard"],
        "telecom": ["TeleSecure", "CommsShield", "NetGuard"],
        "saas": ["AppSecure", "CloudShield", "SaaSOps"],
    }
    
    industry_names = prefixes.get(industry.value, ["Secure"])
    prefix = random.choice(industry_names)
    
    suffixes = ["Inc.", "Holdings", "Corp.", "Ltd.", "Systems", "Solutions"]
    suffix = random.choice(suffixes)
    
    return f"{prefix} {suffix}"


def _apply_variance(base_value: float, variance_pct: float = 0.1) -> float:
    """Apply random variance to a value.
    
    Args:
        base_value: Base value
        variance_pct: Variance percentage (e.g., 0.1 = ±10%)
        
    Returns:
        Value with random variance applied
    """
    variance = base_value * variance_pct
    return base_value + random.uniform(-variance, variance)


# ===== BULK OPERATIONS =====

def load_clients_from_json() -> List[Client]:
    """Load all clients from clients.json.
    
    Returns:
        List of Client instances from JSON data
        
    Raises:
        Exception: If JSON cannot be loaded or parsed
    """
    try:

        with open("data/clients.json", "r") as f:
            data = json.load(f)
    except Exception as e:
        logger.error("Failed to load clients.json", exception=e)
        return []
    
    clients = []
    for client_data in data.get("clients", []):
        try:
            industry = Industry(client_data.get("industry", "technology"))
            client = Client(
                client_id=client_data.get("client_id"),
                company_name=client_data.get("company_name"),
                industry=industry,
                monthly_contract_value=client_data.get("monthly_contract_value"),
                sla_response_time_seconds=client_data.get("sla_response_time_seconds"),
                sla_resolution_time_seconds=client_data.get("sla_resolution_time_seconds"),
                contract_start_month=client_data.get("contract_start_month"),
                contract_end_month=client_data.get("contract_end_month"),
                satisfaction=client_data.get("satisfaction", 1.0),
                is_active=client_data.get("is_active", True),
                avg_monthly_incidents=client_data.get("avg_monthly_incidents", 5),
                threat_landscape=client_data.get("threat_landscape", []),
                incident_severity_distribution=client_data.get(
                    "incident_severity_distribution", {}
                ),
                assigned_specialists=client_data.get("assigned_specialists", []),
                historical_sla_misses=client_data.get("historical_sla_misses", 0),
                months_active=client_data.get("months_active", 0),
            )
            clients.append(client)
            logger.debug(f"Loaded client: {client.company_name}")
        except Exception as e:
            logger.error(
                f"Failed to load client {client_data.get('client_id')}",
                exception=e
            )
    
    logger.info(f"Loaded {len(clients)} clients from JSON")
    return clients
