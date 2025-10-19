---
applies_to:
  - "**/*"
---

# Core Standards - Instructions

**This file contains the absolute standards, quality gates, and daily checklists.**

Reference this when:
- Starting any coding session
- Before committing code
- Reviewing your own work
- Understanding project quality requirements

---

## 🔥 THE MANDATE

**THIS PROJECT OPERATES UNDER ZERO-TOLERANCE FOR MEDIOCRITY.**
**EXCELLENCE IS THE ONLY ACCEPTABLE OUTCOME.**

Run at maximum velocity. This is non-negotiable. This is why we win.
You'll always work autonomously, using these instructions as your sole guide.
Do not ask for clarifications or additional guidance. If you need to, refer back to these instructions.
Never take shortcuts. Always adhere strictly to the standards outlined here and in the referenced documentation. Make decisions that prioritize these values.
Your contributing to a game that is not the usual platformer side project. Cutting edge mechanics, deep systems. Put on your Gamer hat and make a game that players cant put down.

---

Every line must earn its place.
Every function must justify its existence.
Every class must provide undeniable value.

**Weak code will be rejected.**
**Untested code will be rejected.**
**Unclear code will be rejected.**

Code that's crystal clear, thoroughly tested, properly documented, and truly excellent?

**That code gets merged. That code becomes part of something great.**

This is non-negotiable.

---

## ✅ THE 15-POINT GATE (Nothing Passes Without All 15)

Before committing ANY code, verify:

1. ✅ **Self-documenting?** - Could someone read this cold and understand it?
2. ✅ **Type hints complete?** - Every parameter, every return value
3. ✅ **Docstring present?** - Google-style, explaining PURPOSE and INTENT
4. ✅ **Tests written?** - Unit tests for every public function
5. ✅ **Test coverage?** - Minimum 80% on new code (75% overall acceptable for legacy)
6. ✅ **No magic numbers?** - All explained or in JSON config
7. ✅ **Errors explicit?** - Specific exceptions, not generic `Exception` catches
8. ✅ **Logging comprehensive?** - Key decisions, errors, state transitions logged
9. ✅ **No dead code?** - No commented-out code, no debug prints, no TODOs
10. ✅ **JSON-driven?** - Game parameters in JSON, not hardcoded in Python
11. ✅ **DRY principle?** - No copy-paste duplication anywhere
12. ✅ **Separation of concerns?** - Logic, rendering, backend clearly separated
13. ✅ **Performance verified?** - No unoptimized loops, N+1 queries, or blocking operations
14. ✅ **Edge cases handled?** - What breaks this? Did you handle it?
15. ✅ **No redundant patterns?** - Every line serves a purpose

**FAILURE = REJECTION. FIX AND RESUBMIT.**

---

## 🔴 THE 15 RED FLAGS (Instant Rejection)

If your code has ANY of these, it gets rejected immediately:

1. **Untested function** - Every public function needs tests. Period.
2. **Silent exception handling** - `except Exception: pass` is FORBIDDEN
3. **Generic variable names** - `data`, `obj`, `temp`, `x`, `item`
4. **Function doing >1 job** - Assign incidents AND log AND update UI? Split it.
5. **Hardcoded game values** - `multiplier = 1.37` with no explanation
6. **Type hints missing** - This is Python 3.10+, not Python 2.
7. **No docstring** - Public functions must explain PURPOSE, not just WHAT
8. **Copy-paste logic** - If it appears twice, it should be extracted
9. **Commented-out code** - Git history exists. Delete it.
10. **Magic strings/numbers** - Where did you get `"incident_resolved"`?
11. **`TODO` comments** - If you wrote it, you own it. Fix it now.
12. **Overly clever code** - If it requires a PhD to understand, rewrite it
13. **Inconsistent return types** - Function sometimes returns None, sometimes list
14. **No error logging** - If it fails, we need to know why
15. **Disabled code** - No `# commented = True`, no `if DEBUG:` hacks

**See any of these? Your PR gets closed. Fix it locally, resubmit.**

---

## 📝 WHAT A GOOD COMMIT LOOKS LIKE

```
Title: Add specialist burnout mechanic with morale recovery

- Specialists accumulate burnout meter on incident assignment
- Burnout >80% triggers performance penalties (-10% speed, -15% accuracy)
- Rest day action resets burnout to 0 over 8-hour period
- Added burnout thresholds and recovery rates to game_config.json
- Full test coverage: 12 test cases covering all burnout states
- Type hints throughout, docstrings explain design rationale
```

**Key characteristics:**
- Clear title describing WHAT and WHY
- Bullet points explain concrete changes
- References JSON config changes
- Mentions test coverage numbers
- No vague language like "Fixed stuff" or "Improved code"

---

## 🧪 WHAT PASSING TESTS LOOK LIKE

```python
class TestSpecialistBurnout:
    """Burnout mechanic: specialists degrade with overwork, recover with rest."""
    
    def test_burnout_accumulates_on_incident_assignment(self):
        """Verify specialist burnout increases when assigned to incident."""
        specialist = create_specialist(burnout_rate=5)
        incident = create_incident()
        
        specialist.assign_to_incident(incident)
        
        assert specialist.burnout == 5, "Burnout should increase by 5"
    
    def test_burnout_exceeding_80_percent_triggers_penalties(self):
        """Verify performance degradation when burnout >80%."""
        specialist = create_specialist(base_speed=100)
        specialist.burnout = 85
        
        performance_multiplier = specialist.get_performance_multiplier()
        
        assert performance_multiplier == 0.9, "Expected 10% speed penalty at 85% burnout"
    
    def test_rest_day_resets_burnout_to_zero(self):
        """Verify rest day action fully recovers specialist."""
        specialist = create_specialist(burnout=95)
        
        specialist.take_rest_day()
        
        assert specialist.burnout == 0, "Burnout should be fully reset after rest day"
```

**What makes these good:**
- Clear test names that describe behavior
- Docstring explaining what's tested
- Explicit setup
- One clear assertion
- Tests edge cases
- No magic numbers (use named constants)

---

## 🚀 BEFORE EVERY CODING SESSION

1. **READ THIS FILE** - Every time. No shortcuts.
2. **MEMORIZE THE 15-POINT GATE** - Know it cold.
3. **KNOW THE 15 RED FLAGS** - These are deal-breakers.
4. **READ code-style.instructions.md** - Understand naming and anti-patterns.

---

## 💻 BEFORE WRITING CODE

Ask yourself:

1. Is this function testable? If not, redesign it.
2. Can a junior understand this in one read? If not, simplify it.
3. Does this belong in JSON config? If yes, move it there.
4. Am I copy-pasting? If yes, extract to shared function.
5. Is there a magic number here? If yes, name it and justify it.

---

## 🔍 DURING CODE REVIEW (On Your Own Work)

1. Would future me understand this without a comment?
2. Are all paths tested? What breaks this?
3. Is this doing one job or multiple jobs?
4. Does this follow the project's patterns or create something new?
5. Is error handling explicit and logged?
6. Will this perform under load?

---

## ✨ AFTER YOU THINK YOU'RE DONE

Ask yourself these 10 questions:

1. Could I explain this to a new developer in under 2 minutes?
2. Are there ANY commented-out lines?
3. Are there ANY TODO or FIXME comments?
4. Are there ANY debug prints?
5. Did I test edge cases?
6. Did I test with invalid input?
7. Did I add logging for debugging?
8. Is this code DRY or will I regret duplication later?
9. Could this fail silently?
10. Am I PROUD of this code, or just "done" with it?

**If you answer "no" to any of these, keep working.**

---

## 🎯 THE DAILY CHECKLIST

**Before every commit, run through this:**

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
✅ 11. DRY principle?         [ ] No copy-paste duplication anywhere
✅ 12. Concerns separated?    [ ] Logic, rendering, backend clearly split
✅ 13. Performance verified?  [ ] No unoptimized loops, N+1, blocking ops
✅ 14. Edge cases handled?    [ ] What breaks this? Did you handle it?
✅ 15. No redundant patterns? [ ] Every line serves a purpose
```

**If ANY fail, the code is REJECTED.**

---

## 📋 PRE-COMMIT CHECKLIST

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

## 📚 DETAILED REFERENCES

For more details on specific topics, see:

- **[code-style.instructions.md](code-style.instructions.md)** - Naming, type hints, docstrings, anti-patterns
- **[architecture.instructions.md](architecture.instructions.md)** - Project structure, design patterns
- **[testing.instructions.md](testing.instructions.md)** - Testing requirements and fixtures
- **[workflows.instructions.md](workflows.instructions.md)** - How to add features, debug, balance
- **[plugin-system.instructions.md](plugin-system.instructions.md)** - Plugin architecture
- **[data-driven.instructions.md](data-driven.instructions.md)** - JSON configuration patterns

---

## 🚫 FINAL REMINDERS

✅ **DO:**
- Write code a junior dev could understand
- Test everything immediately
- Document why, not what
- Use type hints everywhere
- Fail loudly and clearly
- Keep functions small and focused
- Put all balancing in JSON

❌ **NEVER:**
- Commit untested code
- Use generic names (`data`, `obj`, `value`)
- Hardcode game values
- Swallow exceptions silently
- Write "clever" code
- Comment the obvious
- Leave dead code around
- Ignore type hints
- Skip documentation

---

## 💪 THE BOTTOM LINE

This project will not settle. Excellence is the only acceptable outcome.

Every function you write will be **self-documenting**.
Every class will have **clear purpose**.
Every module will be **testable**.
Every system will be **configurable**.

Weak code will be rejected.
Untested code will be rejected.
Unclear code will be rejected.

But code that's crystal clear, thoroughly tested, properly documented, and truly excellent?

**That code gets merged.**

**This is the standard. This is non-negotiable. This is why we win.**

---

*Print this. Reference it. Live it. This is how we build something great.* 🚀🔒

---

## See Also

- **[copilot-instructions.md](../copilot-instructions.md)** - Main instructions and overview
- **[code-style.instructions.md](code-style.instructions.md)** - Code style and anti-patterns
- **[testing.instructions.md](testing.instructions.md)** - Testing requirements
- **[architecture.instructions.md](architecture.instructions.md)** - System architecture
- **[workflows.instructions.md](workflows.instructions.md)** - Common development tasks
