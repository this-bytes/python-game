# ⚡ QUICK REFERENCE: THE 15-POINT REJECTION GATE

**This is what your code must pass. ALL 15 or it gets REJECTED.**

```
✅ 1.  Self-documenting?      [ ] Could someone read this cold and get it?
✅ 2.  Type hints complete?   [ ] Every parameter, every return value
✅ 3.  Docstring present?     [ ] Google-style, PURPOSE and INTENT
✅ 4.  Tests written?         [ ] Unit tests for every public function
✅ 5.  Coverage >80%?         [ ] New code, minimum 80% coverage
✅ 6.  No magic numbers?      [ ] All explained or in JSON config
✅ 7.  Errors explicit?       [ ] Specific exceptions, not generic catches
✅ 8.  Logging comprehensive? [ ] Key decisions, errors, transitions logged
✅ 9.  No dead code?          [ ] No commented-out, no debug, no TODOs
✅ 10. JSON-driven?           [ ] Game params in JSON, not hardcoded Python
✅ 11. DRY principle?          [ ] No copy-paste duplication anywhere
✅ 12. Concerns separated?     [ ] Logic, rendering, backend clearly split
✅ 13. Performance verified?   [ ] No unoptimized loops, N+1, blocking ops
✅ 14. Edge cases handled?     [ ] What breaks this? Did you handle it?
✅ 15. No redundant patterns?  [ ] Every line serves a purpose
```

---

# 🔴 15 INSTANT REJECTION RED FLAGS

See ANY of these? Your PR is **CLOSED IMMEDIATELY**. Fix locally, resubmit.

```
🚫 Untested function              → Every public function needs tests
🚫 Silent exceptions              → except Exception: pass = BANNED
🚫 Generic variable names         → data, obj, temp, x, item = BANNED
🚫 Function doing >1 job          → Split it into single-responsibility
🚫 Hardcoded game values          → multiplier = 1.37 with no reason = BANNED
🚫 Type hints missing             → This is Python 3.10+, not 2
🚫 No docstring                   → Public functions MUST explain PURPOSE
🚫 Copy-paste logic               → If it appears twice, extract it
🚫 Commented-out code             → Git exists. Delete it.
🚫 Magic strings/numbers          → Where did "incident_resolved" come from?
🚫 TODO comments                  → If you wrote it, YOU own it. Fix NOW.
🚫 Overly clever code             → If it needs a PhD to understand, rewrite
🚫 Inconsistent return types      → Sometimes None, sometimes object = BANNED
🚫 No error logging               → If it fails, we need to know WHY
🚫 Disabled code hacks            → No # commented = True, no if DEBUG:
```

---

# ✅ SELF-DOCUMENTING CODE TEMPLATE

```python
def resolve_incident_with_specialist_applying_synergy_bonus(
    incident: Incident,
    specialist: Specialist,
    game_config: GameConfig
) -> IncidentResolution:
    """Resolve incident with specialist, applying synergy multiplier.
    
    When specialist specialty matches incident requirements, resolution
    time is reduced by the synergy bonus. This encourages strategic team
    composition and makes specialists feel rewarding to level.
    
    Args:
        incident: The incident being resolved
        specialist: The specialist resolving it
        game_config: Current game configuration
        
    Returns:
        IncidentResolution with final time and rewards applied
        
    Raises:
        SpecialtyMismatchError: Specialist cannot handle this incident
        SpecialistUnavailableError: Specialist not available
        SkillLevelError: Specialist too low-level
    """
    # Validate compatibility
    if specialist.specialty != incident.specialty_required:
        logger.warning(
            f"Specialty mismatch: {specialist.name} ({specialist.specialty}) "
            f"cannot handle {incident.name}"
        )
        raise SpecialtyMismatchError(...)
    
    # Calculate resolution with synergy
    synergy_multiplier = (
        game_config.synergy_bonus_multiplier
        if specialist.specialty == incident.specialty_required
        else 1.0
    )
    resolution_time = incident.base_time / synergy_multiplier
    
    logger.info(f"Resolved {incident.id} in {resolution_time}s with {synergy_multiplier}x synergy")
    
    return IncidentResolution(
        incident=incident,
        specialist=specialist,
        time_taken=resolution_time,
        synergy_applied=synergy_multiplier,
        success=True
    )
```

---

# ❌ ANTI-PATTERNS TO AVOID (INSTANT REJECTION)

### Pattern 1: Redundant Constants
```python
# REJECTED
INCIDENT_RESOLVED = "incident_resolved"
SPECIALIST_LEVELED_UP = "specialist_leveled_up"

# ACCEPTED
event_bus.emit("incident_resolved", data)
event_bus.emit("specialist_leveled_up", data)
```

### Pattern 2: Generic Parameter Names
```python
# REJECTED
def process_data(data):
    for item in data:
        obj = item.get('value')

# ACCEPTED
def assign_incidents_to_available_specialists(pending_incidents: list[Incident]):
    for incident in pending_incidents:
        specialist = find_best_specialist(incident)
```

### Pattern 3: Functions Doing Too Much
```python
# REJECTED
def handle_incident(incident_id):
    incident = db.get(incident_id)
    specialist.xp += calc_xp(incident)
    update_ui()
    send_email()

# ACCEPTED
def resolve_incident(incident: Incident, specialist: Specialist) -> IncidentResolution:
    return IncidentResolution(
        incident=incident,
        xp_earned=specialist.calculate_xp(incident)
    )
```

### Pattern 4: Magic Numbers
```python
# REJECTED
multiplier = specialist.xp_gained * 1.37
if damage > 500:
    penalty = damage * 0.42

# ACCEPTED
SPECIALIST_XP_PRESTIGE_MULTIPLIER = 1.37  # Tuned for balance
INCIDENT_DAMAGE_BREACH_THRESHOLD = 500     # High-severity

multiplier = specialist.xp_gained * SPECIALIST_XP_PRESTIGE_MULTIPLIER
if damage > INCIDENT_DAMAGE_BREACH_THRESHOLD:
    penalty = damage * game_config.breach_penalty_multiplier
```

### Pattern 5: Exception Swallowing
```python
# REJECTED
try:
    specialist = load_specialist(specialist_id)
except:
    pass

# ACCEPTED
try:
    specialist = load_specialist(specialist_id)
except SpecialistNotFoundError as e:
    logger.error(f"Specialist {specialist_id} not found: {e}")
    raise
except SpecialistLoadError as e:
    logger.error(f"Failed to load specialist {specialist_id}: {e}")
    return get_default_specialist()
```

---

# 🧪 TEST REQUIREMENTS

**Every public function must have tests. NO EXCEPTIONS.**

```python
class TestSpecialistAssignment:
    """Specialist assignment: Match specialists to incidents strategically."""
    
    def test_specialist_assigned_when_specialty_matches(self):
        """Verify specialist accepts incident of matching specialty."""
        specialist = create_specialist(specialty="Network Security")
        incident = create_incident(specialty_required="Network Security")
        
        result = assign_incident(specialist, incident)
        
        assert result.success, "Assignment should succeed with matching specialty"
    
    def test_assignment_fails_when_specialty_mismatches(self):
        """Verify specialist rejects incident of different specialty."""
        specialist = create_specialist(specialty="Malware Analysis")
        incident = create_incident(specialty_required="Network Security")
        
        with pytest.raises(SpecialtyMismatchError):
            assign_incident(specialist, incident)
    
    def test_assignment_fails_when_specialist_unavailable(self):
        """Verify specialist already assigned cannot accept more incidents."""
        specialist = create_specialist(status="busy")
        incident = create_incident()
        
        with pytest.raises(SpecialistUnavailableError):
            assign_incident(specialist, incident)
    
    def test_assignment_fails_when_level_too_low(self):
        """Verify specialist below minimum level cannot be assigned."""
        specialist = create_specialist(level=1)
        incident = create_incident(minimum_level_required=5)
        
        with pytest.raises(SkillLevelError):
            assign_incident(specialist, incident)
```

---

# 📋 PRE-COMMIT CHECKLIST

**Do this BEFORE you commit. All items must be YES.**

- [ ] Could I explain this code to a junior dev in 2 minutes?
- [ ] Are there ANY commented-out lines?
- [ ] Are there ANY TODO or FIXME comments?
- [ ] Are there ANY debug print statements?
- [ ] Did I test edge cases?
- [ ] Did I test with invalid input?
- [ ] Did I add logging for key decisions?
- [ ] Is this code DRY (no duplication)?
- [ ] Could this fail silently? (Is that OK?)
- [ ] Am I PROUD of this code or just "done" with it?

**If ANY answer is NO, keep working.**

---

# 💪 THE MANDATE

**This project will not settle. Excellence is the only acceptable outcome.**

- Weak code = REJECTED
- Untested code = REJECTED  
- Unclear code = REJECTED
- Code violating standards = REJECTED

**Code that's crystal clear, thoroughly tested, properly documented, and truly excellent? That code gets merged.**

**This is the standard. This is non-negotiable. This is why we win.**

---

*Print this. Reference it. Live it. This is how we build something great.* 🚀🔒
