# [Feature Name] - Instruction Template

**Type**: INSTRUCTION (Desired-State Only)  
**Version**: 1.0  
**Created**: YYYY-MM-DD  
**Priority**: [P0-Critical | P1-High | P2-Medium | P3-Low]

---

## 🎯 Goal

**One sentence describing the player-facing improvement or system capability.**

Example: "Enable specialists to unlock stat bonuses and special abilities through skill point allocation, creating strategic build diversity."

---

## 📊 Success Metrics

**Quantitative measurements that prove this feature achieves its goal.**

- **Player Engagement**: [Target metric, e.g., "Players spend 20+ minutes exploring skill options"]
- **Adoption Rate**: [Target metric, e.g., "80% of specialists have custom builds within first prestige"]
- **Retention Impact**: [Target metric, e.g., "7-day retention increases by 15%"]
- **Performance**: [Target metric, e.g., "Skill UI loads in <100ms"]

---

## 📦 Deliverables

**Explicit artifacts by path - DO NOT include implementation content.**

- `src/core/[system_name].py` - [Brief description of responsibility]
- `src/ui/panels/[panel_name].py` - [Brief description of UI component]
- `data/[config_name].json` - [Brief description of configuration]
- `tests/test_[system_name].py` - [Brief description of test scope]
- `docs/[FEATURE_NAME].md` - [Design document]

**File References Only** - No code snippets, no implementation details.

---

## ⚙️ Non-Functional Constraints

**Performance, UX limits, technical requirements.**

- **Performance**: [e.g., "UI updates must not drop below 60 FPS"]
- **Accessibility**: [e.g., "All interactive elements minimum 40x40px touch targets"]
- **Localization**: [e.g., "All text must be in JSON config for translation"]
- **Data-Driven**: [e.g., "All game parameters in JSON, hot-reloadable"]
- **Compatibility**: [e.g., "Must work in both local and remote server modes"]

---

## ✅ Acceptance Criteria

### Unit Tests
- **Count**: [Minimum number of tests, e.g., "15+ tests"]
- **Coverage**: [Target coverage, e.g., "≥80% coverage for module"]
- **Edge Cases**: [Specific scenarios, e.g., "Test prerequisite validation, max level caps, invalid inputs"]

### Integration Tests
- **System Integration**: [e.g., "Skill effects apply immediately when incident assigned"]
- **Save/Load**: [e.g., "Allocated skills persist across save/load"]
- **Feature Flags**: [e.g., "Feature OFF by default, toggleable via features.json"]

### Manual QA Steps
1. [Step-by-step manual verification]
2. [Example: "Allocate skill point → verify stat increase in specialist panel"]
3. [Example: "Assign specialist with skill bonus → verify faster resolution time"]

### Documentation
- [ ] Feature documented in `docs/[FEATURE_NAME].md`
- [ ] Workflow updated in `.github/instructions/workflows.instructions.md` (if new pattern)
- [ ] User guide updated if player-facing

---

## 👤 Owner & Estimate

**Owner**: [Human | AI Agent | Specific Person]  
**Estimated Duration**: [X days]  
**Dependencies**: [List other tasks/features that must complete first]

---

## ⚠️ Risk Assessment

**Risk Level**: [Low | Medium | High | Critical]

### Potential Risks
1. **[Risk Name]**: [Description] - Probability: [Low/Med/High] - Impact: [Low/Med/High]
2. **[Risk Name]**: [Description] - Probability: [Low/Med/High] - Impact: [Low/Med/High]

### Mitigation Strategy
- [How to reduce risk #1]
- [How to reduce risk #2]

---

## 🔄 Rollback Plan

**If this feature causes issues:**

1. **Feature Flag**: Disable via `features.json` → `"feature_id": {"enabled": false}`
2. **Code Rollback**: `git revert [commit-hash]`
3. **Database Migration**: [If applicable, rollback steps]
4. **User Communication**: [What to tell players if rollback needed]

---

## 🚀 Merge Requirements

**Checklist before merge:**

- [ ] All tests passing (unit + integration)
- [ ] Code review completed by [reviewer name]
- [ ] QA signoff from [QA person]
- [ ] CI/CD pipeline green
- [ ] Documentation complete
- [ ] Performance benchmarks meet targets
- [ ] Feature flag configured (OFF by default for new features)
- [ ] Rollback plan tested

---

## 📝 Notes

**Any additional context, design decisions, or considerations.**

Example:
- "Skill trees follow standard 5-tier progression model"
- "JSON schema allows future expansion without code changes"
- "Design inspired by Path of Exile's passive tree, simplified"

---

## 🚫 FORBIDDEN CONTENT IN INSTRUCTIONS

**DO NOT INCLUDE:**
- Code snippets showing implementation
- Step-by-step "how-to" developer instructions
- Current code references explaining existing implementation
- Diagnostic logs or debug output
- Function signatures or class definitions

**ALLOWED:**
- File paths and structure
- High-level data structure concepts (e.g., "tree structure with parent-child relationships")
- Integration points (e.g., "connects to SpecialistSystem via event bus")
- JSON schema examples (data format only)

---

**Template Version**: 1.0  
**Last Updated**: 2025-10-21
