# Cybersecurity Firm Idle/Tycoon/RPG Game - Copilot Instructions

## Project Overview

This is a Python-based idle/tycoon/RPG game where players manage a startup cybersecurity firm. The game blends three core mechanics:

1. **Idle Mechanics**: Continuous generation of security incidents requiring triage
2. **Tycoon Mechanics**: Resource allocation, profit optimization, and business growth
3. **RPG Mechanics**: Specialist leveling, XP progression, and skill unlocks

## Core Philosophy: "Vibe Coding"

This project prioritizes **iteration speed** and **rapid experimentation** over perfect architecture. Key principles:

- **JSON-first design**: ALL game parameters live in external JSON files
- **Pygame as renderer only**: Visual dashboard, NOT game logic container
- **Hot-reloadable**: Change game balance without restarting
- **Backend-driven debugging**: Live manipulation via CRUD API
- **Human-readable data**: Easy manual editing of all configurations

## Architecture Rules

### Strict Separation of Concerns

```
/src/models/          → Pure game logic (Specialist, Incident, Client, etc.)
/src/core/            → Game systems (generation, assignment, resolution, progression)
/src/ui/              → Pygame rendering ONLY (no game logic)
/backend/             → Flask/FastAPI CRUD API for live debugging
/data/                → JSON configuration files (specialists, incidents, clients, automation)
```

**CRITICAL**: Never put game logic in Pygame rendering code. Rendering reads state; it doesn't create it.

### Data-Driven Everything

- Specialist stats? JSON.
- Incident difficulty curves? JSON.
- Client SLA timers? JSON.
- Automation unlock levels? JSON.
- XP progression curves? JSON.

If it affects gameplay, it's in a JSON file.

## JSON Schema Structure

### Specialists (`/data/specialists.json`)
```json
{
  "specialists": [
    {
      "id": "spec_001",
      "name": "Alice Chen",
      "specialty": "Network Security",
      "level": 5,
      "xp": 2340,
      "stats": {
        "speed": 85,
        "accuracy": 90,
        "experience_bonus": 1.2
      },
      "automation_scripts": ["auto_assign_network_low"],
      "status": "available"
    }
  ]
}
```

### Incidents (`/data/incidents.json`)
```json
{
  "incident_types": [
    {
      "id": "inc_type_001",
      "name": "DDoS Attack",
      "specialty_required": "Network Security",
      "difficulty_range": [1, 5],
      "base_sla_seconds": 300,
      "base_reward": 500,
      "xp_reward": 100
    }
  ]
}
```

### Clients (`/data/clients.json`)
```json
{
  "clients": [
    {
      "id": "client_001",
      "name": "TechCorp Inc.",
      "incident_rate_per_minute": 0.5,
      "sla_multiplier": 1.0,
      "reputation": 80,
      "contract_value": 10000
    }
  ]
}
```

### Automation Scripts (`/data/automation_scripts.json`)
```json
{
  "automation_scripts": [
    {
      "id": "auto_assign_network_low",
      "name": "Auto-Assign Network (Low Priority)",
      "required_level": 3,
      "specialty": "Network Security",
      "trigger_conditions": {
        "max_difficulty": 2,
        "specialty_match": true,
        "specialist_available": true
      },
      "effect": "auto_assign"
    }
  ]
}
```

### Game Config (`/data/game_config.json`)
```json
{
  "game_settings": {
    "starting_specialists": 2,
    "starting_money": 5000,
    "time_scale": 1.0,
    "max_active_incidents": 50
  },
  "xp_curve": {
    "base_xp": 100,
    "exponent": 1.5,
    "level_cap": 20
  },
  "economy": {
    "sla_failure_penalty_multiplier": 0.5,
    "perfect_completion_bonus": 1.2,
    "specialist_hiring_cost_base": 2000
  }
}
```

## Code Style & Conventions

### Naming Conventions

- **Classes**: PascalCase (`Specialist`, `IncidentGenerator`)
- **Functions/Methods**: snake_case (`assign_incident`, `calculate_xp_gain`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_SPECIALISTS`, `BASE_XP`)
- **JSON keys**: snake_case matching Python conventions
- **File names**: snake_case (`specialist.py`, `incident_queue_panel.py`)

### Type Hints

Always use type hints for function signatures:

```python
def assign_incident(specialist: Specialist, incident: Incident) -> bool:
    """Assign an incident to a specialist if compatible."""
    ...
```

### Docstrings

Use Google-style docstrings for all classes and public methods:

```python
def calculate_xp_gain(base_xp: int, difficulty: int, level: int) -> int:
    """Calculate XP gained for completing an incident.
    
    Args:
        base_xp: Base XP value from incident configuration
        difficulty: Incident difficulty (1-5)
        level: Current specialist level
        
    Returns:
        Final XP amount after all modifiers applied
    """
    ...
```

### Error Handling

- Validate ALL JSON data on load
- Fail fast with clear error messages
- Log errors comprehensively for debugging
- Gracefully degrade when backend server unavailable

## Game Logic Implementation Patterns

### Event-Driven Architecture

Use observer pattern for state changes:

```python
class GameState:
    def __init__(self):
        self._observers = []
    
    def register_observer(self, callback):
        self._observers.append(callback)
    
    def notify_observers(self, event_type, data):
        for observer in self._observers:
            observer(event_type, data)
```

### Factory Pattern for Entity Creation

```python
class SpecialistFactory:
    @staticmethod
    def create_from_json(specialist_data: dict) -> Specialist:
        """Create Specialist instance from JSON data."""
        return Specialist(
            id=specialist_data['id'],
            name=specialist_data['name'],
            specialty=specialist_data['specialty'],
            # ... etc
        )
```

### Strategy Pattern for Specialist Abilities

```python
class SpecialistAbility(ABC):
    @abstractmethod
    def apply(self, specialist: Specialist, incident: Incident) -> None:
        pass

class SpeedBoostAbility(SpecialistAbility):
    def apply(self, specialist: Specialist, incident: Incident) -> None:
        incident.time_remaining *= 1.2
```

## Pygame Rendering Guidelines

### Rendering Loop Structure

```python
def render(self, game_state: GameState):
    """Render game state to screen. NO GAME LOGIC HERE."""
    self.screen.fill(BACKGROUND_COLOR)
    
    # Read state, don't modify it
    self._render_incident_queue(game_state.incidents)
    self._render_specialist_roster(game_state.specialists)
    self._render_metrics(game_state.metrics)
    
    pygame.display.flip()
```

### Input Handling

```python
def handle_input(self, events: list[pygame.Event]) -> list[GameAction]:
    """Convert Pygame events to game actions. Return actions, don't execute them."""
    actions = []
    
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            action = self._mouse_to_action(event.pos)
            if action:
                actions.append(action)
    
    return actions  # Game loop executes these
```

## Backend API Conventions

### Endpoint Structure

```
GET    /specialists              → List all specialists
GET    /specialists/{id}         → Get specific specialist
PUT    /specialists/{id}         → Update specialist stats/level
POST   /specialists              → Create new specialist

POST   /incidents/spawn          → Manually spawn incident
GET    /incidents/active         → List currently active incidents

PUT    /clients/{id}             → Update client parameters
POST   /config/reload            → Hot-reload all JSON files

GET    /game/state               → Full game state snapshot (debugging)
```

### Response Format

```json
{
  "success": true,
  "data": { ... },
  "message": "Specialist updated successfully",
  "timestamp": "2025-10-16T14:30:00Z"
}
```

## Testing Standards

### Test Organization

```
/tests/
  test_specialist.py          → Unit tests for Specialist class
  test_incident.py            → Unit tests for Incident class
  test_assignment_system.py   → Integration tests for assignment logic
  test_api.py                 → API endpoint tests
  conftest.py                 → Shared fixtures
```

### Test Naming

```python
def test_specialist_gains_xp_on_incident_completion():
    """Test that specialist XP increases when incident resolved."""
    ...

def test_assignment_fails_when_specialty_mismatch():
    """Test that specialist cannot be assigned to wrong specialty incident."""
    ...
```

### Fixtures

```python
@pytest.fixture
def sample_specialist():
    """Provide a standard specialist for testing."""
    return Specialist(
        id="test_001",
        name="Test Specialist",
        specialty="Network Security",
        level=1,
        xp=0
    )
```

## Common Development Tasks

### Adding a New Specialist Type

1. Add entry to `/data/specialists.json`
2. No code changes needed (data-driven!)
3. Optionally add new specialty-specific automation scripts

### Creating a New Incident Type

1. Add entry to `/data/incidents.json` with new type definition
2. Ensure `specialty_required` matches existing specialist specialties
3. Configure difficulty range and SLA timers
4. Test spawn via backend API: `POST /incidents/spawn`

### Implementing a New Automation Script

1. Add definition to `/data/automation_scripts.json`
2. If custom logic needed beyond simple auto-assign, implement in `/src/core/automation_system.py`
3. Link to specialist via `automation_scripts` array at specific level threshold

### Balancing Game Economy

1. Start game normally
2. Open backend admin dashboard at `http://localhost:5000/admin`
3. Adjust client incident rates, specialist stats, SLA timers in real-time
4. Observe effects immediately without restart
5. Export working parameters back to JSON files

## Debugging Workflow

### Logging Levels

```python
logger.debug("Incident spawn check: rate=0.5, roll=0.32")  # Detailed flow
logger.info("Incident INC_042 assigned to SPEC_003")       # Key events
logger.warning("Specialist busy, assignment delayed")       # Recoverable issues
logger.error("JSON schema validation failed")              # Serious problems
```

### State Inspection

```python
# Via backend API
GET /game/state → Full snapshot for debugging

# Via logs
logger.info(f"GameState: {game_state.to_dict()}")
```

### Hot-Reload Testing

```bash
# Edit JSON file
vim /data/specialists.json

# Trigger reload via API
curl -X POST http://localhost:5000/config/reload

# Changes reflected immediately in running game
```

## Performance Guidelines

- Target 60 FPS for Pygame rendering
- Profile incident generation if >100 active incidents
- Use dirty rect updates for Pygame rendering optimization
- Cache frequently accessed JSON data in memory
- Log performance metrics in debug mode

## Deployment

### Local Development

```bash
# Terminal 1: Run game client
python src/main.py

# Terminal 2: Run backend server
cd backend && python app.py
```

### Configuration

- Backend port: 5000 (configurable in `.env`)
- Game window resolution: 1280x720 (configurable in `game_config.json`)
- Save game location: `/data/saves/`

## Questions to Ask When Implementing

1. **Can this parameter be JSON-driven?** → If yes, make it configurable
2. **Is this game logic or rendering?** → Game logic in `/src/core/`, rendering in `/src/ui/`
3. **Does this need to be tweaked for balance?** → Make it backend-modifiable
4. **Will this block the render loop?** → Move to background thread
5. **Can an automation script handle this?** → Consider data-driven automation system

## Reference Examples

### Complete Incident Resolution Flow

```python
# 1. Incident generated (core/incident_generator.py)
incident = IncidentGenerator.generate(client)

# 2. Player assigns specialist (ui/input_handler.py → core/assignment_system.py)
success = AssignmentSystem.assign(specialist, incident)

# 3. Resolution processed (core/resolution_system.py)
result = ResolutionSystem.resolve(incident)

# 4. Rewards distributed (core/progression_system.py)
ProgressionSystem.award_xp(specialist, result.xp)

# 5. UI updates (ui/renderer.py)
renderer.update_specialist_panel(specialist)
```

### Backend Testing Example

```bash
# Spawn urgent network incident
curl -X POST http://localhost:5000/incidents/spawn \
  -H "Content-Type: application/json" \
  -d '{
    "type": "DDoS Attack",
    "difficulty": 5,
    "client_id": "client_001"
  }'

# Boost specialist level for testing
curl -X PUT http://localhost:5000/specialists/spec_001 \
  -H "Content-Type: application/json" \
  -d '{"level": 10, "xp": 5000}'
```

## Anti-Patterns to AVOID

### ❌ Redundant Constants
**NEVER** create variables named exactly the same as the string they contain:

```python
# ❌ BAD - redundant and dumb
INCIDENT_GENERATED = "incident_generated"
INCIDENT_ASSIGNED = "incident_assigned"

# ✅ GOOD - just use the string directly
"incident_generated"
"incident_assigned"
```

**Why it's dumb:** You're literally writing the same thing twice. The variable name IS the value. This is cargo cult programming and wastes time.

**When to use constants:**
- When the value is NOT obvious from the name (e.g., `MAX_SPECIALISTS = 10`)
- When the value might change (e.g., `API_TIMEOUT_SECONDS = 30`)
- When you need type safety or IDE autocomplete

**When to use strings directly:**
- Event types (e.g., `event_bus.publish("incident_resolved", data)`)
- Dictionary keys that match the key name exactly
- Any case where the constant adds NO value

### Continuous Improvement
If you find me making dumb coding patterns like the one above:
1. **Point it out immediately**
2. **I will add it to this anti-patterns section**
3. **I will fix the code everywhere it appears**
4. **I will learn and never repeat it**

This section grows as we discover and eliminate bad patterns.

## Final Reminders

- **NO hardcoded game values** - always use JSON configuration
- **NO redundant constants** - if the name equals the value, just use the value
- **Pygame renders, doesn't think** - keep it dumb and fast
- **Backend is your debugging superpower** - use it liberally
- **Iterate fast, polish later** - vibe coding philosophy
- **When in doubt, make it configurable** - JSON-first approach

Happy coding! 🚀🔒
