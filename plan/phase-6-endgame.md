# Phase 6: Endgame & Replayability

**Type**: INSTRUCTION (Desired-State Only)  
**Version**: 1.0  
**Created**: 2025-10-21  
**Priority**: P1-High  
**Timeline**: Weeks 11-12 (14 days)

---

## 🎯 Goal

**Create compelling endgame through prestige system, achievements, and leaderboards that drive replayability.**

---

## 📊 Success Metrics

- **Prestige Rate**: 80%+ of players who reach endgame prestige and replay
- **Achievement Completion**: Average 60%+ achievement completion per run
- **Multiple Runs**: 70%+ of players complete 2+ prestige runs
- **Leaderboard Engagement**: 40%+ of players check leaderboards
- **Session Duration**: Average 2+ hours per session after prestige implementation

---

## 📦 Deliverables

### Task 6.1: Prestige System
- `src/core/prestige_system.py` - Prestige reset and permanent bonuses
- `data/prestige_upgrades.json` - 30+ prestige upgrade options
- `src/ui/panels/prestige_panel.py` - Prestige UI and upgrade tree
- `tests/test_prestige.py` - 18+ tests, 80%+ coverage

### Task 6.2: Achievement System
- `src/core/achievement_system.py` - Achievement tracking and rewards
- `data/achievements.json` - 50+ achievements (bronze/silver/gold/platinum)
- `src/ui/panels/achievement_panel.py` - Achievement display UI
- `tests/test_achievements.py` - 15+ tests

### Task 6.3: Leaderboard System
- `src/core/leaderboard_system.py` - Score calculation and ranking
- Backend API integration for online leaderboards
- `src/ui/panels/leaderboard_panel.py` - Leaderboard UI
- `tests/test_leaderboards.py` - 12+ tests

---

## ⚙️ Non-Functional Constraints

- **Prestige Unlocks**: 5+ permanent bonuses per prestige
- **First Prestige Time**: Target 2-4 hours of gameplay
- **Achievement Difficulty**: 40% easy, 40% medium, 15% hard, 5% ultra-rare
- **Leaderboard Metrics**: Total income, fastest completion, highest combo, etc.
- **Score Calculation**: Prevents exploits, rewards skilled play

---

## ✅ Acceptance Criteria

**Unit Tests**: 45+ total tests, 80%+ coverage  
**Integration**: Prestige resets work, achievements unlock, leaderboards sync  
**Manual QA**: Complete prestige cycle, earn 20+ achievements  
**Playtest**: 80%+ prestige and replay after reaching endgame

---

## 👤 Owner & Estimate

**Task 6.1**: AI Agent — 5 days  
**Task 6.2**: AI Agent — 4 days  
**Task 6.3**: AI Agent — 3 days  

**Total**: 12 days (with 2-day buffer = 14 days / Weeks 11-12)

---

## ⚠️ Risk Assessment

**Risk Level**: High - Prestige must feel rewarding or players won't replay

**Mitigation**: 
- Permanent bonuses must be significant (20%+ impact)
- Testing with multiple prestige runs
- Balance prestige curve carefully (not too easy/hard)

---

## 🚀 Merge Requirements

- [ ] All tests passing
- [ ] 5+ playtesters complete prestige run
- [ ] 80%+ prestige and continue playing
- [ ] Achievements feel meaningful (not grindy)
- [ ] Leaderboards functional (if online features included)

---

## 📝 Notes

**Prestige Philosophy**: 
- First run teaches mechanics
- Second run explores optimization
- Third+ runs are for mastery and leaderboards

**Achievement Design**:
- Tie to 7 core systems (not arbitrary)
- Create "aha!" moments (discover strategy)
- Reward experimentation (use different builds)

**Leaderboard Design**:
- Multiple categories (various play styles)
- Weekly/monthly resets (fresh competition)
- Prevent cheating (server-side validation)

---

**Created**: 2025-10-21
