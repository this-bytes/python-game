# 🎯 Quick Reference: Backend Implementation for Coding Agent

## Start Here

You've been assigned to build the backend based on `docs/BACKEND_SPECIFICATION.md`.

This document is a quick reference to get you started immediately.

## 📁 Key Files to Read First

1. **`docs/BACKEND_SPECIFICATION.md`** - Your main blueprint (MUST READ)
2. **`.github/copilot-instructions.md`** - Code quality standards (especially anti-patterns section)
3. **`docs/ideas.md`** - Full game vision for context
4. **`docs/ARCHITECTURE_ROADMAP.md`** - Overall architecture strategy

## 🎯 Your Mission

Build an **EPIC admin panel and backend** that gives the developer god-mode control over the game.

### Core Requirements
1. **JSON-First**: Manipulate JSON files, game reads them
2. **Hot-Reload**: Changes visible instantly without game restart
3. **Real-Time**: WebSockets for live updates (sub-second latency)
4. **Beautiful**: Cyberpunk aesthetic, screenshot-worthy UI
5. **Powerful**: God mode for rapid testing and balancing

## 🏗️ Tech Stack Recommendations

### Backend
- **Framework**: FastAPI (async + auto-generated docs)
- **Database**: SQLite (dev), PostgreSQL ready (production)
- **WebSockets**: FastAPI native WebSocket support
- **Validation**: Pydantic models
- **CORS**: For frontend communication

### Frontend
- **Framework**: Vue 3 + Vite OR React + Vite (your choice)
- **UI Library**: Tailwind CSS + shadcn/ui components
- **Charts**: Chart.js or Recharts
- **Icons**: Lucide icons
- **State**: Pinia (Vue) or Zustand (React)

### Development
- **Hot Reload**: Both backend and frontend
- **API Testing**: Built-in Swagger UI at `/docs`
- **Logging**: Structured logging with levels

## 📂 Suggested Project Structure

```
/backend/
├── app.py                    # FastAPI main app
├── api/
│   ├── game_data.py         # CRUD endpoints
│   ├── game_state.py        # Live state API
│   ├── analytics.py         # Analytics endpoints
│   ├── live_ops.py          # Event scheduling
│   └── testing.py           # Testing utilities
├── models/
│   ├── game_models.py       # Pydantic models for game entities
│   └── api_models.py        # Request/response models
├── services/
│   ├── json_service.py      # JSON file operations
│   ├── websocket_service.py # WebSocket management
│   └── analytics_service.py # Analytics calculations
├── utils/
│   ├── validation.py        # JSON schema validation
│   └── hot_reload.py        # File watching and reload
└── requirements.txt

/admin-panel/
├── index.html
├── package.json
├── vite.config.js
├── src/
│   ├── main.js              # App entry
│   ├── App.vue/jsx
│   ├── components/
│   │   ├── Dashboard.vue    # Main dashboard
│   │   ├── JsonEditor.vue   # Visual JSON editor
│   │   ├── SpecialistManager.vue
│   │   ├── IncidentController.vue
│   │   ├── EconomyBalancer.vue
│   │   ├── AnalyticsDashboard.vue
│   │   ├── GodModeConsole.vue
│   │   └── FeatureFlagManager.vue
│   ├── services/
│   │   ├── api.js           # API client
│   │   └── websocket.js     # WebSocket client
│   └── styles/
│       └── cyberpunk.css    # Cyberpunk theme
```

## 🚀 Phase 1: Core API (Week 1)

### Step 1: Project Setup
```bash
mkdir backend admin-panel
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install fastapi uvicorn pydantic watchfiles websockets
```

### Step 2: Basic FastAPI App
```python
# backend/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Cybersecurity Firm Game - Admin API",
    description="God-mode control panel for game development",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Backend is ALIVE", "status": "legendary"}

# Run with: uvicorn app:app --reload
```

### Step 3: JSON CRUD Endpoints
```python
# backend/api/game_data.py
from fastapi import APIRouter, HTTPException
import json
from pathlib import Path

router = APIRouter(prefix="/api", tags=["game-data"])

DATA_DIR = Path("../data")  # Adjust path to your data folder

@router.get("/specialists")
def get_specialists():
    """Get all specialists from JSON."""
    with open(DATA_DIR / "specialists.json") as f:
        return json.load(f)

@router.put("/specialists/{specialist_id}")
def update_specialist(specialist_id: str, specialist_data: dict):
    """Update a specialist in JSON."""
    specialists_file = DATA_DIR / "specialists.json"
    
    with open(specialists_file) as f:
        data = json.load(f)
    
    # Find and update specialist
    for specialist in data["specialists"]:
        if specialist["id"] == specialist_id:
            specialist.update(specialist_data)
            break
    else:
        raise HTTPException(404, "Specialist not found")
    
    # Write back to file
    with open(specialists_file, "w") as f:
        json.dump(data, f, indent=2)
    
    return {"success": True, "message": "Specialist updated"}

# Similar endpoints for incidents, clients, contracts, features...
```

### Step 4: Hot-Reload Endpoint
```python
@router.post("/config/reload")
def reload_config():
    """Trigger game to reload all JSON configs."""
    # This would send a signal to the running game
    # For now, just return success
    return {"success": True, "message": "Reload signal sent"}
```

## 🎨 Phase 2: Admin Panel (Week 2)

### Step 1: Initialize Vue/React Project
```bash
cd admin-panel
npm create vite@latest . -- --template vue  # or react
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm install chart.js lucide-vue-next  # or lucide-react
npm install axios
```

### Step 2: Create Dashboard Component
```vue
<!-- admin-panel/src/components/Dashboard.vue -->
<template>
  <div class="dashboard">
    <h1 class="text-4xl font-mono text-green-400">
      🎮 Cybersecurity Firm - CONTROL CENTER
    </h1>
    
    <div class="grid grid-cols-3 gap-4 mt-8">
      <div class="stat-card">
        <h3>Revenue</h3>
        <p class="text-3xl">${{ revenue }}</p>
      </div>
      
      <div class="stat-card">
        <h3>Active Specialists</h3>
        <p class="text-3xl">{{ activeSpecialists }}</p>
      </div>
      
      <div class="stat-card">
        <h3>Pending Incidents</h3>
        <p class="text-3xl">{{ pendingIncidents }}</p>
      </div>
    </div>
    
    <div class="event-feed mt-8">
      <h2>Live Event Feed</h2>
      <div v-for="event in events" :key="event.id" class="event">
        {{ event.message }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const revenue = ref(0)
const activeSpecialists = ref(0)
const pendingIncidents = ref(0)
const events = ref([])

onMounted(async () => {
  // Fetch initial data
  const response = await axios.get('http://localhost:8000/api/game/state')
  // Update reactive variables
})
</script>

<style scoped>
.dashboard {
  @apply p-8 bg-black text-green-400 font-mono;
}

.stat-card {
  @apply bg-gray-900 border border-green-500 p-6 rounded;
}
</style>
```

### Step 3: API Client Service
```javascript
// admin-panel/src/services/api.js
import axios from 'axios'

const API_BASE = 'http://localhost:8000/api'

export const api = {
  // Specialists
  getSpecialists: () => axios.get(`${API_BASE}/specialists`),
  updateSpecialist: (id, data) => axios.put(`${API_BASE}/specialists/${id}`, data),
  
  // Game state
  getGameState: () => axios.get(`${API_BASE}/game/state`),
  pauseGame: () => axios.post(`${API_BASE}/game/pause`),
  resumeGame: () => axios.post(`${API_BASE}/game/resume`),
  
  // God mode
  injectMoney: (amount) => axios.post(`${API_BASE}/game/inject-money`, { amount }),
  
  // Config
  reloadConfig: () => axios.post(`${API_BASE}/config/reload`),
}
```

## 📡 Phase 3: WebSocket Integration (Week 3)

### Backend WebSocket
```python
# backend/api/websocket.py
from fastapi import APIRouter, WebSocket
from typing import List

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages
    except:
        manager.disconnect(websocket)
```

### Frontend WebSocket
```javascript
// admin-panel/src/services/websocket.js
class WebSocketService {
  constructor() {
    this.ws = null
    this.callbacks = {}
  }
  
  connect() {
    this.ws = new WebSocket('ws://localhost:8000/ws')
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (this.callbacks[data.type]) {
        this.callbacks[data.type](data)
      }
    }
  }
  
  subscribe(eventType, callback) {
    this.callbacks[eventType] = callback
  }
  
  send(data) {
    this.ws.send(JSON.stringify(data))
  }
}

export const wsService = new WebSocketService()
```

## 🎨 Cyberpunk Styling

### Tailwind Config
```javascript
// admin-panel/tailwind.config.js
export default {
  theme: {
    extend: {
      colors: {
        cyber: {
          black: '#000000',
          green: '#00ff00',
          darkgreen: '#003300',
          blue: '#00ffff',
          pink: '#ff00ff',
        }
      },
      fontFamily: {
        mono: ['Courier New', 'monospace'],
      },
    },
  },
}
```

### Global Styles
```css
/* admin-panel/src/styles/cyberpunk.css */
body {
  @apply bg-black text-green-400 font-mono;
}

.neon-border {
  box-shadow: 0 0 10px #00ff00, 0 0 20px #00ff00, 0 0 30px #00ff00;
  border: 1px solid #00ff00;
}

.glitch {
  animation: glitch 1s infinite;
}

@keyframes glitch {
  0%, 100% { transform: translate(0); }
  20% { transform: translate(-2px, 2px); }
  40% { transform: translate(-2px, -2px); }
  60% { transform: translate(2px, 2px); }
  80% { transform: translate(2px, -2px); }
}

.crt-effect {
  background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%);
  background-size: 100% 4px;
}
```

## ⚡ Quick Testing Commands

### Start Backend
```bash
cd backend
source venv/bin/activate
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend
```bash
cd admin-panel
npm run dev
```

### Test API
```bash
# Get specialists
curl http://localhost:8000/api/specialists

# Update specialist
curl -X PUT http://localhost:8000/api/specialists/spec_001 \
  -H "Content-Type: application/json" \
  -d '{"level": 10}'

# Reload config
curl -X POST http://localhost:8000/api/config/reload
```

## 🚨 Critical Reminders

### Code Quality (READ ANTI-PATTERNS IN COPILOT-INSTRUCTIONS.MD)
- ❌ NO redundant constants: `EVENT_NAME = "event_name"` is DUMB
- ✅ Just use strings directly in your code
- ✅ Type hints on all functions
- ✅ Clear, descriptive names
- ✅ Docstrings for public APIs

### Architecture
- JSON files are source of truth
- Backend reads/writes JSON
- Game reads JSON periodically or on signal
- WebSocket for real-time push to admin panel
- Feature flags control what's enabled

### Testing
- Test every endpoint as you build it
- Use Swagger UI at http://localhost:8000/docs
- Test hot-reload early and often
- Verify WebSocket connections work

## 📚 Additional Resources

- FastAPI docs: https://fastapi.tiangolo.com/
- Vue 3 docs: https://vuejs.org/
- React docs: https://react.dev/
- Tailwind CSS: https://tailwindcss.com/
- Chart.js: https://www.chartjs.org/

## 🎯 Success Criteria

You'll know you're done when:
1. ✅ Developer can edit ANY JSON file via UI
2. ✅ Changes apply instantly without game restart
3. ✅ Live game state visible with <1 second latency
4. ✅ Admin panel is screenshot-worthy beautiful
5. ✅ God mode commands work (inject money, spawn incidents, etc.)
6. ✅ Analytics charts show real data
7. ✅ You feel like a badass building it

## 🔥 NOW GO BUILD SOMETHING LEGENDARY

The specification is comprehensive. The architecture is solid. The vision is clear.

**Build the admin panel so epic that other developers are jealous.** 🚀

*Questions? Check `docs/BACKEND_SPECIFICATION.md` for full details.*
