# CODE STYLE & CONVENTIONS

Reference: See [ABSOLUTE_STANDARDS.md](ABSOLUTE_STANDARDS.md) for the core standards.

---

## NAMING CONVENTIONS

- **Classes**: `PascalCase` → `Specialist`, `IncidentGenerator`, `GameState`
- **Functions/Methods**: `snake_case` → `assign_incident`, `calculate_xp_gain`, `resolve_incident_with_specialist`
- **Constants**: `UPPER_SNAKE_CASE` → `MAX_SPECIALISTS`, `BASE_XP`, `DEFAULT_TIMEOUT`
- **JSON keys**: `snake_case` → `incident_rate_per_minute`, `specialist_xp_multiplier`
- **Files**: `snake_case` → `specialist.py`, `incident_queue_panel.py`, `assignment_system.py`

**Rule**: Names must be crystal clear. No abbreviations unless universal. No single-letter variables (except loop counters).

---

## TYPE HINTS (MANDATORY)

Every function parameter and return value must be typed.

```python
# ❌ WRONG
def assign_incident(specialist, incident):
    return specialist.assign(incident)

# ✅ CORRECT
def assign_incident(
    specialist: Specialist,
    incident: Incident
) -> AssignmentResult:
    """Assign incident to specialist if compatible."""
    return specialist.assign(incident)
```

**Use:**
- Union types: `int | str` or `Optional[Incident]`
- List types: `list[Incident]` not `List[Incident]`
- Dict types: `dict[str, float]` not `Dict[str, float]`

---

## DOCSTRINGS (MANDATORY for Public Functions)

Use Google-style docstrings. Explain PURPOSE and INTENT, not just what the code does.

```python
def calculate_sla_multiplier(
    client: Client,
    current_time_seconds: float,
    game_config: GameConfig
) -> float:
    """Calculate SLA multiplier for incident resolution time penalty.
    
    As SLA deadline approaches, resolution multiplier decreases to create
    pressure. This encourages efficient incident triage and assignment.
    
    At 75%+ SLA elapsed: 20% slower (0.8x)
    At 50-75% SLA elapsed: 10% slower (0.9x)
    Below 50% SLA elapsed: No penalty (1.0x)
    
    Args:
        client: Client with SLA deadline
        current_time_seconds: Time elapsed since incident created
        game_config: Game configuration with SLA thresholds
        
    Returns:
        Multiplier to apply to specialist resolution time
        
    Raises:
        ValueError: current_time_seconds is negative
    """
    if current_time_seconds < 0:
        raise ValueError("current_time_seconds cannot be negative")
    
    sla_seconds = client.sla_seconds
    sla_percent = current_time_seconds / sla_seconds
    
    if sla_percent >= 0.75:
        return game_config.sla_critical_multiplier  # 0.8
    elif sla_percent >= 0.5:
        return game_config.sla_warning_multiplier   # 0.9
    return 1.0  # No penalty
```

**Format:**
- One-line summary (PURPOSE)
- Blank line
- Detailed explanation (WHY it matters)
- Blank line
- Args: (type and description)
- Returns: (type and description)
- Raises: (specific exceptions)

---

## ERROR HANDLING (MANDATORY)

NEVER catch generic `Exception`. Be SPECIFIC about what you're catching.

```python
# ❌ WRONG - Silent failure
try:
    specialist = load_specialist(specialist_id)
except:
    pass

# ❌ WRONG - Generic catch
try:
    specialist = load_specialist(specialist_id)
except Exception:
    specialist = None

# ✅ CORRECT - Specific exceptions with logging
try:
    specialist = load_specialist(specialist_id)
except SpecialistNotFoundError as e:
    logger.error(f"Specialist {specialist_id} not found: {e}")
    raise  # Re-raise so caller handles
except SpecialistLoadError as e:
    logger.error(f"Failed to load specialist {specialist_id}: {e}")
    return get_default_specialist()  # Graceful degradation
```

**Rules:**
- Catch specific exceptions, not `Exception`
- Log the error with context
- Either re-raise or provide graceful fallback
- Never silently swallow errors

---

## LOGGING LEVELS

Use appropriate logging levels for different situations:

```python
logger.debug("Checking specialist availability: specialist_id={}, status={}, time={}".format(
    specialist.id, specialist.status, time.time()
))

logger.info(f"Incident {incident.id} assigned to {specialist.name} with {synergy}x synergy")

logger.warning(f"Specialist {specialist.name} burnout at 85%, performance degraded")

logger.error(f"Failed to resolve incident {incident.id}: {error_message}")
```

**Levels:**
- `debug`: Detailed flow information (variables, conditions, loops)
- `info`: Key events (incident created, specialist assigned, contract completed)
- `warning`: Recoverable issues (specialist busy, low on resources)
- `error`: Serious problems (JSON validation failed, specialist not found)

---

## CONSTANTS vs MAGIC NUMBERS

**Rule**: If a number appears in code, it must be justified or in JSON config.

```python
# ❌ WRONG - Where does this come from?
if specialist.burnout > 80:
    performance_multiplier = 0.9
if damage > 500:
    penalty = damage * 0.42

# ✅ CORRECT - Named constants with justification
SPECIALIST_BURNOUT_PENALTY_THRESHOLD = 80  # At 80%+, specialist performance degrades
SPECIALIST_BURNOUT_PERFORMANCE_MULTIPLIER = 0.9  # 10% slowdown

INCIDENT_DAMAGE_CRITICAL_THRESHOLD = 500  # High-severity threshold (from game_config)
INCIDENT_DAMAGE_PENALTY_MULTIPLIER = 0.42  # Financial penalty rate (from game_config)

if specialist.burnout > SPECIALIST_BURNOUT_PENALTY_THRESHOLD:
    performance_multiplier = SPECIALIST_BURNOUT_PERFORMANCE_MULTIPLIER
if damage > INCIDENT_DAMAGE_CRITICAL_THRESHOLD:
    penalty = damage * INCIDENT_DAMAGE_PENALTY_MULTIPLIER
```

**Better: Use JSON config instead of constants**

```python
# In data/game_config.json:
{
  "specialist": {
    "burnout_penalty_threshold": 80,
    "burnout_performance_multiplier": 0.9
  },
  "incident": {
    "damage_critical_threshold": 500,
    "damage_penalty_multiplier": 0.42
  }
}

# In Python:
if specialist.burnout > game_config.specialist.burnout_penalty_threshold:
    performance_multiplier = game_config.specialist.burnout_performance_multiplier
```

---

## COMMENTS (Explain WHY, not WHAT)

Code shows WHAT happens. Comments explain WHY it matters.

```python
# ❌ WRONG - Stating the obvious
x = 5  # Set x to 5
for i in range(10):  # Loop 10 times
    result.append(x)  # Append x to result

# ❌ WRONG - Comments that duplicate code
if specialist.level >= 5:  # Check if level >= 5
    specialist.unlock_automation()  # Unlock automation

# ✅ CORRECT - Comments explain the WHY
specialist_level_threshold = 5  # At level 5, specialists unlock advanced automation

# Synergy bonus encourages strategic team composition
if specialist.specialty == incident.specialty_required:
    resolution_multiplier = game_config.synergy_bonus_multiplier

# Each experience tier represents exponential skill growth
for level_tier in range(10):
    efficiency_scaling = 1.0 + (level_tier * 0.1)
    efficiency_values.append(base_efficiency * efficiency_scaling)
```

**Rule**: Delete comments that just repeat code. Write comments that explain business logic and design decisions.

---

## VARIABLE NAMING (Crystal Clear)

Variables should tell the story. No abbreviations, no confusion.

```python
# ❌ WRONG - Generic and unclear
data = incident['data']
obj = create_specialist(data)
tmp = calculate_xp(obj, data)
x = apply_bonus(tmp)

# ✅ CORRECT - Crystal clear intent
pending_incident_data = incident_queue.pop()
newly_assigned_specialist = create_specialist(pending_incident_data)
xp_earned_with_modifiers = calculate_xp_gained(
    newly_assigned_specialist,
    pending_incident_data
)
final_reward_multiplier = apply_synergy_and_difficulty_bonus(xp_earned_with_modifiers)
```

**Rules:**
- No single-letter variables (except loop counters: `i`, `j`)
- No abbreviations (unless universal: `id`, `url`)
- Boolean variables start with `is_`, `has_`, `should_`: `is_available`, `has_certification`, `should_rest`
- Collection variables are plural: `specialists`, `incidents`, `active_incidents`
- Duration variables end with `_seconds` or `_minutes`: `sla_remaining_seconds`, `cooldown_minutes`

---

## FUNCTION LENGTH

Keep functions small. If a function is >30 lines, split it.

```python
# ❌ WRONG - Does too much
def handle_incident_completion(incident_id):
    incident = get_incident(incident_id)
    specialist = get_specialist(incident.assigned_to)
    
    # Calculate rewards
    base_reward = incident.base_reward
    time_penalty = calculate_sla_penalty(incident, specialist)
    quality_bonus = calculate_quality_bonus(incident, specialist)
    final_reward = base_reward * time_penalty * quality_bonus
    
    # Award specialist
    specialist.xp += final_reward
    specialist.money += final_reward / 10
    
    # Update metrics
    specialist.incidents_completed += 1
    specialist.average_resolution_time = calculate_average(specialist)
    
    # Notify UI
    update_ui()
    send_notification()
    
    return final_reward

# ✅ CORRECT - Focused, small functions
def calculate_incident_reward(
    incident: Incident,
    specialist: Specialist,
    game_config: GameConfig
) -> float:
    """Calculate total reward for completing incident."""
    base_reward = incident.base_reward
    time_penalty = calculate_sla_penalty(incident, game_config)
    quality_bonus = calculate_quality_bonus(incident, specialist)
    return base_reward * time_penalty * quality_bonus

def award_specialist_for_completion(
    specialist: Specialist,
    incident: Incident,
    reward: float
) -> None:
    """Award specialist XP and money for incident completion."""
    specialist.xp += reward
    specialist.money += reward / 10
    specialist.incidents_completed += 1

def complete_incident(
    incident: Incident,
    specialist: Specialist,
    game_config: GameConfig
) -> float:
    """Complete incident: calculate rewards, award specialist, update metrics."""
    reward = calculate_incident_reward(incident, specialist, game_config)
    award_specialist_for_completion(specialist, incident, reward)
    return reward
```

---

## RETURN TYPE CONSISTENCY

Never mix return types. Be explicit about what you return.

```python
# ❌ WRONG - Inconsistent returns
def find_specialist_by_id(specialist_id: str):
    if specialist_id in cache:
        return cache[specialist_id]  # Specialist object
    elif db.has(specialist_id):
        return db.query(specialist_id)  # Specialist object
    return None  # Different type

# ✅ CORRECT - Always same type
def find_specialist_by_id(specialist_id: str) -> Specialist | None:
    """Find specialist by ID. Returns None if not found."""
    if specialist_id in cache:
        return cache[specialist_id]
    
    if db.has(specialist_id):
        specialist = db.query(specialist_id)
        cache[specialist_id] = specialist
        return specialist
    
    return None
```

---

## LINE LENGTH

- Aim for <100 characters per line
- Break long function signatures across multiple lines
- Break long conditionals across multiple lines

```python
# ❌ WRONG - Too long
if specialist.level > 5 and specialist.burnout < 50 and specialist.is_available and specialist.specialty == incident.specialty_required:
    assign_incident(specialist, incident)

# ✅ CORRECT - Readable
if (specialist.level > game_config.min_level_for_assignment
    and specialist.burnout < game_config.max_burnout_for_assignment
    and specialist.is_available
    and specialist.specialty == incident.specialty_required):
    assign_incident(specialist, incident)
```

---

## STRING FORMATTING

Use f-strings (Python 3.6+), not % or .format()

```python
# ❌ OLD
message = "Specialist %s completed incident %s" % (specialist.name, incident.id)
message = "Specialist {0} completed incident {1}".format(specialist.name, incident.id)

# ✅ CORRECT
message = f"Specialist {specialist.name} completed incident {incident.id}"
```

---

## IMPORTS

- Sort imports: standard library, third-party, local
- One import per line (except from ... import)
- No unused imports

```python
# ✅ CORRECT ORDER
import json
import logging
from abc import ABC, abstractmethod
from typing import Optional

import pygame
from flask import Flask

from src.models.specialist import Specialist
from src.core.assignment_system import AssignmentSystem
```

---

## BLANK LINES

- Two blank lines between top-level functions
- One blank line between methods in a class
- Blank line before return statement (in multi-line functions)

```python
def calculate_xp_gain(level: int) -> int:
    """Calculate XP required for next level."""
    return int(100 * (level ** 1.5))


def calculate_specialist_reward(specialist: Specialist) -> float:
    """Calculate total reward for specialist."""
    return specialist.xp_total * specialist.bonus_multiplier


class Specialist:
    """Represents a security specialist."""
    
    def __init__(self, name: str, specialty: str):
        self.name = name
        self.specialty = specialty
    
    def assign_to_incident(self, incident: Incident) -> bool:
        """Assign incident to specialist."""
        if not self.is_available:
            return False
        
        self.current_incident = incident
        self.is_available = False
        
        return True
    
    def complete_incident(self) -> float:
        """Complete assigned incident and return reward."""
        reward = self.calculate_reward()
        self.xp += reward
        self.current_incident = None
        self.is_available = True
        
        return reward
```

---

## See Also

- [ABSOLUTE_STANDARDS.md](ABSOLUTE_STANDARDS.md) - The core standards
- [ANTI_PATTERNS.md](ANTI_PATTERNS.md) - What NOT to do
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Pre-commit checklist
