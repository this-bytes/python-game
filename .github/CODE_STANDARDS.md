# 🔥 PROJECT CODE STANDARDS - ZERO TOLERANCE FOR MEDIOCRITY

## The Absolute Truth

**This project operates under ZERO TOLERANCE for weak code.**

Every line of code must:
- ✅ Be self-documenting
- ✅ Have complete type hints
- ✅ Have tests (100% public functions)
- ✅ Have a Google-style docstring
- ✅ Handle errors explicitly
- ✅ Include comprehensive logging
- ✅ Live in JSON config (not hardcoded)
- ✅ Pass the 15-point checklist
- ✅ Avoid all red flags
- ✅ Earn its place

---

## 📖 THE QUICK START (5 MINUTES)

### 1. Read This First
Read `/home/localadmin/code/python-game/.github/copilot-instructions.md` lines 5-20 (the warning).

**YOU ARE NOT WELCOME HERE IF YOU WRITE WEAK CODE.**

### 2. Know The 15-Point Gate
Before committing ANY code, verify all 15 points in quick-reference.md pass. If ANY fail, code is **REJECTED**.

### 3. Know The 15 Red Flags
If your code has ANY of these, your PR **GETS CLOSED IMMEDIATELY**:
- Untested function
- Silent exception handling
- Generic variable names
- Function doing >1 job
- Hardcoded game values
- Missing type hints
- Missing docstring
- Copy-paste logic
- Commented-out code
- Magic strings/numbers
- TODO comments
- Overly clever code
- Inconsistent return types
- No error logging
- Disabled code

### 4. Understand The Philosophy
- **Mediocrity is garbage.** Reject it.
- **Excellence is mandatory.** Build it.
- **Code that's unclear is unfixable.** Name things perfectly.
- **Code that's untested is broken.** Test everything.
- **Code that's undocumented is unusable.** Document purpose.

---

## 📚 READING ORDER

### First Time (30 minutes)
1. **THIS FILE** - You're reading it
2. **QUICK_REFERENCE.md** - The enforcement checklist
3. **copilot-instructions.md lines 5-162** - The gate and red flags
4. **copilot-instructions.md lines 630-1000** - The standards and anti-patterns

### Before Each Coding Session (5 minutes)
1. Review QUICK_REFERENCE.md - The 15-point gate
2. Remember the 15 red flags
3. Start coding

### Before Each Commit (10 minutes)
1. Run through QUICK_REFERENCE.md 15-point checklist
2. Verify ZERO red flags
3. Verify ZERO anti-patterns
4. Commit (or fix and retry)

### If You're Stuck (15 minutes)
1. Check copilot-instructions.md for your question
2. Check QUICK_REFERENCE.md for examples
3. If still stuck, re-read the standards section

---

## 🎯 THE STANDARDS IN 30 SECONDS

### DO:
✅ Write code a junior dev can understand in one read
✅ Test everything - every public function gets unit tests
✅ Document WHY, not WHAT (code shows WHAT, you explain WHY)
✅ Use type hints everywhere - every parameter, every return
✅ Fail loudly and clearly - specific exceptions, comprehensive logging
✅ Keep functions small - one job per function
✅ Put all balancing in JSON - zero hardcoded game values

### DON'T:
❌ Commit untested code - not even for "just this once"
❌ Use generic names - `data`, `obj`, `value`, `temp` are banned
❌ Hardcode game values - everything goes in JSON config
❌ Swallow exceptions silently - `except: pass` is forbidden
❌ Write clever code - if it needs a PhD, rewrite it simpler
❌ Comment the obvious - `x = 5  # Set x to 5` is garbage
❌ Leave dead code around - no commented-out lines in commits
❌ Skip type hints - this is Python 3.10+, not Python 2
❌ Write undocumented code - no public function without docstring
❌ Accept mediocrity - weak code gets rejected, period

---

## 🔴 THE RED FLAGS (MEMORIZE THESE)

**See ANY of these? Your PR is CLOSED IMMEDIATELY.**

1. **Untested function** - Every public function needs tests
2. **Silent exceptions** - `except Exception: pass` = BANNED
3. **Generic names** - `data`, `obj`, `temp`, `x`, `item` = BANNED
4. **Multi-job functions** - Split into single-responsibility
5. **Hardcoded values** - `1.37` with no explanation = BANNED
6. **Missing type hints** - All parameters and returns must be typed
7. **Missing docstring** - All public functions must have Google-style docstring
8. **Copy-paste code** - If it appears twice, extract it to one place
9. **Commented code** - Git exists. Delete dead code.
10. **Magic numbers** - Where did this come from? Name it.
11. **TODO comments** - If you wrote it, YOU fix it NOW
12. **Clever code** - If it requires explaining, rewrite it clearer
13. **Inconsistent returns** - Never mix `None` and object returns
14. **No error logging** - If it fails, we must know why
15. **Disabled code** - No `# commented = True`, no `if DEBUG:` hacks

---

## 📋 THE 15-POINT GATE (MUST PASS ALL)

Before committing, verify:

- [ ] Code is readable without questions?
- [ ] Type hints on every parameter and return?
- [ ] Google-style docstring explaining PURPOSE?
- [ ] Unit tests for every public function?
- [ ] >80% test coverage on new code?
- [ ] All magic numbers explained or in JSON?
- [ ] All errors handled explicitly with logging?
- [ ] No commented-out code or debug prints?
- [ ] All game parameters in JSON, not hardcoded?
- [ ] No copy-paste duplication?
- [ ] Game logic vs rendering vs backend clearly separated?
- [ ] No unoptimized loops or blocking operations?
- [ ] All edge cases handled?
- [ ] Every line serves a clear purpose?

**If ANY fail, the code is REJECTED. Fix it and resubmit.**

---

## 🧪 TESTING REQUIREMENT

**EVERY public function MUST have tests. NO EXCEPTIONS.**

Example of passing test:

```python
def test_specialist_gains_xp_on_incident_completion():
    """Test that specialist XP increases when incident resolved."""
    specialist = create_specialist(base_xp=100)
    incident = create_incident(difficulty=2)
    
    specialist.resolve_incident(incident)
    
    assert specialist.xp > 100, "XP should increase after resolving incident"
```

What makes it good:
- Clear name describing behavior
- Docstring explaining what's tested
- Explicit setup
- One clear assertion
- No magic numbers

---

## 💻 CODE STYLE QUICK REFERENCE

### Naming
- **Classes**: `PascalCase` → `Specialist`, `IncidentGenerator`
- **Functions**: `snake_case` → `assign_incident`, `calculate_xp_gain`
- **Constants**: `UPPER_SNAKE_CASE` → `MAX_SPECIALISTS`, `BASE_XP`
- **Files**: `snake_case` → `specialist.py`, `incident_queue_panel.py`
- **JSON keys**: `snake_case` → `incident_rate_per_minute`

### Type Hints (MANDATORY)
```python
def calculate_reward(
    incident: Incident,
    specialist: Specialist,
    config: GameConfig
) -> float:
    """Calculate incident resolution reward."""
    return incident.base_reward * specialist.bonus * config.scale
```

### Docstrings (MANDATORY for public functions)
```python
def assign_incident(
    incident: Incident,
    specialist: Specialist
) -> AssignmentResult:
    """Assign incident to specialist if compatible.
    
    Validates specialty match and specialist availability.
    Updates state immediately on success.
    
    Args:
        incident: The incident to assign
        specialist: The specialist to assign to
        
    Returns:
        AssignmentResult with success status and reason
        
    Raises:
        SpecialtyMismatchError: Specialties don't match
        SpecialistUnavailableError: Specialist not available
    """
    ...
```

### Error Handling (MANDATORY)
```python
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

## 🚀 YOUR FIRST COMMIT CHECKLIST

1. ✅ Read copilot-instructions.md (at least lines 5-162)
2. ✅ Read QUICK_REFERENCE.md
3. ✅ Write code following the standards
4. ✅ Write tests for every public function
5. ✅ Verify all 15 points on the gate
6. ✅ Verify ZERO red flags
7. ✅ Verify code is crystal clear
8. ✅ Verify type hints are complete
9. ✅ Verify docstrings are present
10. ✅ Verify error handling is explicit
11. ✅ Verify tests pass and cover >80% of new code
12. ✅ Verify no commented-out code
13. ✅ Verify no debug prints
14. ✅ Verify no TODO comments
15. ✅ Verify all game params are in JSON

**Then commit.**

---

## 📞 ENFORCEMENT

### What Happens When Code Violates Standards

1. **Code Review**: Checked against 15-point gate
2. **Red Flags Found**: PR **CLOSED IMMEDIATELY**
3. **Anti-Patterns Found**: PR **CLOSED IMMEDIATELY**
4. **Tests Missing**: PR **REJECTED**
5. **Type Hints Missing**: PR **REJECTED**
6. **Docstrings Missing**: PR **REJECTED**

**You must fix and resubmit.**

### There Are No Exceptions

- No "I was in a hurry"
- No "I'll fix it later"
- No "This is just a small change"
- No "Everyone else does it this way"

**The standards apply to EVERY line of code, EVERY commit, EVERY time.**

---

## 💪 THE BOTTOM LINE

This project operates on ONE simple principle:

> **"Mediocrity is not welcome here. Excellence is mandatory."**

Every function you write will be self-documenting.
Every line will earn its existence.
Every test will prove correctness.
Every commit will be undeniable.

Weak code gets rejected.
Untested code gets rejected.
Unclear code gets rejected.

But code that's crystal clear, thoroughly tested, properly documented, and truly excellent?

**That code gets merged.**

**That code becomes part of something great.**

---

## 🎯 STARTING NOW

1. **Go read copilot-instructions.md lines 5-20** - The warning
2. **Go read QUICK_REFERENCE.md** - The checklist
3. **Come back here** - Reference section 2
4. **Start coding** - Follow the standards
5. **Before committing** - Use section 2 again

---

## 📚 FILES TO BOOKMARK

- `/home/localadmin/code/python-game/.github/copilot-instructions.md` - The full standards
- `/home/localadmin/code/python-game/.github/QUICK_REFERENCE.md` - The checklist
- `/home/localadmin/code/python-game/.github/STANDARDS_UPDATE.md` - What changed
- `/home/localadmin/code/python-game/.github/CODE_STANDARDS.md` - This file

---

*This is the standard. This is non-negotiable. This is why we win.* 🚀🔒

**Welcome to excellence.**
