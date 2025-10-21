# QUICK REFERENCE CARD
## Phase 2 Budget System

---

## 📍 WHERE TO START

**New to this work?**
```
1. Read: PHASE_2_STATUS_SUMMARY.md (5 min)
2. Run: python3 verify_budget_system.py (30 sec)
3. Read: PHASE_2_TRANSITION.md (10 min)
4. Continue with Task 5
```

---

## 🎯 CURRENT STATUS

**Phase 2 Progress**: 4/9 tasks = 44% ✅

```
✅ Task 1: Phase 2 Plan
✅ Task 2: Budget Model
✅ Task 3: Budget System
✅ Task 4: Budget Plugin
⏳ Task 5: Budget Tests
⏳ Task 6: SLA Tracker
⏳ Task 7: SLA System
⏳ Task 8: SLA Plugin
⏳ Task 9: Game Loop
```

---

## 🧪 VERIFICATION

Run verification:
```bash
python3 verify_budget_system.py
```

Expected: **6/6 TESTS PASSED** ✅

---

## 💰 KEY CALCULATIONS

### Revenue (Monthly)
```
Revenue = Σ(contract_value × satisfaction)

Example:
  Client: $10,000/month × 0.85 satisfaction
  Revenue: $8,500 ✅
```

### Expenses (Monthly)
```
Expenses = 
  (salary × specialists) +
  (base_infra + client_cost × active_clients) +
  (base_software + specialist_cost × specialists) +
  overhead

Example (1 spec, 1 client):
  $3,000 + $2,500 + $1,200 + $1,500 = $8,200 ✅
```

### Profit
```
Profit = Revenue - Expenses

Example:
  $8,500 - $8,200 = $300 (Profitable ✅)
```

---

## 📁 KEY FILES

| File | Lines | Purpose |
|------|-------|---------|
| `src/core/budget_system.py` | 240 | Core calculations |
| `src/core/plugins/budget_plugin.py` | 200 | Plugin wrapper |
| `src/models/budget.py` | ~100 | Data model |
| `main.py` | ~600 | Game initialization |
| `verify_budget_system.py` | 300 | Tests |

---

## 🔌 EVENTS

**BudgetPlugin subscribes to:**
```
month_ended
```

**BudgetPlugin publishes:**
```
budget_updated        (normal month)
budget_critical       (warning: low reserves)
game_over             (bankruptcy or no specialists)
```

---

## 📊 GAME ENDING CONDITIONS

**Bankruptcy**
```
reserves < $0 → GAME OVER
```

**No Specialists**
```
specialists.count == 0 → GAME OVER
```

**Forced Downsizing**
```
IF critical AND unprofitable:
  • Fire lowest performer
  • Reduce expenses
  • Try to prevent bankruptcy
```

---

## 🚀 WHAT TO DO NEXT

### Task 5: Budget Unit Tests
```
File: tests/test_budget_system.py (create new)
Tests needed:
  ✓ Revenue calculations
  ✓ Expense calculations
  ✓ Bankruptcy detection
  ✓ Forced downsizing
Effort: 2-3 hours
```

### Tasks 6-8: SLA System
```
Expand SLA tracker + create SLA system + create SLA plugin
Effort: 4 hours
```

### Task 9: Game Loop Rewrite
```
Convert to monthly cycles + player assignments
Effort: 3-4 hours
```

---

## ✅ QUALITY CHECKS

Before committing code:

- [ ] Type hints on ALL parameters & returns
- [ ] Google-style docstrings present
- [ ] All public functions have tests
- [ ] >80% code coverage
- [ ] No magic numbers
- [ ] No hardcoded values (use JSON config)
- [ ] Errors are explicit (not silent catches)
- [ ] Comprehensive logging
- [ ] No dead code or TODOs
- [ ] DRY principle (no duplication)
- [ ] Single responsibility per function

---

## 📝 DOCUMENTATION MAP

```
Strategic (Start here)
  └─→ PHASE_2_STATUS_SUMMARY.md

Technical (Implementation details)
  └─→ PHASE_2_BUDGET_SYSTEM_COMPLETE.md

Planning (What to do next)
  └─→ PHASE_2_TRANSITION.md

Navigation (Everything organized)
  └─→ PHASE_2_DOCUMENTATION_INDEX.md

Game Vision (Big picture)
  └─→ /plan/DETAILED_SPECIFICATION.md
```

---

## 🎮 GAMEPLAY FLOW

```
Month starts
  ↓
Generate incidents per client
  ↓
Player assigns specialists to incidents
  ↓
Auto-resolve incidents
  ↓
Month ends
  ↓
Budget plugin processes:
  • Calculate revenue
  • Calculate expenses
  • Update reserves
  • Check bankruptcy
  ↓
Check game over?
  YES → Show end screen
  NO  → Next month
```

---

## 💡 DEBUGGING TIPS

**Revenue seems wrong?**
```python
# Check: client.satisfaction is 0-1.0
# Check: client.is_active is True
# Check: client.monthly_contract_value is set
```

**Expenses seem wrong?**
```python
# Check: len(specialists) is correct
# Check: active_client_count is correct
# Check: All cost values loaded from config
```

**Plugin not working?**
```python
# Check: BudgetPlugin imported in main.py
# Check: BudgetPlugin in plugin_classes list
# Check: month_ended event fired
```

**Tests not passing?**
```bash
pytest tests/test_budget_system.py -v
```

---

## 🎯 SUCCESS CRITERIA

Phase 2 is COMPLETE when:

- [x] Budget system works ✅
- [ ] Budget unit tests written
- [ ] SLA system works
- [ ] SLA plugin works
- [ ] Game loop handles monthly cycles
- [ ] Player can assign incidents
- [ ] Game ends on bankruptcy
- [ ] Full 12-month playthrough works

---

## ⏱️ TIMELINE

```
Today:      Phase 2 Tasks 1-4 COMPLETE ✅
Tomorrow:   Task 5 (Budget Tests)
Day 3:      Tasks 6-7 (SLA System)
Day 4:      Task 8 (SLA Plugin)
Day 5:      Task 9 (Game Loop) + Testing
Expected:   Phase 2 COMPLETE by Oct 25
```

---

## 📞 QUICK LINKS

| Question | Answer |
|----------|--------|
| Status? | `PHASE_2_STATUS_SUMMARY.md` |
| How does it work? | `PHASE_2_BUDGET_SYSTEM_COMPLETE.md` |
| What's next? | `PHASE_2_TRANSITION.md` |
| Is it working? | `python3 verify_budget_system.py` |
| What should I read? | This file + links above |

---

## 🔐 BEFORE YOU CODE

Read: `.github/instructions/core-standards.instructions.md`
(The 15-point quality gate that ALL code must pass)

---

## 🎉 YOU ARE HERE

**Phase 2 Budget System: COMPLETE ✅**

**Next: SLA System Implementation**

```
        Phase 2
    ┌─────────────┐
    │ Budget ✅   │
    │ SLA   ⏳    │
    │ Loop  ⏳    │
    └─────────────┘
         ↓
    Phase 3: Ready
```

---

**Last Updated**: October 21, 2025  
**Status**: 🟢 READY FOR NEXT PHASE  
**Version**: 1.0 (Budget System Complete)  

