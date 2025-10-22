# UI Layout - Management Simulation Style

This document describes the new UI layout inspired by management simulation games.

## Screen Layout (1280x720)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  HUD Overlay (Top Bar)                                      Day 1, $50K │
├──────────┬──────────────────────────────────────────────────────────────┤
│          │                                                               │
│ Dashboard│           SPECIALIST ROSTER PANEL (300px tall)               │
│ Widgets  │  ┌──────────┬──────────┬──────────┐                         │
│ (220px)  │  │ Alice    │ Bob      │ Charlie  │                         │
│          │  │ Network  │ Crypto   │ Forensics│                         │
│ 💰Budget │  │ Lvl 3    │ Lvl 5    │ Lvl 2    │                         │
│ $50,000  │  │ Burnout: │ Burnout: │ Burnout: │                         │
│ +$5,000  │  │ ▓░░░ 25% │ ▓▓░░ 40% │ ▓░░░ 15% │                         │
│          │  │ ✅ Avail │ 🔧 Busy  │ ✅ Avail │                         │
│ 🏢Client │  └──────────┴──────────┴──────────┘                         │
│ Active:6 │  [Click specialist to select for assignment]                │
│ Sat: 85% │                                                               │
│          ├───────────────────────────────────────────────────────────────┤
│ ⏱️ SLA   │          INCIDENT QUEUE PANEL (340px tall)                   │
│ Comp:95% │  ┌────────────────────────────────────────────────────────┐ │
│ Active12 │  │ 🔴 DDoS Attack          Difficulty: 3/5    ⏰ 05:23    │ │
│          │  │    Client: TechCorp...  📋 Network Security             │ │
│ 📋 Incid │  │    SLA: 300s remaining                                  │ │
│ Pending3 │  ├────────────────────────────────────────────────────────┤ │
│ Active12 │  │ 🟡 Malware Infection    Difficulty: 2/5    ⏰ 12:45    │ │
│          │  │    Client: Finance...    📋 Cryptography                │ │
│ 😰Burnou │  │    SLA: 765s remaining                                  │ │
│ Avg: 35% │  ├────────────────────────────────────────────────────────┤ │
│ Crit: 1  │  │ 🟢 Phishing Campaign    Difficulty: 1/5    ⏰ 18:02    │ │
│          │  │    Client: Retail...     📋 Social Engineering          │ │
└──────────┴──┴────────────────────────────────────────────────────────┴─┘
             [Click incident to select for assignment]
```

## UI Components

### Left Sidebar - Dashboard (220px wide)
- Small widgets showing key metrics
- Budget status (money, profit/loss)
- Client count and satisfaction
- SLA compliance rate
- Incident counts
- Team burnout levels
- Click widget to see detailed panel

### Main Area - Specialist Roster (1040px wide, 300px tall)
- Card-based layout showing team members
- 3 cards per row (220x120px each)
- Each card shows:
  * Specialist name and specialty
  * Current level
  * Burnout bar (visual progress bar)
  * Status indicator (available/busy/resting/critical)
  * Color-coded border on hover/selection
- Click to select specialist for assignment

### Main Area - Incident Queue (1040px wide, 340px tall)
- List-based layout showing pending incidents
- Each row shows:
  * Incident type with severity icon
  * Client name (truncated)
  * Required specialty
  * Difficulty rating (1-5)
  * SLA countdown timer (MM:SS format)
  * Color-coded based on urgency
  * Left bar colored by severity
- Click to select incident for assignment
- Scrollable if more than visible rows

## Interaction Flow

### Assignment Workflow
1. Click a specialist card → Highlights with colored border
2. Click an incident row → Triggers assignment
3. Event published to game logic
4. Notification shows "Assignment attempted!"
5. Selections cleared

OR:

1. Click an incident row → Highlights with colored border
2. Click a specialist card → Triggers assignment
3. Event published to game logic
4. Notification shows "Assignment attempted!"
5. Selections cleared

### Color Coding

**Specialist Status:**
- 🟢 Green dot = Available
- 🟠 Orange dot = Busy with incident
- 🔵 Blue dot = Resting
- 🔴 Red dot = Critical burnout

**Burnout Bar:**
- Green: 0-30% (healthy)
- Yellow: 30-60% (caution)
- Orange: 60-80% (warning)
- Red: 80-100% (critical)

**Incident Severity (left bar):**
- Green: Difficulty 1 (easy)
- Yellow: Difficulty 2 (medium)
- Orange: Difficulty 3-4 (hard)
- Red: Difficulty 5 (critical)

**SLA Timer:**
- Green: >50% time remaining
- Yellow: 25-50% time remaining
- Orange: <25% time remaining
- Red: Overdue (negative time)

## Visual Design Principles

1. **Dark Theme**: Dark background (15, 15, 25) for reduced eye strain
2. **High Contrast**: Light text (220, 220, 230) on dark backgrounds
3. **Color-Coded Status**: Immediate visual feedback via colors
4. **Card-Based**: Specialists shown as cards for easy scanning
5. **List-Based**: Incidents shown as list for efficiency
6. **Clear Hierarchy**: Visual weight guides eye to important info
7. **Hover Feedback**: Cards/rows brighten on hover
8. **Selection Feedback**: Bold borders show selected items
9. **Progress Bars**: Visual burnout levels (no numbers needed)
10. **Icons**: Emoji/symbols for quick recognition

## Inspiration From Management Sims

**Similar to RimWorld:**
- Left sidebar with key stats
- Main area shows "colonists" (our specialists)
- Bottom area shows tasks/jobs (our incidents)

**Similar to Prison Architect:**
- Card-based staff view
- Task queue with urgency indicators
- Click-to-assign workflow

**Similar to Theme Hospital:**
- Staff roster with status indicators
- Visual progress bars
- Color-coded urgency

## Benefits Over Previous UI

1. **Visibility**: All specialists visible at once (was hidden)
2. **Context**: All incidents visible at once (was hidden)
3. **Workflow**: Clear 2-click assignment (was unclear how to assign)
4. **Feedback**: Color coding shows status at a glance
5. **Management**: Feels like managing a team (was abstract)
6. **Engagement**: Visual cards > dashboard widgets alone
7. **Clarity**: Purpose of each area is obvious
8. **Scalability**: Scrolling supports growth

## Technical Implementation

**Files Created:**
- `src/ui/panels/specialist_roster_panel.py` - Specialist card grid
- `src/ui/panels/incident_queue_panel.py` - Incident list with scrolling

**Files Modified:**
- `src/ui/game_ui.py` - Integrated new panels, assignment workflow
- `src/ui/panels/__init__.py` - Export new panel classes

**Event Flow:**
```
User clicks specialist → _on_specialist_selected() → Store selection
User clicks incident   → _on_incident_selected()   → Store selection
Both selected?         → _attempt_assignment()     → Publish event
                                                    → Clear selections
                                                    → Show notification
```

**Rendering Order:**
1. Background fill
2. HUD overlay (top bar)
3. Dashboard panel (left sidebar)
4. Specialist roster (main top)
5. Incident queue (main bottom)
6. Detail panel (modal if open)
7. Notifications (always on top)
