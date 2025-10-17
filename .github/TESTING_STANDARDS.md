# TESTING STANDARDS

Reference: See [ABSOLUTE_STANDARDS.md](ABSOLUTE_STANDARDS.md) for core standards.

---

## ABSOLUTE TESTING MANDATE

**EVERY PUBLIC FUNCTION MUST HAVE TESTS. PERIOD. NO EXCEPTIONS.**

This is non-negotiable. Not "when you get time". **Before you commit.**

If a function is public (not prefixed with `_`), it needs unit tests proving it works.

---

## TESTING ORGANIZATION

```
/tests/
  test_specialist.py              → Unit tests for Specialist class
  test_incident.py                → Unit tests for Incident class
  test_assignment_system.py       → Integration tests for assignment flow
  test_progression_system.py      → Integration tests for XP/leveling
  test_client_manager.py          → Tests for client management
  test_incident_generator.py      → Tests for incident generation
  test_api.py                     → API endpoint tests
  conftest.py                     → Shared fixtures
  __init__.py                     → Empty marker
```

**Rule**: Each file tests ONE class or system. Don't mix concerns.

---

## TEST NAMING CONVENTIONS

Test names describe EXACTLY what is being tested:

```python
# ✅ CRYSTAL CLEAR - Anyone knows what this tests
def test_specialist_gains_xp_on_incident_completion():
    """Test that specialist XP increases when incident resolved."""
    ...

def test_assignment_fails_when_specialty_mismatch():
    """Test that specialist cannot be assigned to wrong specialty incident."""
    ...

def test_burnout_exceeding_80_percent_triggers_performance_penalty():
    """Test that performance degrades when burnout threshold exceeded."""
    ...

# ❌ REJECTED - What the hell is this testing?
def test_specialist():
    """Test specialist."""
    ...

def test_assignment():
    """Test assignment."""
    ...
```

**Pattern**: `test_<subject>_<action>_<expected_outcome>`

---

## TEST STRUCTURE - THE GOLD STANDARD

Every test follows this pattern:

```python
def test_specialist_gains_xp_on_incident_completion():
    """Verify specialist XP increases when incident resolved.
    
    Incident completion triggers XP award based on difficulty and specialist level.
    This test proves that reward is calculated and applied correctly.
    """
    # ===== SETUP =====
    # Create test data
    specialist = create_test_specialist(level=5, xp=0)
    incident = create_test_incident(difficulty=3, base_xp=100)
    game_config = create_test_config()
    
    # ===== EXECUTE =====
    # Perform the action being tested
    specialist.complete_incident(incident, game_config)
    
    # ===== VERIFY =====
    # Assert the outcome
    expected_xp = calculate_expected_xp(100, 3, 5, game_config)
    assert specialist.xp == expected_xp, \
        f"Expected {expected_xp} XP, got {specialist.xp}"
```

**Key principles:**
- Clear docstring explaining what and why
- SETUP: Create isolated test data
- EXECUTE: Perform ONE action
- VERIFY: Assert specific outcome
- Assertion includes helpful error message

---

## SHARED FIXTURES (`conftest.py`)

```python
import pytest
from src.models.specialist import Specialist
from src.models.incident import Incident
from src.core.config import GameConfig

@pytest.fixture
def game_config() -> GameConfig:
    """Provide test game configuration.
    
    Returns standard config for testing. Isolated from production data.
    """
    return GameConfig(
        starting_specialists=2,
        starting_money=5000,
        xp_base=100,
        xp_exponent=1.5,
        level_cap=20
    )

@pytest.fixture
def specialist() -> Specialist:
    """Provide test specialist.
    
    Standard specialist for most tests. Override in specific tests if needed.
    """
    return Specialist(
        id="test_specialist_001",
        name="Test Specialist",
        specialty="Network Security",
        level=1,
        xp=0
    )

@pytest.fixture
def incident() -> Incident:
    """Provide test incident.
    
    Standard incident for most tests. Override if specialty/difficulty changes needed.
    """
    return Incident(
        id="test_incident_001",
        name="Test DDoS Attack",
        specialty_required="Network Security",
        difficulty=2,
        base_sla_seconds=300,
        base_reward=500,
        xp_reward=100
    )

# Helper factories for custom test data
def create_specialist(**kwargs) -> Specialist:
    """Create specialist with overrides.
    
    Usage:
        specialist = create_specialist(level=10, specialty="Cryptography")
    """
    defaults = {
        "id": kwargs.get("id", "test_specialist_001"),
        "name": kwargs.get("name", "Test Specialist"),
        "specialty": kwargs.get("specialty", "Network Security"),
        "level": kwargs.get("level", 1),
        "xp": kwargs.get("xp", 0)
    }
    defaults.update(kwargs)
    return Specialist(**defaults)

def create_incident(**kwargs) -> Incident:
    """Create incident with overrides.
    
    Usage:
        incident = create_incident(difficulty=5, specialty_required="Cryptography")
    """
    defaults = {
        "id": kwargs.get("id", "test_incident_001"),
        "name": kwargs.get("name", "Test Incident"),
        "specialty_required": kwargs.get("specialty_required", "Network Security"),
        "difficulty": kwargs.get("difficulty", 2),
        "base_sla_seconds": kwargs.get("base_sla_seconds", 300),
        "base_reward": kwargs.get("base_reward", 500),
        "xp_reward": kwargs.get("xp_reward", 100)
    }
    defaults.update(kwargs)
    return Incident(**defaults)
```

---

## UNIT TEST EXAMPLES

### Example 1: Testing XP Calculation

```python
def test_calculate_xp_gain_applies_difficulty_multiplier():
    """Verify XP multiplier increases with incident difficulty."""
    game_config = create_test_config()
    specialist = create_specialist(level=5)
    
    xp_difficulty_1 = specialist.calculate_xp_gain(100, difficulty=1, game_config=game_config)
    xp_difficulty_5 = specialist.calculate_xp_gain(100, difficulty=5, game_config=game_config)
    
    # Higher difficulty should give more XP
    assert xp_difficulty_5 > xp_difficulty_1, \
        f"Difficulty 5 ({xp_difficulty_5}) should > Difficulty 1 ({xp_difficulty_1})"

def test_calculate_xp_gain_never_negative():
    """Verify XP calculation never returns negative value."""
    game_config = create_test_config()
    
    for difficulty in range(1, 6):
        for level in range(1, 21):
            specialist = create_specialist(level=level)
            xp = specialist.calculate_xp_gain(100, difficulty, game_config)
            assert xp >= 0, f"XP cannot be negative: {xp}"

def test_calculate_xp_gain_scales_with_specialist_level():
    """Verify specialist level affects XP calculation."""
    game_config = create_test_config()
    
    xp_level_1 = create_specialist(level=1).calculate_xp_gain(100, 2, game_config)
    xp_level_10 = create_specialist(level=10).calculate_xp_gain(100, 2, game_config)
    xp_level_20 = create_specialist(level=20).calculate_xp_gain(100, 2, game_config)
    
    # Higher level should get more XP (applies bonus multiplier)
    assert xp_level_1 <= xp_level_10 <= xp_level_20, \
        f"XP scaling broken: L1={xp_level_1}, L10={xp_level_10}, L20={xp_level_20}"
```

### Example 2: Testing Assignment Logic

```python
def test_assignment_fails_when_specialty_mismatch():
    """Verify specialist cannot be assigned to wrong specialty incident."""
    specialist = create_specialist(specialty="Network Security")
    incident = create_incident(specialty_required="Cryptography")
    
    result = specialist.assign_to_incident(incident)
    
    assert result is False, "Assignment should fail on specialty mismatch"
    assert specialist.current_incident is None, "Incident should not be assigned"

def test_assignment_succeeds_with_specialty_match():
    """Verify specialist assigned when specialty matches."""
    specialist = create_specialist(specialty="Network Security")
    incident = create_incident(specialty_required="Network Security")
    
    result = specialist.assign_to_incident(incident)
    
    assert result is True, "Assignment should succeed on specialty match"
    assert specialist.current_incident == incident, "Incident should be assigned"

def test_assignment_fails_when_specialist_already_busy():
    """Verify specialist cannot be assigned to multiple incidents."""
    specialist = create_specialist()
    incident_1 = create_incident()
    incident_2 = create_incident()
    
    # Assign first incident
    specialist.assign_to_incident(incident_1)
    
    # Try to assign second incident
    result = specialist.assign_to_incident(incident_2)
    
    assert result is False, "Assignment should fail when specialist busy"
    assert specialist.current_incident == incident_1, "Should still have first incident"

def test_assignment_fails_when_specialist_underleveled():
    """Verify specialist cannot be assigned if level too low."""
    specialist = create_specialist(level=1)
    incident = create_incident(min_level_required=5)
    
    result = specialist.assign_to_incident(incident)
    
    assert result is False, "Assignment should fail on level requirement"
```

### Example 3: Testing Burnout Mechanic

```python
def test_burnout_accumulates_on_incident_assignment():
    """Verify specialist burnout increases when assigned to incident."""
    specialist = create_specialist(burnout=0)
    incident = create_incident()
    game_config = create_test_config(specialist_burnout_rate=5)
    
    specialist.assign_to_incident(incident)
    specialist.tick(elapsed_seconds=1, game_config=game_config)
    
    assert specialist.burnout == 5, "Burnout should increase by 5"

def test_burnout_exceeding_80_triggers_penalties():
    """Verify performance degrades when burnout >80%."""
    specialist = create_specialist(burnout=85, base_speed=100)
    
    multiplier = specialist.get_performance_multiplier()
    
    assert multiplier < 1.0, "Performance should be penalized"
    assert multiplier == 0.9, "Expected 10% speed penalty at 85% burnout"

def test_burnout_never_exceeds_100():
    """Verify burnout is capped at 100%."""
    specialist = create_specialist(burnout=95)
    incident_1 = create_incident()
    incident_2 = create_incident()
    incident_3 = create_incident()
    game_config = create_test_config(specialist_burnout_rate=10)
    
    specialist.assign_to_incident(incident_1)
    specialist.tick(elapsed_seconds=1, game_config=game_config)
    specialist.assign_to_incident(incident_2)
    specialist.tick(elapsed_seconds=1, game_config=game_config)
    specialist.assign_to_incident(incident_3)
    specialist.tick(elapsed_seconds=1, game_config=game_config)
    
    assert specialist.burnout == 100, "Burnout should be capped at 100%"

def test_rest_day_resets_burnout_to_zero():
    """Verify rest day action fully recovers specialist."""
    specialist = create_specialist(burnout=95)
    
    specialist.take_rest_day()
    
    assert specialist.burnout == 0, "Burnout should be fully reset after rest day"
```

---

## EDGE CASES - ALWAYS TEST THESE

Every system needs edge case tests:

```python
# Boundary testing
def test_xp_calculation_at_level_cap():
    """Test XP calculation when specialist at maximum level."""
    specialist = create_specialist(level=20)
    assert specialist.can_gain_xp() is False

def test_incident_assignment_with_zero_specialists():
    """Test assignment system when no specialists available."""
    assignment_system = AssignmentSystem([])
    incident = create_incident()
    
    result = assignment_system.find_assignment(incident)
    
    assert result is None, "Should return None when no specialists available"

# Empty state testing
def test_incident_generator_with_no_clients():
    """Test incident generation when no clients exist."""
    generator = IncidentGenerator([])
    incidents = generator.generate_incidents(elapsed_seconds=60)
    
    assert len(incidents) == 0, "Should generate no incidents without clients"

# Extreme value testing
def test_specialist_level_cap_enforcement():
    """Test that specialist level cannot exceed configured cap."""
    specialist = create_specialist(level=19)
    game_config = create_test_config(level_cap=20)
    
    specialist.level_up(game_config)
    assert specialist.level == 20
    
    specialist.level_up(game_config)
    assert specialist.level == 20, "Level should not exceed cap"

# Concurrent operation testing
def test_multiple_assignments_to_same_specialist_fail():
    """Test that concurrent assignments are rejected."""
    specialist = create_specialist()
    incident_1 = create_incident()
    incident_2 = create_incident()
    
    result_1 = specialist.assign_to_incident(incident_1)
    result_2 = specialist.assign_to_incident(incident_2)
    
    assert result_1 is True
    assert result_2 is False, "Second assignment should fail"
```

---

## INTEGRATION TESTS

Integration tests verify systems work together:

```python
def test_complete_incident_resolution_flow():
    """Test complete flow: assign → resolve → reward."""
    # Setup
    specialist = create_specialist(level=5, xp=0)
    incident = create_incident(difficulty=3, xp_reward=100)
    game_config = create_test_config()
    
    # Assign incident
    assigned = specialist.assign_to_incident(incident)
    assert assigned is True
    
    # Simulate resolution
    specialist.complete_incident(incident, game_config)
    
    # Verify rewards
    expected_xp = 150  # 100 base * 1.5 difficulty multiplier
    assert specialist.xp >= expected_xp, f"Expected at least {expected_xp} XP"
    assert specialist.current_incident is None, "Should no longer have incident"

def test_specialist_levelup_unlocks_automation():
    """Test that leveling up unlocks automation scripts."""
    specialist = create_specialist(level=4)
    game_config = create_test_config(automation_unlock_level=5)
    
    # Before level 5
    assert len(specialist.available_automations) == 0
    
    # Reach level 5
    specialist.level = 5
    automation_check = specialist.get_available_automations(game_config)
    
    # After level 5
    assert len(automation_check) > 0, "Should unlock automation at level 5"
```

---

## TEST COVERAGE REQUIREMENTS

- **Minimum coverage**: 80% for new code, 75% acceptable for legacy
- **Uncovered code is untested code**: If it's not in coverage report, write a test
- **Coverage command**: `pytest --cov=src --cov-report=html`

```bash
# Run tests with coverage report
pytest --cov=src --cov-report=term-missing tests/

# Generate HTML coverage report
pytest --cov=src --cov-report=html tests/
# Open htmlcov/index.html in browser
```

---

## TESTING WORKFLOW

1. **Write test first** (optional but recommended)
2. **Implement function** to pass test
3. **Run full test suite** before commit: `pytest tests/`
4. **Check coverage**: `pytest --cov=src tests/`
5. **Verify all tests pass**: 100% passing before committing

---

## COMMON TEST PATTERNS

### Parametrized Testing

```python
@pytest.mark.parametrize("difficulty,expected_xp_multiplier", [
    (1, 1.0),
    (2, 1.1),
    (3, 1.2),
    (4, 1.35),
    (5, 1.5),
])
def test_xp_multiplier_by_difficulty(difficulty, expected_xp_multiplier):
    """Verify XP multiplier for each difficulty level."""
    specialist = create_specialist()
    actual = specialist.get_xp_multiplier(difficulty)
    assert actual == expected_xp_multiplier
```

### Fixture Scopes

```python
@pytest.fixture(scope="function")  # New for each test
def fresh_specialist():
    return create_specialist()

@pytest.fixture(scope="module")  # Shared across all tests in module
def database():
    db = Database()
    db.connect()
    yield db
    db.close()
```

### Exception Testing

```python
def test_assignment_raises_on_specialty_mismatch():
    """Verify specific exception raised on specialty mismatch."""
    specialist = create_specialist(specialty="Network Security")
    incident = create_incident(specialty_required="Cryptography")
    
    with pytest.raises(SpecialtyMismatchError) as exc_info:
        specialist.assign_to_incident(incident)
    
    assert "Cryptography" in str(exc_info.value)
```

---

## See Also

- [ABSOLUTE_STANDARDS.md](ABSOLUTE_STANDARDS.md) - Core standards
- [ARCHITECTURE.md](ARCHITECTURE.md) - Project structure and patterns
- [ANTI_PATTERNS.md](ANTI_PATTERNS.md) - Anti-patterns to avoid
