# Command Center UI - User Guide

## Overview

The **Command Center** is a revolutionary desktop-style interface for the Cybersecurity Firm game, providing a comprehensive, professional-grade management experience.

## Key Features

### 🖥️ Desktop Environment

The Command Center transforms the game into a full desktop operating system experience:

- **Desktop Icons**: Quick access to all game modules
- **Windowing System**: Multiple windows can be open simultaneously
- **Taskbar**: Track and switch between active windows
- **Persistent HUD**: Always-visible game statistics

### 📊 Persistent HUD

The HUD (Heads-Up Display) at the top of the screen provides real-time information:

- **Cash**: Current available funds
- **Day**: Current game day
- **Incidents**: Active threats (color-coded by urgency)
- **Team**: Available specialists
- **Reputation**: Average client satisfaction

The HUD is always visible regardless of which windows are open.

### 🪟 Window System

Each game module opens in its own window with full controls:

**Window Controls**:
- **Drag**: Click and drag the title bar to move windows
- **Maximize**: Click the maximize button to fullscreen
- **Close**: Click X to close the window

**Available Windows**:
- 👨‍💼 **Specialists**: Team management and individual specialist details
- 🚨 **Incidents**: Active threats and incident management
- 🏢 **Clients**: Client relationships and satisfaction tracking
- 📊 **Analytics**: Performance metrics and team statistics
- 🎯 **Dispatch**: Quick assignment center (coming soon)
- 📋 **Briefings**: Daily reports and summaries (coming soon)
- ⚡ **Resources**: Equipment and automation (coming soon)
- 🔍 **Intel**: Threat intelligence (coming soon)

### 🎯 Entity Management

**Detailed Entity Views**:
Click any entity card to open a comprehensive detail modal with:
- Full entity information
- Interactive statistics
- Quick actions
- Related entities

**Entity Types**:
- **Specialists**: View stats, level, XP, burnout, and assign to incidents
- **Incidents**: See difficulty, specialty requirements, and assign specialists
- **Clients**: Track satisfaction, contracts, and revenue

### ⚡ Quick Actions

**Quick Assign**: One-click incident assignment
- Automatically finds best available specialist
- Matches specialty requirements when possible
- Instant assignment without opening detail view

**Desktop Shortcuts**: 
- Double-click icons to open modules
- Badge notifications show important counts
- Color-coded status indicators

## Interface Elements

### Desktop Icons

Located in the main desktop area, icons provide quick access:

**Features**:
- Large, clear icons with labels
- Badge counters for pending items
- Hover effects for visual feedback
- Organized grid layout

**Badge Indicators**:
- Red badges = Urgent items requiring attention
- Numbers show quantity (e.g., unassigned incidents)
- Visible even when windows are open

### Window Cards

Entity information displayed in modern card format:

**Card Features**:
- Color-coded status indicators
- Real-time statistics
- Progress bars for visual feedback
- Hover effects for interactivity
- Quick action buttons

**Status Colors**:
- 🟢 **Green (Available)**: Specialist ready for assignment
- 🟡 **Yellow (Busy)**: Currently working on incident
- 🔴 **Red (Critical)**: Unassigned incident requiring attention

### Task Bar

Bottom bar showing active windows and system clock:

**Features**:
- Click window buttons to focus/switch
- Active window highlighted
- Real-time clock display
- Minimalist design stays out of the way

### Notifications

Toast-style notifications in the top-right corner:

**Notification Types**:
- System messages (connection status)
- Action confirmations (assignment successful)
- Error alerts (assignment failed)
- Auto-dismiss after 3 seconds

## Keyboard & Mouse

### Mouse Controls

- **Single Click**: Select/activate items
- **Double Click**: Open windows from desktop
- **Click & Drag**: Move windows (via title bar)
- **Hover**: Show additional information

### Window Management

- **Focus**: Click window or taskbar button
- **Move**: Drag title bar
- **Maximize**: Click maximize button (🗖)
- **Restore**: Click restore button (🗗) when maximized
- **Close**: Click X button

## Workflow Examples

### Managing an Incident

1. **Identify Threat**:
   - Check HUD for incident count
   - Notice red badge on Incidents icon
   
2. **Open Incident Window**:
   - Click Incidents desktop icon
   - Window opens showing all active threats

3. **Quick Assign**:
   - Click "Quick Assign" on incident card
   - System automatically assigns best specialist

OR

4. **Manual Assignment**:
   - Click incident card for detail view
   - Select specialist from dropdown
   - Click "Assign to Incident"

5. **Monitor Progress**:
   - Check Specialists window for status
   - View updated incident status
   - Track via taskbar

### Monitoring Team Performance

1. **Open Analytics Window**:
   - Click Analytics (📊) icon
   
2. **View Key Metrics**:
   - Total resolved incidents
   - Success rate percentage
   - Average team level
   - Total revenue

3. **Individual Performance**:
   - See specialist XP progress bars
   - Track level advancement
   - Identify top performers

### Managing Multiple Tasks

1. **Open Multiple Windows**:
   - Click Specialists icon
   - Click Incidents icon
   - Click Clients icon

2. **Switch Between Windows**:
   - Use taskbar buttons
   - Or click window title bars

3. **Organize Workspace**:
   - Drag windows to desired positions
   - Maximize important windows
   - Close completed tasks

## Performance Tips

### Efficient Workflows

- **Use Quick Assign** for routine incidents
- **Open Detail Views** for complex decisions
- **Monitor HUD** for status at a glance
- **Use Taskbar** for quick window switching

### Window Management

- **Maximize** data-heavy windows (Analytics, Specialists)
- **Stack** windows by dragging to organize
- **Close** unused windows to reduce clutter
- **Focus** active task by clicking taskbar

### Entity Management

- **Filter** by status using visual indicators
- **Sort** mentally by urgency (red badges)
- **Click cards** for detailed information
- **Use quick actions** for common tasks

## Advanced Features

### Real-Time Updates

All data updates automatically via WebSocket:
- Incident statuses change live
- Specialist availability updates instantly
- Money and stats refresh continuously
- No manual refresh needed

### Responsive Design

Interface adapts to screen size:
- Desktop: Full multi-window experience
- Tablet: Simplified window layout
- Mobile: Stack windows, touch-friendly

### Persistent State

Window positions and sizes remembered:
- Reopen windows in same position
- Maintain workspace organization
- Consistent user experience

## Troubleshooting

### Windows Not Moving

- Ensure you're dragging the title bar
- Check if window is maximized (can't move when maximized)
- Try clicking title bar again

### Cards Not Responding

- Check WebSocket connection (top-right HUD)
- Look for red "Offline" indicator
- Wait for auto-reconnect (3 seconds)

### Missing Data

- Verify server is running
- Check browser console (F12) for errors
- Refresh page to reset state
- Ensure port 8765 is accessible

### Performance Issues

- Close unused windows
- Check browser memory usage
- Disable browser extensions
- Use modern browser (Chrome, Firefox, Edge)

## Keyboard Shortcuts (Future)

Coming soon:
- `Ctrl+W`: Close active window
- `Ctrl+M`: Maximize/restore window
- `Ctrl+Tab`: Switch windows
- `Ctrl+Q`: Quick assign
- `Esc`: Close modal/detail view

## Tips & Tricks

1. **Organize Desktop**: Frequently used modules on left
2. **Use Badges**: Red numbers indicate urgent actions
3. **Watch HUD**: Quick overview without opening windows
4. **Stack Windows**: Offset for easy access to multiple
5. **Quick Actions**: Save time on routine tasks
6. **Detail Views**: Deep dive when needed
7. **Taskbar**: Fast window switching
8. **Notifications**: Don't miss important events
9. **Color Codes**: Learn status meanings for speed
10. **Multi-task**: Open multiple windows for complex operations

## What's New vs. Classic Interface

### Command Center Advantages

- **Multiple Windows**: Work on several tasks simultaneously
- **Desktop Icons**: Quick access to all modules
- **Persistent HUD**: Always-visible stats
- **Entity Details**: Comprehensive information views
- **Quick Actions**: Faster workflow
- **Professional UI**: OS-style experience
- **Better Organization**: Logical module separation

### When to Use Each

**Command Center**: 
- Complex multi-tasking
- Detailed analysis needed
- Professional management
- Long play sessions

**Classic Interface**:
- Quick checks
- Simple operations
- Learning the game
- Lower-spec devices

## Future Enhancements

Planned features:
- [ ] Keyboard shortcuts
- [ ] Window snapping
- [ ] Custom layouts
- [ ] Themes/skins
- [ ] Sound effects
- [ ] Hotkeys
- [ ] Advanced filters
- [ ] Data export
- [ ] More modules
- [ ] Mobile optimization

---

**Enjoy the ultimate cybersecurity management experience!**
