# 📋 INSTRUCTION & DOCUMENTATION REFACTOR - REVIEW SUMMARY

**Date**: 2025-10-21  
**Scope**: 52 markdown files across plan/, docs/, root/, and .github/instructions/  
**Status**: 🚨 READY FOR SYSTEMATIC EXECUTION

---

## 🎯 EXECUTIVE SUMMARY

This repository contains extensive planning and documentation that **violates separation of concerns**:
- Instruction files contain implementation code snippets (how-to details)
- Documentation files contain desired-state directives (future plans)
- Mixed content makes autonomous agent execution unreliable

**Required Action**: Systematic refactor to separate:
- **Instructions** → ONLY desired outcomes, acceptance criteria, success metrics
- **Documentation** → ONLY current state, exact TODOs, test status, file references

---

## 🔴 TOP 10 RISKS (Priority Order)

### RISK #1: Data Loss During Refactoring ⚠️ CRITICAL
**Severity**: HIGH  
**Impact**: Permanent loss of planning details or current state information

**Description**: With 52 files containing mixed content, automated refactoring could misclassify content and delete valuable information. Many files contain both historical context and future plans that need careful separation.

**Mitigation**:
- Create backup branch before starting: `git checkout -b backup/pre-refactor`
- Process files in small batches (5-10 at a time)
- Manual review of each refactored file before committing
- Use git diff to verify changes preserve all content

**Rollback Plan**: Revert to backup branch if data loss detected

---

### RISK #2: Misclassification of Content ⚠️ HIGH
**Severity**: HIGH  
**Impact**: Instructions become vague, docs become aspirational

**Description**: Determining "current state" vs "desired state" requires context. Example: "The system loads abilities.json" could be current fact OR future requirement depending on context.

**Example Ambiguity**:
```markdown
# AMBIGUOUS:
"The specialist skill tree should have 30+ skills across 6 specialties."

# IS THIS:
A) Current state fact (docs): "The specialist skill tree currently has 30+ skills"
B) Desired state requirement (instruction): "Implement 30+ skills across 6 specialties"
```

**Mitigation**:
- Use code inspection to verify current state claims
- Check git history to understand intent
- Flag ambiguous content for human review
- Add "VERIFY:" tags for uncertain classifications

---

### RISK #3: Instruction Files Become Too Vague ⚠️ HIGH
**Severity**: HIGH  
**Impact**: Autonomous agents cannot execute instructions

**Description**: If instructions are stripped of ALL implementation guidance (even high-level patterns), they become useless specifications. Example: "Implement skill tree system" with no context about data structure or integration points.

**Bad Example**:
```markdown
# TOO VAGUE:
**Title**: Implement Specialist Skill Trees
**Goal**: Add progression system
**Deliverable**: src/core/skill_trees.py
**Acceptance**: Tests pass
```

**Good Example**:
```markdown
**Title**: Implement Specialist Skill Trees
**Goal**: Enable specialists to unlock stat bonuses and abilities through skill point allocation
**Success Metrics**: Players spend 20+ minutes exploring skill options; 80% of specialists have custom builds
**Deliverables**:
  - src/core/skill_trees.py (skill tree logic)
  - data/skill_trees.json (30+ skills across 6 specialties)
  - tests/test_skill_trees.py (15+ tests, 80%+ coverage)
**Constraints**:
  - Max 5 skill tiers per specialty
  - Skills must be JSON-configurable
  - Prerequisites supported (skill A requires skills B+C)
**Acceptance Criteria**:
  - Unit tests: 15+ tests covering unlock logic, prerequisites, stat application
  - Integration: Can allocate points via UI, effects apply immediately
  - Manual QA: Can unlock all 30 skills through normal gameplay
**Owner**: AI Agent — Est: 5 days
**Risk**: Medium — Complex prerequisite logic
**Rollback**: Feature-flagged OFF by default
```

**Mitigation**:
- Include non-functional constraints (performance, UX)
- Specify data structures (JSON schema)
- Define integration points (which systems interact)
- Provide acceptance test specifications

---

### RISK #4: Documentation Becomes Outdated Immediately ⚠️ MEDIUM
**Severity**: MEDIUM  
**Impact**: Docs show incorrect current state after refactor

**Description**: Documenting "current state" is a snapshot. As soon as code changes, docs are wrong. Need maintenance strategy.

**Mitigation**:
- Add "Last Verified" dates to all docs
- Add "Next Review" date (30 days from last update)
- Document test commands to verify current state
- Add CI check that fails if docs > 60 days old

**Example Doc Header**:
```markdown
# UI System - Current State Documentation

**Last Verified**: 2025-10-21
**Next Review**: 2025-11-21 (monthly)
**Verification Command**: `python -m pytest tests/test_ui/ -v`
**Current Test Results**: 42/42 passing (as of last verified date)
```

---

### RISK #5: .github/instructions/ Files Are Agent Instructions ⚠️ MEDIUM
**Severity**: MEDIUM  
**Impact**: Changing these files changes how GitHub Copilot behaves

**Description**: Files in `.github/instructions/` are loaded by GitHub Copilot as context. These are NOT typical documentation - they are **agent behavior specifications**. Refactoring them incorrectly could break Copilot's ability to help with this project.

**Current State**:
- 10 instruction files define coding standards, patterns, workflows
- These ARE instructions (correct location)
- BUT they contain examples (code snippets showing patterns)

**Question**: Should .github/instructions/ be refactored?

**Recommendation**: 
- **DO NOT** refactor .github/instructions/ files - they are correctly formatted
- Code examples in these files are **pattern demonstrations** not implementation details
- These files teach agents "how to think" about this project
- Exception: Add "current state" metadata (test status, last review dates)

---

### RISK #6: plan/new-vision-IMPORTANT.md Is 1,358 Lines ⚠️ MEDIUM
**Severity**: MEDIUM  
**Impact**: Single massive file is difficult to refactor safely

**Description**: The main planning document is enormous and contains:
- High-level vision (desired state) ✓
- Detailed implementation specs (MIXED) ⚠️
- Code examples (should be removed) ✗
- Acceptance criteria (desired state) ✓

**Current Sections** (by classification):
- Executive Summary → KEEP (vision)
- Phase 1-6 Tasks → REFACTOR (remove code, keep outcomes)
- Implementation checklists → SPLIT (move current done items to docs, keep future as instructions)
- Code examples → REMOVE (violates instruction standard)

**Recommendation**: Split into multiple instruction files:
```
plan/
  vision-overview.md (high-level mission)
  phase-1-core-loop.md (incident resolution, automation)
  phase-2-progression.md (skill trees, dual-class, prestige)
  phase-3-team-dynamics.md (relationships, personalities)
  phase-4-economy.md (contracts, investments)
  phase-5-ui-polish.md (animations, tutorial)
  phase-6-endgame.md (achievements, leaderboards)
```

---

### RISK #7: Test Status Unknown for Most Systems ⚠️ MEDIUM
**Severity**: MEDIUM  
**Impact**: Cannot document accurate current test coverage

**Description**: Documentation requires "Current Test Status" but tests haven't been run in this session. Need to:
1. Run full test suite: `python -m pytest tests/ -v --tb=short`
2. Document pass/fail counts
3. Note any skipped or xfailed tests
4. Document how to run tests for each subsystem

**Action Required**: Run tests before finalizing any documentation files.

---

### RISK #8: Many Root-Level Files Should Be Archived ⚠️ LOW
**Severity**: LOW  
**Impact**: Clutter, confusion, outdated information

**Description**: 21 markdown files in root directory. Many appear to be commit message templates, implementation summaries, or historical reports that should be archived:

**Candidates for Archive**:
- `BURNOUT_COMMIT_MESSAGE.md`
- `CRITICAL_FIXES_COMMIT_MESSAGE.md`
- `LOGGING_COMMIT_MESSAGE.md`
- `BURNOUT_SYSTEM_IMPLEMENTATION.md`
- `LOGGING_IMPLEMENTATION_SUMMARY.md`
- `UI_IMPLEMENTATION_SUMMARY.md`

**Recommendation**:
```bash
mkdir docs/archive/
git mv *_COMMIT_MESSAGE.md docs/archive/
git mv *_IMPLEMENTATION.md docs/archive/
git mv *_SUMMARY.md docs/archive/
```

Keep only:
- README.md (user-facing)
- COMMIT_MESSAGE.md (active template)
- PLAYER_GUIDE.md (user-facing)

---

### RISK #9: No CI/CD Integration for Doc Validation ⚠️ LOW
**Severity**: LOW  
**Impact**: Docs drift out of sync with code

**Description**: No automated checks to ensure documentation stays current. Need CI job that:
- Runs tests mentioned in docs
- Verifies file paths referenced in docs exist
- Checks "Last Review" dates aren't > 60 days old
- Fails build if docs are stale

**Recommendation**: Add `.github/workflows/doc-validation.yml` after refactor

---

### RISK #10: Prestige System vs Multiple Runs Confusion ⚠️ LOW
**Severity**: LOW  
**Impact**: Game design clarity

**Description**: plan/new-vision-IMPORTANT.md mentions "prestige" and "resets" but also emphasizes this is NOT an offline idle game. Need to clarify:
- Is prestige a full reset (lose everything)?
- Or is it New Game+ (keep some progress)?
- How does this fit "Active Strategy Tycoon" vision?

**Recommendation**: Add explicit prestige design doc clarifying:
- What persists across prestige (unlocks, bonuses)
- What resets (money, specialists, contracts)
- Why players want to prestige (permanent bonuses)
- How long first run to prestige (target: 2-4 hours)

---

## ⭐ TOP 5 IMPLEMENTATION TASKS (Priority Order)

### TASK #1: Refactor plan/new-vision-IMPORTANT.md ⚡ CRITICAL
**Priority**: P0 - MUST DO FIRST  
**Estimated Time**: 3-4 hours  
**Owner**: Human + AI Agent

**Why Critical**: This is the master planning document. All other refactoring depends on understanding this vision.

**Approach**:
1. Read entire file (1,358 lines)
2. Extract high-level vision → `plan/vision-overview.md`
3. Split phase tasks → `plan/phase-{1-6}-*.md` (6 new files)
4. Remove ALL code snippets
5. Keep acceptance criteria, deliverables, success metrics
6. Move completed checklist items to docs/PROGRESS.md

**Acceptance Criteria**:
- 7 new instruction files created (vision + 6 phases)
- Zero code snippets in instruction files
- All acceptance criteria preserved
- All success metrics preserved
- Deliverable paths listed (no content)

**Output Files**:
```
plan/
  vision-overview.md (200 lines)
  phase-1-core-loop.md (250 lines)
  phase-2-progression.md (250 lines)
  phase-3-team-dynamics.md (200 lines)
  phase-4-economy.md (200 lines)
  phase-5-ui-polish.md (200 lines)
  phase-6-endgame.md (150 lines)
```

---

### TASK #2: Document Current Test Infrastructure ⚡ HIGH
**Priority**: P1 - BLOCKING FOR DOCS  
**Estimated Time**: 1 hour  
**Owner**: AI Agent

**Why High Priority**: Cannot write accurate docs without knowing test status.

**Approach**:
1. Run: `python -m pytest tests/ -v --tb=short --collect-only` (list all tests)
2. Run: `python -m pytest tests/ -v --tb=short` (execute tests)
3. Document results in `docs/TEST_STATUS.md`
4. Document per-system test commands
5. Add test counts to each system doc

**Acceptance Criteria**:
- TEST_STATUS.md created with full results
- Test pass/fail counts documented
- Instructions for running tests by subsystem
- Example: "Run incident tests: `pytest tests/test_incident*.py -v`"

**Output File**:
```
docs/TEST_STATUS.md
---
Last Run: 2025-10-21
Total Tests: {COUNT}
Passing: {COUNT}
Failing: {COUNT}
Skipped: {COUNT}
Coverage: {PERCENT}%

Per-Subsystem Breakdown:
- Incident System: {COUNT} tests, {PERCENT}% passing
- Specialist System: {COUNT} tests, {PERCENT}% passing
...
```

---

### TASK #3: Create Documentation Templates ⚡ HIGH
**Priority**: P1 - ENABLES SYSTEMATIC WORK  
**Estimated Time**: 30 minutes  
**Owner**: Human

**Why High Priority**: Need consistent structure for 50+ doc files.

**Approach**:
1. Create `docs/templates/INSTRUCTION_TEMPLATE.md`
2. Create `docs/templates/DOCUMENTATION_TEMPLATE.md`
3. Document in `docs/templates/REFACTORING_GUIDE.md` how to apply

**Acceptance Criteria**:
- Two template files created
- Guide explains when to use each
- Examples show before/after refactoring

**Output Files**:
```
docs/templates/
  INSTRUCTION_TEMPLATE.md
  DOCUMENTATION_TEMPLATE.md
  REFACTORING_GUIDE.md
```

---

### TASK #4: Refactor docs/ Files to Current State ⚡ MEDIUM
**Priority**: P2 - AFTER TASK #2  
**Estimated Time**: 4-5 hours  
**Owner**: AI Agent (batch processing)

**Why Medium Priority**: Depends on test status (Task #2) but unblocks clarity.

**Approach**:
1. Process 18 docs/ files systematically
2. Use DOCUMENTATION_TEMPLATE.md for structure
3. For each file:
   - Extract current state facts
   - Add verbatim TODOs
   - Add file references with existence check
   - Add test status from TEST_STATUS.md
   - Add last review date
   - Remove future plans (move to plan/ if needed)

**Acceptance Criteria**:
- All 18 docs/ files updated
- No desired-state language remains
- All files include test status
- All files include file references
- All files include verbatim TODOs

**Output**: 18 updated documentation files in docs/

---

### TASK #5: Archive Historical Root Files ⚡ LOW
**Priority**: P3 - CLEANUP  
**Estimated Time**: 15 minutes  
**Owner**: AI Agent

**Why Low Priority**: Quality of life, not blocking.

**Approach**:
1. Create `docs/archive/` directory
2. Move completed commit message templates
3. Move completed implementation summaries
4. Update README.md to reference archive
5. Add docs/archive/README.md explaining contents

**Acceptance Criteria**:
- docs/archive/ created
- 10-15 files moved
- Archive documented
- Root directory cleaner

**Output**:
```
docs/archive/
  README.md (explains archive purpose)
  BURNOUT_COMMIT_MESSAGE.md
  CRITICAL_FIXES_COMMIT_MESSAGE.md
  ... (10-15 historical files)
```

---

## 📊 FILE INVENTORY SUMMARY

| Location | Total Files | Instructions | Documentation | Mixed |
|----------|-------------|--------------|---------------|-------|
| plan/ | 1 | 0 | 0 | 1 |
| docs/ | 18 | 1 | 2 | 15 |
| root/ | 21 | 0 | 10 | 11 |
| .github/instructions/ | 10 | 0 | 3 | 7 |
| **TOTAL** | **50** | **1** | **15** | **34** |

**Key Insight**: 68% of files (34/50) are MIXED content requiring careful separation.

---

## ✅ RECOMMENDED EXECUTION SEQUENCE

### Week 1: Foundation
1. **Day 1**: Complete TASK #1 (refactor main plan)
2. **Day 2**: Complete TASK #2 (test status)
3. **Day 3**: Complete TASK #3 (templates)

### Week 2: Systematic Refactoring
4. **Day 1-2**: Complete TASK #4 (docs/ files) - 9 files/day
5. **Day 3**: Refactor root/ files using templates
6. **Day 4**: Review .github/instructions/ (decide: refactor or leave)
7. **Day 5**: Complete TASK #5 (archive), create PR

### Week 3: Review & Polish
8. **Day 1**: Create REVIEW_SUMMARY.md final version
9. **Day 2**: Write brutally honest review log
10. **Day 3**: Final QA, merge PR

**Total Estimated Time**: 10-12 working days

---

## 🎯 SUCCESS CRITERIA

### Instruction Files
- [ ] Zero code snippets or implementation details
- [ ] All contain: Title, Goal, Success Metrics, Deliverables, Constraints, Acceptance Criteria, Owner, Risk, Rollback
- [ ] Acceptance criteria specify exact tests required
- [ ] Deliverables list file paths (no content)
- [ ] All are priority-ranked

### Documentation Files
- [ ] Accurately reflect CURRENT repository state
- [ ] Include verbatim TODOs from existing files
- [ ] Include test status with exact commands
- [ ] Include file references (verified to exist)
- [ ] Include "Last Verified" and "Next Review" dates
- [ ] No desired-state language

### Repository Cleanliness
- [ ] Root directory has <10 .md files
- [ ] Historical files archived to docs/archive/
- [ ] README.md is user-facing
- [ ] COMMIT_MESSAGE.md is active template

---

## 🔄 ROLLBACK PLAN

If refactoring causes issues:

1. **Immediate Rollback**:
   ```bash
   git checkout backup/pre-refactor
   git branch -D refactor/instructions-docs
   ```

2. **Partial Rollback** (if some files are good):
   ```bash
   git checkout backup/pre-refactor -- plan/specific-file.md
   ```

3. **Undo Last Commit**:
   ```bash
   git reset --soft HEAD~1
   git restore --staged .
   ```

---

## 📝 NEXT STEPS

**IMMEDIATE ACTIONS** (in order):

1. Create backup branch: `git checkout -b backup/pre-refactor`
2. Create working branch: `git checkout -b refactor/instructions-docs`
3. Execute TASK #1: Refactor plan/new-vision-IMPORTANT.md
4. Execute TASK #2: Document test status
5. Execute TASK #3: Create templates
6. Begin systematic docs/ refactoring (TASK #4)

**DECISION POINTS**:

- [ ] Should .github/instructions/ be refactored? (Recommendation: NO)
- [ ] Should root files be archived? (Recommendation: YES)
- [ ] Split large files or refactor in-place? (Recommendation: SPLIT)

---

## 🚨 FINAL WARNING

**This is a HIGH-RISK, HIGH-VALUE refactoring.**

- **Risk**: Data loss if automated without review
- **Value**: Clean separation enables autonomous agent execution
- **Time**: 10-12 days of focused work
- **Requirement**: Manual human review at each checkpoint

**DO NOT** attempt to automate this entire refactoring in one go. Process in small batches with review between each batch.

---

**Prepared by**: GitHub Copilot Agent  
**Date**: 2025-10-21  
**Status**: Ready for human review and execution authorization
