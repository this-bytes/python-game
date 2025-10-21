# Phase 2: Progression Depth

**Type**: INSTRUCTION (Desired-State Only)  
**Version**: 1.0  
**Created**: 2025-10-21  
**Priority**: P1-High  
**Timeline**: Weeks 3-4 (14 days)

---

## 🎯 Goal

**Add meaningful specialist progression through skill trees, dual-class system, and equipment drops to create strategic build diversity.**

---

## 📊 Success Metrics

- **Build Diversity**: 70%+ of specialists have unique builds (different skills/equipment)
- **Engagement**: Players spend 15+ minutes exploring skill tree options
- **Equipment Value**: 80%+ of equipment drops are equipped (not ignored)
- **Dual-Class Usage**: 50%+ of specialists reach dual-class by mid-game

---

## 📦 Deliverables

### Task 2.1: Skill Tree System
- `src/core/skill_tree_system.py` - Skill unlocking and stat application
- `data/skill_trees.json` - 30+ skills across 6 specialties (5 tiers each)
- `src/ui/panels/skill_tree_panel.py` - Visual skill tree display
- `tests/test_skill_tree.py` - 15+ tests, 80%+ coverage

### Task 2.2: Dual-Class Mechanic
- `src/core/dual_class_system.py` - Secondary specialty system
- Updated `data/specialists.json` - Secondary specialty support
- `tests/test_dual_class.py` - 10+ tests

### Task 2.3: Equipment Drop System
- `src/core/equipment_drops.py` - Drop calculation and rarity
- `data/equipment_catalog.json` - 50+ equipment items (5 rarity tiers)
- `tests/test_equipment_drops.py` - 12+ tests

---

## ⚙️ Non-Functional Constraints

- **Skill Points**: 1 point per level, cap at 20 points total
- **Prerequisites**: Max 2 prerequisite skills per skill
- **Respec Cost**: 1000 × current_level (expensive but possible)
- **Equipment Slots**: 5 slots (weapon, armor, accessory, tool, badge)
- **Drop Rates**: Common 50%, Uncommon 30%, Rare 15%, Epic 4%, Legendary 1%

---

## ✅ Acceptance Criteria

**Unit Tests**: 37+ total tests across all 3 tasks, 80%+ coverage each  
**Integration**: Skills/equipment apply stat bonuses correctly in combat  
**Manual QA**: Can allocate all skills, equip all items, reach dual-class  
**Documentation**: Design docs + workflow guides for each system

---

## 👤 Owner & Estimate

**Task 2.1**: AI Agent — 5 days  
**Task 2.2**: AI Agent — 3 days  
**Task 2.3**: AI Agent — 4 days  

**Total**: 12 days (with 2-day buffer = 14 days / Weeks 3-4)

---

## ⚠️ Risk Assessment

**Risk Level**: Medium - Build diversity might not happen despite options

**Mitigation**: Provide clear skill recommendations, make respec accessible, balance equipment stats carefully

---

## 🚀 Merge Requirements

- [ ] All tests passing, 80%+ coverage
- [ ] Playtest shows 70%+ build diversity
- [ ] Equipment drops feel rewarding (not ignored)
- [ ] Skill tree navigation intuitive

---

**Created**: 2025-10-21
