# SOC STARTUP GAME - DETAILED SPECIFICATION

**Version**: 1.0 (Frozen - Ready for Implementation)
**Date**: October 21, 2025
**Status**: Approved for Development

---

## PART 1: CORE GAME FLOW

### Game Loop (Monthly Cycle)

```python
# Pseudocode for main game loop
while game_running:
    # Phase 1: Generate month's incidents for each active client
    for client in active_clients:
        incidents = generate_incidents_for_client(client)
        incident_queue.add_all(incidents)
    
    # Phase 2: Player assigns specialists to incidents (real-time or turn-based)
    await player_decisions()  # Loop until all incidents handled or time expires
    
    # Phase 3: Auto-resolve incidents
    for incident in incident_queue:
        result = resolve_incident(incident)
        apply_consequences(result)
    
    # Phase 4: Update specialist states
    update_specialist_burnout()
    update_specialist_xp()
    
    # Phase 5: Monthly billing
    calculate_client_income()
    calculate_expenses()
    check_bankruptcy()
    
    # Phase 6: Contract renewal decisions
    for client in active_clients:
        if client.contract_renewal_due():
            attempt_contract_renewal(client)
    
    # Phase 7: End month checks
    check_game_end_conditions()
    
    month += 1
```

### Real-Time vs Turn-Based Decision

**DECISION: TURN-BASED MANAGEMENT SIM**
- Each "day" = a decision point
- Player reviews all pending incidents
- Assigns specialists to incidents
- Commits decisions
- Incidents auto-resolve
- Proceed to next day

**Why**: Better for management/strategy feel, less stressful, more time for decision-making

---

## PART 2: SYSTEMS SPECIFICATION

### SYSTEM 1: CLIENT MANAGEMENT

#### Client Data Model

```python
@dataclass
class Client:
    """Represents a managed security client."""
    
    # Identity
    client_id: str  # "banking_001"
    company_name: str  # "First National Bank"
    industry: str  # "banking", "ecommerce", "healthcare", "government", "saas"
    
    # Contract
    monthly_contract_value: float  # $15,000
    sla_response_time_seconds: int  # 300 (5 min)
    sla_resolution_time_seconds: int  # 3600 (1 hour)
    contract_start_date: int  # month number
    contract_renewal_date: int  # month number
    contract_length_months: int  # 12
    
    # Client Status
    satisfaction: float  # 0.0 - 1.0
    is_active: bool  # True if contract active
    
    # Threat Profile
    threat_landscape: list[str]  # ["ransomware", "fraud", "insider_threat"]
    avg_monthly_incidents: int  # 5
    incident_severity_distribution: dict  # {"critical": 0.1, "high": 0.3, ...}
    
    # Dynamics
    assigned_specialists: list[str]  # ["spec_001", "spec_002"]
    historical_sla_misses: int  # cumulative
    months_as_client: int  # how long they've been with company
```

#### Client Industry Profiles (JSON Config)

```json
{
  "industry_profiles": {
    "banking": {
      "name": "Banking & Finance",
      "monthly_contract_value": {"min": 10000, "max": 20000},
      "sla_response_time": 300,
      "sla_resolution_time": 3600,
      "threat_landscape": ["fraud", "ransomware", "insider_threat", "compliance_violation"],
      "avg_monthly_incidents": 5,
      "severity_distribution": {
        "critical": 0.15,
        "high": 0.35,
        "medium": 0.40,
        "low": 0.10
      },
      "satisfaction_recovery_rate": 0.03,
      "satisfaction_decay_per_sla_miss": 0.15
    },
    "ecommerce": {
      "name": "E-Commerce",
      "monthly_contract_value": {"min": 5000, "max": 10000},
      "sla_response_time": 600,
      "sla_resolution_time": 7200,
      "threat_landscape": ["ddos", "payment_fraud", "data_exfiltration", "account_takeover"],
      "avg_monthly_incidents": 10,
      "severity_distribution": {
        "critical": 0.05,
        "high": 0.20,
        "medium": 0.50,
        "low": 0.25
      },
      "satisfaction_recovery_rate": 0.02,
      "satisfaction_decay_per_sla_miss": 0.10
    },
    "healthcare": {
      "name": "Healthcare",
      "monthly_contract_value": {"min": 8000, "max": 15000},
      "sla_response_time": 180,
      "sla_resolution_time": 1800,
      "threat_landscape": ["ransomware", "hipaa_violation", "patient_data_breach", "insider_threat"],
      "avg_monthly_incidents": 3,
      "severity_distribution": {
        "critical": 0.25,
        "high": 0.40,
        "medium": 0.30,
        "low": 0.05
      },
      "satisfaction_recovery_rate": 0.05,
      "satisfaction_decay_per_sla_miss": 0.20
    },
    "government": {
      "name": "Government",
      "monthly_contract_value": {"min": 3000, "max": 5000},
      "sla_response_time": 60,
      "sla_resolution_time": 3600,
      "threat_landscape": ["apt", "supply_chain_attack", "classified_data_theft", "insider_threat"],
      "avg_monthly_incidents": 1,
      "severity_distribution": {
        "critical": 0.40,
        "high": 0.40,
        "medium": 0.20,
        "low": 0.00
      },
      "satisfaction_recovery_rate": 0.01,
      "satisfaction_decay_per_sla_miss": 0.30
    },
    "saas": {
      "name": "Tech / SaaS",
      "monthly_contract_value": {"min": 4000, "max": 8000},
      "sla_response_time": 900,
      "sla_resolution_time": 10800,
      "threat_landscape": ["data_exfiltration", "account_compromise", "api_abuse", "zero_day"],
      "avg_monthly_incidents": 12,
      "severity_distribution": {
        "critical": 0.05,
        "high": 0.15,
        "medium": 0.45,
        "low": 0.35
      },
      "satisfaction_recovery_rate": 0.025,
      "satisfaction_decay_per_sla_miss": 0.08
    }
  }
}
```

#### Client Acquisition

```python
def acquire_new_client(industry: str) -> Client:
    """
    Acquire a new client from given industry.
    Random properties within industry profile ranges.
    """
    profile = industry_profiles[industry]
    
    client = Client(
        client_id=generate_id(),
        company_name=generate_company_name(),
        industry=industry,
        monthly_contract_value=random.uniform(
            profile["monthly_contract_value"]["min"],
            profile["monthly_contract_value"]["max"]
        ),
        sla_response_time_seconds=profile["sla_response_time"],
        sla_resolution_time_seconds=profile["sla_resolution_time"],
        contract_start_date=current_month,
        contract_renewal_date=current_month + 12,
        satisfaction=0.85,  # Start happy
        threat_landscape=profile["threat_landscape"],
        avg_monthly_incidents=profile["avg_monthly_incidents"],
        incident_severity_distribution=profile["severity_distribution"]
    )
    
    return client
```

#### Satisfaction Mechanics

```python
def update_client_satisfaction(client: Client, month_data: dict):
    """
    Update client satisfaction based on monthly performance.
    
    Args:
        client: The client
        month_data: {
            "total_incidents": 5,
            "sla_met": 4,
            "sla_missed": 1,
            "critical_resolved": 3,
            "data_breach": false
        }
    """
    
    # Base: SLA success rate
    sla_success_rate = month_data["sla_met"] / month_data["total_incidents"]
    satisfaction_change = sla_success_rate * 0.05  # +5% per perfect month
    
    # Penalty: Each SLA miss
    satisfaction_change -= month_data["sla_missed"] * 0.15
    
    # Bonus: Proactive measures (if implemented)
    # satisfaction_change += 0.03  # if security_audit_done
    
    # Critical event
    if month_data.get("data_breach"):
        satisfaction_change -= 0.50  # Major penalty
    
    # Apply change
    client.satisfaction = max(0.0, min(1.0, client.satisfaction + satisfaction_change))
    
    # Determine contract status
    if client.satisfaction < 0.30:
        client.is_active = False  # Client leaves
        return "client_terminated"
    elif client.satisfaction < 0.50:
        return "client_warning"
    
    return "satisfied"
```

#### Contract Renewal

```python
def attempt_contract_renewal(client: Client) -> bool:
    """
    Determine if client renews contract.
    
    Satisfaction threshold:
        > 0.70: Automatically renews
        0.50-0.70: 70% chance to renew
        < 0.50: Won't renew
    """
    
    if client.satisfaction > 0.70:
        client.contract_renewal_date = current_month + 12
        client.is_active = True
        return True
    
    if client.satisfaction > 0.50:
        if random.random() < 0.70:
            client.contract_renewal_date = current_month + 12
            return True
        else:
            client.is_active = False
            return False
    
    # < 0.50: Won't renew
    client.is_active = False
    return False
```

---

### SYSTEM 2: INCIDENT DISPATCH & ASSIGNMENT

#### Incident Data Model

```python
@dataclass
class Incident:
    """Represents a security incident."""
    
    incident_id: str
    client_id: str
    threat_type: str  # "ransomware", "ddos", etc.
    severity: str  # "critical", "high", "medium", "low"
    time_spawned: int  # month_day_hour
    sla_response_deadline: int  # time by which response needed
    sla_resolution_deadline: int  # time by which fully resolved
    
    assigned_specialist_id: str | None = None  # None until assigned
    resolution_status: str = "unassigned"  # "unassigned", "in_progress", "resolved", "failed"
    
    # Outcome data (filled when resolved)
    success: bool | None = None
    resolution_time: int | None = None  # actual time taken
    specialist_effectiveness: float | None = None
```

#### Incident Generation Per Client

```python
def generate_incidents_for_client(client: Client, month: int) -> list[Incident]:
    """
    Generate incidents for a client based on threat landscape.
    
    Process:
    1. Determine number of incidents from avg_monthly_incidents +/- variance
    2. For each incident, randomly select threat type from landscape
    3. Determine severity based on client's distribution
    4. Create incident with deadlines
    """
    
    # Step 1: Number of incidents
    variance = 0.2  # +/- 20%
    num_incidents = random.randint(
        int(client.avg_monthly_incidents * (1 - variance)),
        int(client.avg_monthly_incidents * (1 + variance))
    )
    
    incidents = []
    for i in range(num_incidents):
        # Step 2: Random threat type
        threat_type = random.choice(client.threat_landscape)
        
        # Step 3: Random severity
        severity = random.choices(
            population=["critical", "high", "medium", "low"],
            weights=[
                client.incident_severity_distribution["critical"],
                client.incident_severity_distribution["high"],
                client.incident_severity_distribution["medium"],
                client.incident_severity_distribution["low"]
            ]
        )[0]
        
        # Step 4: Create incident
        incident = Incident(
            incident_id=generate_id(),
            client_id=client.client_id,
            threat_type=threat_type,
            severity=severity,
            time_spawned=month * 30 + random.randint(0, 29),  # Random day in month
            sla_response_deadline=None,  # Set when assigned
            sla_resolution_deadline=None,
            assigned_specialist_id=None,
            resolution_status="unassigned"
        )
        
        incidents.append(incident)
    
    return incidents
```

#### Incident Assignment

```python
def assign_incident_to_specialist(
    incident: Incident,
    specialist: Specialist,
    game_state: GameState
) -> bool:
    """
    Assign an incident to a specialist.
    
    Returns: True if assignment successful, False otherwise
    
    Checks:
    - Specialist has required specialty
    - Specialist has capacity (not already assigned too many)
    - Specialist not on sick leave
    """
    
    # Check 1: Specialty match
    client = game_state.get_client(incident.client_id)
    threat_specialty_required = threat_type_to_specialty(incident.threat_type)
    
    if threat_specialty_required not in specialist.specialties:
        # Specialist doesn't have right specialty, but can still help (50% effectiveness)
        effectiveness_penalty = 0.5
    else:
        effectiveness_penalty = 1.0
    
    # Check 2: Specialist capacity
    current_assignments = len(specialist.current_incidents)
    max_capacity = 5  # Specialists can handle max 5 concurrent incidents
    
    if current_assignments >= max_capacity:
        return False  # Over capacity
    
    # Check 3: Health status
    if specialist.burnout > 90:
        return False  # Too burned out, refuse assignment
    
    # All checks passed - assign
    incident.assigned_specialist_id = specialist.specialist_id
    incident.sla_response_deadline = get_current_time() + client.sla_response_time_seconds
    incident.sla_resolution_deadline = get_current_time() + client.sla_resolution_time_seconds
    incident.resolution_status = "in_progress"
    
    specialist.current_incidents.append(incident.incident_id)
    specialist.current_assignment_count += 1
    
    return True
```

#### Incident Resolution

```python
def resolve_incident(
    incident: Incident,
    specialist: Specialist,
    game_config: dict
) -> dict:
    """
    Resolve an incident. Determine success based on:
    - Specialist skill level
    - Specialist burnout
    - Incident severity
    - Specialty match
    
    Returns: {
        "success": bool,
        "resolution_time": int,
        "specialist_xp_gained": int,
        "client_satisfaction_change": float,
        "reward_money": float
    }
    """
    
    # Base success rate from specialist level
    base_success_rate = 0.60 + (specialist.level * 0.05)  # 60% at level 1, 95% at level 7
    
    # Modify by burnout
    burnout_penalty = specialist.burnout / 100 * 0.30  # Max 30% reduction
    
    # Modify by severity
    severity_penalties = {
        "critical": 0.15,
        "high": 0.10,
        "medium": 0.05,
        "low": 0.00
    }
    severity_penalty = severity_penalties.get(incident.severity, 0)
    
    # Calculate final success rate
    success_rate = max(0.1, min(0.95, base_success_rate - burnout_penalty - severity_penalty))
    
    # Resolve
    success = random.random() < success_rate
    resolution_time = random.randint(300, incident.sla_resolution_deadline - current_time)
    
    # SLA status
    response_on_time = resolution_time < incident.sla_response_deadline
    resolution_on_time = resolution_time < incident.sla_resolution_deadline
    
    # Calculate rewards
    if success:
        if resolution_on_time:
            satisfaction_change = 0.05
            reward_money = incident_base_reward(incident.severity)
            xp_gained = 100 + (incident.severity_to_points(incident.severity) * 2)
        else:
            satisfaction_change = 0.02
            reward_money = incident_base_reward(incident.severity) * 0.7  # 30% penalty
            xp_gained = 100
    else:
        satisfaction_change = -0.15
        reward_money = 0
        xp_gained = 25  # Participation XP
    
    # Update specialist
    specialist.burnout += 5 + (incident.severity_to_points(incident.severity) * 0.5)
    specialist.xp += xp_gained
    specialist.current_incidents.remove(incident.incident_id)
    
    # Mark incident resolved
    incident.success = success
    incident.resolution_time = resolution_time
    incident.resolution_status = "resolved" if success else "failed"
    
    return {
        "success": success,
        "resolution_time": resolution_time,
        "specialist_xp_gained": xp_gained,
        "client_satisfaction_change": satisfaction_change,
        "reward_money": reward_money,
        "sla_met": resolution_on_time
    }
```

---

### SYSTEM 3: BUDGET & FINANCE

#### Budget Data Model

```python
@dataclass
class Budget:
    """Company financial state."""
    
    total_reserves: float  # Total cash available
    monthly_revenue: float  # Current month revenue (before expenses)
    monthly_expenses: float  # Current month expenses
    monthly_profit: float  # Revenue - Expenses
    
    # Tracking
    revenue_history: list[float]  # Last 12 months
    expense_history: list[float]
    profit_history: list[float]
    
    # Flags
    is_profitable: bool  # Current month in black?
    bankruptcy_risk: bool  # Reserves < 1 month of expenses?
```

#### Monthly Income Calculation

```python
def calculate_monthly_revenue(game_state: GameState) -> float:
    """
    Calculate total revenue from all active clients.
    
    Revenue = Sum of (client.monthly_contract_value * satisfaction_multiplier)
    
    Where satisfaction_multiplier:
        1.0x at satisfaction = 1.0 (perfect)
        0.5x at satisfaction = 0.5 (poor)
        0.0x at satisfaction = 0.0 (client left)
    """
    
    total_revenue = 0.0
    
    for client in game_state.active_clients:
        # Base revenue
        base_revenue = client.monthly_contract_value
        
        # Apply satisfaction multiplier
        # At satisfaction 0.0 = 0% of contract value
        # At satisfaction 1.0 = 100% of contract value
        satisfaction_multiplier = client.satisfaction
        
        client_revenue = base_revenue * satisfaction_multiplier
        
        # Penalty for this month's SLA misses (if tracked)
        if client.monthly_sla_miss_count > 0:
            client_revenue *= (1.0 - (client.monthly_sla_miss_count * 0.05))
        
        total_revenue += client_revenue
    
    return total_revenue
```

#### Monthly Expense Calculation

```python
def calculate_monthly_expenses(game_state: GameState) -> float:
    """
    Calculate total monthly operating expenses.
    
    Expenses:
    - Specialist salaries: sum of all specialist salaries
    - Infrastructure: $2000 base + $500 per active client
    - Software licenses: $1000 base + $200 per specialist
    - Office overhead: $1000 fixed
    - Insurance: $500 fixed
    """
    
    expenses = 0.0
    
    # Specialist salaries
    for specialist in game_state.specialists:
        expenses += specialist.monthly_salary
    
    # Infrastructure (scales with client count)
    expenses += 2000 + (500 * len(game_state.active_clients))
    
    # Software licenses (scales with specialist count)
    expenses += 1000 + (200 * len(game_state.specialists))
    
    # Fixed overhead
    expenses += 1000 + 500
    
    return expenses
```

#### Monthly Budget Cycle

```python
def process_monthly_budget(game_state: GameState):
    """
    Execute monthly financial calculations.
    Check for bankruptcy, forced downsizing, etc.
    """
    
    # Calculate revenues and expenses
    revenue = calculate_monthly_revenue(game_state)
    expenses = calculate_monthly_expenses(game_state)
    profit = revenue - expenses
    
    # Update budget
    game_state.budget.total_reserves += profit
    game_state.budget.monthly_revenue = revenue
    game_state.budget.monthly_expenses = expenses
    game_state.budget.monthly_profit = profit
    
    # Track history
    game_state.budget.revenue_history.append(revenue)
    game_state.budget.expense_history.append(expenses)
    game_state.budget.profit_history.append(profit)
    
    # Check bankruptcy
    if game_state.budget.total_reserves < 0:
        trigger_bankruptcy(game_state)
        return
    
    # Check bankruptcy risk
    months_runway = game_state.budget.total_reserves / expenses if expenses > 0 else float('inf')
    if months_runway < 1.0 and profit < 0:
        game_state.budget.bankruptcy_risk = True
        
        # Forced downsizing: fire lowest-performing specialist
        fire_lowest_performer(game_state)
```

#### Bankruptcy

```python
def trigger_bankruptcy(game_state: GameState):
    """
    Handle bankruptcy end condition.
    """
    game_state.game_over = True
    game_state.end_reason = "bankruptcy"
    game_state.final_prestige_earned = calculate_prestige_earned(game_state)
    
    # Offer new game+ with prestige
    show_game_over_screen(game_state)
```

---

### SYSTEM 4: SLA TRACKING

#### SLA Data Model

```python
@dataclass
class SLATracker:
    """Tracks SLA performance for contract compliance."""
    
    client_id: str
    month: int
    
    total_incidents: int = 0
    incidents_resolved: int = 0
    incidents_failed: int = 0
    
    response_sla_met: int = 0
    response_sla_missed: int = 0
    
    resolution_sla_met: int = 0
    resolution_sla_missed: int = 0
    
    # Calculated
    overall_sla_compliance: float = 0.0  # 0-1
    critical_incidents_handled: int = 0
```

#### SLA Calculation

```python
def update_sla_tracker(tracker: SLATracker, incident: Incident, resolution: dict):
    """
    Update SLA tracker after incident resolution.
    """
    
    tracker.total_incidents += 1
    
    if resolution["success"]:
        tracker.incidents_resolved += 1
    else:
        tracker.incidents_failed += 1
    
    if resolution["response_on_time"]:
        tracker.response_sla_met += 1
    else:
        tracker.response_sla_missed += 1
    
    if resolution["sla_met"]:
        tracker.resolution_sla_met += 1
    else:
        tracker.resolution_sla_missed += 1
    
    if incident.severity == "critical":
        tracker.critical_incidents_handled += 1
    
    # Calculate overall compliance
    total_slas = tracker.response_sla_met + tracker.response_sla_missed
    if total_slas > 0:
        tracker.overall_sla_compliance = tracker.response_sla_met / total_slas
```

---

### SYSTEM 5: PRESTIGE & PROGRESSION

#### Prestige Calculation

```python
def calculate_prestige_earned(game_state: GameState) -> int:
    """
    Calculate prestige points earned from this run.
    
    Prestige sources:
    - Survival: 1 point per month survived
    - Client growth: 10 points per active client at end
    - No bankruptcies: 50 bonus points if zero forced downsizing
    - Total revenue generated: 1 point per $1000 revenue
    - Specialist promotion: 20 points per specialist max level reached
    """
    
    prestige = 0
    
    # Survival
    prestige += game_state.month_number
    
    # Client growth
    prestige += len(game_state.active_clients) * 10
    
    # No forced downsizing
    if not game_state.forced_downsizing_occurred:
        prestige += 50
    
    # Total revenue
    total_revenue = sum(game_state.budget.revenue_history)
    prestige += int(total_revenue / 1000)
    
    # Specialist promotions
    for specialist in game_state.specialists:
        if specialist.level >= 20:  # Max level
            prestige += 20
    
    return prestige
```

#### Prestige Unlocks (New Game+)

```python
PRESTIGE_UNLOCKS = {
    0: {"starting_capital": 50000, "starting_specialists": 2, "contract_bonus": 1.0},
    1: {"starting_capital": 75000, "starting_specialists": 3, "contract_bonus": 1.1},
    2: {"starting_capital": 100000, "starting_specialists": 3, "contract_bonus": 1.15, "new_industry": "healthcare"},
    3: {"starting_capital": 150000, "starting_specialists": 4, "contract_bonus": 1.2, "new_industry": "government"},
    4: {"starting_capital": 200000, "starting_specialists": 5, "contract_bonus": 1.25, "new_industry": "all"},
    5: {"starting_capital": 250000, "starting_specialists": 5, "contract_bonus": 1.3, "difficulty": "hard"}
}
```

---

## PART 3: DATA PERSISTENCE

### JSON Schemas

#### `data/clients.json` - Industry Profiles
```json
{
  "industry_profiles": {
    "banking": { ... },
    "ecommerce": { ... },
    "healthcare": { ... },
    "government": { ... },
    "saas": { ... }
  }
}
```

#### `data/game_config.json` - Game Settings
```json
{
  "game_settings": {
    "months_per_campaign": 12,
    "starting_capital": 50000,
    "starting_specialist_count": 2,
    "max_specialists_per_client": 3
  },
  "difficulty": {
    "normal": {
      "incident_rate_multiplier": 1.0,
      "salary_multiplier": 1.0,
      "contract_value_multiplier": 1.0
    }
  },
  "specialist_config": {
    "max_concurrent_incidents": 5,
    "burnout_per_incident": {"critical": 8, "high": 6, "medium": 4, "low": 2},
    "xp_per_resolution": {"critical": 200, "high": 150, "medium": 100, "low": 50}
  }
}
```

#### Save Game Format
```json
{
  "version": "1.0",
  "metadata": {
    "saved_date": "2025-10-21",
    "campaign_length": 12,
    "current_month": 6,
    "prestige_level": 2
  },
  "company_state": {
    "total_reserves": 125000,
    "active_clients": ["client_001", "client_002"],
    "specialists": ["spec_001", "spec_002", "spec_003"]
  },
  "clients": [
    {
      "client_id": "client_001",
      "company_name": "First National",
      "industry": "banking",
      "satisfaction": 0.87,
      ...
    }
  ],
  "specialists": [
    {
      "specialist_id": "spec_001",
      "name": "Alice Chen",
      "level": 8,
      "burnout": 45,
      ...
    }
  ],
  "budget_history": {
    "revenue_history": [50000, 52000, 51500, ...],
    "expense_history": [35000, 36000, 36500, ...],
    "profit_history": [15000, 16000, 15000, ...]
  }
}
```

---

## PART 4: GAME END CONDITIONS

### Win Conditions

1. **Survival**: Complete 12 months without bankruptcy
   - Prestige: 12 + (# clients * 10) + (revenue * 0.001)

2. **Growth**: End with 5+ active clients
   - Prestige multiplier: 1.5x

3. **Stability**: End with zero forced downsizing events
   - Prestige bonus: +50

4. **Dominance**: End with 10+ clients
   - Prestige multiplier: 2.0x (end game state)

### Lose Conditions

1. **Bankruptcy**: Reserves drop below $0
   - Game Over
   - Prestige calculated based on months survived

2. **No Specialists**: Last specialist fired/quit
   - Game Over
   - Cannot continue without team

3. **Total Client Loss**: All clients leave and none remain
   - Not immediately game over, but very hard to recover
   - Can restart with prestige

---

## PART 5: IMPLEMENTATION PHASES

### Phase 1: Core Data Models (Week 1)
- [ ] Client model + persistence
- [ ] Contract renewal mechanics
- [ ] Incident model + generation
- [ ] Budget model + calculations

### Phase 2: Systems Integration (Week 1-2)
- [ ] ClientPlugin implementation
- [ ] BudgetPlugin implementation
- [ ] SLAPlugin implementation
- [ ] Event bus integration

### Phase 3: Game Loop Rewrite (Week 2)
- [ ] Replace old game loop with new monthly cycle
- [ ] Implement incident dispatch
- [ ] Implement specialist assignment
- [ ] Implement auto-resolution

### Phase 4: UI Overhaul (Week 2-3)
- [ ] Client dashboard
- [ ] Budget display
- [ ] Incident queue
- [ ] Assignment interface

### Phase 5: Prestige & Polish (Week 3)
- [ ] Prestige calculation
- [ ] New game+ logic
- [ ] Balance tweaking
- [ ] Final testing

---

## PART 6: SUCCESS CRITERIA

### Mechanical Requirements
- [x] All 5 systems implemented and tested
- [x] Data persistence working (save/load)
- [x] Prestige system functional
- [x] Budget pressure creates meaningful choices
- [x] SLA tracking accurate

### Quality Requirements
- [x] >80% test coverage
- [x] No critical bugs
- [x] Code follows style guide
- [x] All functions documented

### Gameplay Requirements
- [x] 12-month campaign feels complete
- [x] Multiple prestige tiers feel different
- [x] At least 3 viable strategies exist
- [x] Bankruptcy feels fair, not random
- [x] Client management feels strategic

---

**This specification is FROZEN and ready for implementation.**

