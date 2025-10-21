# Phase 1: Core Loop Refinement

**Type**: INSTRUCTION (Desired-State Only)  
**Version**: 1.0  
**Created**: 2025-10-21  
**Priority**: P0-Critical  
**Timeline**: Weeks 1-2 (14 days)

---

## 🎯 Goal

**Make the 30-second core loop PERFECT before adding depth.**

Players must experience satisfying incident resolution with meaningful decision-making and clear progression feedback.

---

## 📊 Success Metrics

- **Loop Completion Time**: 30-60 seconds from incident spawn to resolution
- **Player Agency**: 3-5 meaningful decisions per incident
- **Satisfaction Score**: 8/10+ rating from playtesters on loop enjoyment
- **Clarity**: 100% of playtesters understand what to do within 2 minutes
- **Performance**: 60 FPS maintained with 20+ active incidents

---

## 📦 Deliverables

### Task 1.1: Decision-Based Incident Resolution
- `src/core/resolution_system.py` - Resolution logic with decision trees
- `data/resolution_trees.json` - 5 decision trees (DDoS, Malware, Phishing, Data Breach, Ransomware)
- `tests/test_resolution_system.py` - 15+ tests, 80%+ coverage
- `docs/INCIDENT_RESOLUTION_SYSTEM.md` - Design documentation

### Task 1.2: Automation Script Builder
- `src/core/automation_builder.py` - Rule creation and evaluation engine
- `data/automation_rules.json` - 5 default automation templates
- `src/ui/panels/automation_panel.py` - Visual rule builder UI
- `tests/test_automation_builder.py` - 20+ tests, 80%+ coverage
- `docs/AUTOMATION_SYSTEM.md` - Design documentation

### Task 1.3: Progressive Difficulty Curve
- Updated `src/core/incident_generator.py` - Difficulty scaling logic
- Updated `data/game_config.json` - Difficulty curve configuration
- `tests/test_difficulty_scaling.py` - 10+ tests
- `docs/DIFFICULTY_SYSTEM.md` - Balance documentation

---

## ⚙️ Non-Functional Constraints

### Task 1.1 Constraints:
- **Decision Trees**: 3-5 stages per incident type, 2-4 decisions per stage
- **Time Pressure**: 30-60 second limit per stage
- **Consequence Impact**: Decisions affect time (0.5-2.0x), money (±$0-5000), accuracy (±0-50)
- **Skill Integration**: Specialist stats influence success probability (60-95%)

### Task 1.2 Constraints:
- **Rule Complexity**: Max 5 conditions per rule (avoid overwhelming players)
- **Condition Types**: Minimum 10 types (difficulty, specialty, level, burnout, etc.)
- **Action Types**: Minimum 5 types (auto_assign, notify, escalate, skip, delegate)
- **Priority System**: 0-100 priority scale (higher executes first)

### Task 1.3 Constraints:
- **Early Game**: 0-10 minutes, difficulty 1-2, 0.8x incident rate
- **Mid Game**: 10-30 minutes, difficulty 2-4, 1.0x incident rate
- **Late Game**: 30+ minutes, difficulty 3-5, 1.2x incident rate
- **Smooth Scaling**: No sudden difficulty spikes

---

## ✅ Acceptance Criteria

### Task 1.1: Decision-Based Incident Resolution

**Unit Tests**:
- [ ] 15+ tests covering all decision paths
- [ ] Test specialist skill checks (accuracy determines outcomes)
- [ ] Test time pressure mechanics (decisions under timer)
- [ ] Test consequence application (time, money, burnout effects)
- [ ] 80%+ code coverage

**Integration Tests**:
- [ ] Player can make 3-5 decisions during incident resolution
- [ ] Decisions visibly affect outcome (faster/slower resolution)
- [ ] Specialist stats influence success (high accuracy = better outcomes)
- [ ] Time pressure creates tension (SLA ticking creates urgency)
- [ ] Resolution integrates with existing incident flow

**Manual QA**:
1. Start incident resolution
2. Make decision A → verify effect applied
3. Make decision B → verify consequences stack correctly
4. Complete resolution → verify rewards calculated correctly

**Documentation**:
- [ ] Design doc explains decision tree structure
- [ ] Workflow guide: "How to add new resolution tree"
- [ ] Balance notes: effect multiplier ranges documented

### Task 1.2: Automation Script Builder

**Unit Tests**:
- [ ] 20+ tests covering all condition/action types
- [ ] Test rule evaluation (conditions → actions)
- [ ] Test priority system (higher priority executes first)
- [ ] Test rule enabling/disabling
- [ ] 80%+ code coverage

**Integration Tests**:
- [ ] Player can create custom automation rules via UI
- [ ] Rules execute based on priority (observable in logs)
- [ ] 10+ condition types available and functional
- [ ] 5+ action types available and functional
- [ ] Rules persist across save/load

**Manual QA**:
1. Open automation panel
2. Create rule: "IF difficulty < 3 AND specialty matches THEN auto-assign"
3. Enable rule
4. Verify rule executes on matching incident
5. Test rule with non-matching incident (should not execute)

**Documentation**:
- [ ] Design doc explains rule structure
- [ ] Workflow guide: "How to create automation rule"
- [ ] Examples: 5 common automation patterns

### Task 1.3: Progressive Difficulty Curve

**Unit Tests**:
- [ ] 10+ tests for difficulty calculation
- [ ] Test time-based scaling (early/mid/late game)
- [ ] Test specialist-level-based scaling
- [ ] Test SLA-performance-based scaling
- [ ] Test prestige multipliers

**Integration Tests**:
- [ ] Early game generates difficulty 1-2 incidents only
- [ ] Mid game increases to difficulty 2-4
- [ ] Late game reaches difficulty 3-5
- [ ] Smooth progression (no sudden spikes observable)
- [ ] Specialist levels influence difficulty range

**Manual QA**:
1. Start new game → verify difficulty 1-2 incidents
2. Play 10 minutes → verify difficulty increases to 2-3
3. Play 30 minutes → verify difficulty reaches 3-5
4. Level up specialists → verify difficulty range adjusts

**Documentation**:
- [ ] Balance document explains difficulty curve formula
- [ ] Configuration guide: how to adjust curve in JSON
- [ ] Playtesting results: curve feels smooth

---

## 👤 Owner & Estimate

**Task 1.1**: AI Agent — 3 days  
**Task 1.2**: AI Agent — 4 days  
**Task 1.3**: AI Agent — 2 days  

**Total Phase 1**: 9 days (with 5-day buffer = 14 days / Weeks 1-2)

**Dependencies**: None (can start immediately)

---

## ⚠️ Risk Assessment

**Risk Level**: Medium

### Task 1.1 Risks:
1. **Decision Trees Too Complex**: Players overwhelmed by choices - Probability: Medium - Impact: High
   - Mitigation: Limit to 3-5 stages, 2-4 decisions per stage
   - Test with playtesters early

2. **Time Pressure Too Stressful**: Players feel rushed - Probability: Low - Impact: Medium
   - Mitigation: Configurable time limits in JSON (easy to tune)

### Task 1.2 Risks:
1. **UI Too Complicated**: Rule builder confusing - Probability: High - Impact: High
   - Mitigation: Start with templates, add visual builder later
   - Provide 5 pre-made rules to start

2. **Rule Conflicts**: Multiple rules triggering - Probability: Medium - Impact: Low
   - Mitigation: Priority system (highest priority wins)

### Task 1.3 Risks:
1. **Difficulty Too Easy/Hard**: Balance issues - Probability: High - Impact: Medium
   - Mitigation: JSON-configurable (easy to adjust)
   - Extensive playtesting

---

## 🔄 Rollback Plan

**If Phase 1 tasks fail:**

### Task 1.1 Rollback:
- Feature flag OFF: `"decision_based_resolution": {"enabled": false}`
- Revert to simple time-based resolution
- Keep existing incident system

### Task 1.2 Rollback:
- Feature flag OFF: `"automation_builder": {"enabled": false}`
- Use only pre-defined automation (no custom rules)
- Keep basic auto-assignment

### Task 1.3 Rollback:
- Revert to flat difficulty distribution
- Use simple random difficulty (1-5)

**Data Preservation**: All changes are JSON-driven, code rollback is safe

---

## 🚀 Merge Requirements

**Phase 1 Complete When**:

- [ ] All 3 tasks delivered with acceptance criteria met
- [ ] All tests passing (unit + integration)
- [ ] Code review completed
- [ ] Playtesting validates 30-second loop satisfaction (8/10+ rating)
- [ ] Performance maintained (60 FPS with 20+ incidents)
- [ ] Documentation complete (design docs + workflow guides)
- [ ] No P0 or P1 bugs outstanding

**Playtest Requirements**:
- [ ] 5+ playtesters complete 30-minute session
- [ ] Feedback form shows 8/10+ satisfaction on core loop
- [ ] All playtesters understand what to do within 2 minutes
- [ ] No playtesters report confusion on incident resolution

---

## 📝 Notes

**Design Principles for Phase 1**:
- **Simplicity First**: Start with simple decision trees, add complexity later
- **JSON Everything**: All parameters configurable (easy iteration)
- **Fast Feedback**: Visual feedback for every decision (<200ms)
- **Progressive Disclosure**: Tutorial introduces one concept at a time

**Integration with Existing Systems**:
- Resolution system hooks into existing incident flow
- Automation builder extends existing auto-assignment
- Difficulty curve uses existing incident generator

**Next Phase Dependencies**:
- Phase 2 builds on automation foundation
- Phase 3 requires decision-making established
- Phase 4 needs difficulty scaling for economy balance

---

## 🚫 FORBIDDEN CONTENT

**This file contains ONLY**:
- Task goals and success metrics
- File paths to create (no implementation)
- Acceptance criteria (testable outcomes)
- Risk assessment and mitigation

**This file does NOT contain**:
- Function implementations or code snippets
- Step-by-step developer instructions
- Algorithm details or data structures
- Current state or progress tracking

For implementation patterns, see `.github/instructions/` files.

---

**Created**: 2025-10-21  
**Last Updated**: 2025-10-21  
**Next Review**: After Phase 1 completion (Week 2)
