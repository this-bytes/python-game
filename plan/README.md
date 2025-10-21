# 📋 Game Development Plan - Instruction Files

**This directory contains INSTRUCTION files only - desired-state specifications for autonomous agents.**

---

## 🎯 Purpose

These files describe **WHAT to achieve**, not **HOW to implement**:
- Clear goals and success metrics
- Deliverable file paths (no code content)
- Acceptance criteria (testable outcomes)
- Risk assessments and rollback plans

**For implementation patterns**, see `.github/instructions/` files.

---

## 📁 File Structure

### Core Vision
- **vision-overview.md** - Game vision, 7 core systems, success metrics

### Phase Instructions (12-Week Critical Path)
1. **phase-1-core-loop.md** (Weeks 1-2) - Decision-based resolution, automation, difficulty
2. **phase-2-progression.md** (Weeks 3-4) - Skill trees, dual-class, equipment
3. **phase-3-team-dynamics.md** (Weeks 5-6) - Relationships, synergy, team building
4. **phase-4-economy.md** (Weeks 7-8) - Contracts, passive income, facilities
5. **phase-5-ui-polish.md** (Weeks 9-10) - Animations, tutorial, QOL features
6. **phase-6-endgame.md** (Weeks 11-12) - Prestige, achievements, leaderboards

---

## 🚀 How to Use These Files

### For AI Agents:
1. Read `vision-overview.md` first (understand game identity)
2. Execute phases in order (Phase 1 → Phase 6)
3. Follow acceptance criteria exactly
4. Refer to `.github/instructions/` for coding patterns
5. Document completed work in `docs/` directory

### For Humans:
1. Review phase instructions for clarity
2. Approve before agent execution
3. Playtest after each phase completion
4. Adjust JSON configs for balance tuning

---

## ✅ Instruction File Standards

Each instruction file contains:
- **Goal**: One-sentence player-facing improvement
- **Success Metrics**: Quantitative measurements
- **Deliverables**: File paths only (no implementation)
- **Acceptance Criteria**: Testable outcomes with test counts
- **Owner & Estimate**: Who and how long
- **Risk Assessment**: Probability and mitigation
- **Rollback Plan**: How to undo if fails

Each instruction file does NOT contain:
- ❌ Code snippets or function signatures
- ❌ Step-by-step implementation instructions
- ❌ Current state descriptions
- ❌ Algorithm details or data structures

---

## 📊 Progress Tracking

**Current Status**: Foundation complete, Phase 1 ready to execute

**Completed Phases**: None (starting)

**Next Milestone**: Phase 1 completion (Week 2)

**For detailed current state**, see `docs/` directory.

---

## 🔄 Archive

**plan/archive/** contains previous versions of instruction files for historical reference.

- `new-vision-IMPORTANT-original.md` - Original 1,358-line combined plan (archived 2025-10-21)

---

## 📝 Maintenance

**When to update these files**:
- Phase completion → Mark phase as complete
- Scope changes → Update affected phase instruction
- New patterns discovered → Update `.github/instructions/` (not here)

**When NOT to update these files**:
- Tracking current progress → Use `docs/PROGRESS.md`
- Documenting completed features → Use `docs/[FEATURE].md`
- Reporting bugs → Use GitHub Issues

---

**Last Updated**: 2025-10-21  
**Next Review**: After Phase 1 completion
