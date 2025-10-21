# Instruction & Documentation Refactoring Guide

**Version**: 1.0  
**Date**: 2025-10-21  
**Purpose**: Systematic guide for separating mixed content into instruction (desired-state) and documentation (current-state) files

---

## 🎯 Refactoring Philosophy

**The Core Principle**: 
- **Instructions** tell agents WHAT to achieve (outcomes, goals, success metrics)
- **Documentation** tells humans WHAT EXISTS NOW (current state, TODOs, test status)

**Never Mix**: Desired-state directives do not belong in documentation. Current-state facts do not belong in instructions.

---

## 📋 Classification Decision Tree

### Step 1: Read the File

Ask these questions:

1. **Does it contain code snippets showing implementation?**
   - YES → MIXED (needs separation)
   - NO → Continue to #2

2. **Does it contain "should", "will", "must implement" language?**
   - YES → INSTRUCTION content present
   - NO → Continue to #3

3. **Does it contain "currently", "exists", "last updated" language?**
   - YES → DOCUMENTATION content present
   - NO → Continue to #4

4. **Does it contain both future plans AND current state facts?**
   - YES → MIXED (needs separation)
   - NO → Classify based on primary content

### Step 2: Classify the File

| Primary Content | Classification | Action |
|----------------|----------------|--------|
| Future goals, acceptance criteria, deliverables | INSTRUCTION | Use instruction template |
| Current state, TODOs, test results | DOCUMENTATION | Use documentation template |
| Both future AND current | MIXED | Split into two files |

---

## 🔄 Refactoring Workflows

### Workflow A: Pure Instruction File

**When to use**: File is 90%+ future-oriented planning

**Steps**:
1. Copy `docs/templates/INSTRUCTION_TEMPLATE.md`
2. Rename to appropriate name in `plan/`
3. Extract goal, success metrics, deliverables
4. Remove ALL code snippets
5. Keep acceptance criteria
6. Add owner, estimate, risk assessment
7. Delete original if fully replaced

**Example**:
```
Before: docs/SKILL_TREE_IMPLEMENTATION.md (mixed)
After:  plan/phase-2-skill-trees.md (instruction only)
```

### Workflow B: Pure Documentation File

**When to use**: File is 90%+ current-state description

**Steps**:
1. Copy `docs/templates/DOCUMENTATION_TEMPLATE.md`
2. Rename appropriately in `docs/`
3. Add "Last Verified" date (TODAY)
4. List current files (verify they exist)
5. Extract verbatim TODOs with line numbers
6. Run tests, document results
7. Remove future plans (move to plan/ if needed)
8. Replace original file

**Example**:
```
Before: docs/RENDERING_AUDIT.md (mostly current)
After:  docs/RENDERING_AUDIT.md (documentation only - updated)
```

### Workflow C: Mixed File Requiring Split

**When to use**: File has significant future plans AND current state

**Steps**:
1. Read entire file, identify content blocks
2. Mark blocks as "CURRENT" or "FUTURE"
3. Create instruction file in `plan/` for FUTURE content
4. Create documentation file in `docs/` for CURRENT content
5. Ensure no content lost in split
6. Cross-reference the two files
7. Delete or archive original

**Example**:
```
Before: docs/PLUGIN_ARCHITECTURE.md (mixed)
After:  plan/phase-x-plugin-expansion.md (future features)
        docs/PLUGIN_ARCHITECTURE.md (current implementation)
```

---

## 📝 Content Separation Rules

### INSTRUCTION Content (Move to plan/)

**Identifying Features**:
- "Requirements", "Deliverables", "Acceptance Criteria"
- "Should", "Will", "Must implement"
- Goals, success metrics, KPIs
- Feature descriptions that don't exist yet
- Roadmaps, phases, sprints

**Handling**:
```markdown
# BEFORE (in docs/):
"The skill tree system should have 30+ skills across 6 specialties."

# AFTER (in plan/):
**Deliverables**: 30+ skills across 6 specialties
**Success Metric**: 80% of specialists have custom builds
```

### DOCUMENTATION Content (Keep in docs/)

**Identifying Features**:
- "Currently", "Exists", "Last updated"
- File paths with line numbers
- TODO comments from code
- Test results
- Git commit history
- Known bugs/issues

**Handling**:
```markdown
# BEFORE (mixed):
"The skill tree system should support respec. Currently has 30 skills."

# AFTER (in docs/):
**Current Features**:
- 30 skills across 6 specialties (verified in data/skill_trees.json)

**Known TODOs**:
- src/core/skill_tree_system.py:47 - TODO: Add respec functionality
```

---

## 🚫 Common Mistakes to Avoid

### Mistake #1: Keeping Code Snippets in Instructions

❌ **WRONG**:
```markdown
# Instruction file
Create skill tree system:

```python
class SkillTreeSystem:
    def unlock_skill(self, specialist, skill_id):
        # Implementation here
        pass
```
```

✅ **CORRECT**:
```markdown
# Instruction file
**Deliverable**: `src/core/skill_tree_system.py`
- Implements `unlock_skill(specialist, skill_id)` method
- Validates prerequisites before unlocking
- Applies stat bonuses to specialist
```

### Mistake #2: Future Plans in Documentation

❌ **WRONG**:
```markdown
# Documentation file
The skill tree currently has 30 skills. In the future, we will add tier 5 skills.
```

✅ **CORRECT**:
```markdown
# Documentation file
**Current Features**: 30 skills across tiers 1-4

**Known TODOs** (from data/skill_trees.json):
```json
// TODO: Add tier 5 skills for all specialties
```
```

### Mistake #3: Vague Instructions

❌ **WRONG**:
```markdown
# Instruction
**Goal**: Make skill trees better
**Deliverable**: Improve code
```

✅ **CORRECT**:
```markdown
# Instruction
**Goal**: Increase skill tree engagement by adding 10 tier-5 high-impact skills
**Success Metric**: Average skills per specialist increases from 2.3 to 4.0
**Deliverables**: 
  - data/skill_trees.json (add 10 tier-5 skills)
  - tests/test_skill_trees.py (add 5+ tests for tier-5)
**Acceptance**: Playtesting shows 60%+ specialists reach tier 5
```

---

## 🔍 Quality Checklist

### For Instruction Files

- [ ] No code snippets (function bodies, class definitions)
- [ ] File paths listed but no file contents
- [ ] Goal is one clear sentence
- [ ] Success metrics are quantitative
- [ ] Acceptance criteria specify exact tests
- [ ] Owner and estimate present
- [ ] Risk assessment present
- [ ] Rollback plan present

### For Documentation Files

- [ ] "Last Verified" date is TODAY
- [ ] All file paths verified to exist
- [ ] TODOs are verbatim from code (with line numbers)
- [ ] Test status from actual test run
- [ ] No future plans or "should/will" language
- [ ] Git history included (if relevant)
- [ ] Known issues listed (from code/issues)

---

## 📊 Example Refactorings

### Example 1: Simple Instruction

**Before** (docs/FEATURE_SPEC.md - mixed):
```markdown
# Skill Tree Feature

The skill tree system will allow specialists to unlock abilities.

Currently not implemented.

Implementation:
- Create SkillTreeSystem class
- Load skills from JSON
- Create UI panel

Code:
```python
def unlock_skill(self, skill_id):
    if skill_id in self.skills:
        return True
    return False
```

Success: Players use skill trees
```

**After** (plan/phase-2-skill-trees.md - instruction):
```markdown
# Specialist Skill Trees - Instruction

**Goal**: Enable specialists to unlock stat bonuses through skill point allocation

**Success Metrics**:
- 80% of specialists have allocated 3+ skill points
- Average time in skill tree UI: 5+ minutes per session

**Deliverables**:
- src/core/skill_tree_system.py
- src/ui/panels/skill_tree_panel.py
- data/skill_trees.json (30+ skills)
- tests/test_skill_trees.py (15+ tests, 80% coverage)

**Acceptance Criteria**:
- Unit tests: skill unlock, prerequisites, stat application
- Integration: Skills persist across save/load
- Manual QA: Can allocate all skills through normal gameplay

**Owner**: AI Agent — Est: 5 days
**Risk**: Medium
```

---

### Example 2: Pure Documentation

**Before** (docs/CURRENT_IMPLEMENTATION.md - mixed):
```markdown
# Current Implementation

The game currently has:
- 5 specialists
- 30 incidents types
- TODO: Add skill trees

Future plans:
- Add prestige system
- Add leaderboards
```

**After** (docs/CURRENT_IMPLEMENTATION.md - documentation):
```markdown
# Game Systems - Current State Documentation

**Last Verified**: 2025-10-21
**Next Review**: 2025-11-21

## Current Implementation

### Specialists
- **Count**: 5 specialists (verified in data/specialists.json)
- **File**: src/models/specialist.py (247 lines)
- **Tests**: 12 passing (pytest tests/test_specialist.py)

### Incidents
- **Count**: 30 incident types (verified in data/incidents.json)
- **File**: src/models/incident.py (189 lines)
- **Tests**: 18 passing (pytest tests/test_incident.py)

## Known TODOs

From src/models/specialist.py:
```python
# Line 87: TODO: Implement skill tree integration
```

From project backlog:
- Issue #23: "Add prestige system"
- Issue #45: "Add leaderboards"
```

---

## 🎯 Refactoring Checklist (Per File)

Before starting:
- [ ] Read entire file
- [ ] Classify as INSTRUCTION, DOCUMENTATION, or MIXED
- [ ] Choose appropriate workflow (A, B, or C)

During refactoring:
- [ ] Copy appropriate template
- [ ] Extract relevant content
- [ ] Remove forbidden content
- [ ] Verify file references exist
- [ ] Run tests (for documentation)
- [ ] Cross-check against checklist

After refactoring:
- [ ] Review changes with `git diff`
- [ ] Verify no content lost
- [ ] Test any file paths listed
- [ ] Commit with descriptive message

---

## 📦 Batch Processing Strategy

For large volumes (20+ files):

1. **Batch 1** (Days 1-2): plan/ files (highest priority)
2. **Batch 2** (Days 3-4): docs/ architecture files
3. **Batch 3** (Days 5-6): docs/ feature files
4. **Batch 4** (Day 7): root/ files (archive most)
5. **Batch 5** (Day 8): .github/instructions/ (review only)

**Commit after each batch** with clear message:
```
refactor(docs): Batch 2 - Convert architecture docs to current-state

- Updated docs/ARCHITECTURE_ROADMAP.md
- Updated docs/PLUGIN_ARCHITECTURE.md
- Updated docs/BACKEND_SPECIFICATION.md
- All files now reflect current state only
- Future plans moved to plan/ directory
```

---

## 🚀 Getting Started

1. Create backup: `git checkout -b backup/pre-refactor`
2. Create working branch: `git checkout -b refactor/instructions-docs`
3. Start with **plan/new-vision-IMPORTANT.md** (largest, most important)
4. Process systematically, batch by batch
5. Commit frequently with descriptive messages
6. Review each batch before moving to next

---

**Guide Version**: 1.0  
**Last Updated**: 2025-10-21  
**Maintained by**: Documentation team
