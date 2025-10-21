# SOC STARTUP MANAGEMENT GAME - VISION DOCUMENT

**Game Title**: SOC Tycoon / Security Operations Center / [TBD]

**Core Concept**: Manage a boutique Security Operations Center startup. Hire specialists, acquire clients across different industries, handle their incident response, manage budget, grow the business or face bankruptcy.

---

## THE 30-SECOND HOOK

*You're starting a Security Operations Center startup. You hire specialists, sign clients from different industries (each with different threat landscapes), manage their security incidents under SLA pressure, balance hiring costs vs. revenue, and try to grow without going broke. Miss SLAs → clients leave → you downsize → game over or reset with new strategy.*

---

## CORE GAME LOOP

```
┌─ DAY STARTS ─────────────────────────────────────────┐
│                                                        │
│  1. THREATS SPAWN FOR EACH CLIENT                     │
│     (Different industries = different threat types)   │
│                                                        │
│  2. PLAYER ASSIGNS SPECIALISTS TO INCIDENTS           │
│     (Who handles what? Based on specialties)          │
│                                                        │
│  3. RESOLUTION HAPPENS                                │
│     (Based on specialist skill, SLA timer)            │
│                                                        │
│  4. CONSEQUENCES & FEEDBACK                           │
│     - SLA Met? Client satisfaction ↑                  │
│     - SLA Missed? Client satisfaction ↓               │
│     - Client satisfaction → money in / out            │
│                                                        │
│  5. END OF DAY: BUDGET UPDATE                          │
│     - Revenue from clients                            │
│     - Salaries paid to specialists                    │
│     - Profit/loss calculated                          │
│     - Can hire/fire based on budget?                  │
│                                                        │
│  6. REPEAT                                             │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## GAME SYSTEMS (All Interconnected)

### 1. CLIENT SYSTEM
**The heart of the game**: Different clients = different threat landscapes

#### Client Properties
```json
{
  "client_id": "acme_corp",
  "company_name": "ACME Corp",
  "industry": "Banking",
  "threat_landscape": ["fraud", "ransomware", "insider_threats"],
  "monthly_contract_value": 15000,
  "sla_response_time": 300,  // seconds to respond
  "sla_resolution_time": 3600,  // seconds to resolve
  "satisfaction": 0.85,  // 0-1, affects retention
  "contract_renewal_in_days": 30,
  "monthly_incident_rate": 5  // average incidents per month
}
```

#### Client Types by Industry
**Banking/Finance**
- Threats: Fraud, ransomware, insider threats, compliance violations
- SLA: Strict (300s response, 1h resolution)
- Revenue: High ($10k-20k/month)
- Incidents: Medium frequency (3-5/month), HIGH severity

**E-Commerce**
- Threats: DDoS, payment fraud, data exfiltration
- SLA: Medium (600s response, 2h resolution)
- Revenue: Medium ($5k-10k/month)
- Incidents: High frequency (8-12/month), MEDIUM severity

**Healthcare**
- Threats: Ransomware, HIPAA violations, patient data breach
- SLA: Strict (180s response, 30min resolution)
- Revenue: Medium-High ($8k-15k/month)
- Incidents: Low-Medium frequency (2-4/month), CRITICAL severity

**Government**
- Threats: APT, supply chain attacks, classified data theft
- SLA: Strictest (60s response, unlimited resolution once started)
- Revenue: Low ($3k-5k/month - red tape) but stable
- Incidents: Rare (0-2/month) but DEVASTATING severity

**Tech/SaaS**
- Threats: Data exfiltration, account compromise, API abuse
- SLA: Medium (900s response, 3h resolution)
- Revenue: Low-Medium ($4k-8k/month)
- Incidents: High frequency (10-15/month), LOW-MEDIUM severity

#### Client Satisfaction Mechanics
```
Satisfaction = (SLAs Met / Total SLAs) * 100
If Satisfaction drops below:
  - 70%: Warning, client considers leaving
  - 50%: Client unhappy, increased chance of leaving
  - 30%: Contract terminated, client leaves

Satisfaction Recovery:
  - Successful SLA responses: +2% per incident
  - Proactive security improvements: +5% per quarter
  - Incident-free month: +3% bonus
```

#### Client Lifecycle
1. **Acquisition**: Pitch new clients (turn-based decision, random chance based on budget spent)
2. **Active Contract**: Manage incidents monthly
3. **Contract Renewal**: Client decides to renew or leave (based on satisfaction)
4. **Termination**: Client leaves if too unhappy OR you fire them (to free up budget)

---

### 2. SPECIALIST SYSTEM
**The people who do the work**

#### Specialist Properties
```json
{
  "specialist_id": "alice_001",
  "name": "Alice Chen",
  "specialties": ["Network Security", "Incident Response"],
  "level": 5,
  "xp": 2340,
  "salary_per_month": 6000,
  "monthly_incidents_handled": 8,
  "burnout": 35,  // 0-100, affects performance
  "sick_leave_days": 0,
  "current_clients_assigned": ["acme_corp", "globex_inc"]
}
```

#### Hiring & Firing
```
Hiring:
  - Junior Specialist: $4k/month, learns slowly, handles easy incidents
  - Mid-Level: $6k/month, balanced, handles most incidents
  - Senior: $9k/month, expensive, can handle critical incidents
  - Cost: 3 months salary as hiring/training cost upfront

Firing:
  - Instant: Saves salary but damages team morale
  - Voluntary Resignation: If too burned out, they leave (lose specialist)
  - Effect: Can trigger if budget is too tight (bankruptcy avoided by downsizing)
```

#### Specialist Specialties Matter
Different specialists good at different threat types:
```
Alice (Network Security) → Better at: DDoS, Ransomware
Bob (Application Security) → Better at: Data Exfiltration, API Abuse
Carol (Forensics) → Better at: Post-breach investigation, Evidence gathering
```

#### Burnout & Morale
- **Burnout accumulates** when handling many incidents
- **High burnout** = worse performance, more mistakes
- **Recovery**: Rest days, but costs productivity
- **Threshold**: >80% burnout → specialist requests time off OR leaves

---

### 3. BUDGET SYSTEM
**The ticking clock of capitalism**

#### Monthly Income
```
Total Income = Sum of (Client Contract Values) + Interest on Savings
If SLA missed: Income for that client reduced by 5-50% based on severity
If client leaves: Income drops immediately and permanently
```

#### Monthly Expenses
```
Total Expenses = (Sum of Specialist Salaries) + Operational Costs

Operational Costs:
  - Infrastructure: $2k/month (baseline, scales with client count)
  - Tools/Software licenses: $1k/month
  - Office/Overhead: $1k/month
  - Insurance: $500/month
```

#### Budget States
```
Profitable Month:
  - Income > Expenses
  - Can save money or invest in hiring/improvements
  - Growing trend = prestige points

Loss-Making Month:
  - Expenses > Income
  - Drawing from reserves
  - If reserves hit $0: BANKRUPTCY END GAME

Critical Threshold:
  - If expenses > income AND you have <$10k reserves
  - FORCED TO DOWNSIZE (fire a specialist)
  - Cannot refuse: Specialist fired automatically
  - Game over if you can't afford to keep 1 specialist
```

#### Profit Calculation
```python
monthly_profit = total_income - total_expenses
total_reserves += monthly_profit  # Or -= if negative

if total_reserves < 0:
    Game Over → Bankruptcy
```

---

### 4. INCIDENT SYSTEM
**The moment-to-moment gameplay**

#### Incident Generation
```
Each month, each client generates incidents based on:
  - Industry threat landscape
  - Client's SLA requirements
  - Random variance

Example:
  ACME Corp (Banking) this month:
    - 1x Ransomware attempt (HIGH severity)
    - 2x Fraud attempts (MEDIUM severity)
    - 1x Compliance audit (LOW, administrative)
```

#### Incident Response Flow
```
1. INCIDENT SPAWNS
   - Type: Ransomware
   - Client: ACME Corp
   - Severity: HIGH
   - SLA Response: 5 minutes
   - SLA Resolution: 1 hour
   - Time Remaining: 60 minutes

2. PLAYER DECISION: Assign Specialist
   - Alice (Network Security, Level 5): 92% success rate
   - Bob (Application Security, Level 3): 65% success rate
   - Carol (Forensics, Level 4): 78% success rate
   - [Unassigned]: No one → Incident fails, SLA missed

3. RESOLUTION HAPPENS
   - Time to resolve: Based on specialist skill, incident complexity
   - Success/Failure: Probability-based, skill affects odds
   
4. CONSEQUENCES
   - Success, on time: Client satisfaction +5%, $reward
   - Success, late: Client satisfaction +2%, $reward - penalty
   - Failure: Client satisfaction -15%, $penalty, incident escalates
   
5. SPECIALIST UPDATE
   - Alice gains 150 XP
   - Alice burnout +8 (incident caused fatigue)
```

#### Decision Branching (Optional)
If you want deeper decisions per incident:
```
After specialist assigned, player chooses approach:
  A) Quick Patch (Fast, risky, might break things)
  B) Full Investigation (Slow, thorough, safer)
  C) Isolate & Monitor (Defensive, slow resolution but no damage)

Each choice affects:
  - Resolution time
  - Success probability
  - Follow-up consequences
  - Client satisfaction differently
```

---

### 5. PROGRESSION SYSTEM
**How the game gets harder/more interesting**

#### Prestige/Meta-Progression
```
After bankruptcy or reaching end-game:
  - Prestige Points earned based on:
    - Final company size
    - Total revenue generated
    - Longest active contract
    - Specialists promoted
    
  - Prestige unlocks permanent bonuses for next run:
    - Starting capital increased
    - First specialist gets bonus XP
    - Contract negotiation bonuses
    - Lower operational costs
    
  - Multiple difficulty tiers (Prestige 0-5)
```

#### Client Acquisition Difficulty Scales
```
Early game: Easier to get first 2-3 clients
Mid game: Harder to get new clients, must compete
Late game: Must have proven track record to get new clients
```

#### Specialist Growth
```
As specialists level up:
  - Better success rates
  - Handle more severe incidents
  - Command higher salary
  - Burnout recovers faster
  
New specialists enter market as demand increases:
  - Generated randomly
  - Can recruit specific specialties if budget allows
```

---

## THE END GAME / FAILURE STATES

### Win Condition: (Multiple Paths)
1. **Survival**: Maintain a profitable company for 12 months → Prestige earned
2. **Growth**: Grow from 1 client to 5+ clients → Prestige multiplier
3. **Stability**: Zero forced downsizing over full year → Bonus prestige
4. **Dominance**: Manage 10+ clients simultaneously → Maximum prestige

### Lose Conditions:
1. **Bankruptcy**: Reserves hit $0 → Game Over
2. **Complete Team Loss**: All specialists fired or quit → Game Over
3. **Total Client Loss**: All clients leave → Can recover with 1, but hard
4. **Cascade Failure**: Miss multiple SLAs → Clients mass-leave → Bankruptcy

### Prestige/New Game+
```
After completing a run, start new with:
  - Same core mechanics
  - But with permanent bonuses from prestige
  - Harder client resistance (scaling)
  - New client types unlock
  - Specialists start with higher potential
```

---

## WHAT MAKES THIS THEMATIC & DEEP

### It's Authentically SOC
- Real SOCs manage multiple clients
- Real SOCs balance hiring costs vs. client needs
- Real SOCs lose clients over SLA misses
- Real SOCs face burnout and specialist turnover
- Real SOCs grow or fail based on client satisfaction

### Strategic Decisions
- WHO to hire (specialist type, level, cost)
- WHEN to fire (stay profitable or lose clients?)
- WHICH clients to take (high revenue vs. high SLA pressure?)
- HOW to handle incidents (quick fix vs. thorough?)
- WHEN to expand vs. consolidate

### Continuous Engagement
- Incidents happen naturally (not waves)
- Budget pressure is constant (not artificial)
- Client satisfaction creates urgency (not fake urgency)
- Specialist morale matters (burnout = real consequence)

### Replayability
- Different client mixes → different strategies
- Prestige unlocks → different starting conditions
- RNG on incidents → no two runs identical
- Multiple paths to success (fast growth vs. slow stability)

---

## PLUGIN ARCHITECTURE (Why This Is Buildable)

### Current Reusable Systems
✅ Specialist model (already have)
✅ Team dynamics/relationships (already have)
✅ Burnout system (already have)
✅ Event system (already have)
✅ JSON config structure (already have)
✅ Plugin architecture (already have)

### New Systems Needed
❌ Client management system
❌ SLA tracking system
❌ Budget/money system
❌ Contract renewal mechanics
❌ Incident assignment (single incident, multiple specialists option)
❌ Satisfaction tracking

### Plugin-Friendly Design
Each system can be a plugin:
- `ClientManagementPlugin` - handles all client logic
- `BudgetPlugin` - handles money, expenses, income
- `SLAPlugin` - handles SLA timers, satisfaction
- `IncidentDispatchPlugin` - handles incident assignment

---

## WHY THIS IS SALVAGEABLE

### What You Keep (60% of code)
- Specialist model + leveling
- Team dynamics + relationships
- Burnout mechanics
- Event bus architecture
- JSON configuration
- UI framework
- Plugin system
- Testing infrastructure

### What You Replace (30% of code)
- Game loop (from "assign incident" to "manage SOC")
- Incident generation (from random to per-client)
- UI flow (from single view to multi-client management)

### What You Add (10% of code)
- Client system (new)
- Budget system (new)
- SLA system (new)
- Contract renewal (new)

**Estimate**: 2-3 weeks of focused development to get playable prototype

---

## IMMEDIATE NEXT STEPS

1. **Validate**: Do you want to build THIS game?
2. **Document**: Detail each system (client types, SLA mechanics, etc.)
3. **Prototype**: Build core loop (1 client, 1 specialist, basic incidents)
4. **Iterate**: Add complexity layer by layer
5. **Polish**: UI, balance, feels good to play

---

## QUESTIONS TO ANSWER

- How many clients can the player manage simultaneously? (Start: 1-3, max: 10?)
- What's the campaign length? (1 month? 1 year? Infinite until bankruptcy?)
- Should incidents have decision branches or just succeed/fail?
- Can players pause and think or is it real-time?
- How much of the SOC operations should be "management sim" vs. "action"?

---
