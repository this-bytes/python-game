---
applies_to:
  - "tests/**/*.py"
  - "src/**/*.py"
---

# Testing Standards - Instructions

**This file contains comprehensive testing requirements and patterns.**

Reference this when:
- Writing new tests
- Understanding test organization
- Implementing test fixtures
- Achieving coverage requirements

---

## ABSOLUTE TESTING MANDATE

**EVERY PUBLIC FUNCTION MUST HAVE TESTS. PERIOD. NO EXCEPTIONS.**

This is non-negotiable. Not "when you get time". **Before you commit.**

If a function is public (not prefixed with `_`), it needs unit tests proving it works.

---

## Testing Requirements

- **Minimum 80% coverage** for new code
- **75% acceptable** for legacy code
- **One test file per class/system**
- Test naming: `test_<subject>_<action>_<expected_outcome>`
- Comprehensive edge case coverage

---

## Test Organization

```
/tests/
  test_specialist.py              → Unit tests for Specialist class
  test_incident.py                → Unit tests for Incident class
  test_assignment_system.py       → Integration tests for assignment flow
  test_progression_system.py      → Integration tests for XP/leveling
  test_burnout_plugin.py          → Tests for BurnoutPlugin
  conftest.py                     → Shared fixtures
  __init__.py                     → Empty marker
```

**Rule**: Each file tests ONE class or system. Don't mix concerns.

---

## Test Naming Conventions

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

## Test Structure - THE GOLD STANDARD

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

## Shared Fixtures (`conftest.py`)

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

## Plugin Testing Pattern

```python
import pytest
from src.core.plugins.my_plugin import MyPlugin
from src.models.game_state import GameState

class TestMyPlugin:
    """Test suite for MyPlugin."""

    @pytest.fixture
    def plugin(self):
        """Create plugin instance."""
        return MyPlugin()

    @pytest.fixture
    def game_state(self):
        """Create test game state."""
        return GameState()

    def test_initialization(self, plugin, game_state):
        """Test plugin initializes correctly."""
        plugin.initialize(game_state)
        assert plugin.get_name() == "MyPlugin"
        assert plugin.get_feature_id() == "my_feature"

    def test_event_subscription(self, plugin, game_state):
        """Test plugin subscribes to events."""
        plugin.initialize(game_state)
        # Verify subscriptions created
        assert len(plugin._subscription_ids) > 0

    def test_event_handling(self, plugin, game_state):
        """Test plugin handles events correctly."""
        plugin.initialize(game_state)
        
        # Trigger event
        from src.core.event_bus import get_event_bus
        event_bus = get_event_bus()
        event_bus.publish("test_event", {"data": "value"})
        
        # Verify plugin processed event
        # ...

    def test_state_persistence(self, plugin, game_state):
        """Test plugin saves and loads state correctly."""
        plugin.initialize(game_state)
        
        # Modify plugin state
        # ...
        
        # Save state
        state_data = plugin.save_state(game_state)
        assert "plugin_data" in state_data
        
        # Create new plugin and load state
        new_plugin = MyPlugin()
        new_plugin.initialize(game_state)
        new_plugin.load_state(game_state, state_data)
        
        # Verify state restored
        # ...

    def test_shutdown_cleanup(self, plugin, game_state):
        """Test plugin cleans up resources on shutdown."""
        plugin.initialize(game_state)
        
        # Shutdown
        plugin.shutdown(game_state)
        
        # Verify cleanup
        assert len(plugin._subscription_ids) == 0
```

---

## Edge Cases - ALWAYS TEST THESE

Every system needs edge case tests:

```python
# Boundary testing
def test_xp_calculation_at_level_cap():
    """Test XP calculation when specialist at maximum level."""
    specialist = create_specialist(level=20)
    assert specialist.can_gain_xp() is False

# Empty state testing
def test_incident_generator_with_no_clients():
    """Test incident generation when no clients exist."""
    generator = IncidentGenerator([])
    incidents = generator.generate_incidents(elapsed_seconds=60)
    assert len(incidents) == 0

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

## Parametrized Testing

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

---

## Exception Testing

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

## Test Coverage Commands

```bash
# Run tests with coverage report
pytest --cov=src --cov-report=term-missing tests/

# Generate HTML coverage report
pytest --cov=src --cov-report=html tests/
# Open htmlcov/index.html in browser

# Run specific test file
pytest tests/test_specialist.py -v

# Run specific test
pytest tests/test_specialist.py::TestSpecialist::test_gain_xp -v
```

---

## Testing Workflow

1. **Write test first** (optional but recommended - TDD)
2. **Implement function** to pass test
3. **Run full test suite** before commit: `pytest tests/`
4. **Check coverage**: `pytest --cov=src tests/`
5. **Verify all tests pass**: 100% passing before committing

---

## Pre-Commit Testing Checklist

Before every commit:

- [ ] All new functions have tests
- [ ] All tests passing (pytest tests/)
- [ ] Coverage >80% on new code (pytest --cov=src tests/)
- [ ] Edge cases tested
- [ ] Exception handling tested
- [ ] Integration tests added if needed
- [ ] No skipped tests without justification
- [ ] Test names are descriptive
- [ ] Fixtures used for common setup

---

## See Also

- [core-standards.instructions.md](../instructions/core-standards.instructions.md) - Core testing mandate
- [code-style.instructions.md](../instructions/code-style.instructions.md) - Code style for tests
- [ARCHITECTURE.md](../instructions/architeture.instructions.md) - System architecture
- [copilot-instructions.md](../copilot-instructions.md) - Main instructions
