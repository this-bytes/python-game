# WebSocket Game UI - Visual Preview

## Landing Page (index.html)

The landing page features a modern launcher with server status detection:

**Key Features:**
- 🔒 Large logo and title
- 📝 Feature list with icons
- 🎮 "Launch Game" button
- ✅ Automatic server status check
- 🎨 Cyberpunk-themed design with gradients

**Color Scheme:**
- Background: Dark blue gradient (#0a0e27 → #1e2442)
- Primary accent: Bright cyan/green (#00ff88)
- Secondary accent: Cyan (#00ccff)
- Danger/alerts: Pink (#ff3366)

---

## Main Game Interface (game.html)

### Header Bar
```
┌─────────────────────────────────────────────────────────────┐
│ 🔒 Cybersecurity Firm          Money: $10,000  Day: 1       │
│                                Time: 00:12:34  [Connected]   │
└─────────────────────────────────────────────────────────────┘
```

### Main Layout

```
┌─────────────────────┬──────────────────────────────────────┐
│  👨‍💼 SPECIALISTS     │  🚨 ACTIVE INCIDENTS                 │
│  (5 total)          │  (10 active)                         │
├─────────────────────┼──────────────────────────────────────┤
│                     │                                      │
│ ┌─────────────────┐ │ ┌──────────────────────────────────┐ │
│ │ Alice Chen      │ │ │ DDoS Attack        [Unassigned] │ │
│ │ [Available] 🟢  │ │ │ Difficulty: 3                    │ │
│ │ Network Security│ │ │ Specialty: Network Security      │ │
│ │ Level: 5        │ │ │ [Assign Specialist] [button]     │ │
│ └─────────────────┘ │ └──────────────────────────────────┘ │
│                     │                                      │
│ ┌─────────────────┐ │ ┌──────────────────────────────────┐ │
│ │ Marcus          │ │ │ Ransomware                      │ │
│ │ [Busy] 🟡       │ │ │ [Assigned] 🟡                   │ │
│ │ Malware Analysis│ │ │ Assigned to: Marcus Rodriguez   │ │
│ │ Level: 3        │ │ │                                  │ │
│ └─────────────────┘ │ └──────────────────────────────────┘ │
│                     │                                      │
└─────────────────────┴──────────────────────────────────────┘

┌─────────────────────┬──────────────────────────────────────┐
│  🏢 CLIENTS         │  📊 STATISTICS                        │
│  (6 active)         │                                       │
├─────────────────────┼──────────────────────────────────────┤
│                     │                                      │
│ ┌─────────────────┐ │ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ │
│ │ TechCorp Inc.   │ │ │Total │ │Success│ │Avg   │ │Active│ │
│ │ Healthcare      │ │ │  42  │ │  87%  │ │Level │ │  5   │ │
│ │ $5,000/mo       │ │ │      │ │   ✓   │ │ 4.2  │ │of 10 │ │
│ │ Satisfaction:   │ │ └──────┘ └──────┘ └──────┘ └──────┘ │
│ │ [████████░░] 85%│ │                                      │
│ └─────────────────┘ │                                      │
│                     │                                      │
└─────────────────────┴──────────────────────────────────────┘
```

### Modal Dialog (Assignment)

```
        ┌──────────────────────────────────┐
        │ Assign Specialist               │
        ├──────────────────────────────────┤
        │ Select a specialist to handle   │
        │ DDoS Attack                     │
        │                                  │
        │ ┌──────────────────────────────┐│
        │ │▼ Alice Chen - Network (Lvl 5)││
        │ │  Sarah Johnson - Forensics   ││
        │ │  Dev Patel - Cryptography    ││
        │ └──────────────────────────────┘│
        │                                  │
        │ [Assign] [Cancel]               │
        └──────────────────────────────────┘
```

### Toast Notification

```
                    ┌───────────────────────────┐
                    │ ✅ Incident assigned      │
                    │    successfully!          │
                    └───────────────────────────┘
```

---

## Visual Style Guide

### Typography
- **Headings**: 20-36px, Bold, Gradient text
- **Body**: 14-16px, Regular, High contrast
- **Labels**: 12px, Uppercase, Secondary color

### Colors
```css
--bg-primary:   #0a0e27  /* Deep space blue */
--bg-secondary: #151937  /* Panel background */
--bg-tertiary:  #1e2442  /* Card background */
--accent-primary:   #00ff88  /* Bright cyan/green */
--accent-secondary: #00ccff  /* Cyan */
--accent-danger:    #ff3366  /* Pink/red */
--text-primary:     #ffffff  /* White */
--text-secondary:   #8892b0  /* Muted blue-gray */
```

### Component States
- **Available**: Green (#00ff88) + light background
- **Busy/Assigned**: Yellow (#ffcc00) + light background
- **Unassigned**: Red (#ff3366) + light background
- **Connected**: Green dot with no animation
- **Disconnected**: Red dot with pulse animation

### Spacing
- Panel padding: 20px
- Card padding: 15px
- Grid gap: 20px
- Item spacing: 10px

### Effects
- **Hover**: Transform translateY(-2px) + shadow
- **Transitions**: 0.3s ease for all animations
- **Border radius**: 8-10px for cards, 6px for buttons
- **Shadows**: 0 4px 6px rgba(0, 0, 0, 0.3)

---

## Responsive Behavior

### Desktop (1600px+)
- 2-column main grid (2fr + 3fr)
- 2-column bottom grid
- All panels visible
- Full feature set

### Tablet (768px - 1200px)
- Single column main grid
- 2-column bottom grid
- Panels stack vertically
- Touch-optimized buttons

### Mobile (< 768px)
- Single column layout
- Panels stack vertically
- Larger touch targets
- Simplified statistics cards

---

## Animation Examples

### Connection Status Pulse
```
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}
```

### Toast Slide In
```
@keyframes slideIn {
    from { transform: translateX(400px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}
```

### Loading Dots
```
@keyframes dots {
    0%, 20% { content: '.'; }
    40% { content: '..'; }
    60%, 100% { content: '...'; }
}
```

---

## Accessibility

- High contrast text (WCAG AA compliant)
- Keyboard navigation support (Alpine.js handles focus)
- Clear status indicators
- Descriptive button text
- Touch-friendly targets (44x44px minimum)
- Screen reader friendly (semantic HTML)

---

## Technical Implementation

**Framework**: Alpine.js 3.x
- Reactive data binding with `x-data`
- Event handling with `@click`
- Conditional rendering with `x-if` and `x-show`
- Dynamic attributes with `:class` and `:style`
- List rendering with `x-for`

**No Build Tools Required**:
- Single HTML file
- CDN-hosted Alpine.js
- Inline CSS styles
- Pure JavaScript (no transpilation)

**Real-time Updates**:
- WebSocket connection to `ws://localhost:8765`
- Automatic reconnection on disconnect
- State sync every 1 second
- Optimistic UI updates

---

## User Flow

1. **Landing** → Server status check → "Launch Game" button
2. **Game Load** → WebSocket connects → Initial state received
3. **Gameplay** → Monitor incidents → Assign specialists → See updates
4. **Real-time** → State syncs automatically → Toast notifications
5. **Reconnection** → If disconnect → Auto-reconnect → Resume gameplay

---

This visual preview shows the complete UI design and user experience of the web-based game interface!
