---
applyTo: "**"
---

# Workflows - Instructions

**This file contains step-by-step guides for common development tasks during Phase 2.**

Reference this when:
- Implementing Phase 2 core systems
- Following current task sequence
- Understanding current workflow priorities

**Current Phase**: Phase 2: Core Tycoon Mechanics (Tasks 9-11)
- ✅ Tasks 5-8: COMPLETE (Budget & SLA Systems, 90 tests passing)
- ⏳ Tasks 9-11: IN-PROGRESS (SLA Plugin, Game Loop, Integration)

For Phase 3+ workflows and feature examples, see [plan/IMPLEMENTATION_ROADMAP.md](../../plan/IMPLEMENTATION_ROADMAP.md).

---

## BEFORE YOU START ANY TASK

1. Read [core-standards.instructions.md](core-standards.instructions.md) - specifically the 15-point gate
2. Identify where your code fits: models, core, ui, backend, or data?
3. Understand: **If it's game logic, it goes in `/src/models/` or `/src/core/`, NEVER in UI**
4. Remember: **All game parameters must be in JSON config, not hardcoded**
5. Type hints and tests: **Non-negotiable before committing**
6. Reference the authoritative vision: [plan/SOC_STARTUP_VISION.md](../../plan/SOC_STARTUP_VISION.md)

---

## PHASE 2: CORE TYCOON MECHANICS

**Phase 2 Focus**: Budget System, SLA System, Game Loop Integration

**Current Status**:
- ✅ Task 5: Budget System Unit Tests (25/25 passing, 100%)
- ✅ Task 6: SLA Tracker Model Expansion (3 methods added, tested)
- ✅ Task 7: SLA Tracker Unit Tests (28/28 passing, 100%)
- ✅ Task 8: SLA System Core Functions (37/37 passing, 100%)
- ⏳ Task 9: Create SLA Plugin (1-2 hours)
- ⏳ Task 10: Rewrite Game Loop (2-3 hours)
- ⏳ Task 11: Phase 2 Integration Testing (1-2 hours)

---

## TASK 9: CREATE SLA PLUGIN

### Overview
Convert the existing SLA system into a plugin that integrates with the game loop through the event bus.

### What You're Building
- Plugin wrapper for SLA system
- Event subscriptions (incident_created, incident_assigned, incident_completed)
- SLA timer updates in game loop
- SLA violation detection and reporting

### Files to Modify
- Create: `/src/core/plugins/sla_plugin.py`
- Update: `/src/main.py` (register plugin)
- Update: `/tests/test_sla_plugin.py` (comprehensive tests)

### Step-by-Step Implementation

**Step 1: Understand Current SLA System**

The SLA system from Tasks 5-8 includes:
- `SLATracker`: Core SLA tracking model
- `SLACalculator`: Calculation methods
- `SLAMonitor`: State management
- All tested with 28+ unit tests

Review: `/src/core/sla_system.py`

**Step 2: Create SLA Plugin Class**

```python
from src.core.game_system import GameSystem
from src.core.event_bus import get_event_bus, Event
from src.core.sla_system import SLATracker, SLACalculator, SLAMonitor
import logging

class SLAPlugin(GameSystem):
    """Plugin that manages SLA tracking and violation detection."""
    
    def __init__(self):
        super().__init__()
        self._sla_monitor = SLAMonitor()
        self._event_bus = get_event_bus()
        self._subscription_ids = []
        self._logger = logging.getLogger(__name__)
    
    def get_name(self) -> str:
        """Get plugin name."""
        return "SLAPlugin"
    
    def get_feature_id(self) -> str:
        """Get feature flag ID."""
        return "sla_system"
    
    def initialize(self, game_state) -> None:
        """Initialize SLA plugin."""
        # Subscribe to events
        self._subscription_ids = [
            self._event_bus.subscribe("incident_created", self._on_incident_created),
            self._event_bus.subscribe("incident_assigned", self._on_incident_assigned),
            self._event_bus.subscribe("incident_completed", self._on_incident_completed),
        ]
        self._logger.info("SLA Plugin initialized")
    
    def update(self, game_state, delta_time: float) -> None:
        """Update SLA timers and check for violations."""
        current_time = getattr(game_state, 'game_time', 0.0)
        
        # Check each active SLA for violations
        for sla_tracker in self._sla_monitor.get_active_trackers():
            time_remaining = sla_tracker.get_time_remaining(current_time)
            
            if time_remaining <= 0:
                # SLA violated
                self._event_bus.publish("sla_violated", {
                    "sla_id": sla_tracker.id,
                    "incident_id": sla_tracker.incident_id,
                    "client_id": sla_tracker.client_id
                })
                sla_tracker.mark_violated()
                self._logger.warning(f"SLA {sla_tracker.id} violated for incident {sla_tracker.incident_id}")
    
    def shutdown(self, game_state) -> None:
        """Shutdown SLA plugin."""
        for subscription_id in self._subscription_ids:
            self._event_bus.unsubscribe(subscription_id)
        self._subscription_ids.clear()
    
    def save_state(self, game_state) -> dict:
        """Save SLA plugin state."""
        return {
            "sla_trackers": [t.to_dict() for t in self._sla_monitor.get_all_trackers()]
        }
    
    def load_state(self, game_state, state_data: dict) -> None:
        """Load SLA plugin state."""
        trackers = state_data.get("sla_trackers", [])
        for tracker_data in trackers:
            tracker = SLATracker.from_dict(tracker_data)
            self._sla_monitor.add_tracker(tracker)
    
    # Event handlers
    def _on_incident_created(self, event: Event) -> None:
        """Handle incident created event."""
        incident = event.data.get("incident")
        client = event.data.get("client")
        
        # Create SLA tracker
        tracker = SLATracker(
            id=f"sla_{incident.id}",
            incident_id=incident.id,
            client_id=client.id,
            sla_response_seconds=client.sla_response_time,
            sla_resolution_seconds=client.sla_resolution_time,
            created_time=getattr(game_state, 'game_time', 0.0)
        )
        self._sla_monitor.add_tracker(tracker)
        self._logger.info(f"Created SLA tracker for incident {incident.id}")
    
    def _on_incident_assigned(self, event: Event) -> None:
        """Handle incident assigned event."""
        incident_id = event.data.get("incident_id")
        sla_tracker = self._sla_monitor.get_tracker_for_incident(incident_id)
        
        if sla_tracker:
            sla_tracker.mark_assigned(getattr(game_state, 'game_time', 0.0))
            self._logger.info(f"SLA response timer started for incident {incident_id}")
    
    def _on_incident_completed(self, event: Event) -> None:
        """Handle incident completed event."""
        incident_id = event.data.get("incident_id")
        sla_tracker = self._sla_monitor.get_tracker_for_incident(incident_id)
        
        if sla_tracker:
            sla_tracker.mark_completed(getattr(game_state, 'game_time', 0.0))
            self._logger.info(f"SLA tracked as completed for incident {incident_id}")
```

**Step 3: Register Plugin in main.py**

In `/src/main.py`:

```python
from src.core.plugins.sla_plugin import SLAPlugin

# In Game.initialize():
self.system_manager = SystemManager()
self.system_manager.register_system(SLAPlugin())
# ... other plugins
```

**Step 4: Write Comprehensive Tests**

Create `/tests/test_sla_plugin.py`:

```python
import pytest
from src.core.plugins.sla_plugin import SLAPlugin
from src.core.event_bus import get_event_bus
from src.models.incident import Incident
from src.models.client import Client

class TestSLAPlugin:
    """Test suite for SLA plugin."""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin instance."""
        return SLAPlugin()
    
    @pytest.fixture
    def event_bus(self):
        """Get event bus."""
        return get_event_bus()
    
    def test_plugin_initialization(self, plugin):
        """Test plugin initializes correctly."""
        plugin.initialize(None)
        assert plugin.get_name() == "SLAPlugin"
        assert plugin.get_feature_id() == "sla_system"
    
    def test_sla_tracker_created_on_incident(self, plugin, event_bus):
        """Test SLA tracker created when incident spawned."""
        plugin.initialize(None)
        
        # Publish incident created event
        event_bus.publish("incident_created", {
            "incident": Incident(...),
            "client": Client(...)
        })
        
        # Verify tracker created
        trackers = plugin._sla_monitor.get_all_trackers()
        assert len(trackers) == 1
    
    def test_sla_violation_detected(self, plugin, event_bus):
        """Test SLA violation is detected and reported."""
        plugin.initialize(None)
        
        # Create tracker with expired timer
        tracker = SLATracker(
            id="sla_001",
            incident_id="inc_001",
            client_id="client_001",
            sla_resolution_seconds=300,
            created_time=0.0
        )
        plugin._sla_monitor.add_tracker(tracker)
        
        # Update with time > SLA
        plugin.update(None, delta_time=400)
        
        # Verify violation marked
        assert tracker.is_violated
```

### Testing Requirements

- [ ] Plugin initializes without errors
- [ ] Subscribes to correct events
- [ ] SLA trackers created for new incidents
- [ ] Violations detected and reported
- [ ] State saves and loads correctly
- [ ] Event unsubscribe works on shutdown
- [ ] >80% test coverage

### Acceptance Criteria

- ✅ Plugin created in `/src/core/plugins/sla_plugin.py`
- ✅ Registered in `/src/main.py`
- ✅ All tests passing (>25 tests)
- ✅ Type hints complete
- ✅ Docstrings present (Google-style)
- ✅ No hardcoded values
- ✅ Logs SLA violations with context

---

## TASK 10: REWRITE GAME LOOP

### Overview
Integrate all Phase 2 systems into a unified game loop that represents one "day" in the game.

### What You're Building
- Main game update loop
- Day/turn cycle with phases
- Event-driven phase transitions
- Budget calculation at end of day
- Client satisfaction updates

### The Game Loop (6-Step Day Cycle)

```
1. THREATS SPAWN FOR EACH CLIENT
2. PLAYER ASSIGNS SPECIALISTS TO INCIDENTS
3. RESOLUTION HAPPENS
4. CONSEQUENCES & FEEDBACK
5. END OF DAY: BUDGET UPDATE
6. REPEAT
```

### Files to Modify
- Update: `/src/core/game_loop.py` (or create if doesn't exist)
- Update: `/src/main.py` (integrate into main update)
- Create: `/tests/test_game_loop_integration.py`

### Step-by-Step Implementation

**Step 1: Design Day Cycle**

A day has these phases:
1. **Morning** (0-25% of day): Incidents spawn
2. **Day** (25-75%): Player assigns specialists
3. **Evening** (75-95%): Resolutions complete
4. **Night** (95-100%): Budget calculations
5. Loop back to Morning

**Step 2: Create Game Loop Manager**

```python
from enum import Enum
from src.core.event_bus import get_event_bus

class DayPhase(Enum):
    MORNING = 1    # Incidents spawn
    DAY = 2        # Player assigns
    EVENING = 3    # Resolutions happen
    NIGHT = 4      # Budget updates

class GameLoop:
    """Main game loop managing day cycle."""
    
    def __init__(self, game_config):
        self._game_config = game_config
        self._event_bus = get_event_bus()
        self._current_phase = DayPhase.MORNING
        self._day_counter = 0
        self._time_in_phase = 0.0
        self._phase_duration = game_config.game_settings.get("day_duration_seconds", 600)  # 10 min per day
    
    def update(self, game_state, delta_time: float) -> None:
        """Update game loop."""
        self._time_in_phase += delta_time
        
        # Check if phase should transition
        if self._time_in_phase >= self._phase_duration / 4:
            self._transition_phase(game_state)
    
    def _transition_phase(self, game_state) -> None:
        """Transition to next phase."""
        current = self._current_phase
        
        if current == DayPhase.MORNING:
            self._current_phase = DayPhase.DAY
            self._event_bus.publish("phase_changed", {"phase": "day", "day": self._day_counter})
        
        elif current == DayPhase.DAY:
            self._current_phase = DayPhase.EVENING
            self._event_bus.publish("phase_changed", {"phase": "evening", "day": self._day_counter})
        
        elif current == DayPhase.EVENING:
            self._current_phase = DayPhase.NIGHT
            self._event_bus.publish("phase_changed", {"phase": "night", "day": self._day_counter})
        
        elif current == DayPhase.NIGHT:
            # End of day - calculate budget, update satisfaction, etc.
            self._end_of_day(game_state)
            self._current_phase = DayPhase.MORNING
            self._day_counter += 1
            self._event_bus.publish("day_ended", {"day": self._day_counter})
        
        self._time_in_phase = 0.0
    
    def _end_of_day(self, game_state) -> None:
        """Execute end-of-day calculations."""
        # Calculate revenue from clients
        total_revenue = sum(client.monthly_contract_value for client in game_state.clients 
                          if client.satisfaction > 0)
        
        # Calculate expenses
        total_salary_cost = sum(specialist.salary for specialist in game_state.specialists)
        
        # Update budget
        profit = total_revenue - total_salary_cost
        game_state.money += profit
        
        # Update client satisfaction based on SLA performance
        for client in game_state.clients:
            sla_compliance = self._calculate_client_sla_compliance(game_state, client)
            client.satisfaction = min(1.0, client.satisfaction + (sla_compliance * 0.1))
            
            # Check contract renewal
            if client.satisfaction < 0.3:
                self._event_bus.publish("client_lost", {"client_id": client.id})
                game_state.clients.remove(client)
        
        self._event_bus.publish("end_of_day_calculated", {
            "revenue": total_revenue,
            "expenses": total_salary_cost,
            "profit": profit
        })
    
    def _calculate_client_sla_compliance(self, game_state, client) -> float:
        """Calculate SLA compliance rate for client."""
        # Get all incidents for this client today
        incidents = [i for i in game_state.incidents if i.client_id == client.id]
        
        if not incidents:
            return 1.0  # No incidents = perfect compliance
        
        met_count = sum(1 for i in incidents if i.sla_met)
        return met_count / len(incidents)
```

**Step 3: Integrate into Main Game Loop**

In `/src/main.py`:

```python
def update(self, delta_time: float) -> None:
    """Update game state."""
    # Update game time
    self.game_state.game_time += delta_time
    
    # Update all plugins
    self.system_manager.update_all(self.game_state, delta_time)
    
    # Update main game loop (phases)
    self.game_loop.update(self.game_state, delta_time)
```

**Step 4: Write Integration Tests**

Create `/tests/test_game_loop_integration.py`:

```python
def test_day_cycle_completes():
    """Test complete day cycle transitions."""
    game_state = create_test_game_state()
    game_loop = GameLoop(create_test_config())
    
    # Start morning
    assert game_loop._current_phase == DayPhase.MORNING
    
    # Simulate day progression
    for _ in range(4):  # 4 phase transitions
        game_loop.update(game_state, 150)  # 150s per phase
    
    # Should be back to morning next day
    assert game_loop._current_phase == DayPhase.MORNING
    assert game_loop._day_counter == 1

def test_end_of_day_budget_calculated():
    """Test budget is calculated at end of day."""
    game_state = create_test_game_state(money=10000)
    client = create_test_client(monthly_contract_value=2000)
    specialist = create_test_specialist(salary=500)
    
    game_state.clients = [client]
    game_state.specialists = [specialist]
    
    game_loop = GameLoop(create_test_config())
    
    # Progress to night phase
    for _ in range(3):
        game_loop.update(game_state, 150)
    
    # Check budget updated
    # Revenue = 2000, Salary = 500, Profit = 1500
    assert game_state.money == 11500
```

### Testing Requirements

- [ ] Day cycle transitions correctly
- [ ] Budget calculated at end of day
- [ ] Client satisfaction updated
- [ ] Losing clients with low satisfaction works
- [ ] Events fired at phase transitions
- [ ] Game time advances properly
- [ ] >25 integration tests

### Acceptance Criteria

- ✅ Game loop created/updated in `/src/core/game_loop.py`
- ✅ 6-step day cycle implemented
- ✅ Budget calculations working
- ✅ Client satisfaction tracking
- ✅ Phase transitions firing events
- ✅ Integration tests comprehensive
- ✅ Type hints complete
- ✅ Docstrings present

---

## TASK 11: PHASE 2 INTEGRATION TESTING

### Overview
Comprehensive testing that verifies all Phase 2 systems (Budget, SLA, Game Loop) work together.

### What You're Testing

1. **Budget System** + **Game Loop**: Revenue/expense calculations
2. **SLA System** + **Game Loop**: SLA violations affect client satisfaction
3. **Specialist Assignment** + **Budget**: Salary costs reflect hiring/firing
4. **Full Day Cycle**: All systems interact correctly

### Test File

Create `/tests/test_phase_2_integration.py`:

```python
class TestPhase2Integration:
    """Integration tests for Phase 2 systems."""
    
    def test_full_day_cycle_budget_sla(self):
        """Test complete day: incidents → assignment → SLA → budget."""
        # Setup
        game_state = create_test_game_state(money=10000, day=0)
        client = create_test_client(satisfaction=1.0)
        specialist = create_test_specialist(salary=500)
        incident = create_test_incident(
            client_id=client.id,
            sla_seconds=600,
            base_reward=1000
        )
        
        game_state.clients = [client]
        game_state.specialists = [specialist]
        
        # Day: Assign specialist to incident
        specialist.assign_to_incident(incident)
        
        # Day: Complete incident (met SLA)
        incident.mark_completed(time_taken=300, success=True)
        
        # Progress to end of day
        game_loop = GameLoop(create_test_config())
        for _ in range(4):
            game_loop.update(game_state, 150)
        
        # Verify:
        # - Revenue received
        assert game_state.money == (10000 + 1000 - 500)  # Initial + reward - salary
        # - Client satisfaction maintained
        assert client.satisfaction > 0.9
        # - Day advanced
        assert game_loop._day_counter == 1
    
    def test_sla_violation_reduces_client_satisfaction(self):
        """Test SLA violation reduces satisfaction and may lose client."""
        game_state = create_test_game_state(money=10000)
        client = create_test_client(satisfaction=0.5)
        incident = create_test_incident(sla_seconds=600)
        
        game_state.clients = [client]
        game_state.incidents = [incident]
        
        # Incident exceeds SLA (time_taken > sla_seconds)
        incident.mark_completed(time_taken=1000, success=False, sla_met=False)
        
        # Progress day
        game_loop = GameLoop(create_test_config())
        for _ in range(4):
            game_loop.update(game_state, 150)
        
        # Verify satisfaction decreased
        assert client.satisfaction < 0.5
    
    def test_multiple_incidents_same_day(self):
        """Test handling multiple incidents in same day."""
        game_state = create_test_game_state(money=10000)
        client = create_test_client()
        spec1 = create_test_specialist(specialty="Network Security")
        spec2 = create_test_specialist(specialty="Cryptography")
        
        incident1 = create_test_incident(specialty_required="Network Security")
        incident2 = create_test_incident(specialty_required="Cryptography")
        
        game_state.clients = [client]
        game_state.specialists = [spec1, spec2]
        game_state.incidents = [incident1, incident2]
        
        # Assign both
        spec1.assign_to_incident(incident1)
        spec2.assign_to_incident(incident2)
        
        # Complete both
        incident1.mark_completed(time_taken=300, success=True)
        incident2.mark_completed(time_taken=300, success=True)
        
        # Progress day
        game_loop = GameLoop(create_test_config())
        for _ in range(4):
            game_loop.update(game_state, 150)
        
        # Verify both rewarded
        assert spec1.xp > 0
        assert spec2.xp > 0
```

### Testing Checklist

- [ ] Full day cycle works end-to-end
- [ ] Budget calculations correct
- [ ] SLA violations tracked
- [ ] Client satisfaction updates
- [ ] Multiple incidents handled
- [ ] Plugin integration works
- [ ] Events fire correctly
- [ ] >20 integration tests
- [ ] All tests passing
- [ ] >80% code coverage

### Acceptance Criteria

- ✅ Integration tests cover all Phase 2 systems
- ✅ Full day cycle tested end-to-end
- ✅ Budget + SLA interaction tested
- ✅ Client satisfaction mechanics verified
- ✅ All tests passing
- ✅ Type hints complete
- ✅ Docstrings present
- ✅ Ready for Phase 3

---

## DEBUGGING CHECKLIST

When something isn't working:

- [ ] Check logs: `tail -50 logs/game.log`
- [ ] Verify JSON: `python -m json.tool data/game_config.json`
- [ ] Test function directly: `pytest tests/test_*.py -v`
- [ ] Check backend state: `curl http://localhost:5000/game/state | jq`
- [ ] Review recent changes: `git diff`
- [ ] Verify type hints: `mypy src/`
- [ ] Run full test suite: `pytest tests/`

---

## COMMIT CHECKLIST

Before committing ANY changes:

1. [ ] Read [core-standards.instructions.md](core-standards.instructions.md) 15-point gate
2. [ ] All functions have type hints
3. [ ] All public functions have docstrings
4. [ ] All public functions have tests (>80% coverage)
5. [ ] No hardcoded values (use JSON config)
6. [ ] No duplicate code (DRY principle)
7. [ ] Errors are explicit and logged
8. [ ] Tests pass: `pytest tests/`
9. [ ] No commented-out code or debug prints
10. [ ] Code is self-documenting and clear
11. [ ] Git diff shows intent clearly
12. [ ] Commit message explains WHAT and WHY
13. [ ] JSON changes are valid: `python -m json.tool`
14. [ ] No anti-patterns from [code-style.instructions.md](code-style.instructions.md)
15. [ ] Changes follow [code-style.instructions.md](code-style.instructions.md) conventions

**If ANY item fails, keep working. Don't commit.**

---

## See Also

- **[plan/SOC_STARTUP_VISION.md](../../plan/SOC_STARTUP_VISION.md)** - Authoritative game vision
- **[plan/IMPLEMENTATION_ROADMAP.md](../../plan/IMPLEMENTATION_ROADMAP.md)** - Full project roadmap
- **[copilot-instructions.md](../copilot-instructions.md)** - Main instructions and overview
- **[core-standards.instructions.md](core-standards.instructions.md)** - Absolute standards
- **[code-style.instructions.md](code-style.instructions.md)** - Code style and anti-patterns
- **[architecture.instructions.md](architecture.instructions.md)** - Project structure
- **[testing.instructions.md](testing.instructions.md)** - Testing requirements
- **[plugin-system.instructions.md](plugin-system.instructions.md)** - Plugin architecture
- **[data-driven.instructions.md](data-driven.instructions.md)** - JSON configuration

### Scenario
Your game needs a new specialist type, e.g., "Incident Responder" with different stats.

### Step 1: Add to JSON Configuration

Edit `/data/specialist_templates.json`:

```json
{
  "specialist_templates": [
    {
      "id": "template_incident_responder",
      "name": "Incident Responder",
      "specialty": "Incident Response",
      "description": "Specializes in rapid incident containment and response",
      "base_stats": {
        "speed": 95,
        "accuracy": 80,
        "experience_bonus": 1.0
      },
      "starting_level": 1,
      "starting_xp": 0
    }
  ]
}
```

### Step 2: No Code Changes Needed

That's it. The specialist system is data-driven. The JSON change is sufficient.

**Why?** All specialist types are loaded from JSON via `SpecialistFactory.create_from_json()`.

### Step 3: Create Test

Add to `/tests/test_specialist.py`:

```python
def test_incident_responder_specialist_loads_from_json():
    """Verify Incident Responder specialist loads correctly from template."""
    template = {
        "id": "template_incident_responder",
        "name": "Incident Responder",
        "specialty": "Incident Response",
        "base_stats": {
            "speed": 95,
            "accuracy": 80,
            "experience_bonus": 1.0
        }
    }
    
    specialist = SpecialistFactory.create_from_json(template)
    
    assert specialist.name == "Incident Responder"
    assert specialist.specialty == "Incident Response"
    assert specialist.speed == 95
```

### Step 4: Verify via Backend

```bash
# Start backend if not running
cd backend && python run_backend.py &

# Test the specialist type
curl -X GET http://localhost:5000/specialists \
  | grep -i "Incident Responder"
```

---

## TASK 2: CREATE A NEW INCIDENT TYPE

### Scenario
Your game needs a new incident: "Supply Chain Attack" requiring "Supply Chain Security" specialty.

### Step 1: Create Specialty (if needed)

If "Supply Chain Security" is new, nothing to do - the system dynamically recognizes specialties.

### Step 2: Add to JSON Configuration

Edit `/data/incidents.json`:

```json
{
  "incident_types": [
    {
      "id": "inc_type_supply_chain",
      "name": "Supply Chain Attack",
      "description": "Attacker compromises vendor software in supply chain",
      "specialty_required": "Supply Chain Security",
      "difficulty_range": [2, 4],
      "base_sla_seconds": 600,
      "base_reward": 800,
      "xp_reward": 150,
      "criticality": "high"
    }
  ]
}
```

### Step 3: Test in Backend

```bash
# Manually spawn this incident type
curl -X POST http://localhost:5000/incidents/spawn \
  -H "Content-Type: application/json" \
  -d '{
    "type": "Supply Chain Attack",
    "difficulty": 3
  }'
```

### Step 4: Add to Unit Tests

Add to `/tests/test_incident.py`:

```python
def test_supply_chain_attack_creates_correctly():
    """Verify Supply Chain Attack incident creates with correct properties."""
    incident_data = {
        "id": "inc_type_supply_chain",
        "name": "Supply Chain Attack",
        "specialty_required": "Supply Chain Security",
        "difficulty_range": [2, 4],
        "base_sla_seconds": 600,
        "base_reward": 800,
        "xp_reward": 150
    }
    
    incident = IncidentFactory.create_from_json(incident_data)
    
    assert incident.name == "Supply Chain Attack"
    assert incident.specialty_required == "Supply Chain Security"
    assert incident.base_sla_seconds == 600
    assert incident.base_reward == 800
```

---

## TASK 2.5: ADD A NEW RESOLUTION TREE

### Scenario
You need to add interactive decision-based resolution for a new incident type, like "Zero-Day Exploit" with multiple response strategies.

### Step 1: Design the Decision Tree

Plan your resolution tree:
- **3-5 stages** for engagement without overwhelming
- **2-4 decisions per stage** with clear risk/reward tradeoffs
- **Time pressure** (30-60 seconds per stage)
- **Specialist skill relevance** (different approaches favor different specialties)

### Step 2: Add to JSON Configuration

Edit `/data/resolution_trees.json`:

```json
{
  "zero_day_exploit": {
    "stages": [
      {
        "stage_id": "detection",
        "prompt": "Unknown exploit detected. Initial assessment needed.",
        "decisions": [
          {
            "id": "quarantine_system",
            "text": "Quarantine affected systems immediately",
            "effects": {
              "time_multiplier": 0.7,
              "burnout_cost": 8,
              "success_chance": 0.9
            },
            "next_stage": "analysis"
          },
          {
            "id": "monitor_behavior",
            "text": "Monitor exploit behavior before acting",
            "effects": {
              "time_multiplier": 1.3,
              "accuracy_bonus": 25,
              "burnout_cost": 12,
              "success_chance": 0.75
            },
            "next_stage": "analysis"
          }
        ],
        "time_limit_seconds": 45.0
      },
      {
        "stage_id": "analysis",
        "prompt": "Exploit behavior analyzed. Choose containment strategy.",
        "decisions": [
          {
            "id": "patch_deployment",
            "text": "Deploy emergency security patches",
            "effects": {
              "time_multiplier": 1.0,
              "money_cost": 3000,
              "burnout_cost": 6,
              "success_chance": 0.95
            },
            "resolution_complete": true
          },
          {
            "id": "honey_pot",
            "text": "Set up honeypot to capture attacker data",
            "effects": {
              "time_multiplier": 1.5,
              "accuracy_bonus": 30,
              "burnout_cost": 15,
              "success_chance": 0.7
            },
            "resolution_complete": true
          }
        ],
        "time_limit_seconds": 60.0
      }
    ]
  }
}
```

### Step 3: Balance Decision Effects

Follow these guidelines:
- **Time Multipliers**: 0.5-2.0 (faster/slower resolution)
- **Success Chances**: 0.6-0.95 (realistic probabilities)
- **Burnout Costs**: 5-20 points (fatigue accumulation)
- **Money Costs**: 0-5000 credits (expensive options)
- **Accuracy Bonuses**: 0-50 points (precision improvements)

### Step 4: Test the Resolution Tree

Create comprehensive tests in `/tests/test_decision_based_resolution.py`:

```python
def test_zero_day_resolution_tree(self, resolution_system, specialist):
    """Test zero-day exploit resolution tree navigation."""
    # Create zero-day incident
    incident = Incident(
        id="inc_zero_day_001",
        incident_type="Zero-Day Exploit",
        specialty_required="Network Security",
        difficulty=4,
        sla_seconds=900,
        base_reward=2000,
        xp_reward=300,
        client_id="client_001"
    )
    
    session = resolution_system.start_resolution(incident, specialist)
    
    # Navigate through stages
    assert session.current_stage == "detection"
    
    # Make first decision
    resolution_system.make_decision(session, "quarantine_system", specialist)
    assert session.current_stage == "analysis"
    
    # Complete resolution
    stage_info = resolution_system.get_current_stage_info(session)
    if stage_info["decisions"]:
        resolution_system.make_decision(session, stage_info["decisions"][0]["id"], specialist)
    
    result = resolution_system.complete_resolution(session, specialist, incident)
    assert isinstance(result, ResolutionResult)
```

### Step 5: Update Incident Mapping

Ensure the new incident type maps to the resolution tree in `ResolutionSystem._get_tree_id_for_incident()`:

```python
def _get_tree_id_for_incident(self, incident: Incident) -> str:
    """Map incident type to resolution tree ID."""
    type_mapping = {
        "DDoS Attack": "ddos_attack",
        "Malware Infection": "malware_infection",
        "Phishing": "phishing_attack",
        "Data Breach": "data_breach",
        "Ransomware": "ransomware_attack",
        "Zero-Day Exploit": "zero_day_exploit"  # Add new mapping
    }
    return type_mapping.get(incident.incident_type, "ddos_attack")
```

### Step 6: Verify Integration

- Run all tests: `pytest tests/test_decision_based_resolution.py`
- Test in-game resolution flow
- Verify time pressure mechanics work
- Confirm specialist skill modifiers apply
- Check burnout accumulation is correct

---

## TASK 3: IMPLEMENT A NEW AUTOMATION SCRIPT

### Scenario
Players should be able to auto-assign low-difficulty Cryptography incidents to specialists level 3+.

### Step 1: Add to JSON Configuration

Edit `/data/automation_scripts.json`:

```json
{
  "automation_scripts": [
    {
      "id": "auto_assign_crypto_low",
      "name": "Auto-Assign Cryptography (Low Priority)",
      "description": "Automatically assign low-difficulty cryptography incidents",
      "required_level": 3,
      "specialty": "Cryptography",
      "trigger_conditions": {
        "max_difficulty": 2,
        "specialty_match": true,
        "specialist_available": true
      },
      "effect": "auto_assign",
      "enabled_by_default": false
    }
  ]
}
```

### Step 2: Add Automation Logic (if needed)

If custom logic needed beyond simple auto-assign, add to `/src/core/automation_system.py`:

```python
class AutomationScript:
    """Base automation script."""
    
    def execute(self, game_state: GameState, trigger_data: dict) -> list[GameAction]:
        """Execute automation. Return list of actions to perform."""
        pass

class AutoAssignScript(AutomationScript):
    """Auto-assign matching incidents to available specialists."""
    
    def execute(self, game_state: GameState, trigger_data: dict) -> list[GameAction]:
        """Find matching incidents and assign to available specialists."""
        script_config = trigger_data["script_config"]
        actions = []
        
        # Find specialists with this automation unlocked
        for specialist in game_state.specialists:
            if specialist.level < script_config["required_level"]:
                continue
            if not specialist.is_available:
                continue
            
            # Find matching incidents
            for incident in game_state.unassigned_incidents:
                if incident.specialty_required != script_config["specialty"]:
                    continue
                if incident.difficulty > script_config["max_difficulty"]:
                    continue
                
                # Create assignment action
                actions.append(AssignAction(
                    specialist_id=specialist.id,
                    incident_id=incident.id
                ))
                break  # Move to next specialist
        
        return actions
```

### Step 3: Add Tests

Add to `/tests/test_automation_script.py`:

```python
def test_auto_assign_crypto_low_finds_matching_incidents():
    """Verify automation finds and assigns low-difficulty crypto incidents."""
    specialist = create_specialist(level=3, specialty="Cryptography")
    incident_low = create_incident(difficulty=1, specialty_required="Cryptography")
    incident_high = create_incident(difficulty=4, specialty_required="Cryptography")
    game_state = create_test_game_state(
        specialists=[specialist],
        incidents=[incident_low, incident_high]
    )
    
    script_config = {
        "required_level": 3,
        "specialty": "Cryptography",
        "max_difficulty": 2
    }
    
    automation = AutoAssignScript(script_config)
    actions = automation.execute(game_state, {})
    
    # Should only assign low incident
    assert len(actions) == 1
    assert actions[0].incident_id == incident_low.id
```

---

## TASK 4: BALANCE GAME ECONOMY

### Scenario
You're adjusting reward multipliers, SLA timers, or specialist costs to improve game balance.

### Step 1: Update JSON Configuration

Edit `/data/game_config.json`:

```json
{
  "economy": {
    "sla_failure_penalty_multiplier": 0.4,
    "perfect_completion_bonus": 1.3,
    "specialist_hiring_cost_base": 1800,
    "incident_reward_multiplier": 1.1
  }
}
```

### Step 2: Test Immediately (No Restart Needed!)

The backend supports hot-reload:

```bash
# Terminal 1: Game running
python src/main.py

# Terminal 2: Update config
vim data/game_config.json  # Make changes

# Terminal 3: Hot-reload
curl -X POST http://localhost:5000/config/reload

# Changes applied immediately!
```

### Step 3: Observe Effects

Changes take effect immediately. No restart needed. Verify:

```bash
# Check current config
curl -X GET http://localhost:5000/game/config

# Check game state
curl -X GET http://localhost:5000/game/state
```

### Step 4: Add Test for New Balance

Add to `/tests/test_economy.py`:

```python
def test_specialist_hiring_cost_uses_config():
    """Verify specialist hiring uses config-driven cost."""
    game_config = create_test_config(specialist_hiring_cost_base=1800)
    cost = calculate_specialist_hiring_cost(1, game_config)
    
    assert cost == 1800, f"Expected 1800, got {cost}"

def test_incident_reward_applies_multiplier():
    """Verify incident rewards apply config multiplier."""
    game_config = create_test_config(incident_reward_multiplier=1.1)
    base_reward = 500
    
    final_reward = apply_reward_multipliers(base_reward, game_config)
    
    assert final_reward == 550, f"Expected 550, got {final_reward}"
```

---

## TASK 5: ADD NEW SPECIALIST ABILITY

### Scenario
"Network Specialists" should get 20% faster incident resolution when assigned to network incidents.

### Step 1: Add to JSON Configuration

Edit `/data/abilities.json`:

```json
{
  "abilities": [
    {
      "id": "ability_network_specialist_synergy",
      "name": "Network Specialist Synergy",
      "description": "20% faster resolution on network security incidents",
      "specialty": "Network Security",
      "required_level": 1,
      "effect": {
        "type": "resolution_speed_multiplier",
        "value": 0.8
      }
    }
  ]
}
```

### Step 2: Apply in Resolution System

In `/src/core/resolution_system.py`:

```python
def calculate_resolution_time(
    specialist: Specialist,
    incident: Incident,
    game_config: GameConfig
) -> float:
    """Calculate how long to resolve incident."""
    base_time = incident.base_sla_seconds
    
    # Apply specialist abilities
    for ability in specialist.abilities:
        if ability.type == "resolution_speed_multiplier":
            # Check if ability applies (specialty match)
            if specialist.specialty == incident.specialty_required:
                base_time *= ability.value
    
    return base_time
```

### Step 3: Test the Ability

```python
def test_network_specialist_synergy_speeds_resolution():
    """Verify network specialist resolves network incidents 20% faster."""
    specialist = create_specialist(specialty="Network Security")
    incident = create_incident(
        specialty_required="Network Security",
        base_sla_seconds=100
    )
    
    # Load ability from config
    ability_data = load_ability("ability_network_specialist_synergy")
    specialist.add_ability(ability_data)
    
    resolution_time = calculate_resolution_time(specialist, incident, game_config)
    
    assert resolution_time == 80, f"Expected 80s, got {resolution_time}s"
```

---

## TASK 6: DEBUG WITH BACKEND GODMODE

### Scenario
You want to quickly test something without playing normally.

### Step 1: Start Backend

```bash
cd backend && python run_backend.py
```

### Step 2: Access Admin Panel

Open: `http://localhost:5000/admin`

### Step 3: Use GodMode Endpoints

```bash
# Instantly level up specialist
curl -X PUT http://localhost:5000/godmode/specialist/spec_001 \
  -H "Content-Type: application/json" \
  -d '{"level": 20, "xp": 10000}'

# Instantly add money
curl -X POST http://localhost:5000/godmode/add-money \
  -H "Content-Type: application/json" \
  -d '{"amount": 100000}'

# Spawn specific incident
curl -X POST http://localhost:5000/godmode/spawn-incident \
  -H "Content-Type: application/json" \
  -d '{
    "type": "DDoS Attack",
    "difficulty": 5,
    "client_id": "client_001"
  }'

# Get full game state snapshot
curl -X GET http://localhost:5000/godmode/game-state | jq
```

---

## TASK 7: ANALYZE PERFORMANCE

### Scenario
Game is stuttering or running slow.

### Step 1: Profile Code

```bash
# Run with profiler
python -m cProfile -s cumulative src/main.py 2>&1 | head -30
```

### Step 2: Check Logs

```bash
tail -100 logs/game.log | grep -i "warning\|error"
```

### Step 3: Check Metrics via Backend

```bash
# Get performance metrics
curl -X GET http://localhost:5000/analytics/performance
```

### Step 4: Common Issues

**High CPU (100%+):**
- Check incident generation loop (should be O(1) or O(log n))
- Check assignment algorithm (should not iterate all specialists for each incident)
- Look for unoptimized sorting/filtering

**Memory leak:**
- Check if events are being cleaned up
- Verify JSON parsing isn't accumulating objects
- Ensure removed specialists/incidents are garbage collected

**Slow saves:**
- JSON serialization is bottleneck? Profile JSON operations
- Writing to disk? Use async file I/O
- Too much state? Prune old incidents

---

## TASK 8: ADD NEW STATISTIC/METRIC

### Scenario
You want to track "Total Incidents Resolved" across game lifetime.

### Step 1: Add to Game State

In `/src/models/game_state.py`:

```python
class GameState:
    def __init__(self):
        self.total_incidents_resolved = 0
    
    def complete_incident(self, incident: Incident, specialist: Specialist) -> None:
        """Complete incident and update metrics."""
        self.total_incidents_resolved += 1
        # ... rest of logic
```

### Step 2: Add to Save Data

Ensure save/load includes this:

```python
def to_dict(self) -> dict:
    """Convert game state to dict for saving."""
    return {
        "total_incidents_resolved": self.total_incidents_resolved,
        # ... other fields
    }

def from_dict(data: dict) -> "GameState":
    """Load game state from dict."""
    game_state = GameState()
    game_state.total_incidents_resolved = data.get("total_incidents_resolved", 0)
    # ... other fields
    return game_state
```

### Step 3: Add API Endpoint

In `/backend/routes/analytics.py`:

```python
@app.get("/analytics/metrics")
def get_metrics():
    """Get current game metrics."""
    return {
        "total_incidents_resolved": game_state.total_incidents_resolved,
        "total_money_earned": game_state.total_money_earned,
        "total_xp_gained": game_state.total_xp_gained
    }
```

### Step 4: Test It

```python
def test_total_incidents_resolved_increments():
    """Verify incident counter increments on completion."""
    game_state = create_test_game_state()
    specialist = create_specialist()
    incident = create_incident()
    
    assert game_state.total_incidents_resolved == 0
    
    game_state.complete_incident(incident, specialist)
    
    assert game_state.total_incidents_resolved == 1
```

---

## TASK 9: ADD NEW CONFIGURATION SECTION

### Scenario
You want to add "social features" config section for prestige/reputation systems.

### Step 1: Add to game_config.json

```json
{
  "social_features": {
    "prestige_unlock_level": 20,
    "prestige_multiplier": 2.0,
    "reputation_gain_per_perfect_incident": 10,
    "reputation_gain_per_failed_incident": -5,
    "leaderboard_update_frequency": 300
  }
}
```

### Step 2: Load in Config Class

In `/src/core/config.py`:

```python
class GameConfig:
    def __init__(self):
        self.social_features = {}
    
    @staticmethod
    def load_from_json(path: str = "data/game_config.json") -> "GameConfig":
        with open(path) as f:
            data = json.load(f)
        
        config = GameConfig()
        config.social_features = data.get("social_features", {})
        # ... other sections
        
        logger.info("Loaded game configuration")
        return config
```

### Step 3: Use in Game Logic

```python
def calculate_prestige_gain(
    specialist: Specialist,
    game_config: GameConfig
) -> int:
    """Calculate prestige gained from this specialist."""
    if specialist.level < game_config.social_features["prestige_unlock_level"]:
        return 0
    
    return int(specialist.level * game_config.social_features["prestige_multiplier"])
```

### Step 4: Test

```python
def test_prestige_multiplier_from_config():
    """Verify prestige multiplier uses config value."""
    config = create_test_config()
    config.social_features["prestige_multiplier"] = 2.5
    specialist = create_specialist(level=20)
    
    prestige = calculate_prestige_gain(specialist, config)
    
    assert prestige == 50, f"Expected 50, got {prestige}"
```

---

## DEBUGGING CHECKLIST

When something isn't working:

- [ ] Check logs: `tail -50 logs/game.log`
- [ ] Verify JSON: `python -m json.tool data/game_config.json`
- [ ] Test function directly: `pytest tests/test_*.py -v`
- [ ] Check backend state: `curl http://localhost:5000/game/state | jq`
- [ ] Review recent changes: `git diff`
- [ ] Verify type hints: `mypy src/`
- [ ] Run full test suite: `pytest tests/`

---

## COMMIT CHECKLIST

Before committing ANY changes:

1. [ ] Read ABSOLUTE_STANDARDS.md 15-point gate
2. [ ] All functions have type hints
3. [ ] All public functions have docstrings
4. [ ] All public functions have tests (>80% coverage)
5. [ ] No hardcoded values (use JSON config)
6. [ ] No duplicate code (DRY principle)
7. [ ] Errors are explicit and logged
8. [ ] Tests pass: `pytest tests/`
9. [ ] No commented-out code or debug prints
10. [ ] Code is self-documenting and clear
11. [ ] Git diff shows intent clearly
12. [ ] Commit message explains WHAT and WHY
13. [ ] JSON changes are valid: `python -m json.tool`
14. [ ] No anti-patterns from [code-style.instructions.md](code-style.instructions.md)
15. [ ] Changes follow [code-style.instructions.md](code-style.instructions.md) conventions

**If ANY item fails, keep working. Don't commit.**

---

## See Also

- **[copilot-instructions.md](../copilot-instructions.md)** - Main instructions and overview
- **[core-standards.instructions.md](core-standards.instructions.md)** - Absolute standards
- **[code-style.instructions.md](code-style.instructions.md)** - Code style and anti-patterns
- **[architecture.instructions.md](architecture.instructions.md)** - Project structure
- **[testing.instructions.md](testing.instructions.md)** - Testing requirements
- **[plugin-system.instructions.md](plugin-system.instructions.md)** - Plugin architecture
- **[data-driven.instructions.md](data-driven.instructions.md)** - JSON configuration
