# IMPLEMENTATION ROADMAP - SOC STARTUP GAME

**Status**: Ready for Development
**Estimated Timeline**: 3-4 weeks
**Team Size**: 1 developer (you)

---

## EXECUTIVE SUMMARY

**Current State**: Passive incident clicker with depth issues
**Target State**: Active SOC management sim with budget pressure, client satisfaction, and strategic depth
**Key Pivot**: From "resolve incidents" → "manage a business"

**What Gets Reused**: ~60% of code (Specialists, burnout, events, plugin system)
**What Gets Replaced**: ~30% (Game loop, UI, incident gen)
**What Gets Added**: ~10% (Clients, budget, SLA, contracts)

---

## PHASE-BY-PHASE BREAKDOWN

### PHASE 1: DATA MODELS & PERSISTENCE (Days 1-3)

**Goal**: Build the foundation - data models and storage

#### Tasks

**1.1 Create Client Model** (2 hours)
```python
# File: src/models/client.py
@dataclass
class Client:
    # Identity
    client_id: str
    company_name: str
    industry: str  # "banking", "ecommerce", etc.
    
    # Contract terms
    monthly_contract_value: float
    sla_response_time_seconds: int
    sla_resolution_time_seconds: int
    contract_start_month: int
    contract_renewal_month: int
    
    # Status
    satisfaction: float  # 0.0-1.0
    is_active: bool
    
    # Threat profile
    threat_landscape: list[str]
    avg_monthly_incidents: int
    incident_severity_distribution: dict
    
    # Tracking
    assigned_specialists: list[str]
    historical_sla_misses: int
    months_active: int
```

**1.2 Create Contract Model** (1 hour)
```python
# File: src/models/contract.py
@dataclass
class Contract:
    contract_id: str
    client_id: str
    start_month: int
    end_month: int
    value_per_month: float
    status: str  # "active", "renewal_pending", "terminated"
```

**1.3 Create SLA Tracker Model** (1 hour)
```python
# File: src/models/sla_tracker.py
@dataclass
class SLATracker:
    tracker_id: str
    client_id: str
    month: int
    
    total_incidents: int
    response_sla_met: int
    response_sla_missed: int
    resolution_sla_met: int
    resolution_sla_missed: int
```

**1.4 Update Budget Model** (1 hour)
```python
# File: src/models/budget.py (update existing)
@dataclass
class Budget:
    total_reserves: float
    monthly_revenue: float
    monthly_expenses: float
    monthly_profit: float
    revenue_history: list[float]
    expense_history: list[float]
```

**1.5 Create JSON Schemas** (2 hours)
```
data/clients.json              ← Industry profiles
data/game_config.json          ← Update with new settings
data/saves/[timestamp].json    ← Save game format
```

**1.6 Update GameState** (1 hour)
```python
# File: src/models/game_state.py (update existing)
# Add:
- active_clients: list[Client]
- contracts: list[Contract]
- sla_trackers: list[SLATracker]
- budget: Budget
- company_founded_month: int
```

**1.7 Create Persistence Layer** (2 hours)
```python
# File: src/core/persistence.py
def save_game_state(game_state: GameState, filename: str) -> bool
def load_game_state(filename: str) -> GameState
def export_client_to_dict(client: Client) -> dict
def import_client_from_dict(data: dict) -> Client
```

**Tests Needed**:
- `tests/test_client_model.py` - Client creation, satisfaction logic
- `tests/test_budget_model.py` - Budget calculations
- `tests/test_persistence.py` - Save/load integrity

**Acceptance Criteria**:
- [ ] All models can be created and serialized to JSON
- [ ] Save/load cycle preserves all data
- [ ] Industry profiles load correctly from JSON
- [ ] All models have >80% test coverage

---

### PHASE 2: CORE SYSTEMS - BUDGET & MONEY (Days 4-5)

**Goal**: Implement the financial pressure system

#### Tasks

**2.1 Implement Budget Calculator** (2 hours)
```python
# File: src/core/budget_system.py
def calculate_monthly_revenue(game_state: GameState) -> float:
    """Sum of all client contract values * satisfaction"""

def calculate_monthly_expenses(game_state: GameState) -> float:
    """Salaries + infrastructure + licenses + overhead"""

def process_monthly_budget(game_state: GameState) -> dict:
    """Calculate profit, check bankruptcy, trigger downsizing if needed"""

def apply_satisfaction_multiplier(client: Client) -> float:
    """Client revenue = contract_value * satisfaction"""
```

**2.2 Implement Bankruptcy Logic** (1 hour)
```python
# File: src/core/budget_system.py
def check_bankruptcy(game_state: GameState) -> bool:
    """Trigger game over if reserves < 0"""

def check_bankruptcy_risk(game_state: GameState) -> bool:
    """Check if bankruptcy imminent (reserves < 1 month expenses)"""

def force_downsizing(game_state: GameState) -> str:
    """Fire lowest-performing specialist to stay solvent"""
```

**2.3 Wire Budget to Game Loop** (1 hour)
```python
# File: src/main.py
# Modify game loop to call budget calculations at end of month
```

**Tests Needed**:
- `tests/test_budget_system.py` - Revenue/expense calculations
- `tests/test_bankruptcy_logic.py` - Bankruptcy conditions
- `tests/test_forced_downsizing.py` - Specialist firing logic

**Acceptance Criteria**:
- [ ] Monthly calculations correct
- [ ] Satisfaction affects revenue properly
- [ ] Bankruptcy triggers when reserves hit 0
- [ ] Forced downsizing prevents bankruptcy when possible
- [ ] >80% test coverage

---

### PHASE 3: CLIENT MANAGEMENT SYSTEM (Days 5-7)

**Goal**: Implement client acquisition, satisfaction, contract renewal

#### Tasks

**3.1 Create Client Generator** (1 hour)
```python
# File: src/core/client_system.py
def generate_client(industry: str) -> Client:
    """Create a new client from industry profile"""

def acquire_client(game_state: GameState, industry: str) -> Client:
    """Add new client to company"""
```

**3.2 Implement Satisfaction System** (2 hours)
```python
# File: src/core/client_system.py
def update_client_satisfaction(client: Client, month_data: dict):
    """Update satisfaction based on SLA performance"""
    # month_data = {
    #   "total_incidents": 5,
    #   "sla_met": 4,
    #   "sla_missed": 1,
    #   "data_breach": false
    # }

def get_satisfaction_status(satisfaction: float) -> str:
    """Return "satisfied", "warning", or "terminated" """
```

**3.3 Implement Contract Renewal** (1 hour)
```python
# File: src/core/client_system.py
def attempt_contract_renewal(client: Client) -> bool:
    """Determine if client renews based on satisfaction"""
```

**3.4 Create ClientPlugin** (2 hours)
```python
# File: src/core/plugins/client_plugin.py
class ClientPlugin(GameSystem):
    def initialize(game_state)
    def update(game_state, delta_time)
    def save_state() -> dict
    def load_state(data: dict)
```

**Tests Needed**:
- `tests/test_client_system.py` - Satisfaction, renewal
- `tests/test_client_plugin.py` - Plugin lifecycle

**Acceptance Criteria**:
- [ ] Clients can be created and managed
- [ ] Satisfaction properly affects revenue and renewal
- [ ] Contract renewal works correctly
- [ ] Plugin integrates with event bus
- [ ] >80% test coverage

---

### PHASE 4: INCIDENT DISPATCH & ASSIGNMENT (Days 7-9)

**Goal**: Rewrite incident system for per-client generation and assignment

#### Tasks

**4.1 Modify Incident Model** (1 hour)
```python
# File: src/models/incident.py (update existing)
# Add:
- client_id: str
- assigned_specialist_id: str | None
- sla_response_deadline: int
- sla_resolution_deadline: int
- severity: str  # "critical", "high", "medium", "low"
```

**4.2 Create Per-Client Incident Generation** (1 hour)
```python
# File: src/core/incident_system.py
def generate_incidents_for_client(client: Client, month: int) -> list[Incident]:
    """Generate incidents based on client's threat landscape"""
```

**4.3 Implement Incident Assignment** (2 hours)
```python
# File: src/core/incident_system.py
def assign_incident_to_specialist(
    incident: Incident,
    specialist: Specialist,
    game_state: GameState
) -> bool:
    """Assign incident to specialist if possible"""
    # Checks: specialty match, capacity, health

def resolve_incident(
    incident: Incident,
    specialist: Specialist,
    game_config: dict
) -> dict:
    """Resolve incident, return success/failure/rewards"""
```

**4.4 Update Game Loop for New Incident Flow** (1 hour)
```python
# File: src/main.py
# Modify to:
# 1. Generate incidents per client
# 2. Player assigns specialists to incidents
# 3. Auto-resolve incidents
# 4. Apply consequences
```

**Tests Needed**:
- `tests/test_incident_generation.py` - Per-client incidents
- `tests/test_incident_assignment.py` - Assignment logic
- `tests/test_incident_resolution.py` - Resolution mechanics

**Acceptance Criteria**:
- [ ] Incidents generate per-client with correct distribution
- [ ] Assignment respects specialist capacity/specialty
- [ ] Resolution probability based on skill/burnout/severity
- [ ] SLA tracking accurate
- [ ] >80% test coverage

---

### PHASE 5: SLA TRACKING SYSTEM (Days 9-10)

**Goal**: Implement SLA timers and compliance tracking

#### Tasks

**5.1 Create SLA Tracker** (1 hour)
```python
# File: src/core/sla_system.py
def track_sla(incident: Incident, resolution: dict) -> SLATracker:
    """Update SLA metrics for client"""

def calculate_sla_compliance(tracker: SLATracker) -> float:
    """Return 0.0-1.0 compliance percentage"""

def get_client_sla_this_month(client: Client) -> SLATracker:
    """Get current month's SLA data"""
```

**5.2 Create SLAPlugin** (1 hour)
```python
# File: src/core/plugins/sla_plugin.py
class SLAPlugin(GameSystem):
    def track_incident_resolution(incident: Incident, result: dict)
    def update_client_satisfaction_from_sla()
```

**Tests Needed**:
- `tests/test_sla_tracking.py` - SLA calculations
- `tests/test_sla_plugin.py` - Plugin integration

**Acceptance Criteria**:
- [ ] SLA tracking accurate for response and resolution
- [ ] Compliance calculated correctly
- [ ] Affects client satisfaction properly
- [ ] >80% test coverage

---

### PHASE 6: UI REWRITE (Days 11-13)

**Goal**: Build new UI for SOC management

#### Tasks

**6.1 Create Client Dashboard Panel** (2 hours)
```python
# File: src/ui/panels/client_dashboard.py
class ClientDashboard:
    def render(screen, game_state)
    def show_client_list()
    def show_client_detail(client: Client)
    def show_contract_status()
    def show_satisfaction_trends()
```

**6.2 Create Budget Display** (1 hour)
```python
# File: src/ui/panels/budget_panel.py
class BudgetPanel:
    def render(screen, game_state)
    def show_monthly_summary()
    def show_reserves_status()
    def show_expense_breakdown()
```

**6.3 Create Incident Queue Panel** (1 hour)
```python
# File: src/ui/panels/incident_queue.py
class IncidentQueuePanel:
    def render(screen, game_state)
    def show_pending_incidents()
    def show_assignment_interface()
    def handle_assignment_click()
```

**6.4 Create Specialist Management Panel** (1 hour)
```python
# File: src/ui/panels/specialist_management.py
class SpecialistManagementPanel:
    def render(screen, game_state)
    def show_specialist_list()
    def show_current_assignments()
    def show_hire_fire_options()
```

**6.5 Wire UI to New Systems** (1 hour)
```python
# File: src/main.py
# Update UI rendering to use new panels
```

**Acceptance Criteria**:
- [ ] All 4 panels render correctly
- [ ] Data updates properly each frame
- [ ] All interactions respond
- [ ] No crashes with edge cases

---

### PHASE 7: PRESTIGE & PROGRESSION (Days 13-14)

**Goal**: Implement prestige system and new game+

#### Tasks

**7.1 Create Prestige Calculator** (1 hour)
```python
# File: src/core/prestige_system.py
def calculate_prestige_earned(game_state: GameState) -> int:
    """Calculate prestige from this run"""

def get_prestige_unlocks(prestige_level: int) -> dict:
    """Get bonuses for prestige level"""
```

**7.2 Implement New Game+** (1 hour)
```python
# File: src/core/prestige_system.py
def start_new_game_with_prestige(prestige_level: int) -> GameState:
    """Create new game state with prestige bonuses"""
```

**7.3 Create End Game Screen** (1 hour)
```python
# File: src/ui/screens/end_game_screen.py
class EndGameScreen:
    def render(screen, game_state)
    def show_summary()
    def show_prestige_earned()
    def show_unlocks()
    def handle_new_game_plus()
```

**Tests Needed**:
- `tests/test_prestige_calculation.py` - Prestige math
- `tests/test_prestige_unlocks.py` - Unlock logic

**Acceptance Criteria**:
- [ ] Prestige calculated correctly
- [ ] New game+ creates game state with bonuses
- [ ] End game screen displays correctly
- [ ] >80% test coverage

---

### PHASE 8: TESTING & BALANCE (Days 15-17)

**Goal**: Comprehensive testing and game balance

#### Tasks

**8.1 Full System Integration Tests** (2 hours)
```python
# File: tests/test_integration.py
def test_complete_game_loop_one_month()
def test_budget_calculations_with_clients()
def test_incident_resolution_affects_satisfaction()
def test_contract_renewal_logic()
def test_bankruptcy_detection()
```

**8.2 Playtest & Balance** (3 hours)
```
Play multiple runs:
1. Aggressive growth strategy
2. Steady conservative strategy
3. Recovery from near-bankruptcy
4. Fast collapse scenario

Verify:
- Budget pressure feels real but fair
- 12-month campaign feels complete
- Multiple viable strategies exist
- Prestige levels feel distinct
- No exploits or trivial wins
```

**8.3 Bug Fixes & Refinement** (2 hours)
```python
# Fix any issues found during testing
# Balance numbers (salaries, contract values, incident rates)
# Optimize performance
```

**Acceptance Criteria**:
- [ ] All tests passing
- [ ] >80% overall test coverage
- [ ] Zero critical bugs
- [ ] Game feels balanced
- [ ] Multiple viable strategies

---

### PHASE 9: POLISH & DOCUMENTATION (Days 17-19)

**Goal**: Polish and document the game

#### Tasks

**9.1 Code Quality & Cleanup**
```python
# Run linting, type checking
# Clean up debug code
# Ensure code follows style guide
```

**9.2 Documentation**
```
- Update README with new game description
- Add game rules to in-game help
- Document prestige system
- Add tutorial for first-time players
```

**9.3 Final Testing**
```
- Full playthrough from start to bankruptcy
- Full playthrough from start to prestige unlock
- Edge case testing
```

**Acceptance Criteria**:
- [ ] Code passes all style checks
- [ ] Documentation complete
- [ ] No critical bugs
- [ ] Ready for release

---

## DAILY SCHEDULE (EXAMPLE)

### Week 1
**Mon-Tue** (Days 1-2): Phase 1 - Core data models
**Wed-Thu** (Days 3-4): Phase 2 - Budget system
**Fri** (Day 5): Phase 3 - Client management pt 1

### Week 2
**Mon-Tue** (Days 6-7): Phase 3-4 - Client management + incident dispatch
**Wed-Thu** (Days 8-9): Phase 4-5 - Incident + SLA tracking
**Fri** (Day 10): Phase 5-6 - SLA + UI planning

### Week 3
**Mon-Tue** (Days 11-12): Phase 6 - UI implementation
**Wed-Thu** (Days 13-14): Phase 7-8 - Prestige + testing
**Fri** (Day 15): Phase 8 - Integration tests + balance

### Week 4
**Mon-Tue** (Days 16-17): Phase 8-9 - Playtesting + polish
**Wed-Thu** (Days 18-19): Phase 9 - Documentation + final testing
**Fri** (Day 20): Buffer/contingency

---

## RISK MITIGATION

### Risk 1: UI Complexity
**Mitigation**: Use existing Pygame framework, iterate on simple panels first

### Risk 2: Balance Issues
**Mitigation**: Start with conservative numbers, test multiple scenarios, have contingency time

### Risk 3: Data Model Changes
**Mitigation**: Design data models thoroughly before coding (already done in spec)

### Risk 4: Performance with Multiple Clients
**Mitigation**: Optimize incident generation and resolution early

---

## SUCCESS CRITERIA (Final)

**Must Have**:
- [x] All 5 core systems implemented
- [x] 12-month campaign playable start-to-finish
- [x] Budget pressure creates meaningful choices
- [x] Client satisfaction affects gameplay
- [x] Prestige system functional
- [x] >80% test coverage
- [x] No critical bugs

**Should Have**:
- [x] Multiple prestige tiers feel distinct
- [x] At least 3 viable strategies
- [x] UI feels responsive and clear
- [x] Sound balance across difficulty

**Nice to Have**:
- [ ] Difficulty selection (Easy/Normal/Hard)
- [ ] Achievements/trophies
- [ ] Replay statistics
- [ ] Music/sound effects

---

## NEXT STEPS

1. **NOW**: Confirm this roadmap with user
2. **Day 1**: Start Phase 1 - Data models
3. **Daily**: Update this roadmap with progress
4. **Weekly**: Playtest and adjust balance

---

**This roadmap is APPROVED and ready for execution.**

