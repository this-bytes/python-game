# UI Visual Design

## Screen Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Cybersecurity Firm - Idle/Tycoon/RPG           Money: $50,000  Time: 123.4s│  <- Header Bar (Blue)
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌────────────────┐  ┌──────────────────┐  ┌──────────────────┐            │
│  │ Specialist [▢][─][ X ]                │  [ Metrics Panel ][─][X]         │
│  │ Roster          │  │ Active Incidents │  │                  │            │
│  ├────────────────┤  ├──────────────────┤  ├──────────────────┤            │
│  │ ┌────────────┐ │  │ ┌──────────────┐ │  │ ┌────┐  ┌────┐  │            │
│  │ │Alice Chen  │ │  │ │|DDoS Attack  │ │  │ │$50K│  │420 │  │            │
│  │ │Lv.5 Network│ │  │ │★★★★☆        │ │  │ │Money│  │Incdt│  │            │
│  │ │[====75%====]│ │  │ │Network Sec  │ │  │ └────┘  └────┘  │            │
│  │ │AVAILABLE   │ │  │ │SLA: 04:35   │ │  │ ┌────┐  ┌────┐  │            │
│  │ └────────────┘ │  │ │$5,000       │ │  │ │95% │  │12  │  │            │
│  │                │  │ └──────────────┘ │  │ │SLA │  │Fail│  │            │
│  │ ┌────────────┐ │  │                  │  │ └────┘  └────┘  │            │
│  │ │Bob Smith   │ │  │ ┌──────────────┐ │  │                  │            │
│  │ │Lv.3 App Sec│ │  │ │|Malware      │ │  │ Stats:           │            │
│  │ │[====40%====]│ │  │ │★★☆☆☆        │ │  │ • XP: 1,500     │            │
│  │ │WORKING     │ │  │ │Application  │ │  │ • Clients: 5    │            │
│  │ └────────────┘ │  │ │SLA: 12:04   │ │  │ • Util: 75%     │            │
│  │       ↓        │  │ │$2,500       │ │  │                  │            │
│  │ (scroll bar)   │  │ └──────────────┘ │  │                  │            │
│  └────────────────┘  └──────────────────┘  └──────────────────┘            │
│                                                                               │
│  [Assign Specialist]  ← Button (enabled when both selected)                 │
│                                                                               │
│  Hotkeys: 1-6: Panels | SPACE: Pause | H: Help | +/-: Speed                │
│                                                                               │
│                                               ┌──────────────────┐   ┐       │
│                                               │ ✓ Success!       │   │       │
│                                               │ Alice assigned   │   │ Toast │
│                                               │ to DDoS Attack   │   │ Stack │
│                                               └──────────────────┘   ┘       │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Color Schemes

### Dark Cyber (Default)
```
Background:    #0F0F19 (Dark navy blue)
Panel BG:      #191928 (Slightly lighter)
Primary:       #00B4FF (Bright cyan blue)
Success:       #00FF64 (Bright green)
Warning:       #FFC800 (Yellow)
Danger:        #FF3232 (Bright red)
Text:          #DCDCE6 (Off-white)
Border:        #323250 (Dark gray-blue)
```

### Light Professional
```
Background:    #F0F0F5 (Light gray)
Panel BG:      #FFFFFF (White)
Primary:       #0078D7 (Microsoft blue)
Success:       #009600 (Green)
Warning:       #C89600 (Gold)
Danger:        #C80000 (Red)
Text:          #1E1E1E (Almost black)
Border:        #C8C8D2 (Light gray)
```

### Hacker Green
```
Background:    #000000 (Pure black)
Panel BG:      #050A05 (Very dark green)
Primary:       #00FF00 (Terminal green)
Success:       #00FF64 (Bright green)
Warning:       #FFFF00 (Yellow)
Danger:        #FF0000 (Red)
Text:          #00FF00 (Terminal green)
Border:        #009600 (Dark green)
```

## Component Details

### Specialist Card
```
┌─────────────────────┐
│ Alice Chen         │ ← Name (bold)
│ Lv.5  Network Sec  │ ← Level, Specialty
│ [■■■■■■■■□□] 75%   │ ← XP Progress Bar
│ ● AVAILABLE        │ ← Status (color-coded)
└─────────────────────┘
```

Status Colors:
- 🟢 AVAILABLE (green)
- 🟡 WORKING (yellow)
- 🔵 RESTING (blue)

### Incident Card
```
┌─────────────────────┐
│ |DDoS Attack        │ ← | = Urgency bar (left)
│ ★★★★☆ Difficulty   │ ← Stars for difficulty
│ Network Security    │ ← Specialty required
│ SLA: 04:35          │ ← Countdown timer
│ $5,000              │ ← Reward
│ PENDING             │ ← Status
└─────────────────────┘
```

Urgency Colors (left bar):
- 🟢 Green: >50% SLA remaining
- 🟡 Yellow: 20-50% SLA remaining
- 🔴 Red: <20% SLA remaining (CRITICAL!)

### KPI Card
```
┌──────────┐
│  $50,000 │ ← Large value (colored)
│          │
│  Money   │ ← Label
└──────────┘
```

### Button States
```
Normal:   [  Button Text  ]
Hover:    [  Button Text  ] (brighter)
Pressed:  [  Button Text  ] (darker)
Disabled: [  Button Text  ] (grayed out)
```

### Notification Toast
```
┌─────────────────┐
│ ✓ Success!      │ ← Icon + Title (colored)
│ Operation done  │ ← Message
└─────────────────┘
  (fades out after 3s)
```

Types:
- ℹ️ INFO (blue)
- ✓ SUCCESS (green)
- ⚠ WARNING (yellow)
- ✗ ERROR (red)

### Help Overlay (press H)
```
┌───────────────────────────┐
│    Hotkey Reference       │
├───────────────────────────┤
│ 1         - Specialists   │
│ 2         - Incidents     │
│ 3         - Metrics       │
│ SPACE     - Pause/Resume  │
│ +         - Speed Up      │
│ -         - Speed Down    │
│ H         - This Help     │
│ ESC       - Close Panels  │
└───────────────────────────┘
```

## Interaction Patterns

### Panel Dragging
1. Click and hold title bar
2. Move mouse (panel follows cursor)
3. Release to drop

### Panel Controls
- 🔴 X button: Close panel
- ⚪ − button: Minimize panel
- ⚪ □ button: Maximize panel (if enabled)

### Selection
- Click specialist card → Blue border appears
- Click incident card → Blue border appears
- Both selected → Assign button becomes enabled

### Scrolling
- Mouse wheel in panel → Scroll content
- Scroll bar on right → Visual indicator

### Keyboard Shortcuts
- Number keys (1-6) → Toggle panels
- Space → Pause/unpause
- H → Show/hide help
- ESC → Close all panels

## Animation States

### Smooth Transitions
- Panel minimize: Shrink to title bar (0.2s)
- Panel maximize: Expand to full screen (0.2s)
- Button hover: Color brightens (instant)
- Button press: Color darkens (instant)
- Notification fade: Opacity 100% → 0% (0.5s)

### Visual Feedback
- Selection: Border changes to blue
- Hover: Slight brightness increase
- Click: Brief color change
- Status change: Immediate color update

## Responsive Layout

Panels maintain minimum sizes:
- Min width: 200px
- Min height: 100px

Default positions prevent overlap:
- Specialist Roster: (20, 80)
- Incident Queue: (420, 80)
- Metrics Panel: (840, 80)

Z-order: Last clicked panel appears on top

## Accessibility

- Clear visual hierarchy
- Color + text for status (not color alone)
- Keyboard shortcuts available
- Readable font sizes (14-24px)
- High contrast in all themes
- Clear hover states
- Descriptive button labels
