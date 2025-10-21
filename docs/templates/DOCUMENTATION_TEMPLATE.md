# [System/Feature Name] - Current State Documentation

**Type**: DOCUMENTATION (Current-State Only)  
**Last Verified**: YYYY-MM-DD  
**Next Review**: YYYY-MM-DD (30 days from last verified)  
**Status**: [Active | Deprecated | In Development | Needs Review]

---

## 📋 Overview

**Brief description of what this system/feature currently does.**

Example: "The Specialist Skill Tree system currently provides 5 skills per specialty, loaded from `data/skill_trees.json`. Players can allocate skill points earned through leveling to unlock stat bonuses."

---

## 🔍 Current Implementation

### Files
**List exact file paths and verify they exist.**

- `src/core/skill_tree_system.py` - ✅ EXISTS - 247 lines
- `src/ui/panels/skill_tree_panel.py` - ✅ EXISTS - 183 lines
- `data/skill_trees.json` - ✅ EXISTS - 89 lines
- `tests/test_skill_tree_system.py` - ✅ EXISTS - 156 lines

**Verification**: Run `ls -la [file paths]` to confirm existence.

### Key Components
**Verbatim list of classes/functions currently implemented (no code).**

- `SkillTreeSystem` class (src/core/skill_tree_system.py)
  - `unlock_skill(specialist, skill_id)` - Unlocks skill if requirements met
  - `get_available_skills(specialist)` - Returns unlockable skills
  - `apply_skill_effects(specialist, skill)` - Applies stat bonuses
  
- `SkillTreePanel` UI (src/ui/panels/skill_tree_panel.py)
  - Displays skill tree visualization
  - Handles point allocation UI
  - Shows skill descriptions on hover

### Configuration
**Current configuration files with structure overview.**

`data/skill_trees.json` (current structure):
```json
{
  "network_security": {
    "name": "Network Security Specialist",
    "tiers": [...]
  }
}
```

**6 specialties defined**: Network Security, Malware Analysis, Social Engineering, Cryptography, Digital Forensics, Compliance

---

## ✅ Current Features

**What currently works (verified features only).**

- [x] Skill points earned on level up
- [x] Skills unlockable via UI
- [x] Stat bonuses apply to specialist
- [x] Prerequisites enforced
- [x] 30 total skills across 6 specialties
- [x] Skill descriptions show on hover

---

## ⚠️ Known Issues / TODOs

**Verbatim TODOs from code/docs (with file references).**

### From `src/core/skill_tree_system.py`:
```python
# Line 47: TODO: Add respec functionality (costs money)
# Line 102: TODO: Implement skill cooldowns for active abilities
# Line 156: TODO: Validate skill tree integrity on load
```

### From `data/skill_trees.json`:
```json
// TODO: Add tier 5 skills for all specialties
// TODO: Balance stat bonuses (some skills overpowered)
```

### From GitHub Issues:
- Issue #42: "Skill tree UI doesn't show locked skills clearly"
- Issue #67: "Skills don't save/load correctly"

---

## 🧪 Test Status

**Current test results and how to run tests.**

### Run Tests
```bash
# All skill tree tests
pytest tests/test_skill_tree_system.py -v

# Specific test
pytest tests/test_skill_tree_system.py::test_unlock_skill_with_prerequisites -v
```

### Last Test Run: 2025-10-21
- **Total Tests**: 12
- **Passing**: 11 ✅
- **Failing**: 1 ❌
  - `test_respec_functionality` - Not implemented yet
- **Skipped**: 0
- **Coverage**: 78% (below 80% target)

### Test Breakdown
| Test Category | Count | Status |
|--------------|-------|---------|
| Unlock Logic | 4 | ✅ All passing |
| Prerequisites | 3 | ✅ All passing |
| Stat Application | 3 | ✅ All passing |
| Respec | 1 | ❌ Failing (not implemented) |
| UI Integration | 1 | ✅ Passing |

---

## 🔗 Dependencies

**Systems this feature depends on (verified).**

- **SpecialistSystem**: Provides specialist object, level, XP
- **GameState**: Manages skill point allocation
- **EventBus**: Publishes `skill_unlocked` events
- **SaveManager**: Persists allocated skills

**Verified by**: Checking imports in `src/core/skill_tree_system.py`

---

## 📊 Usage Statistics

**If metrics are tracked, include current usage data.**

- **Average skills per specialist**: 2.3 (from analytics)
- **Most popular skill**: "Packet Analysis" (47% of specialists)
- **Respec usage**: N/A (not implemented)

---

## 🔄 Recent Changes

**Last 3-5 significant changes (from git log).**

```
commit abc123 - 2025-10-15 - Added tier 3 skills for all specialties
commit def456 - 2025-10-10 - Fixed prerequisite validation bug
commit ghi789 - 2025-10-05 - Implemented skill point UI
```

**Verification**: Run `git log --oneline -- src/core/skill_tree_system.py | head -5`

---

## 💾 Data Format

**Current data structure (exact schema from code).**

### Skill Object (from `data/skill_trees.json`):
```json
{
  "id": "packet_analysis",
  "name": "Packet Analysis",
  "description": "+10% speed on Network Security incidents",
  "tier": 1,
  "cost": 1,
  "prerequisites": [],
  "effects": {
    "speed_multiplier": 1.1,
    "specialty_filter": "Network Security"
  }
}
```

**Required Fields**: id, name, description, tier, cost, effects  
**Optional Fields**: prerequisites, specialty_filter

---

## 🚨 Breaking Changes

**Any known breaking changes or migration notes.**

- **v1.2.0 → v1.3.0**: Skill IDs changed from numeric to string
  - **Migration**: Run `python scripts/migrate_skill_ids.py`
- **v1.1.0**: Added prerequisite support
  - **Migration**: No action needed (backward compatible)

---

## 📍 Integration Points

**Where this system connects to others (current state).**

### Events Published:
- `skill_unlocked` - When specialist unlocks skill
- `skill_point_allocated` - When skill point spent

### Events Subscribed:
- `specialist_leveled_up` - Grants skill point

### API Endpoints (if applicable):
- `POST /api/skills/unlock` - Unlock skill for specialist
- `GET /api/skills/available/{specialist_id}` - Get available skills

---

## 🎯 Recommended Next Steps

**Human action items based on current state.**

1. **Fix Failing Test**: Implement respec functionality or remove test
2. **Increase Coverage**: Add tests for edge cases (target: 80%+)
3. **Address TODOs**: Review 3 TODO comments in code
4. **Update Documentation**: Add examples to user guide
5. **Performance Review**: Profile skill tree rendering (UI lag reported)

---

## 🔍 Verification Commands

**Commands to verify current state claims.**

```bash
# Verify files exist
ls -la src/core/skill_tree_system.py src/ui/panels/skill_tree_panel.py data/skill_trees.json

# Count skills in JSON
cat data/skill_trees.json | jq '.[] | .tiers | length' | awk '{s+=$1} END {print s}'

# Run tests
pytest tests/test_skill_tree_system.py -v --tb=short

# Check git history
git log --oneline -- src/core/skill_tree_system.py | head -10
```

---

## 🚫 FORBIDDEN CONTENT IN DOCUMENTATION

**DO NOT INCLUDE:**
- Desired-state language ("should have", "will implement")
- Future plans or roadmaps
- Unverified claims about implementation
- Code that doesn't exist yet
- Placeholder content

**ALLOWED:**
- Exact code excerpts (verbatim quotes)
- Current file paths (verified to exist)
- TODOs from actual code (with line numbers)
- Test results from actual test runs
- Git commit history (verifiable)

---

**Template Version**: 1.0  
**Last Updated**: 2025-10-21
