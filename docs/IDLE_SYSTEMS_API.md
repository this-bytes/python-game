# Idle Systems API Documentation

This document describes the new API endpoints added for idle systems functionality.

## Overview

The idle systems include:
- **Advanced Automation**: Upgrade automation scripts, adjust priorities and cooldowns
- **Passive Income**: Make investments and earn passive income
- **Prestige System**: Reset game with permanent bonuses
- **Offline Progress**: Simulate game progress while AFK
- **Save/Load**: Persist game state across sessions

All endpoints return JSON with the format:
```json
{
  "success": true,
  "message": "Optional message",
  "data": { ... },
  "timestamp": "2025-10-16T10:00:00.000000"
}
```

## Automation Endpoints

### Upgrade Automation Script
**POST** `/api/automation-scripts/{script_id}/upgrade`

Upgrade an automation script to the next level (max 5). Each upgrade:
- Reduces cooldown by 10%
- Increases effect magnitude by 5%

**Response:**
```json
{
  "success": true,
  "message": "Automation script upgraded to level 2",
  "data": {
    "new_level": 2,
    "cost": 1500,
    "effective_cooldown": 4.5,
    "effective_magnitude": 1.05
  }
}
```

### Set Script Priority
**PUT** `/api/automation-scripts/{script_id}/set-priority`

Change execution priority (higher = executed first).

**Request:**
```json
{
  "priority": 50
}
```

### Set Script Cooldown
**PUT** `/api/automation-scripts/{script_id}/set-cooldown`

Adjust cooldown duration (admin only).

**Request:**
```json
{
  "cooldown_seconds": 3.0
}
```

### Get Automation Statistics
**GET** `/api/automation-scripts/stats`

Get detailed statistics about automation execution.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_scripts_evaluated": 1500,
    "total_scripts_executed": 450,
    "scripts_executed_by_type": {
      "auto_assign": 350,
      "speed_boost": 75,
      "accuracy_boost": 25
    },
    "execution_failures": 5,
    "last_execution_time": 1729123456.789,
    "triggers_per_script": {
      "auto_assign_network_low": 120
    }
  }
}
```

## Economy Endpoints

### Make Investment
**POST** `/api/economy/invest`

Invest money in one of three risk tiers.

**Request:**
```json
{
  "investment_type": "medium_risk",
  "amount": 50000
}
```

Investment types:
- `low_risk`: 2% annual return, 0% risk, min $10,000
- `medium_risk`: 5% annual return, 10% risk, min $50,000
- `high_risk`: 10% annual return, 25% risk, min $100,000

**Response:**
```json
{
  "success": true,
  "data": {
    "investment_type": "medium_risk",
    "amount": 50000,
    "total_invested": 50000,
    "return_rate": 0.05,
    "risk": 0.1
  }
}
```

### Withdraw Investment
**POST** `/api/economy/withdraw`

Withdraw money from an investment.

**Request:**
```json
{
  "investment_type": "medium_risk",
  "amount": 10000
}
```

### Get Passive Income
**GET** `/api/economy/passive-income`

Get breakdown of passive income sources.

**Response:**
```json
{
  "success": true,
  "data": {
    "statistics": {
      "total_retainer_income": 5000.0,
      "total_investment_income": 2500.0,
      "total_investment_losses": 100.0,
      "total_reputation_bonus": 500.0
    },
    "current_investments": {
      "low_risk": 10000,
      "medium_risk": 50000
    },
    "total_invested": 60000
  }
}
```

## Prestige Endpoints

### Calculate Prestige Points
**GET** `/api/prestige/calculate`

Calculate how many prestige points you would earn if you reset now.

**Response:**
```json
{
  "success": true,
  "data": {
    "prestige_points_to_earn": 25,
    "current_prestige_points": 10,
    "total_after_prestige": 35
  }
}
```

Points are earned from:
- Total specialist XP (1 point per 10,000 XP)
- Total money earned (1 point per $100,000)
- Total specialist levels (1 point per 10 levels)
- Incidents handled (1 point per 100 incidents)
- SLA compliance bonuses (5-10 points)

### Perform Prestige
**POST** `/api/prestige/perform`

Reset the game with prestige bonuses. This will:
- Reset specialists, incidents, money, facilities
- Keep clients (reputation reduced to 50%)
- Award prestige points
- Maintain prestige upgrades

**Response:**
```json
{
  "success": true,
  "message": "Prestige performed successfully",
  "data": {
    "prestige_points": 35,
    "total_prestiges": 1
  }
}
```

### List Prestige Upgrades
**GET** `/api/prestige/upgrades`

List all prestige upgrades with current status.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "xp_boost_1",
      "name": "Experience Mastery I",
      "description": "Increase XP gain by 10% per level",
      "effect_type": "xp_multiplier",
      "effect_magnitude": 0.10,
      "current_level": 2,
      "max_level": 5,
      "cost": 11,
      "can_afford": true,
      "at_max_level": false,
      "total_effect": 0.2
    }
  ],
  "count": 23
}
```

### Purchase Prestige Upgrade
**POST** `/api/prestige/upgrades/{upgrade_id}/purchase`

Purchase the next level of a prestige upgrade.

**Response:**
```json
{
  "success": true,
  "message": "Prestige upgrade purchased: level 3",
  "data": {
    "upgrade_id": "xp_boost_1",
    "new_level": 3,
    "cost": 11,
    "remaining_points": 24
  }
}
```

## Offline Progress Endpoints

### Get Offline Progress Report
**GET** `/api/offline-progress`

Get the report from the last offline session.

**Response:**
```json
{
  "success": true,
  "data": {
    "time_elapsed": 86400,
    "time_simulated": 86400,
    "was_capped": false,
    "summary": {
      "total_income": 5000.0,
      "total_xp": 500,
      "incidents_handled": 120,
      "incidents_failed": 30
    }
  }
}
```

### Simulate Offline Progress
**POST** `/api/offline-progress/simulate`

Simulate offline progress for testing (admin only).

**Request:**
```json
{
  "time_elapsed": 3600
}
```

**Response:**
```json
{
  "success": true,
  "message": "Simulated 1.0 hours of offline progress",
  "data": {
    "time_elapsed": 3600,
    "time_simulated": 3600,
    "incidents": [...],
    "automation": {...},
    "income": {...}
  }
}
```

## Save/Load Endpoints

### Save Game
**POST** `/api/state/save`

Save game state to a slot (0-9, slot 0 is auto-save).

**Request:**
```json
{
  "slot": 1
}
```

**Response:**
```json
{
  "success": true,
  "message": "Game state saved to slot 1",
  "data": {
    "slot": 1,
    "filepath": "/path/to/slot_1.json",
    "metadata": {
      "save_time": 1729123456.789,
      "money": 50000,
      "specialist_count": 5,
      "prestige_level": 2
    }
  }
}
```

### Load Game
**POST** `/api/state/load`

Load game state from a slot.

**Request:**
```json
{
  "slot": 1
}
```

**Response:**
```json
{
  "success": true,
  "message": "Game state loaded from slot 1",
  "data": {
    "slot": 1,
    "money": 50000,
    "specialists": 5,
    "prestige_level": 2
  }
}
```

### List Saves
**GET** `/api/saves`

List all save files with metadata.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "slot": 0,
      "filepath": "/path/to/slot_0.json",
      "exists": true,
      "metadata": {
        "save_time": 1729123456.789,
        "money": 50000
      }
    },
    {
      "slot": 1,
      "exists": false
    }
  ],
  "count": 3
}
```

### Delete Save
**DELETE** `/api/saves/{slot}`

Delete a save file.

**Response:**
```json
{
  "success": true,
  "message": "Save slot 1 deleted"
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "success": false,
  "message": "Error description",
  "timestamp": "2025-10-16T10:00:00.000000"
}
```

Common error codes:
- **400**: Invalid request (bad parameters, insufficient funds, etc.)
- **404**: Resource not found (save file, script, upgrade, etc.)
- **500**: Server error
- **503**: Service unavailable (game state not initialized)

## Testing

You can test the API using cURL:

```bash
# Upgrade automation script
curl -X POST http://localhost:5000/api/automation-scripts/auto_assign_network_low/upgrade

# Make investment
curl -X POST http://localhost:5000/api/economy/invest \
  -H "Content-Type: application/json" \
  -d '{"investment_type": "medium_risk", "amount": 50000}'

# Calculate prestige
curl http://localhost:5000/api/prestige/calculate

# Save game
curl -X POST http://localhost:5000/api/state/save \
  -H "Content-Type: application/json" \
  -d '{"slot": 1}'
```

Or using Python:

```python
import requests

BASE_URL = "http://localhost:5000/api"

# Upgrade script
response = requests.post(f"{BASE_URL}/automation-scripts/auto_assign_network_low/upgrade")
print(response.json())

# Make investment
response = requests.post(f"{BASE_URL}/economy/invest", json={
    "investment_type": "medium_risk",
    "amount": 50000
})
print(response.json())

# Save game
response = requests.post(f"{BASE_URL}/state/save", json={"slot": 1})
print(response.json())
```
