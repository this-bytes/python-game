# PHASE 1 STARTER: BUILD THE DATA MODELS

**Timeline**: Days 1-3
**Status**: Ready to begin immediately
**Difficulty**: 🟢 Low (straightforward data modeling)

---

## WHAT YOU'RE DOING THIS PHASE

Building the foundation: all the data structures needed for the SOC management game. After Phase 1, you'll have:
- Client model with all properties
- Contract tracking
- SLA tracker
- Budget model
- Full persistence (save/load)
- JSON schemas for configuration

**Why This Matters**: Everything after Phase 1 depends on these models being solid. Get this right and the rest flows naturally.

---

## TASK 1: CREATE CLIENT MODEL (2 hours)

**File**: `src/models/client.py`

```python
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

@dataclass
class Client:
    """Represents a SOC client."""
    
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
```

**Test File**: `tests/test_client_model.py`

```python
import pytest
from src.models.client import Client, Industry

def test_create_client():
    """Test creating a client."""
    client = Client(
        client_id="client_001",
        company_name="Acme Bank",
        industry=Industry.BANKING,
        monthly_contract_value=5000,
        sla_response_time_seconds=900,
        sla_resolution_time_seconds=3600,
        contract_start_month=1,
        contract_end_month=12,
    )
    
    assert client.client_id == "client_001"
    assert client.satisfaction == 1.0
    assert client.is_active is True
    assert client.months_active == 0

def test_client_to_dict():
    """Test serialization to dict."""
    client = Client(
        client_id="client_001",
        company_name="Acme Bank",
        industry=Industry.BANKING,
        monthly_contract_value=5000,
        sla_response_time_seconds=900,
        sla_resolution_time_seconds=3600,
        contract_start_month=1,
        contract_end_month=12,
    )
    
    data = client.to_dict()
    
    assert data["client_id"] == "client_001"
    assert data["industry"] == "banking"
    assert data["satisfaction"] == 1.0

def test_client_from_dict():
    """Test deserialization from dict."""
    data = {
        "client_id": "client_001",
        "company_name": "Acme Bank",
        "industry": "banking",
        "monthly_contract_value": 5000,
        "sla_response_time_seconds": 900,
        "sla_resolution_time_seconds": 3600,
        "contract_start_month": 1,
        "contract_end_month": 12,
        "satisfaction": 0.8,
        "is_active": True,
    }
    
    client = Client.from_dict(data)
    
    assert client.client_id == "client_001"
    assert client.satisfaction == 0.8
    assert client.industry == Industry.BANKING
```

**Run It**:
```bash
cd /home/localadmin/code/python-game
pytest tests/test_client_model.py -v
```

**Expected Output**:
```
tests/test_client_model.py::test_create_client PASSED
tests/test_client_model.py::test_client_to_dict PASSED
tests/test_client_model.py::test_client_from_dict PASSED
```

---

## TASK 2: CREATE CONTRACT MODEL (1 hour)

**File**: `src/models/contract.py`

```python
from dataclasses import dataclass
from enum import Enum

class ContractStatus(Enum):
    """Contract lifecycle states."""
    ACTIVE = "active"
    RENEWAL_PENDING = "renewal_pending"
    TERMINATED = "terminated"

@dataclass
class Contract:
    """Represents a client contract."""
    
    contract_id: str
    client_id: str
    start_month: int
    end_month: int
    value_per_month: float
    status: ContractStatus = ContractStatus.ACTIVE
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "contract_id": self.contract_id,
            "client_id": self.client_id,
            "start_month": self.start_month,
            "end_month": self.end_month,
            "value_per_month": self.value_per_month,
            "status": self.status.value,
        }
    
    @staticmethod
    def from_dict(data: dict) -> "Contract":
        """Create Contract from JSON dict."""
        return Contract(
            contract_id=data["contract_id"],
            client_id=data["client_id"],
            start_month=data["start_month"],
            end_month=data["end_month"],
            value_per_month=data["value_per_month"],
            status=ContractStatus(data.get("status", "active")),
        )
```

**Test**: Create `tests/test_contract_model.py` with similar tests.

---

## TASK 3: CREATE SLA TRACKER MODEL (1 hour)

**File**: `src/models/sla_tracker.py`

```python
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class SLATracker:
    """Tracks SLA compliance for a client in a given month."""
    
    tracker_id: str
    client_id: str
    month: int
    
    total_incidents: int = 0
    response_sla_met: int = 0
    response_sla_missed: int = 0
    resolution_sla_met: int = 0
    resolution_sla_missed: int = 0
    
    def get_response_compliance(self) -> float:
        """Get response SLA compliance rate (0.0-1.0)."""
        total = self.response_sla_met + self.response_sla_missed
        if total == 0:
            return 1.0
        return self.response_sla_met / total
    
    def get_resolution_compliance(self) -> float:
        """Get resolution SLA compliance rate (0.0-1.0)."""
        total = self.resolution_sla_met + self.resolution_sla_missed
        if total == 0:
            return 1.0
        return self.resolution_sla_met / total
    
    def get_overall_compliance(self) -> float:
        """Get combined SLA compliance (average of response + resolution)."""
        response_comp = self.get_response_compliance()
        resolution_comp = self.get_resolution_compliance()
        return (response_comp + resolution_comp) / 2.0
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "tracker_id": self.tracker_id,
            "client_id": self.client_id,
            "month": self.month,
            "total_incidents": self.total_incidents,
            "response_sla_met": self.response_sla_met,
            "response_sla_missed": self.response_sla_missed,
            "resolution_sla_met": self.resolution_sla_met,
            "resolution_sla_missed": self.resolution_sla_missed,
        }
    
    @staticmethod
    def from_dict(data: dict) -> "SLATracker":
        """Create SLATracker from JSON dict."""
        return SLATracker(
            tracker_id=data["tracker_id"],
            client_id=data["client_id"],
            month=data["month"],
            total_incidents=data.get("total_incidents", 0),
            response_sla_met=data.get("response_sla_met", 0),
            response_sla_missed=data.get("response_sla_missed", 0),
            resolution_sla_met=data.get("resolution_sla_met", 0),
            resolution_sla_missed=data.get("resolution_sla_missed", 0),
        )
```

---

## TASK 4: UPDATE BUDGET MODEL (1 hour)

**File**: `src/models/budget.py` (update existing or create new)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class Budget:
    """Tracks company finances."""
    
    total_reserves: float
    monthly_revenue: float = 0.0
    monthly_expenses: float = 0.0
    
    revenue_history: List[float] = field(default_factory=list)
    expense_history: List[float] = field(default_factory=list)
    
    specialist_salary_per_month: float = 3000
    infrastructure_cost_per_month: float = 2000
    overhead_per_month: float = 1000
    
    def get_monthly_profit(self) -> float:
        """Return monthly_revenue - monthly_expenses."""
        return self.monthly_revenue - self.monthly_expenses
    
    def get_months_runway(self) -> float:
        """How many months can we survive at current burn rate?"""
        if self.get_monthly_profit() >= 0:
            return float('inf')  # Profitable
        
        monthly_burn = abs(self.get_monthly_profit())
        if monthly_burn == 0:
            return float('inf')
        
        return self.total_reserves / monthly_burn
    
    def is_bankrupt(self) -> bool:
        """Check if company is bankrupt."""
        return self.total_reserves < 0
    
    def is_in_critical_condition(self) -> bool:
        """Check if company is in critical condition (near bankruptcy)."""
        return self.get_months_runway() < 1.0 and not self.is_bankrupt()
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "total_reserves": self.total_reserves,
            "monthly_revenue": self.monthly_revenue,
            "monthly_expenses": self.monthly_expenses,
            "revenue_history": self.revenue_history,
            "expense_history": self.expense_history,
            "specialist_salary_per_month": self.specialist_salary_per_month,
            "infrastructure_cost_per_month": self.infrastructure_cost_per_month,
            "overhead_per_month": self.overhead_per_month,
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
            specialist_salary_per_month=data.get("specialist_salary_per_month", 3000),
            infrastructure_cost_per_month=data.get("infrastructure_cost_per_month", 2000),
            overhead_per_month=data.get("overhead_per_month", 1000),
        )
```

---

## TASK 5: UPDATE GAMESTATE MODEL (1 hour)

**File**: `src/models/game_state.py` (update existing)

Add these fields to the GameState class:

```python
@dataclass
class GameState:
    """Represents complete game state."""
    
    # [EXISTING FIELDS]
    # specialists, incidents, etc.
    
    # [NEW FIELDS]
    active_clients: List[Client] = field(default_factory=list)
    contracts: List[Contract] = field(default_factory=list)
    sla_trackers: List[SLATracker] = field(default_factory=list)
    budget: Budget = field(default_factory=lambda: Budget(total_reserves=10000))
    
    company_founded_month: int = 0
    current_month: int = 1
    
    # Helper methods
    def get_active_clients(self) -> List[Client]:
        """Get all currently active clients."""
        return [c for c in self.active_clients if c.is_active]
    
    def get_client_by_id(self, client_id: str) -> Client | None:
        """Get client by ID."""
        for client in self.active_clients:
            if client.client_id == client_id:
                return client
        return None
    
    def get_sla_tracker_for_client_this_month(self, client_id: str) -> SLATracker | None:
        """Get SLA tracker for client in current month."""
        for tracker in self.sla_trackers:
            if tracker.client_id == client_id and tracker.month == self.current_month:
                return tracker
        return None
```

---

## TASK 6: CREATE PERSISTENCE LAYER (2 hours)

**File**: `src/core/persistence.py`

```python
import json
import logging
from datetime import datetime
from pathlib import Path
from src.models.game_state import GameState
from src.models.client import Client
from src.models.contract import Contract
from src.models.sla_tracker import SLATracker

logger = logging.getLogger(__name__)

def save_game_state(game_state: GameState, filename: str = None) -> str:
    """Save game state to JSON file.
    
    Args:
        game_state: The game state to save
        filename: Optional filename. If None, creates timestamped file.
    
    Returns:
        Path to saved file
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"saves/game_{timestamp}.json"
    
    save_path = Path(filename)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to JSON
    data = {
        "company_founded_month": game_state.company_founded_month,
        "current_month": game_state.current_month,
        "budget": game_state.budget.to_dict(),
        "active_clients": [c.to_dict() for c in game_state.active_clients],
        "contracts": [c.to_dict() for c in game_state.contracts],
        "sla_trackers": [t.to_dict() for t in game_state.sla_trackers],
    }
    
    with open(save_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"Saved game state to {save_path}")
    return str(save_path)


def load_game_state(filename: str) -> GameState | None:
    """Load game state from JSON file.
    
    Args:
        filename: Path to save file
    
    Returns:
        GameState if successful, None if file not found
    """
    save_path = Path(filename)
    
    if not save_path.exists():
        logger.error(f"Save file not found: {filename}")
        return None
    
    with open(save_path, 'r') as f:
        data = json.load(f)
    
    game_state = GameState()
    game_state.company_founded_month = data["company_founded_month"]
    game_state.current_month = data["current_month"]
    game_state.budget = Budget.from_dict(data["budget"])
    game_state.active_clients = [Client.from_dict(c) for c in data["active_clients"]]
    game_state.contracts = [Contract.from_dict(c) for c in data["contracts"]]
    game_state.sla_trackers = [SLATracker.from_dict(t) for t in data["sla_trackers"]]
    
    logger.info(f"Loaded game state from {filename}")
    return game_state
```

---

## TASK 7: CREATE INDUSTRY PROFILES JSON (1 hour)

**File**: `data/industry_profiles.json`

```json
{
  "industry_profiles": {
    "banking": {
      "name": "Banking",
      "threat_level": "critical",
      "avg_monthly_incidents": 12,
      "severity_distribution": {
        "critical": 0.15,
        "high": 0.35,
        "medium": 0.35,
        "low": 0.15
      },
      "threat_landscape": [
        "Fraud Detection",
        "Account Takeover",
        "DDoS Attacks",
        "Data Exfiltration",
        "Ransomware",
        "Insider Threats"
      ],
      "compliance_requirements": "PCI-DSS, SOX"
    },
    "ecommerce": {
      "name": "E-Commerce",
      "threat_level": "high",
      "avg_monthly_incidents": 8,
      "severity_distribution": {
        "critical": 0.10,
        "high": 0.25,
        "medium": 0.45,
        "low": 0.20
      },
      "threat_landscape": [
        "Payment Card Fraud",
        "Account Compromise",
        "Web App Attacks",
        "Inventory Theft",
        "DDOS",
        "Malware"
      ],
      "compliance_requirements": "PCI-DSS"
    },
    "healthcare": {
      "name": "Healthcare",
      "threat_level": "critical",
      "avg_monthly_incidents": 15,
      "severity_distribution": {
        "critical": 0.20,
        "high": 0.40,
        "medium": 0.30,
        "low": 0.10
      },
      "threat_landscape": [
        "Patient Data Breach",
        "Ransomware",
        "Medical Device Compromise",
        "Phishing",
        "Insider Theft",
        "Regulatory Violation"
      ],
      "compliance_requirements": "HIPAA"
    },
    "government": {
      "name": "Government",
      "threat_level": "critical",
      "avg_monthly_incidents": 20,
      "severity_distribution": {
        "critical": 0.25,
        "high": 0.45,
        "medium": 0.25,
        "low": 0.05
      },
      "threat_landscape": [
        "Nation-State Attacks",
        "Classified Data Theft",
        "Infrastructure Attack",
        "Zero-Day Exploitation",
        "Supply Chain Attack",
        "Insider Compromise"
      ],
      "compliance_requirements": "NIST, FedRAMP"
    },
    "saas": {
      "name": "SaaS",
      "threat_level": "medium",
      "avg_monthly_incidents": 5,
      "severity_distribution": {
        "critical": 0.05,
        "high": 0.20,
        "medium": 0.50,
        "low": 0.25
      },
      "threat_landscape": [
        "API Abuse",
        "Account Enumeration",
        "Data Exfiltration",
        "Account Takeover",
        "Denial of Service",
        "Privilege Escalation"
      ],
      "compliance_requirements": "SOC2"
    }
  }
}
```

---

## TESTING CHECKLIST

After completing all 7 tasks, run:

```bash
cd /home/localadmin/code/python-game

# Run all Phase 1 tests
pytest tests/test_client_model.py tests/test_contract_model.py tests/test_sla_tracker_model.py tests/test_budget_model.py tests/test_persistence.py -v

# Check coverage
pytest tests/ --cov=src/models --cov-report=term-missing
```

**Expected Coverage**: >80% on all models

---

## ACCEPTANCE CRITERIA

✅ All 7 tasks complete
✅ All models can be created and have to_dict() / from_dict()
✅ Save/load cycle preserves all data
✅ Industry profiles load correctly from JSON
✅ >80% test coverage on all models
✅ All tests passing

---

## IF YOU GET STUCK

| Problem | Solution |
|---------|----------|
| "Can't import Client" | Make sure `src/models/__init__.py` exports it |
| "JSON won't serialize" | Check that all fields have to_dict() methods |
| "Save file not found" | Create `data/saves/` directory if it doesn't exist |
| "Tests not running" | Run from project root: `cd /home/localadmin/code/python-game` then `pytest` |

---

## NEXT PHASE

Once Phase 1 is complete and all tests pass, you'll move to **Phase 2: Budget System** where you'll implement the financial pressure mechanics.

**But First**: Take the Phase 1 checkpoint! Verify:
- [ ] All code committed to git
- [ ] All tests passing
- [ ] No warnings or errors
- [ ] Save/load works end-to-end

---

**You're ready. Start with Task 1 now.** 🚀

