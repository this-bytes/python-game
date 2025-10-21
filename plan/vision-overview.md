# 🎮 Cybersecurity Firm Tycoon - Game Vision

**Type**: INSTRUCTION (Desired-State Only)  
**Version**: 1.0  
**Created**: 2025-10-21  
**Priority**: P0-Critical (Defines entire project direction)

---

## 🎯 Goal

**Create an Active Strategy Tycoon game where players progress from manual incident triage (responder) → automated systems (manager) → empire orchestration (CEO).**

Players must make strategic decisions about incident assignment, team composition, and automation rules while managing a cybersecurity incident response firm.

---

## 📊 Success Metrics

- **Engagement Duration**: Player can play for 2+ hours without getting bored
- **Prestige Appeal**: 80%+ of players who reach prestige reset to play again
- **Core Loop Satisfaction**: 30-second loop (Incident → Assignment → Resolution → Reward) feels satisfying
- **Progression Clarity**: Players understand their progression path within 10 minutes
- **Automation Balance**: Early game 90% manual, late game 90% automated (smooth transition)

---

## 🎮 Game Identity

### What This Game IS:
- **Active Decision-Making**: Player makes strategic choices about WHO handles WHAT
- **Strategic Team Management**: Compose teams, manage burnout, optimize automation rules
- **Progressive Automation**: Early game = manual triage, Late game = systems work for you
- **Prestige Replayability**: Reset for permanent bonuses, multiple runs with different strategies

### What This Game IS NOT:
- ❌ NOT an offline idle game - No "click once, play for 8 hours offline"
- ❌ NOT a facility management sim - No break rooms, training centers, office decorations
- ❌ NOT a market-driven economy - No random global events (tech booms, recessions)
- ❌ NOT a dating sim - Relationships are mechanical (synergy bonuses), not narrative

### The 30-Second Core Loop:
```
Incident Spawns → Player Decides → Specialist Works → Incident Resolves → Rewards Earned → REPEAT
```

---

## 🎯 The 7 Core Systems (Non-Negotiable)

Every feature must serve one or more of these systems:

1. **Incident Generation** - Continuous spawning based on client contracts
2. **Specialist Assignment** - Decision-based player choices (THE core mechanic)
3. **Specialist Progression** - Leveling, XP, stats, abilities
4. **Team Dynamics** - Friendships/rivalries create synergy bonuses
5. **Economy** - Money management, retainer contracts, investments
6. **Automation** - Late-game scripts reduce tedium without removing strategy
7. **Prestige** - Reset for permanent bonuses and replayability

**If a feature doesn't clearly fit into one of these 7 systems, it shouldn't exist.**

---

## 📦 Deliverables

### Critical Path Timeline
- **12 weeks** to playable v1.0
- **6 months** to feature-complete

### Phase Structure
- Phase 1 (Weeks 1-2): Core Loop Refinement
- Phase 2 (Weeks 3-4): Progression Depth
- Phase 3 (Weeks 5-6): Team Dynamics
- Phase 4 (Weeks 7-8): Economy & Contracts
- Phase 5 (Weeks 9-10): UI/UX Polish
- Phase 6 (Weeks 11-12): Endgame & Replayability

**See individual phase instruction files** for detailed task specifications.

---

## ⚙️ Non-Functional Constraints

- **Performance**: Maintain 60 FPS on mid-tier hardware
- **Data-Driven**: All game parameters in JSON config files (hot-reloadable)
- **Test Coverage**: 80%+ coverage for all game systems
- **Plugin Architecture**: All game systems as plugins with event-driven communication
- **Save/Load**: Complete game state serialization in <2 seconds
- **Accessibility**: WCAG AA+ contrast, keyboard navigation support

---

## ✅ Acceptance Criteria

### v1.0 Playability Requirements
- [ ] Player can play continuously for 2+ hours without boredom
- [ ] Core loop (30 seconds) is satisfying and clear
- [ ] Progression feels meaningful (visible advancement)
- [ ] Automation transition feels natural (manual → automated)
- [ ] Prestige system creates replayability desire
- [ ] No game-breaking bugs
- [ ] 60 FPS performance maintained
- [ ] Save/load works reliably

### Technical Requirements
- [ ] 80%+ test coverage across all systems
- [ ] All 7 core systems fully implemented
- [ ] Plugin architecture operational
- [ ] Event bus handling all system communication
- [ ] JSON configuration for all game parameters
- [ ] Documentation complete for all systems

### Player Experience Requirements
- [ ] Tutorial guides first 10 minutes
- [ ] UI is intuitive (can play without external guide)
- [ ] Feedback is immediate and clear
- [ ] Progression is visible and rewarding

---

## 👤 Owner & Estimate

**Owner**: Development Team (Human + AI Agents)  
**Estimated Duration**: 12 weeks to v1.0, 6 months to feature-complete  
**Dependencies**: None (this is the starting point)

---

## ⚠️ Risk Assessment

**Risk Level**: Medium

### Potential Risks
1. **Scope Creep**: Feature requests beyond 7 core systems - Probability: High - Impact: High
2. **Automation Balance**: Too much automation removes player agency - Probability: Medium - Impact: High
3. **Engagement Failure**: 30-second loop not satisfying - Probability: Medium - Impact: Critical
4. **Technical Debt**: Plugin architecture not properly utilized - Probability: Medium - Impact: Medium

### Mitigation Strategy
- Strict adherence to "7 Core Systems" rule (reject features outside scope)
- Regular playtesting (weekly) to validate engagement
- Prototype core loop first before adding depth
- Architecture review before each phase

---

## 🔄 Rollback Plan

**If game vision proves unachievable:**

1. **Pivot Decision Point**: Week 6 (after Phase 3)
2. **Success Check**: Can player enjoy 30-minute session?
3. **If NO**: Reassess core loop, potentially simplify to pure idle mechanics
4. **If YES**: Continue with current vision

**Fallback Vision**: Pure idle tycoon (remove active decision-making if engagement fails)

---

## 🚀 Merge Requirements

**Before considering this vision "locked in":**

- [ ] Core loop prototype playable (Phase 1 complete)
- [ ] Playtesting validates 30-second loop satisfaction
- [ ] Technical architecture supports vision (plugin system operational)
- [ ] Team consensus on direction
- [ ] No major technical blockers identified

---

## 📝 Notes

**Design Philosophy**: "Vibe Coding"
- Iteration speed over perfect architecture
- JSON-first design for easy tweaking
- Pygame as renderer only (not logic container)
- Hot-reloadable configuration without restart
- Backend-driven debugging for live parameter editing

**Player Psychology Target**:
- Dopamine hits from incident completion
- Sense of progression from specialist leveling
- Strategic satisfaction from optimization
- "One more run" prestige appeal

**Terminology Standards**: Use established cybersecurity industry terms - do NOT make up words. This is a simulation of a real-world industry.

---

## 🚫 FORBIDDEN CONTENT

**This file contains ONLY**:
- High-level game vision
- Success metrics
- Core systems definition
- Non-functional constraints

**This file does NOT contain**:
- Implementation code
- Function signatures
- Step-by-step developer instructions
- Current state descriptions

For implementation details, see phase-specific instruction files.

---

**Created**: 2025-10-21  
**Last Updated**: 2025-10-21  
**Next Review**: After Phase 1 completion
