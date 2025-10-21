# Phase 3: Team Dynamics

**Type**: INSTRUCTION (Desired-State Only)  
**Version**: 1.0  
**Created**: 2025-10-21  
**Priority**: P1-High  
**Timeline**: Weeks 5-6 (14 days)

---

## 🎯 Goal

**Create emergent team dynamics through relationship systems, personality traits, and synergy bonuses that reward strategic team composition.**

---

## 📊 Success Metrics

- **Relationship Formation**: 90%+ of specialists develop at least 1 friendship or rivalry
- **Synergy Impact**: 15% average performance boost from optimal team composition
- **Strategic Depth**: Players consider relationships in 70%+ of assignments
- **Emergent Stories**: Playtesters report 3+ memorable relationship moments

---

## 📦 Deliverables

### Task 3.1: Relationship System
- `src/core/relationships_system.py` - Friendship/rivalry tracking and effects
- `data/personality_traits.json` - 20+ personality types
- `tests/test_relationships.py` - 18+ tests, 80%+ coverage

### Task 3.2: Synergy Engine
- `src/core/synergy_engine.py` - Team composition bonus calculation
- `data/synergy_rules.json` - 30+ synergy patterns
- `tests/test_synergy.py` - 15+ tests

### Task 3.3: Team Formation AI
- `src/core/team_recommender.py` - Suggest optimal team compositions
- `src/ui/panels/team_builder_panel.py` - Visual team building interface
- `tests/test_team_recommender.py` - 10+ tests

---

## ⚙️ Non-Functional Constraints

- **Relationship Range**: -100 (rivals) to +100 (best friends)
- **Synergy Bonus Range**: 1.0x (neutral) to 1.5x (perfect synergy)
- **Personality Traits**: 5-7 traits per specialist
- **Team Size**: 2-5 specialists per team
- **Interaction Frequency**: Relationships update after every shared incident

---

## ✅ Acceptance Criteria

**Unit Tests**: 43+ total tests, 80%+ coverage  
**Integration**: Synergy bonuses apply during incident resolution  
**Manual QA**: Relationships form naturally, team recommendations useful  
**Documentation**: Relationship mechanics clearly explained

---

## 👤 Owner & Estimate

**Task 3.1**: AI Agent — 5 days  
**Task 3.2**: AI Agent — 4 days  
**Task 3.3**: AI Agent — 3 days  

**Total**: 12 days (with 2-day buffer = 14 days / Weeks 5-6)

---

## ⚠️ Risk Assessment

**Risk Level**: Medium - Relationships might feel gimmicky rather than strategic

**Mitigation**: Make synergy bonuses significant (15%+), provide clear UI feedback, integrate into core gameplay

---

## 🚀 Merge Requirements

- [ ] All tests passing
- [ ] Playtest shows relationships affect decisions (70%+ of assignments)
- [ ] Synergy bonuses feel meaningful (measurable impact)
- [ ] UI clearly shows relationship status and synergy potential

---

**Created**: 2025-10-21
