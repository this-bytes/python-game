# Code Style - Instructions

**This file contains coding conventions, naming standards, and anti-patterns to avoid.**

Reference this when:
- Writing new code
- Reviewing code quality
- Understanding naming conventions
- Learning what NOT to do

---

## NAMING CONVENTIONS

- **Classes**: `PascalCase` → `Specialist`, `IncidentGenerator`, `GameState`
- **Functions/Methods**: `snake_case` → `assign_incident`, `calculate_xp_gain`, `resolve_incident_with_specialist`
- **Constants**: `UPPER_SNAKE_CASE` → `MAX_SPECIALISTS`, `BASE_XP`, `DEFAULT_TIMEOUT`
- **JSON keys**: `snake_case` → `incident_rate_per_minute`, `specialist_xp_multiplier`
- **Files**: `snake_case` → `specialist.py`, `incident_queue_panel.py`, `assignment_system.py`

**Rule**: Names must be crystal clear. No abbreviations unless universal. No single-letter variables (except loop counters).

### Variable Naming (Crystal Clear)

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

# ANTI-PATTERNS - What NOT To Do

Each anti-pattern shows ❌ REJECTED examples and ✅ ACCEPTED alternatives.

---

## 1. REDUNDANT CONSTANT DEFINITIONS

**Problem:** Creating constants that just duplicate their own value adds zero value.

```python
# ❌ REJECTED - Cargo cult programming
INCIDENT_RESOLVED = "incident_resolved"
SPECIALIST_LEVELED_UP = "specialist_leveled_up"
AUTOMATION_TRIGGERED = "automation_triggered"

# Usage doesn't benefit:
event_bus.emit(INCIDENT_RESOLVED, data)  # Same as: event_bus.emit("incident_resolved", data)

# ❌ REJECTED - Enum wrapper that adds nothing
class Events(Enum):
    INCIDENT_RESOLVED = "incident_resolved"
    SPECIALIST_LEVELED_UP = "specialist_leveled_up"

# ✅ ACCEPTED - Just use strings directly
event_bus.emit("incident_resolved", incident_data)
event_bus.on("specialist_leveled_up", handle_level_up)

# ✅ ACCEPTED - Constants that ADD value (computed/grouped)
class HTTPStatus:
    SUCCESS = 200              # Meaningful constant
    NOT_FOUND = 404
    SERVER_ERROR = 500

class GameConfig:
    MAX_ACTIVE_INCIDENTS = 100  # Computed/meaningful value
    XP_MULTIPLIER_PER_LEVEL = 1.05
    STARTING_SPECIALISTS = 2
```

**Why this matters:** You're wasting lines of code for zero benefit. The string IS the constant. If you add constants, they must provide actual value (computed values, meaningful groupings, clarity).

---

## 2. GENERIC PARAMETER NAMES

**Problem:** Using `data`, `obj`, `item`, `value` forces readers to dig into the code to understand.

```python
# ❌ REJECTED - What the hell is this?
def process_data(data):
    for item in data:
        obj = item.get('value')
        # What are we processing? What is this for?

# ❌ REJECTED - Still unclear
def handle_input(input_obj):
    temp = calculate(input_obj)
    return temp

# ✅ ACCEPTED - Crystal clear intent
def assign_incidents_to_available_specialists(pending_incidents: list[Incident]):
    """Assign pending incidents to available specialists."""
    for incident in pending_incidents:
        specialist = self._find_best_specialist_for_incident(incident)
        if specialist:
            self._assign_incident(incident, specialist)

# ✅ ACCEPTED - Immediate understanding
def calculate_specialist_xp_multiplier(base_xp: int) -> float:
    """Calculate XP multiplier for specialist based on level and bonuses."""
    xp_multiplier = 1.0
    
    if self.level >= game_config.level_threshold:
        xp_multiplier *= game_config.level_bonus
    
    if self.has_certification:
        xp_multiplier *= game_config.certification_bonus
    
    return xp_multiplier
```

**Why this matters:** Generic names force every reader (including future you) to dig into the function to understand what's happening. Clear names make code self-documenting.

---

## 3. FUNCTIONS DOING TOO MANY THINGS

**Problem:** A function that assigns incidents AND logs AND updates UI AND calculates bonuses does too much.

```python
# ❌ REJECTED - This does 5 things at once (ANTI-PATTERN)
def handle_incident_resolution(incident_id):
    incident = db.get(incident_id)
    specialist = find_specialist(incident)
    specialist.xp += calculate_xp(incident)      # Calculate
    update_ui_panel()                             # Update UI
    send_email_to_client()                        # Notify
    calculate_penalties()                         # Calculate
    log_everything()                              # Log
    return specialist

# ✅ ACCEPTED - Each function has ONE job
def calculate_incident_reward(incident: Incident, specialist: Specialist) -> float:
    """Calculate XP reward for resolving incident."""
    return incident.xp_reward * specialist.xp_multiplier

def award_specialist(specialist: Specialist, xp: float) -> None:
    """Award specialist XP."""
    specialist.xp += xp
    logger.info(f"Awarded {xp} XP to {specialist.name}")

def resolve_incident(incident: Incident, specialist: Specialist) -> IncidentResolution:
    """Resolve incident with specialist. Side effects handled by caller."""
    resolution_time = specialist.calculate_resolution_time(incident)
    xp_earned = calculate_incident_reward(incident, specialist)
    
    return IncidentResolution(
        incident=incident,
        specialist=specialist,
        time_taken=resolution_time,
        xp_earned=xp_earned
    )

# Caller handles side effects
result = resolve_incident(incident, specialist)
award_specialist(specialist, result.xp_earned)
update_ui(specialist)  # Separate concern
```

**Why this matters:** Functions that do multiple things are hard to test, hard to reuse, and hard to understand. Each function should have ONE clear responsibility.

---

## 4. HARDCODED MAGIC NUMBERS

**Problem:** Numbers appearing without explanation are confusing and break when game balance changes.

```python
# ❌ REJECTED - Where the hell does 1.37 come from?
multiplier = specialist.xp_gained * 1.37
if damage > 500:
    penalty = damage * 0.42

# ❌ REJECTED - Still magic (what about next month?)
# Tuned 1.37x on Tuesday
multiplier = specialist.xp_gained * 1.37

# ✅ ACCEPTED - Named constants with justification
SPECIALIST_XP_PRESTIGE_MULTIPLIER = 1.37  # Tuned for balance per GDD-2025
INCIDENT_DAMAGE_BREACH_THRESHOLD = 500     # High-severity threshold

multiplier = specialist.xp_gained * SPECIALIST_XP_PRESTIGE_MULTIPLIER
if damage > INCIDENT_DAMAGE_BREACH_THRESHOLD:
    penalty = damage * game_config.breach_penalty_multiplier

# ✅ BEST - Put in JSON config (hot-reloadable)
# In data/game_config.json:
{
  "specialist": {
    "xp_prestige_multiplier": 1.37
  },
  "incident": {
    "damage_breach_threshold": 500,
    "breach_penalty_multiplier": 0.42
  }
}

# In Python:
multiplier = specialist.xp_gained * game_config.specialist.xp_prestige_multiplier
if damage > game_config.incident.damage_breach_threshold:
    penalty = damage * game_config.incident.breach_penalty_multiplier
```

**Why this matters:** Magic numbers break game balance and confuse future developers. Named constants with justification or JSON config enable easy tuning.

---

## 5. EXCEPTION SWALLOWING

**Problem:** Silently catching and ignoring errors makes debugging impossible.

```python
# ❌ REJECTED - If it fails, nobody knows
try:
    specialist = self._load_specialist(specialist_id)
except:
    pass  # What error happened? Why did it fail?

# ❌ REJECTED - Generic catch-all that hides bugs
try:
    json_data = json.loads(raw_data)
except Exception:
    json_data = {}  # Silently use empty dict - what went wrong?

# ✅ ACCEPTED - Specific exceptions with logging
try:
    specialist = self._load_specialist(specialist_id)
except SpecialistNotFoundError as e:
    logger.error(f"Specialist {specialist_id} not found: {e}")
    raise  # Re-raise so caller can handle
except SpecialistLoadError as e:
    logger.error(f"Failed to load specialist {specialist_id}: {e}")
    # Graceful degradation: use default
    return self._get_default_specialist()

try:
    json_data = json.loads(raw_data)
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON in specialist data: {e}")
    raise ValidationError("Specialist data corrupted")
```

**Why this matters:** Silent failures make bugs invisible. Specific error handling with logging makes debugging possible.

---

## 6. INCONSISTENT RETURN TYPES

**Problem:** Functions that return different types in different code paths are impossible to use safely.

```python
# ❌ REJECTED - What am I getting back?
def find_specialist(id):
    if id in cache:
        return cache[id]           # Specialist object
    if db.has(id):
        return db.query(id)        # Also Specialist object
    return None                    # Sometimes None - INCONSISTENT

# Usage is dangerous:
specialist = find_specialist(id)
specialist.do_something()  # Crashes if None returned!

# ✅ ACCEPTED - Consistent type contract
def find_specialist(specialist_id: str) -> Specialist | None:
    """Find specialist by ID. Returns None if not found."""
    if specialist_id in self._cache:
        return self._cache[specialist_id]
    
    db_specialist = self._db.query_specialist(specialist_id)
    if db_specialist:
        self._cache[specialist_id] = db_specialist
        return db_specialist
    
    return None

# Usage is safe:
specialist = find_specialist(id)
if specialist:
    specialist.do_something()  # Type checker verifies this
```

**Why this matters:** Type checkers can't help if return types are inconsistent. Consistent returns make code safe.

---

## 7. MISSING TYPE HINTS

**Problem:** Without type hints, readers have to read the entire function to understand what types go in/come out.

```python
# ❌ REJECTED - Nobody knows what goes in or comes out
def calculate_reward(incident, specialist, config):
    base = incident['base_reward']
    multiplier = specialist['xp_bonus']
    return base * multiplier * config['economy_scale']

# ✅ ACCEPTED - Crystal clear contract
def calculate_reward(
    incident: Incident,
    specialist: Specialist,
    game_config: GameConfig
) -> float:
    """Calculate incident resolution reward.
    
    Accounts for incident base reward, specialist XP bonus,
    and global economy scaling from configuration.
    """
    return (
        incident.base_reward 
        * specialist.xp_bonus_multiplier 
        * game_config.economy_scale
    )
```

**Why this matters:** Type hints are documentation. They let IDEs and type checkers catch bugs before runtime.

---

## 8. COPY-PASTE CODE DUPLICATION

**Problem:** Same logic in 3 different places means 3 places to update when it changes.

```python
# ❌ REJECTED - This exact code appears in 5 files
if specialist.level >= 5:
    xp_multiplier *= 1.2
if specialist.has_certification:
    xp_multiplier *= 1.1
if specialist.has_mentor:
    xp_multiplier *= 1.15

# ✅ ACCEPTED - Extract to single source of truth
def calculate_xp_multiplier(specialist: Specialist, game_config: GameConfig) -> float:
    """Calculate all XP multipliers for specialist.
    
    Accounts for level thresholds, certifications, mentor bonuses.
    Single source of truth for all XP calculation logic.
    """
    multiplier = 1.0
    
    if specialist.level >= game_config.xp_level_threshold:
        multiplier *= game_config.xp_level_bonus
    
    if specialist.has_certification:
        multiplier *= game_config.xp_certification_bonus
    
    if specialist.mentor:
        multiplier *= game_config.xp_mentor_bonus
    
    return multiplier
```

**Why this matters:** Duplication means bugs in one place don't get fixed everywhere. Extract shared logic to one place.

---

## 9. OBVIOUS COMMENTS

**Problem:** Comments that just repeat what the code says waste space and mental effort.

```python
# ❌ REJECTED - The code already says this
x = 5  # Set x to 5
for i in range(10):  # Loop 10 times
    result.append(x)  # Append x to result
if len(result) > 0:  # Check if result is not empty
    return result  # Return result

# ❌ REJECTED - Comments that duplicate code
if specialist.level >= 5:  # Check if level >= 5
    specialist.unlock_automation()  # Unlock automation

# ✅ ACCEPTED - Comments explain the WHY
specialist_level_threshold = 5  # At level 5, specialists unlock advanced automation

# Synergy bonus encourages strategic team composition
if specialist.specialty == incident.specialty_required:
    resolution_multiplier = game_config.synergy_bonus_multiplier

# Each experience tier represents exponential skill growth
for level_tier in range(10):
    efficiency_scaling = 1.0 + (level_tier * 0.1)
    efficiency_values.append(base_efficiency * efficiency_scaling)
```

**Why this matters:** Good code reads like English. Comments should explain design decisions and WHY things work, not WHAT they do.

---

## 10. DISABLED CODE THAT'S NEVER REMOVED

**Problem:** Commented-out code, debug prints, and TODO comments create clutter and confusion.

```python
# ❌ REJECTED - Dead code clutters the file
# specialist.award_xp(incident.xp)
# logger.debug(f"DEBUG: XP = {calculated_xp}")
# TODO: This needs refactoring someday maybe
# print("TEMP DEBUG REMOVE LATER")
if DEBUG_MODE:
    print("Special debug path here")

# ✅ ACCEPTED - Git history exists. Delete dead code.
specialist.award_xp(incident.xp)
```

**Why this matters:** Git keeps history. Commented code is just noise. If you need it, it's in git history.

---

## Summary: How To Avoid These Anti-Patterns

1. **Ask before coding:** "Will someone understand this without asking?"
2. **Extract duplication:** If it appears twice, extract it to one place
3. **Single responsibility:** Each function does ONE thing
4. **Named constants:** All magic numbers get names or go in JSON
5. **Explicit errors:** Catch specific exceptions, log them
6. **Clear names:** Variables tell the story
7. **Type hints:** Every parameter and return type
8. **Delete dead code:** Comments, debugs, TODOs - delete them
9. **Test edge cases:** What breaks this? Handle it
10. **Comments explain WHY:** Code shows WHAT, comments show WHY

---

## See Also

- **[copilot-instructions.md](copilot-instructions.md)** - Main instructions and overview
- **[core-standards.instructions.md](core-standards.instructions.md)** - Absolute standards and quality gates
- **[testing.instructions.md](testing.instructions.md)** - Testing requirements
- **[architecture.instructions.md](architecture.instructions.md)** - System architecture
- **[workflows.instructions.md](workflows.instructions.md)** - Common development tasks
