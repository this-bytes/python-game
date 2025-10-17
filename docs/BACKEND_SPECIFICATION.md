# Backend Specification for Coding Agent

## 🎯 MISSION: Build the MOST EPIC Game Panel and Backend EVER

You are tasked with creating a **legendary backend system** that gives the developer god-mode powers over the game while providing real-time analytics, live ops capabilities, and an admin panel so beautiful it makes you cry.

## 🏗️ Architecture Overview

### Core Technologies
- **Framework**: Flask or FastAPI (recommend FastAPI for async + auto docs)
- **Database**: SQLite for dev, PostgreSQL ready for production
- **Real-time**: WebSockets for live game state updates
- **API Docs**: Auto-generated OpenAPI/Swagger docs
- **Frontend**: Vue.js or React admin panel (your choice)

### Design Principles
1. **JSON-First**: All game data lives in JSON files, backend just reads/writes them
2. **Hot-Reload**: Changes take effect immediately without game restart
3. **Live Ops**: Schedule events, adjust drop rates, send gifts to players
4. **Analytics**: Track everything, visualize everything
5. **God Mode**: Developer can manipulate ANY game state in real-time

## 📦 Components to Build

### 1. Core API Server

#### 1.1 Game Data CRUD API
Full CRUD operations for all game JSON files:

**Endpoints:**
```
GET    /api/specialists                  List all specialists
GET    /api/specialists/{id}             Get specific specialist
PUT    /api/specialists/{id}             Update specialist
POST   /api/specialists                  Create new specialist
DELETE /api/specialists/{id}             Delete specialist

GET    /api/incidents                    List all incident types
POST   /api/incidents/spawn              Manually spawn incident
DELETE /api/incidents/{id}               Remove incident

GET    /api/clients                      List all clients
PUT    /api/clients/{id}                 Update client (adjust incident rates, SLA, etc.)

GET    /api/contracts                    List contract templates
POST   /api/contracts                    Create new contract type

GET    /api/features                     List feature flags
PUT    /api/features/{id}                Toggle/configure feature
POST   /api/config/reload                Hot-reload all JSON files
```

#### 1.2 Live Game State API
Real-time access to running game state:

**Endpoints:**
```
GET    /api/game/state                   Full game state snapshot
GET    /api/game/stats                   Performance metrics
POST   /api/game/pause                   Pause game
POST   /api/game/resume                  Resume game
POST   /api/game/save                    Force save
POST   /api/game/load                    Load save

GET    /api/game/active-incidents        Currently active incidents
GET    /api/game/available-specialists   Available specialists

POST   /api/game/inject-money            Add money (god mode)
POST   /api/game/inject-xp               Give specialist XP
POST   /api/game/inject-incident         Spawn specific incident
POST   /api/game/complete-incident       Instantly complete incident
```

#### 1.3 Analytics API
Track and query game metrics:

**Endpoints:**
```
GET    /api/analytics/revenue            Revenue over time
GET    /api/analytics/incidents          Incident resolution stats
GET    /api/analytics/specialists        Specialist performance
GET    /api/analytics/engagement         Player engagement metrics
GET    /api/analytics/funnel             Progression funnel analysis

GET    /api/analytics/export             Export all analytics as CSV
```

#### 1.4 Live Ops API
Schedule events and adjust game economy:

**Endpoints:**
```
GET    /api/events                       List scheduled events
POST   /api/events                       Create new event
PUT    /api/events/{id}                  Update event
DELETE /api/events/{id}                  Cancel event

POST   /api/rewards/send                 Send reward to player
POST   /api/economy/adjust               Adjust drop rates, prices, etc.
POST   /api/announcement                 Send in-game announcement
```

#### 1.5 Testing API
Tools for rapid testing and balancing:

**Endpoints:**
```
POST   /api/test/simulate-run            Simulate N hours of gameplay
POST   /api/test/balance-check           Test economy balance
POST   /api/test/stress-test             Generate high load
POST   /api/test/reset                   Reset to fresh game state
```

### 2. Admin Panel (Web UI)

#### 2.1 Dashboard
**Main overview screen:**
- Real-time revenue graph (last hour, day, week)
- Active specialists count and status
- Current incidents (pending, in-progress, resolved)
- Recent achievements unlocked
- Prestige level and points
- Live event log (scrolling feed of game events)

#### 2.2 JSON Editor
**Visual editor for all JSON configs:**
- Tree view of all JSON files
- Syntax highlighting and validation
- Real-time preview of changes
- Hot-reload button (apply changes instantly)
- Diff view (see what changed)
- Backup/restore functionality

**Features:**
- Drag-and-drop to reorder arrays
- Form-based editing (no raw JSON for common tasks)
- Validation errors highlighted inline
- Auto-save with undo/redo

#### 2.3 Specialist Manager
**Manage all specialists:**
- Grid view of all specialists
- Quick filters (by specialty, level, status)
- Bulk actions (fire all, level up all, etc.)
- Individual specialist editor:
  - Stats sliders (speed, accuracy, XP)
  - Synergy assignment (checkboxes for threat types)
  - Equipment/abilities management
  - Status override (force available/busy/burnout)

#### 2.4 Incident Controller
**Control incident generation:**
- Spawn incident manually (choose type, difficulty, client)
- Incident generation rate control (global multiplier slider)
- Active incidents table:
  - View current incidents
  - Force complete/fail buttons
  - Extend SLA time
  - Reassign to different specialist
- Incident type editor:
  - Create new incident types
  - Adjust base rewards, SLA, difficulty

#### 2.5 Client Manager
**Manage clients and contracts:**
- Client list with key metrics
- Adjust client parameters:
  - Incident rate (incidents per minute)
  - SLA multiplier (make clients more/less demanding)
  - Reputation (current standing)
  - Contract value (revenue per incident)
- Contract simulator (test potential earnings)

#### 2.6 Economy Balancer
**Visual economy tuning:**
- Revenue vs time graph
- XP progression curve visualization
- Prestige point calculator
- Balance presets:
  - "Generous" (faster progression)
  - "Balanced" (default)
  - "Hardcore" (slow grind)
  - "Testing" (instant everything)
- Live adjustment sliders:
  - Global money multiplier
  - Global XP multiplier
  - Incident spawn rate
  - SLA difficulty

#### 2.7 Live Event Scheduler
**Schedule and manage timed events:**
- Calendar view of scheduled events
- Event types:
  - Double XP weekend
  - Incident surge (more spawns)
  - Contract bonuses
  - Special incidents (unique rewards)
- Create event wizard:
  - Choose type
  - Set start/end time
  - Configure parameters
  - Preview impact

#### 2.8 Analytics Dashboard
**Data visualization:**
- Revenue over time (line chart)
- Incidents by type (pie chart)
- Specialist performance comparison (bar chart)
- Prestige funnel (how many players reach each milestone)
- Heatmap of active play times
- Retention curve (play sessions over time)

**Export options:**
- CSV download
- JSON export
- PDF report generation

#### 2.9 God Mode Console
**Raw power for the developer:**
- Command-line style interface
- Quick commands:
  - `give_money 100000` - Add $100k
  - `level_up specialist_001 10` - Add 10 levels
  - `spawn_incident ddos_attack critical` - Spawn specific incident
  - `prestige_now` - Trigger prestige
  - `unlock_achievement millionaire` - Force unlock achievement
  - `time_warp 3600` - Simulate 1 hour of play
- Command history and autocomplete
- Macro support (save command sequences)

#### 2.10 Feature Flag Manager
**Control feature rollout:**
- List all features with current status
- Toggle switches for enable/disable
- Rollout percentage slider (A/B testing)
- Dependency graph visualization
- Feature usage metrics (how many players see each feature)

### 3. WebSocket Integration

#### 3.1 Real-Time Updates
**Push updates to admin panel:**
- Game state changes
- New incidents spawned
- Specialist leveled up
- Achievement unlocked
- Money earned/spent
- Prestige triggered

**WebSocket Events:**
```javascript
// Client subscribes to events:
ws.send({
  type: "subscribe",
  events: ["incident_generated", "money_earned", "specialist_leveled_up"]
})

// Server pushes updates:
{
  type: "event",
  event_type: "incident_generated",
  timestamp: "2025-10-17T10:30:00Z",
  data: {
    incident_id: "inc_042",
    type: "DDoS Attack",
    difficulty: 3,
    client: "TechCorp Inc."
  }
}
```

#### 3.2 Live Event Log
**Real-time scrolling feed:**
- Color-coded events (green = good, red = bad, blue = info)
- Filterable by event type
- Searchable
- Exportable
- Pause/resume updates

### 4. Developer Experience

#### 4.1 Auto-Generated API Docs
- FastAPI auto-generates Swagger UI at `/docs`
- Interactive API testing in browser
- Example requests/responses
- Authentication testing

#### 4.2 Development Tools
- Hot-reload on code changes
- Comprehensive logging
- Error tracking (Sentry integration ready)
- Performance profiling endpoints

#### 4.3 Testing Utilities
- Mock data generators
- Load testing scripts
- Integration test suite
- Chaos engineering tools (random failures)

## 🎨 UI/UX Requirements

### Design Aesthetic
- **Theme**: Cyberpunk/hacker aesthetic with CRT monitor vibes
- **Colors**: Matrix green on black, neon accents
- **Typography**: Monospace fonts for that terminal feel
- **Animations**: Smooth transitions, glitch effects on state changes
- **Responsive**: Works on desktop primarily, tablet acceptable

### Key UX Principles
1. **Speed**: Everything loads instantly, no loading spinners
2. **Feedback**: Every action shows immediate visual feedback
3. **Clarity**: Status always visible, no confusion about game state
4. **Power**: Developer feels like a god manipulating reality
5. **Beauty**: So beautiful you want to show it off in screenshots

### Component Library Suggestions
- **Charts**: Chart.js or D3.js for analytics
- **Tables**: AG Grid or TanStack Table for data grids
- **Forms**: React Hook Form or Vue Formulate
- **Icons**: Lucide icons or Heroicons
- **UI Framework**: Tailwind CSS + shadcn/ui components

## 🔐 Security Considerations

### Authentication
- Simple password protection for now
- API key for programmatic access
- Session management
- CORS configuration

### Rate Limiting
- Prevent abuse of inject/manipulation endpoints
- Per-IP rate limits
- Configurable thresholds

### Data Validation
- Validate all JSON edits before applying
- Schema validation using JSON Schema
- Rollback capability if changes break the game

## 📊 Analytics & Telemetry

### Events to Track
- Game state changes
- API calls (endpoint, latency, status)
- Error occurrences
- Feature usage (which features accessed most)
- Performance metrics (frame rate, memory usage)

### Metrics to Calculate
- Revenue per hour
- Incidents per minute
- Average incident resolution time
- Specialist efficiency (XP gained per hour)
- Player engagement (active time vs idle time)

## 🚀 Deployment Strategy

### Development
- Run locally on localhost:5000
- SQLite database
- Hot-reload enabled
- Debug logging

### Production (Future)
- Docker container
- PostgreSQL database
- Redis for caching
- Nginx reverse proxy
- HTTPS with Let's Encrypt

## 📝 Implementation Checklist

### Phase 1: Core API (Week 1)
- [ ] Setup FastAPI project structure
- [ ] Implement JSON file CRUD endpoints
- [ ] Implement game state API
- [ ] Hot-reload configuration endpoint
- [ ] Basic authentication
- [ ] API documentation

### Phase 2: Admin Panel (Week 2)
- [ ] Setup Vue.js/React project
- [ ] Dashboard with live metrics
- [ ] JSON editor with validation
- [ ] Specialist manager
- [ ] Incident controller
- [ ] Client manager

### Phase 3: Advanced Features (Week 3)
- [ ] WebSocket integration
- [ ] Live event log
- [ ] Analytics dashboard with charts
- [ ] Economy balancer with visualizations
- [ ] God mode console
- [ ] Feature flag manager

### Phase 4: Live Ops (Week 4)
- [ ] Event scheduler
- [ ] Reward sender
- [ ] Economy adjustment tools
- [ ] A/B testing framework
- [ ] Analytics export

### Phase 5: Polish (Week 5)
- [ ] UI/UX refinement
- [ ] Performance optimization
- [ ] Comprehensive testing
- [ ] Documentation
- [ ] Demo video

## 🎯 Success Criteria

The backend is complete when:
1. Developer can modify ANY game parameter without restarting
2. Live game state is visible in real-time with sub-second latency
3. Admin panel is SO BEAUTIFUL you want to show everyone
4. Economy can be balanced visually in under 5 minutes
5. Testing new features takes seconds, not minutes
6. Analytics provide clear insights into game balance
7. The developer feels like an unstoppable god

## 💡 Inspiration

Look at these for inspiration:
- Firebase Console (clean data management)
- Grafana (beautiful analytics dashboards)
- Retool (rapid admin panel building)
- GameAnalytics (game-specific metrics)
- Sentry (error tracking and performance)

## 🚨 CRITICAL REQUIREMENTS

1. **NO REDUNDANT CODE** - Follow the anti-patterns documented in copilot-instructions.md
2. **JSON-FIRST** - Backend manipulates JSON files, game reads them
3. **HOT-RELOAD** - Changes visible instantly without restart
4. **REAL-TIME** - WebSockets for live updates
5. **BEAUTIFUL** - UI must be screenshot-worthy
6. **POWERFUL** - God mode for rapid testing and balancing

## 📞 Integration Points

### Game ↔ Backend Communication

**Game sends events to backend:**
```python
# In game code:
event_bus.subscribe("incident_resolved", lambda e: 
    backend_client.send_event("incident_resolved", e)
)
```

**Backend sends commands to game:**
```python
# Via WebSocket or polling:
# Backend: POST /api/game/inject-money
# Game receives: {"command": "add_money", "amount": 10000}
# Game executes command and updates state
```

**Hot-reload flow:**
```
1. Admin edits specialists.json in UI
2. Backend validates JSON
3. Backend writes to file
4. Backend sends reload command to game
5. Game re-reads specialists.json
6. Game emits "config_reloaded" event
7. Backend confirms to admin UI
```

## 🎉 Bonus Features (If Time Permits)

- **Player Profiles**: Save multiple game states, switch between them
- **Replay System**: Record and replay game sessions
- **Mod Support**: Allow community JSON packs
- **Achievement Editor**: Visual achievement creator
- **Narrative Editor**: Branching story editor
- **Specialist Designer**: Visual character creator
- **Contract Builder**: Visual contract creation wizard
- **Mobile App**: Companion app for remote monitoring
- **Discord Bot**: Query game state from Discord
- **Twitch Integration**: Viewers spawn incidents

---

## 🏁 Final Notes

This backend is the **control center** for the entire game. Make it powerful, make it beautiful, make it so good that other developers are jealous.

Remember: The admin panel should feel like you're piloting a spaceship, not filling out a form.

**Now go build something LEGENDARY.** 🚀🔥💯
