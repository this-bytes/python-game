# Quick Start Guide - New UI System

## 🎮 Playing the Game

### First Time Playing

1. **Launch the game**
   ```bash
   python src/main.py
   ```

2. **Initial screen** shows three panels:
   - Left: Specialist Roster (your team)
   - Middle: Incident Queue (incoming threats)
   - Right: Metrics Dashboard (statistics)

3. **Basic workflow**:
   - Incidents appear automatically in the queue
   - Click a specialist to select them
   - Click an incident to select it
   - Click "Assign Specialist" button
   - Watch specialist handle the incident!

### Keyboard Shortcuts ⌨️

Press these keys anytime:

| Key | Action |
|-----|--------|
| `1` | Toggle Specialist Roster |
| `2` | Toggle Incident Queue |
| `3` | Toggle Metrics Panel |
| `SPACE` | Pause/Resume Game |
| `+` / `=` | Increase Game Speed |
| `-` | Decrease Game Speed |
| `H` | Show/Hide Help Overlay |
| `ESC` | Close All Panels |

### Panel Controls 🪟

Every panel has controls in the title bar:

- **Drag**: Click and hold title bar, move panel
- **[−]**: Minimize panel (title bar only)
- **[X]**: Close panel (reopen with hotkeys)

### Understanding the UI 🎨

#### Specialist Cards

```
┌─────────────────┐
│ Alice Chen      │ ← Name
│ Lv.5 Network    │ ← Level & Specialty
│ [■■■■■■□□] 75%  │ ← XP to next level
│ ● AVAILABLE     │ ← Current status
└─────────────────┘
```

**Status Colors:**
- 🟢 Green = Available (ready for work)
- 🟡 Yellow = Working (handling incident)
- 🔵 Blue = Resting (recovering)

#### Incident Cards

```
┌─────────────────┐
│ |DDoS Attack    │ ← Bar shows urgency
│ ★★★★☆          │ ← Difficulty (1-5 stars)
│ Network Sec     │ ← Required specialty
│ SLA: 04:35      │ ← Time remaining!
│ $5,000          │ ← Money reward
└─────────────────┘
```

**Urgency (left bar color):**
- 🟢 Green = Plenty of time (>50% SLA left)
- 🟡 Yellow = Getting urgent (20-50% SLA)
- 🔴 Red = CRITICAL (<20% SLA) - Assign fast!

#### Metrics Panel

Shows 4 big KPI cards:
- 💰 Total Money
- 📈 Total Profit
- ✅ Incidents Handled
- 🎯 SLA Compliance %

Plus additional stats below.

### Notifications 🔔

Toast messages appear in top-right corner:

- ℹ️ **Blue** = Info (game events)
- ✅ **Green** = Success (good news!)
- ⚠️ **Yellow** = Warning (attention needed)
- ❌ **Red** = Error (something failed)

They auto-dismiss after 3 seconds.

### Themes 🎨

The game includes 3 color schemes:

1. **Dark Cyber** (default)
   - Cyberpunk blue/purple on dark background
   - Best for the cybersecurity aesthetic

2. **Light Professional**
   - Clean white panels, corporate blue
   - Easy on the eyes in bright rooms

3. **Hacker Green**
   - Classic terminal green on black
   - For that authentic hacker feel

*Note: Theme switching will be added to settings in a future update*

## 💡 Tips & Tricks

### Efficient Gameplay

1. **Watch SLA timers**: Red incidents are urgent!
2. **Match specialties**: Specialists work faster on their specialty
3. **Level up specialists**: Higher level = better performance
4. **Monitor XP bars**: Plan for level-ups
5. **Check metrics**: Track your SLA compliance

### Panel Management

- **Minimize unused panels**: More screen space
- **Drag panels around**: Position how you like
- **Use hotkeys**: Faster than clicking
- **Press H anytime**: Remind yourself of shortcuts

### Workflow Optimization

Best setup:
1. Specialist roster on left
2. Incident queue in center (where action is!)
3. Metrics on right (quick glance)

Quick select:
1. Click specialist → Click incident → Click Assign
2. Keyboard shortcut → Click → Click → Click
3. Profit! 💰

## 🐛 Troubleshooting

### Panel disappeared
- Press the number key for that panel (1-6)
- It will reappear at default position

### Can't assign specialist
- Check specialist is AVAILABLE (green status)
- Check incident is PENDING (not already assigned)
- Check specialty matches (or accept slower resolution)

### UI feels laggy
- Close unused panels
- Restart game if playing for hours
- Check system resources

### Colors look wrong
- Check which theme is active
- Themes are in `data/themes.json`

### Hotkeys not working
- Make sure no panel text input has focus
- Try clicking on game background first
- Check if another app is capturing keys

## 🎯 Advanced Usage

### For Power Users

- **Panel positioning**: Arrange for your workflow
- **Selective visibility**: Hide distracting panels
- **Hotkey mastery**: Never touch mouse
- **Status at a glance**: Color codes tell the story
- **Metrics tracking**: Watch trends over time

### Understanding The Numbers

**XP Bars:**
- Shows progress to next level
- Specialists gain XP from incidents
- Higher difficulty = more XP

**SLA Timers:**
- Start when incident spawns
- Count down to zero
- Miss SLA = lose money!

**Money:**
- Earn from successful incidents
- Lose from SLA failures
- Spend on upgrades (future feature)

## 📖 Learning More

- **Full API docs**: See `docs/UI_SYSTEM.md`
- **Visual design**: See `docs/UI_VISUAL_DESIGN.md`
- **Implementation**: See `UI_IMPLEMENTATION_SUMMARY.md`
- **Game rules**: See main `README.md`

## 🆘 Getting Help

If you encounter issues:

1. Check this guide first
2. Press `H` for in-game help
3. Check documentation in `docs/`
4. Review console logs for errors
5. Report bugs on GitHub

## 🚀 What's Next?

Upcoming features:
- Additional panels (Clients, Automation, Shop)
- Animation effects
- Sound effects
- Tutorial system for new players
- More themes
- Customizable hotkeys

Stay tuned! The UI system is designed to grow with the game.

---

**Enjoy your professional cybersecurity dashboard!** 🔒✨
