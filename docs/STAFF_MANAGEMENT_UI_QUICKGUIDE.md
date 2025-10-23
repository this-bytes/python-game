# Staff Management UI - Quick Visual Guide

## Layout Overview

```
┌─ CYBERSECURITY FIRM ── Dashboard › [Current View] ──── Budget: $45,200 ── Time: 1,245s ──┐
├──────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  ┌─ Dashboard ─┐  ┌──── SPECIALIST ROSTER ────────────────────────┐  ┌─ WORKLOAD ──┐   │
│  │ • Clients   │  │                                               │  │ Team Util  │   │
│  │ • Budget    │  │  [Alice ⭐]  [Bob]  [Carol]  [Dave]           │  │ ████░░░░ │   │
│  │ • SLAs      │  │  Level 5    Level 3  Level 4   Level 2        │  │ 65%        │   │
│  │ • Team      │  │  ✅ Avail   🔧 Busy  ✅ Avail  💤 Rest        │  │            │   │
│  │ • Economy   │  │  Burnout:   Burnout: Burnout: Burnout:        │  │ Avg Burn   │   │
│  │            │  │  35% 🟢    72% 🟡   40% 🟢   25% 🟢           │  │ ████░░░░ │   │
│  └────────────┘  │                                               │  │ 42.5%      │   │
│                  │  ┌──── INCIDENT QUEUE ────────────────────┐  │  │            │   │
│                  │  │                                         │  │  │ Balance    │   │
│                  │  │ 🔴 DDoS Attack        Network Sec   2m │  │  │ ████████░░│   │
│                  │  │ 🟡 Malware Infection  Incident Re  5m │  │  │ 7.2/10     │   │
│                  │  │ 🟢 Data Exfil Attempt App Sec     8m │  │  │            │   │
│                  │  │ 🔴 Ransomware Threat  Network Sec  1m │  │  │ Backlog: 4 │   │
│                  │  │ 🟡 API Compromise     App Sec     6m │  │  │ Available: │   │
│                  │  │                                         │  │  │ 2/4 specs  │   │
│                  │  └─────────────────────────────────────────┘  │  └────────────┘   │
│                  └───────────────────────────────────────────────┘                     │
│                                                                  ┌─ TEAM MGMT ───┐   │
│                                                                  │               │   │
│                                                                  │ 👤 Hire Entry │   │
│                                                                  │ 👥 Hire Mid   │   │
│                                                                  │ 🛌 Rest All   │   │
│                                                                  │ ⬆️  Promote   │   │
│                                                                  │ 🚪 Fire       │   │
│                                                                  │ 📊 Details    │   │
│                                                                  │               │   │
│                                                                  └───────────────┘   │
│                                                                  ┌─ ASSIGNMENT ──┐   │
│                                                                  │               │   │
│                                                                  │ Specialist:   │   │
│                                                                  │ Alice (Lvl 5) │   │
│                                                                  │ Network Sec   │   │
│                                                                  │               │   │
│                                                                  │ Incident:     │   │
│                                                                  │ DDoS Attack   │   │
│                                                                  │ Req: Network  │   │
│                                                                  │               │   │
│                                                                  │ ✓ Excellent   │   │
│                                                                  │                    │
│                                                                  │ [Confirm] [Reset] │
│                                                                  └───────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Panel Interactions

### 1. Workload Analytics Panel

**What It Shows**:
- Team utilization percentage (how busy everyone is)
- Average burnout level (team stress)
- Balance score (is work evenly distributed?)
- Incident backlog count
- Available specialists count

**What It Helps You Decide**:
- Do I need to hire more staff?
- Is my team overworked?
- Should I rest some specialists?
- Can I handle more clients?

**Color Guide**:
- 🟢 Green: Healthy (0-50%)
- 🟡 Yellow: Caution (50-75%)
- 🟠 Orange: Warning (75-90%)
- 🔴 Red: Critical (90%+)

---

### 2. Team Management Panel

**Available Actions** (enabled/disabled based on game state):

| Action | Cost | Enables When | Impact |
|--------|------|--------------|--------|
| 👤 Hire Entry | $2,000 | Budget ≥ $2,000 | Adds junior specialist |
| 👥 Hire Mid | $4,000 | Budget ≥ $4,000 | Adds experienced specialist |
| 🛌 Rest All | Free | Burnout > 70% | Reduces team burnout |
| ⬆️ Promote | Varies | Level < 10 | Increases specialist level |
| 🚪 Fire | Refund | Multiple specs | Removes specialist |
| 📊 Details | Free | Always | View detailed stats |

**When to Use Each**:
- **Hire Entry**: Early game, limited budget
- **Hire Mid**: Mid-game, ready to invest
- **Rest All**: Team burnout rising (yellow/orange/red)
- **Promote**: Specialist reaching level cap
- **Fire**: Reducing costs, severe budget crisis
- **Details**: Need deep information about specialist

---

### 3. Assignment Workflow Panel

**The Assignment Process**:

```
┌─────────────────────────────────────────────┐
│ STEP 1: SELECT SPECIALIST                   │
│ ⏳ Click a specialist in the Roster         │
│                                             │
│ Example: You click "Alice"                  │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ STEP 2: SELECT INCIDENT                     │
│ Specialist: Alice (Level 5, Network Sec)    │
│ ⏳ Click an incident in the Queue           │
│                                             │
│ Example: You click "DDoS Attack"            │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ STEP 3: REVIEW COMPATIBILITY                │
│ Specialist: Alice (Level 5)                 │
│ Specialty: Network Security                 │
│                                             │
│ Incident: DDoS Attack                       │
│ Required: Network Security                  │
│ Level Req: 2                                │
│                                             │
│ Analysis: ✓ EXCELLENT MATCH                 │
│ (Specialty matches, level adequate)         │
│                                             │
│ [Confirm]  [Reset]                          │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ STEP 4: RESULT                              │
│                                             │
│ ✓ Assigned to Alice                         │
│                                             │
│ [Reset]                                     │
└─────────────────────────────────────────────┘
```

**Possible Outcomes**:

- ✓ **Excellent Match**: Specialty + Level both perfect → Do it!
- ⚠ **Level Mismatch**: Specialty matches but underleveled → May fail
- ✗ **Incompatible**: Specialty mismatch or unavailable → Choose someone else

---

## Common Gameplay Sequences

### Scenario 1: Early Game (Building Team)

1. **Check Workload Analytics**: Team util 40%, no backlog → Relax
2. **Check Budget**: $15,000 available → Time to hire!
3. **Click "Hire Entry"**: Add junior specialist
4. **Assign New Hire**: Select + select incident + confirm
5. **Repeat**: Next assignment

### Scenario 2: Mid Game (Team Growing)

1. **Check Workload**: Util 75%, Balance 6.2 → Okay but watch
2. **Check Incidents**: 8 backlog → Getting busy
3. **Consider Actions**: Promote promising specialist
4. **Assign Incidents**: Use workflow to match specialists
5. **Monitor Burnout**: Use Analytics to prevent crisis

### Scenario 3: Crisis (Team Overworked)

1. **Check Workload**: Util 90%, Avg Burn 65% → CRISIS!
2. **Check Incidents**: 15 backlog → Drowning
3. **Take Action**: "Rest All" to recovery
4. **Consider Hiring**: Add more specialists if budget allows
5. **Delegate**: Get backlog down to manageable level

---

## Strategic Tips

### Using Analytics
- **Green Zone (0-60%)**: Safe to take more clients
- **Yellow Zone (60-75%)**: Monitor closely, don't overcommit
- **Orange Zone (75-90%)**: Rest specialists, consider hiring
- **Red Zone (90%+)**: Emergency! Must reduce workload NOW

### Using Staff Management
- **Always have room to hire**: Keep $5,000+ buffer
- **Don't let burnout rise**: Use "Rest All" before it hits 70%
- **Level up strategically**: Promote specialists for specialty diversity
- **Fire only in crisis**: Losing specialists costs reputation

### Using Assignment Workflow
- **Green matches only?**: NO! Some orange/yellow matches are worth risk
- **Specialty mismatch is danger**: Can result in incident failure
- **Level matters less**: An overleveled specialist is fine
- **Trust the analysis**: If it says "Incompatible", it is!

---

## Hotkeys & Quick Controls

| Key | Action |
|-----|--------|
| Click Specialist | Select in workflow |
| Click Incident | Select in workflow |
| [Confirm] | Execute assignment |
| [Reset] | Clear selections |
| [Hire Entry] | Hire junior specialist |
| [Rest All] | Rest overworked team |
| H | Show help overlay |
| ESC | Close modal / Exit |

---

## Visual Indicators at a Glance

### Specialist Status (Roster Panel)
- ✅ **Green dot**: Available
- 🔧 **Orange dot**: Currently assigned
- 💤 **Blue dot**: Resting
- ⚠️ **Red dot**: Critical burnout

### Incident Priority (Queue Panel)
- 🔴 **Red**: Critical (>90% time used)
- 🟡 **Yellow**: Urgent (60-90% time used)
- 🟠 **Orange**: Important (30-60% time used)
- 🟢 **Green**: Low (< 30% time used)

### Action Button States
- 🔵 **Blue + Hover**: Available and clickable
- ⚫ **Gray**: Disabled (condition not met)
- ⭐ **Highlighted**: Currently selected

---

## Troubleshooting

### "I can't hire more specialists"
- Check budget in top-right corner
- Need $2,000+ for entry level
- Check workload analytics first

### "Why is this action grayed out?"
- Rest All: Team burnout < 70%
- Promote: All specialists at level 10
- Fire: Only one specialist left

### "Why can't I assign this specialist?"
- Already assigned (check Roster panel)
- Specialty mismatch (check Requirements)
- Level too low (check Level Requirement)

### "I don't understand the compatibility?"
- ✓ Excellent: Both specialty AND level perfect
- ⚠ Level Mismatch: Specialty good, but level low
- ✗ Incompatible: Specialty doesn't match

---

## Summary

The enhanced UI gives you **complete visibility and control** over team management:

1. **Analytics** = Understand your team
2. **Management** = Make strategic decisions
3. **Workflow** = Execute with confidence

Master these three panels and you'll manage your team like a pro!
