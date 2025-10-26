# Web UI User Guide

## Getting Started

### Quick Start

1. **Start the game server:**
   ```bash
   python start_web_game.py
   ```
   
   Your browser will automatically open to http://localhost:8000

2. **Click "Launch Game"** on the landing page

3. **Start playing!** The game will connect to the server automatically.

### Alternative Methods

**Using main.py directly:**
```bash
python main.py --local-server --headless
```
Then manually navigate to http://localhost:8000

**Using the dedicated WebSocket server:**
```bash
python run_ws_game.py
```
Then open http://localhost:8000 (requires separate static file server)

## Game Interface

### Header Bar

The header displays key information:

- **Money**: Your current funds (used for hiring specialists)
- **Day**: Current game day
- **Game Time**: Elapsed time in HH:MM:SS format
- **Connection Status**: Shows if you're connected to the game server
  - 🟢 Green dot = Connected
  - 🔴 Red dot = Disconnected (will auto-reconnect)

### Main Panels

#### Specialists Panel (Left)

Displays your team of security specialists:

- **Name & Status**: Shows if specialist is available or busy
- **Specialty**: Their area of expertise (Network Security, Malware Analysis, etc.)
- **Level**: Current experience level
- **XP**: Experience points earned
- **Current Assignment**: Which incident they're working on (if any)

**Status Indicators:**
- 🟢 **Available**: Ready to be assigned
- 🟡 **Busy**: Currently working on an incident

#### Incidents Panel (Right)

Shows active security incidents requiring attention:

- **Incident Type**: Type of security threat
- **Specialty Required**: What kind of specialist can handle it
- **Difficulty**: How challenging the incident is (1-5)
- **Assignment Status**: Whether a specialist is assigned

**Actions:**
- Click **"Assign Specialist"** to open assignment modal
- Select an available specialist from the dropdown
- Click **"Assign"** to confirm

### Bottom Panels

#### Clients Panel

Shows your active client contracts:

- **Client Name & Industry**: Who they are and what sector
- **Contract Value**: Monthly revenue from this client
- **Satisfaction**: How happy they are (0-100%)
  - Visual bar shows satisfaction level
  - Higher satisfaction = better retention

#### Statistics Panel

Real-time game statistics:

- **Total Incidents**: Lifetime incidents resolved
- **Success Rate**: Percentage of successfully resolved incidents
  - ✓ Excellent: 80%+
  - ⚠ Good: 60-79%
  - ✗ Needs Work: <60%
- **Avg Level**: Average level of your specialist team
- **Active Jobs**: How many incidents are currently being worked on

## Gameplay Loop

1. **Monitor Incidents**: New security incidents appear automatically
2. **Assign Specialists**: Match specialists to incidents based on specialty
3. **Wait for Resolution**: Specialists work on incidents in real-time
4. **Earn Rewards**: Successfully resolved incidents earn XP and money
5. **Manage Resources**: Use money to hire more specialists
6. **Keep Clients Happy**: Meet SLAs to maintain high satisfaction

## Tips & Strategies

### Matching Specialties

Always assign specialists whose specialty matches the incident requirement:
- Network Security → Network-related incidents
- Malware Analysis → Malware infections
- Digital Forensics → Investigation-heavy incidents
- Incident Response → Active breaches
- Cryptography → Encryption/decryption tasks

### Level Progression

Specialists gain XP and level up by:
- Resolving incidents successfully
- Matching incidents to their specialty (bonus XP)
- Completing difficult incidents (higher XP rewards)

Higher level specialists:
- Work faster
- Have better success rates
- Can handle more difficult incidents

### Client Management

Keep clients satisfied by:
- Resolving incidents quickly (meet SLA deadlines)
- Maintaining high success rates
- Responding to incidents promptly

Low satisfaction leads to:
- Reduced contract value
- Contract cancellation (below 30%)

### Resource Management

Balance your budget:
- **Income**: Monthly contract values from clients
- **Expenses**: Specialist salaries
- **Growth**: Hire new specialists when profitable
- **Risk**: Don't over-hire or you'll go broke!

## Keyboard Shortcuts

Currently no keyboard shortcuts implemented. All interactions are click-based.

## Troubleshooting

### Can't Connect to Server

**Problem**: "Connecting..." status never goes green

**Solutions:**
1. Check if server is running:
   ```bash
   ps aux | grep "python main.py"
   ```
2. Restart the server:
   ```bash
   python start_web_game.py
   ```
3. Check if port 8765 is available:
   ```bash
   lsof -i :8765
   ```

### Assignments Not Working

**Problem**: Clicking "Assign" doesn't do anything

**Solutions:**
1. Check browser console (F12 → Console) for errors
2. Verify WebSocket connection is active (green dot in header)
3. Refresh the page to reconnect
4. Check server logs for errors

### Page Not Loading

**Problem**: Browser shows "Can't reach this page"

**Solutions:**
1. Verify server is running
2. Check if port 8000 is available
3. Try accessing directly: http://localhost:8000/game.html
4. Clear browser cache and reload

### Game State Not Updating

**Problem**: Specialists/incidents don't change

**Solutions:**
1. Check connection status in header
2. Look at browser Network tab (F12 → Network → WS)
3. Verify WebSocket messages are being received
4. Restart both browser and server

## Browser Compatibility

### Supported Browsers

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Opera 76+

### Required Features

- JavaScript enabled
- WebSocket support
- LocalStorage (for future save feature)
- Modern CSS (Grid, Flexbox)

### Not Supported

- ❌ Internet Explorer (any version)
- ❌ Very old mobile browsers
- ❌ Text-only browsers

## Performance

### Recommended Specs

- **Processor**: Any modern CPU (2015+)
- **RAM**: 4GB+ available
- **Network**: Localhost connection (minimal bandwidth)
- **Screen**: 1280x720 minimum resolution

### Known Limitations

- Maximum 50 concurrent incidents (configurable)
- Maximum 20 specialists (configurable)
- Updates every 1 second (heartbeat rate)
- Browser tab must be visible for updates (browser background throttling)

## Advanced Features

### Multiple Tabs

You can open multiple browser tabs to view the game from different angles:
- All tabs share the same game state
- Changes in one tab appear in all tabs
- Useful for monitoring while managing

### Mobile Support

The UI is responsive and works on mobile devices:
- Panels stack vertically on small screens
- Touch-friendly buttons and modals
- Optimized for portrait orientation

### Developer Console

Press F12 to open browser developer tools:
- **Console**: See WebSocket messages and debug info
- **Network → WS**: Monitor WebSocket traffic
- **Application → LocalStorage**: View saved data (future feature)

## Getting Help

### In-Game Help

Currently no in-game help system. Refer to this guide.

### Server Logs

Check server logs for debugging:
```bash
tail -f logs/game_*.log
```

### Community

- Check GitHub Issues for known problems
- Create new issue for bugs or feature requests
- Join Discord (if available) for real-time help

## Future Features

Planned enhancements:
- [ ] Keyboard shortcuts
- [ ] Sound effects and music
- [ ] Achievement system
- [ ] Leaderboards
- [ ] Save/load slots
- [ ] Settings panel
- [ ] Tutorial mode
- [ ] Multiplayer (spectator mode)
- [ ] Mobile app (PWA)

---

**Need more help?** Check the [WebSocket Architecture](WEBSOCKET_ARCHITECTURE.md) documentation for technical details.
