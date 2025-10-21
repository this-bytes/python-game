# Phase 4: Economy & Contracts

**Type**: INSTRUCTION (Desired-State Only)  
**Version**: 1.0  
**Created**: 2025-10-21  
**Priority**: P2-Medium  
**Timeline**: Weeks 7-8 (14 days)

---

## 🎯 Goal

**Create sustainable economy through contract negotiation, retainer income, passive investments, and facility upgrades.**

---

## 📊 Success Metrics

- **Economic Stability**: 80%+ of playthroughs avoid bankruptcy after Week 1
- **Contract Engagement**: Players complete 10+ contract negotiations per run
- **Passive Income**: 30%+ of late-game income from passive sources
- **Investment ROI**: Average 20% return on facility investments

---

## 📦 Deliverables

### Task 4.1: Contract System
- `src/core/contract_manager.py` - Contract negotiation and terms
- `data/contract_templates.json` - 20+ contract types
- `src/ui/panels/contract_panel.py` - Contract management UI
- `tests/test_contracts.py` - 20+ tests, 80%+ coverage

### Task 4.2: Passive Income System
- `src/core/passive_income.py` - Retainer and investment tracking
- `data/investments.json` - 15+ investment types
- `tests/test_passive_income.py` - 12+ tests

### Task 4.3: Facility Upgrades
- `src/core/facility_system.py` - Office improvements and automation unlocks
- `data/facility_upgrades.json` - 25+ upgrade options
- `tests/test_facilities.py` - 15+ tests

---

## ⚙️ Non-Functional Constraints

- **Starting Cash**: $5,000 (enough for 2-3 specialists)
- **Contract Values**: $500-50,000 based on difficulty/duration
- **Retainer Income**: 10-30% of contract value per month
- **Investment Returns**: 5-25% ROI based on risk
- **Facility Costs**: $1,000-100,000 per upgrade

---

## ✅ Acceptance Criteria

**Unit Tests**: 47+ total tests, 80%+ coverage  
**Integration**: Economy balanced (no easy money exploits)  
**Manual QA**: Can sustain operations, upgrades feel impactful  
**Documentation**: Economic balance documented with formulas

---

## 👤 Owner & Estimate

**Task 4.1**: AI Agent — 5 days  
**Task 4.2**: AI Agent — 4 days  
**Task 4.3**: AI Agent — 3 days  

**Total**: 12 days (with 2-day buffer = 14 days / Weeks 7-8)

---

## ⚠️ Risk Assessment

**Risk Level**: High - Economy balance is critical and hard to get right

**Mitigation**: Extensive playtesting, JSON-configurable values, start conservative (harder to earn money)

---

## 🚀 Merge Requirements

- [ ] All tests passing
- [ ] 10+ playtest runs show economic viability
- [ ] No money exploits found
- [ ] Passive income scales appropriately

---

**Created**: 2025-10-21
