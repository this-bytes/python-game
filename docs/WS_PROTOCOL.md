# WebSocket & REST Protocol Specification

**Version**: 1.0.0  
**Last Updated**: 2025-10-19  
**Status**: Canonical Reference

---

## Overview

This document defines the **canonical communication protocol** between UI clients (Pygame or web) and the backend server. All communication must follow this specification for both local and remote backend modes.

**Key Principles:**
1. **Backend is authoritative** - All game logic executes on backend, UI renders state
2. **Multi-instance support** - Backend manages multiple game instances, each isolated
3. **Event-driven updates** - WebSocket broadcasts state changes to clients
4. **Action-based control** - UI submits actions via REST or WebSocket, backend processes them
5. **Protocol version** - Clients must declare protocol version for compatibility

---

## Multi-Instance Architecture

The backend supports **multiple concurrent game instances**, each with isolated GameState:

```
┌──────────────────────────────────────────┐
│            Backend Server                 │
│  ┌────────────────────────────────────┐ │
│  │      Instance Manager              │ │
│  │  ┌──────────┐  ┌──────────┐       │ │
│  │  │Instance 1│  │Instance 2│  ...  │ │
│  │  │GameState │  │GameState │       │ │
│  │  └──────────┘  └──────────┘       │ │
│  └────────────────────────────────────┘ │
│              ▲                           │
│              │                           │
│         instance_id                      │
│              │                           │
└──────────────┼───────────────────────────┘
               │
      ┌────────┴─────────┐
      │                  │
┌─────▼─────┐     ┌─────▼─────┐
│  Client 1  │     │  Client 2  │
│ (Pygame)   │     │   (Web)    │
└───────────┘     └────────────┘
```

**Key Concepts:**
- Each client/game session gets a unique `instance_id`
- All API requests include `instance_id` to route to correct game
- Admin panel can select which instance to manage
- Save files are per-instance
- Default instance used when `instance_id` omitted

---

1. **Initialization**
   - Client connects to backend via WebSocket
   - Backend sends `connection` event with protocol version
   - Client subscribes to desired event channels

2. **State Synchronization**
   - Backend broadcasts `game_snapshot` events (periodic or on-change)
   - Client updates local state representation
   - UI renders current state

3. **Player Actions**
   - User interacts with UI (click, drag, hotkey)
   - UI creates action object (no game logic)
   - Action submitted via REST POST or WebSocket emit
   - Backend validates, processes, updates state
   - Backend broadcasts relevant events to all clients

4. **Event Notifications**
   - Backend emits specific events: `incident_generated`, `specialist_updated`, etc.
   - Clients receive and update UI accordingly
   - No client-side game logic, only rendering updates

---

## REST API Endpoints

### Instance Management

#### `POST /api/game/register`
Register a new game instance with the backend.

**Request:**
```json
{
  "instance_id": "optional-custom-id",  # Auto-generated if not provided
  "client_name": "My Game Client"       # Optional friendly name
}
```

**Response:**
```json
{
  "success": true,
  "instance_id": "abc-123-def",
  "message": "Game registration acknowledged",
  "backend_ready": true
}
```

#### `GET /api/instances`
List all registered game instances.

**Response:**
```json
{
  "success": true,
  "instances": [
    {
      "instance_id": "abc-123",
      "client_name": "Player 1",
      "created_at": "2025-10-19T12:00:00Z",
      "last_activity": "2025-10-19T12:05:00Z",
      "connected": true,
      "has_state": true,
      "state_summary": {
        "money": 15000,
        "specialists": 3,
        "incidents": 5
      }
    }
  ],
  "default_instance_id": "abc-123"
}
```

#### `GET /api/instances/{instance_id}`
Get information about a specific instance.

**Response:**
```json
{
  "success": true,
  "instance": {
    "instance_id": "abc-123",
    "client_name": "Player 1",
    ...
  }
}
```

#### `POST /api/instances/{instance_id}/select`
Set the default instance for admin panel operations.

**Response:**
```json
{
  "success": true,
  "message": "Default instance set to abc-123"
}
```

---

### Game State

#### `GET /api/game/state`
Get full game state snapshot for a specific instance.

**Query Parameters:**
- `instance_id` (optional): Instance ID to query, uses default if omitted

**Response:**
```json
{
  "success": true,
  "data": {
    "specialists": [...],
    "incidents": [...],
    "clients": [...],
    "current_money": 15000.50,
    "metrics": {...},
    "prestige_points": 5,
    "unlocked_achievements": [...]
  },
  "timestamp": "2025-10-19T12:00:00Z"
}
```

#### `PUT /api/game/state`
Update game state (partial updates allowed).

**Request:**
```json
{
  "current_money": 20000,
  "is_paused": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Game state updated successfully"
}
```

---

### Player Actions

#### `POST /api/action`
Submit player action for backend processing.

**Request:**
```json
{
  "instance_id": "abc-123",  # Optional, uses default if omitted
  "action_type": "assign_incident",
  "data": {
    "incident_id": "inc_001",
    "specialist_id": "spec_001"
  },
  "timestamp": 1697712000
}
```

**Response (Success):**
```json
{
  "success": true,
  "result": {
    "assigned": true,
    "estimated_completion_time": 300
  }
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": {
    "code": "SPECIALTY_MISMATCH",
    "message": "Specialist specialty doesn't match incident requirement",
    "details": {
      "specialist_specialty": "Cryptography",
      "required_specialty": "Network Security"
    }
  }
}
```

---

### Save/Load

#### `POST /api/save`
Save current game state to slot.

**Request:**
```json
{
  "slot": 0,
  "auto_save": false
}
```

**Response:**
```json
{
  "success": true,
  "save_id": "save_20251019_120000",
  "timestamp": "2025-10-19T12:00:00Z"
}
```

#### `POST /api/load`
Load game state from slot.

**Request:**
```json
{
  "slot": 0
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "specialists": [...],
    "incidents": [...],
    ...
  }
}
```

---

### Configuration

#### `POST /api/config/reload`
Reload configuration from JSON files (hot-reload).

**Response:**
```json
{
  "success": true,
  "configs_reloaded": [
    "game_config.json",
    "specialists.json",
    "incidents.json"
  ]
}
```

---

### God Mode (Admin Only)

#### `POST /api/godmode/add-money`
Add money to game state.

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Request:**
```json
{
  "amount": 10000
}
```

**Response:**
```json
{
  "success": true,
  "new_balance": 25000.50
}
```

#### `POST /api/godmode/spawn-incident`
Spawn specific incident type.

**Request:**
```json
{
  "type": "DDoS Attack",
  "difficulty": 4,
  "client_id": "client_001"
}
```

**Response:**
```json
{
  "success": true,
  "incident": {
    "id": "inc_generated_001",
    "incident_type": "DDoS Attack",
    "difficulty": 4,
    "status": "pending"
  }
}
```

#### `PUT /api/godmode/specialist/{specialist_id}`
Modify specialist properties.

**Request:**
```json
{
  "level": 10,
  "xp": 5000,
  "burnout_level": 0
}
```

---

## WebSocket Events

### Client → Server

#### `subscribe`
Subscribe to specific event channels.

```json
{
  "event": "subscribe",
  "data": {
    "channels": ["game_state", "incidents", "specialists", "plugin_events"]
  }
}
```

#### `action` (Alternative to REST)
Submit action via WebSocket.

```json
{
  "event": "action",
  "data": {
    "action_type": "assign_incident",
    "data": {
      "incident_id": "inc_001",
      "specialist_id": "spec_001"
    }
  }
}
```

---

### Server → Client

#### `connection`
Sent immediately upon WebSocket connection.

```json
{
  "event": "connection",
  "data": {
    "message": "Connected to game server",
    "protocol_version": "1.0.0",
    "server_time": 1697712000,
    "backend_mode": "local"
  }
}
```

#### `game_snapshot`
Periodic or on-change full game state.

**Frequency**: Configurable (default: every 2 seconds or on state change)

```json
{
  "event": "game_snapshot",
  "data": {
    "specialists": [...],
    "incidents": [...],
    "current_money": 15000.50,
    "metrics": {...},
    "timestamp": 1697712000
  }
}
```

**Note**: Can be full or incremental (delta) depending on configuration.

#### `event`
Generic game event notification.

```json
{
  "event": "event",
  "data": {
    "event_type": "achievement_unlocked",
    "data": {
      "achievement_id": "ach_first_incident",
      "name": "First Response",
      "reward": 500
    },
    "timestamp": 1697712000
  }
}
```

#### `incident_generated`
New incident spawned.

```json
{
  "event": "incident_generated",
  "data": {
    "incident": {
      "id": "inc_002",
      "incident_type": "Malware Infection",
      "difficulty": 2,
      "sla_seconds": 300,
      "base_reward": 800,
      "client_id": "client_001",
      "status": "pending"
    },
    "timestamp": 1697712000
  }
}
```

#### `incident_updated`
Incident state changed.

```json
{
  "event": "incident_updated",
  "data": {
    "incident_id": "inc_001",
    "changes": {
      "status": "assigned",
      "assigned_specialist_id": "spec_001",
      "assignment_time": 1697712000
    },
    "timestamp": 1697712000
  }
}
```

#### `incident_resolved`
Incident completed or failed.

```json
{
  "event": "incident_resolved",
  "data": {
    "incident_id": "inc_001",
    "specialist_id": "spec_001",
    "success": true,
    "resolution_time": 285,
    "reward": 1200,
    "xp_earned": 150,
    "sla_met": true,
    "timestamp": 1697712000
  }
}
```

#### `specialist_updated`
Specialist state changed.

```json
{
  "event": "specialist_updated",
  "data": {
    "specialist_id": "spec_001",
    "changes": {
      "level": 6,
      "xp": 1500,
      "status": "available",
      "burnout_level": 35
    },
    "timestamp": 1697712000
  }
}
```

#### `plugin_event`
Plugin-specific event (burnout, achievements, etc.).

```json
{
  "event": "plugin_event",
  "data": {
    "plugin_name": "BurnoutPlugin",
    "event_type": "burnout_threshold_reached",
    "data": {
      "specialist_id": "spec_001",
      "burnout_level": 85,
      "performance_penalty": 0.75
    },
    "timestamp": 1697712000
  }
}
```

#### `error`
Error notification.

```json
{
  "event": "error",
  "data": {
    "code": "SPECIALIST_BUSY",
    "message": "Specialist is already assigned to an incident",
    "details": {
      "specialist_id": "spec_001",
      "current_incident_id": "inc_003"
    }
  }
}
```

---

## Action Types

All action types that can be submitted via `POST /api/action` or WebSocket `action` event.

### Incident Management

#### `assign_incident`
```json
{
  "action_type": "assign_incident",
  "data": {
    "incident_id": "string (required)",
    "specialist_id": "string (required)"
  }
}
```

#### `unassign_incident`
```json
{
  "action_type": "unassign_incident",
  "data": {
    "incident_id": "string (required)"
  }
}
```

### Specialist Management

#### `hire_specialist`
```json
{
  "action_type": "hire_specialist",
  "data": {
    "template_id": "string (required)",
    "name": "string (optional)"
  }
}
```

#### `fire_specialist`
```json
{
  "action_type": "fire_specialist",
  "data": {
    "specialist_id": "string (required)"
  }
}
```

#### `rest_specialist`
```json
{
  "action_type": "rest_specialist",
  "data": {
    "specialist_id": "string (required)",
    "duration_hours": "number (optional, default 8)"
  }
}
```

### Equipment

#### `equip_item`
```json
{
  "action_type": "equip_item",
  "data": {
    "specialist_id": "string (required)",
    "equipment_id": "string (required)",
    "slot": "string (required)"
  }
}
```

#### `purchase_equipment`
```json
{
  "action_type": "purchase_equipment",
  "data": {
    "equipment_id": "string (required)"
  }
}
```

### Abilities

#### `activate_ability`
```json
{
  "action_type": "activate_ability",
  "data": {
    "specialist_id": "string (required)",
    "ability_id": "string (required)",
    "target_id": "string (optional)"
  }
}
```

### Progression

#### `prestige`
```json
{
  "action_type": "prestige",
  "data": {
    "confirm": "boolean (required, must be true)"
  }
}
```

#### `purchase_prestige_upgrade`
```json
{
  "action_type": "purchase_prestige_upgrade",
  "data": {
    "upgrade_id": "string (required)"
  }
}
```

### Contracts & Facilities

#### `sign_contract`
```json
{
  "action_type": "sign_contract",
  "data": {
    "contract_id": "string (required)"
  }
}
```

#### `build_facility`
```json
{
  "action_type": "build_facility",
  "data": {
    "facility_type": "string (required)"
  }
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| `INVALID_ACTION` | Action type not recognized or malformed |
| `UNAUTHORIZED` | Admin token required or invalid |
| `SPECIALIST_NOT_FOUND` | Specialist ID does not exist |
| `INCIDENT_NOT_FOUND` | Incident ID does not exist |
| `SPECIALTY_MISMATCH` | Specialist specialty doesn't match incident requirement |
| `SPECIALIST_BUSY` | Specialist is already assigned to an incident |
| `INSUFFICIENT_FUNDS` | Not enough money to complete action |
| `COOLDOWN_ACTIVE` | Ability is on cooldown |
| `INVALID_STATE` | Game state does not allow this action |
| `SERVER_ERROR` | Internal server error |

---

## Implementation Requirements

### Backend

1. **REST endpoints** must return JSON responses matching this spec
2. **WebSocket events** must use exact event names and data structures
3. **Action validation** must return specific error codes
4. **State broadcasts** should be rate-limited (configurable, default 2s)
5. **Authentication** for god-mode endpoints via admin token in Authorization header

### UI Client

1. **No game logic** - UI only renders state and submits actions
2. **Action objects** created from user input, sent to backend
3. **WebSocket subscription** on connection
4. **Reconnection handling** with full state resync on disconnect
5. **Error display** from backend error responses

---

## Testing

### Protocol Compliance Tests

All endpoints and events must have tests verifying:
- Request/response format matches spec
- Error codes are used correctly
- WebSocket events have required fields
- Action validation works correctly

### Integration Tests

- UI → Backend → UI round-trip
- Local vs remote mode behave identically
- State synchronization under network latency
- Disconnection and reconnection handling

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-19 | Initial protocol specification |

---

## Maintenance

**This document must be updated when:**
- New action types are added
- WebSocket events are added/modified
- REST endpoints are added/modified
- Error codes are added

**Review Frequency**: Before every PR that adds/modifies backend/UI communication

---

**Last Review**: 2025-10-19  
**Next Review**: When Phase B implementation begins
