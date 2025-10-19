---
applies_to:
  - "**/*"
---

# Workflows - Instructions

**This file contains step-by-step guides for common development tasks.**

Reference this when:
- Adding new game features
- Implementing new systems
- Following established workflows
- Understanding task sequences

---

## BEFORE YOU START ANY TASK

1. Read [core-standards.instructions.md](core-standards.instructions.md) - specifically the 15-point gate
2. Identify where your code fits: models, core, ui, backend, or data?
3. Understand: **If it's game logic, it goes in `/src/models/` or `/src/core/`, NEVER in UI**
4. Remember: **All game parameters must be in JSON config, not hardcoded**
5. Type hints and tests: **Non-negotiable before committing**

---

## TASK 1: ADD A NEW SPECIALIST TYPE

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
