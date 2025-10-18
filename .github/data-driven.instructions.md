# Data-Driven Design - Instructions

**This file contains all JSON configuration patterns and data-driven design principles.**

Reference this when:
- Adding new game parameters
- Creating configuration files
- Understanding data-driven architecture
- Implementing hot-reloadable systems

---

## Data-Driven Philosophy

**ALL GAME PARAMETERS MUST BE IN JSON FILES.**

Never hardcode game balance values in Python. Everything that affects gameplay must be configurable through JSON files in `/data/`.

**Why?**
- Balance changes without code changes
- Hot-reload during development
- Easy A/B testing
- Designer-friendly tuning
- Version control of balance changes

---

## JSON Configuration Structure

```
/data/
  game_config.json           → Core game settings and economy
  specialist_templates.json  → Specialist types and starting stats
  specialists.json           → Active specialist instances
  incidents.json             → Incident types and templates
  clients.json               → Client data and contracts
  contracts.json             → Contract templates
  automation_scripts.json    → Automation script definitions
  abilities.json             → Ability definitions
  equipment.json             → Equipment catalog
  achievements.json          → Achievement definitions
  prestige_upgrades.json     → Prestige upgrade tree
  facilities.json            → Facility upgrade data
  features.json              → Feature flag configuration
  market_events.json         → Market event definitions
  themes.json                → UI theme configuration
```

---

## Game Configuration (`game_config.json`)

```json
{
  "game_settings": {
    "starting_specialists": 2,
    "starting_money": 5000,
    "time_scale": 1.0,
    "max_active_incidents": 50,
    "max_specialists": 10
  },
  "xp_curve": {
    "base_xp": 100,
    "exponent": 1.5,
    "level_cap": 20
  },
  "economy": {
    "sla_failure_penalty_multiplier": 0.5,
    "perfect_completion_bonus": 1.2,
    "specialist_hiring_cost_base": 2000,
    "incident_reward_multiplier": 1.0
  },
  "burnout": {
    "burnout_rate_per_incident": 5,
    "recovery_rate_per_hour": 10,
    "penalty_threshold": 80,
    "performance_multiplier_at_critical": 0.25
  },
  "relationships": {
    "friendship_bonus_multiplier": 1.15,
    "rivalry_penalty_multiplier": 0.85,
    "relationship_intensity_per_incident": 0.1
  }
}
```

**Pattern**: Nested configuration organized by system. Each value should have a clear, descriptive key.

---

## Specialist Templates (`specialist_templates.json`)

```json
{
  "specialist_templates": [
    {
      "id": "template_network_security",
      "name": "Network Security Specialist",
      "specialty": "Network Security",
      "description": "Expert in network infrastructure and threat detection",
      "base_stats": {
        "speed": 100,
        "accuracy": 85,
        "experience_bonus": 1.0
      },
      "starting_level": 1,
      "starting_xp": 0,
      "hiring_cost": 2000
    }
  ]
}
```

**Pattern**: Templates define DEFAULT values. Instances are created from templates.

---

## Incident Types (`incidents.json`)

```json
{
  "incident_types": [
    {
      "id": "inc_type_ddos",
      "name": "DDoS Attack",
      "description": "Distributed denial of service attack overwhelming servers",
      "specialty_required": "Network Security",
      "difficulty_range": [1, 5],
      "base_sla_seconds": 300,
      "base_reward": 500,
      "xp_reward": 100,
      "criticality": "high",
      "tags": ["network", "availability", "attack"]
    }
  ]
}
```

**Pattern**: Each incident type defines requirements, rewards, and metadata.

---

## Automation Scripts (`automation_scripts.json`)

```json
{
  "automation_scripts": [
    {
      "id": "auto_assign_low_priority",
      "name": "Auto-Assign Low Priority",
      "description": "Automatically assign low-difficulty incidents",
      "required_level": 3,
      "specialty": "Network Security",
      "trigger_conditions": {
        "max_difficulty": 2,
        "specialty_match": true,
        "specialist_available": true,
        "min_accuracy": 80
      },
      "effect": "auto_assign",
      "cooldown_seconds": 60,
      "enabled_by_default": false
    }
  ]
}
```

**Pattern**: Declarative automation with trigger conditions and effects.

---

## Abilities (`abilities.json`)

```json
{
  "abilities": [
    {
      "id": "ability_speed_boost",
      "name": "Adrenaline Rush",
      "description": "Temporarily increase resolution speed by 50%",
      "specialty": "Network Security",
      "required_level": 5,
      "cooldown_seconds": 300,
      "duration_seconds": 60,
      "effect": {
        "type": "resolution_speed_multiplier",
        "value": 1.5
      },
      "targets": ["self"]
    }
  ]
}
```

**Pattern**: Abilities with clear effects, cooldowns, and targeting.

---

## Equipment (`equipment.json`)

```json
{
  "equipment": [
    {
      "id": "eq_laptop_gaming",
      "name": "Gaming Laptop",
      "description": "High-performance laptop with excellent specs",
      "slot": "primary_tool",
      "rarity": "rare",
      "stat_bonuses": {
        "speed": 15,
        "accuracy": 5
      },
      "required_level": 5,
      "drop_weight": 10
    }
  ]
}
```

**Pattern**: Equipment with stats, rarity, and drop rates.

---

## Achievements (`achievements.json`)

```json
{
  "achievements": [
    {
      "id": "ach_first_incident",
      "name": "First Response",
      "description": "Complete your first incident",
      "category": "progression",
      "criteria": {
        "type": "incidents_resolved",
        "threshold": 1
      },
      "rewards": {
        "money": 500,
        "xp": 100
      },
      "hidden": false
    }
  ]
}
```

**Pattern**: Achievements with criteria and rewards.

---

## Feature Flags (`features.json`)

```json
{
  "features": [
    {
      "id": "burnout_system",
      "name": "Burnout System",
      "enabled": true,
      "description": "Enable specialist burnout mechanics",
      "rollout_percentage": 100,
      "dependencies": []
    },
    {
      "id": "relationships_system",
      "name": "Relationships System",
      "enabled": true,
      "description": "Enable specialist relationship dynamics",
      "rollout_percentage": 100,
      "dependencies": ["burnout_system"]
    }
  ]
}
```

**Pattern**: Feature flags with dependencies and rollout control.

---

## Loading Configuration in Python

```python
import json
from typing import Dict, Any

def load_game_config(path: str = "data/game_config.json") -> Dict[str, Any]:
    """Load game configuration from JSON.
    
    Args:
        path: Path to configuration file
        
    Returns:
        Dictionary containing configuration
        
    Raises:
        FileNotFoundError: Configuration file not found
        json.JSONDecodeError: Invalid JSON format
    """
    with open(path, 'r') as f:
        config = json.load(f)
    
    # Validate schema
    required_keys = ["game_settings", "xp_curve", "economy"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required key: {key}")
    
    return config

# Usage
config = load_game_config()
starting_money = config["game_settings"]["starting_money"]
```

---

## Hot-Reloading Configuration

```python
class ConfigurableSystem:
    """System that reloads configuration on demand."""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        return load_game_config(self.config_path)
    
    def reload_config(self) -> None:
        """Hot-reload configuration without restart."""
        self.config = self.load_config()
        logger.info(f"Reloaded configuration from {self.config_path}")
```

**Backend hot-reload endpoint:**
```bash
curl -X POST http://localhost:5000/config/reload
```

---

## Configuration Access Patterns

### ❌ WRONG - Hardcoded values
```python
def calculate_reward(difficulty: int) -> float:
    base_reward = 500  # Magic number!
    multiplier = 1.37  # Where did this come from?
    return base_reward * difficulty * multiplier
```

### ✅ CORRECT - Configuration-driven
```python
def calculate_reward(difficulty: int, config: GameConfig) -> float:
    """Calculate reward from configuration.
    
    Args:
        difficulty: Incident difficulty (1-5)
        config: Game configuration
        
    Returns:
        Calculated reward
    """
    base_reward = config.economy.base_reward
    multiplier = config.economy.difficulty_multiplier
    return base_reward * difficulty * multiplier
```

---

## Named Constants for Magic Numbers

When a value appears in code, it must be justified:

```python
# ❌ WRONG
if specialist.burnout > 80:
    performance_multiplier = 0.9

# ✅ CORRECT - From configuration
BURNOUT_PENALTY_THRESHOLD = config.burnout.penalty_threshold  # 80
BURNOUT_PERFORMANCE_MULTIPLIER = config.burnout.performance_multiplier  # 0.9

if specialist.burnout > BURNOUT_PENALTY_THRESHOLD:
    performance_multiplier = BURNOUT_PERFORMANCE_MULTIPLIER
```

---

## JSON Schema Validation

Validate JSON files against schemas in `/data/schemas/`:

```python
import jsonschema

def validate_config(config: Dict[str, Any], schema_path: str) -> None:
    """Validate configuration against JSON schema.
    
    Args:
        config: Configuration to validate
        schema_path: Path to JSON schema file
        
    Raises:
        jsonschema.ValidationError: Configuration invalid
    """
    with open(schema_path, 'r') as f:
        schema = json.load(f)
    
    jsonschema.validate(instance=config, schema=schema)
```

---

## Data-Driven Development Workflow

1. **Identify game parameter** (difficulty multiplier, reward amount, etc.)
2. **Add to appropriate JSON file** with descriptive key
3. **Load configuration in code** via structured config object
4. **Never hardcode** the value in Python
5. **Test with different values** via hot-reload
6. **Document in JSON** with comments (use `_comment` keys if needed)

---

## Configuration Best Practices

✅ **DO:**
- Use clear, descriptive keys (`burnout_penalty_threshold` not `bp_thresh`)
- Group related settings together
- Provide reasonable default values
- Document expected ranges and units
- Version control configuration changes
- Use feature flags for new systems

❌ **DON'T:**
- Hardcode game balance values
- Use magic numbers without explanation
- Create config keys for one-time values
- Mix configuration with code
- Use abbreviations or unclear names

---

## Backend Configuration API

```bash
# Get current configuration
curl http://localhost:5000/config

# Reload configuration
curl -X POST http://localhost:5000/config/reload

# Update specific value (development only)
curl -X PUT http://localhost:5000/config/update \
  -H "Content-Type: application/json" \
  -d '{
    "path": "economy.incident_reward_multiplier",
    "value": 1.5
  }'
```

---

## See Also

- [ARCHITECTURE.md](ARCHITECTURE.md) - Overall architecture
- [COMMON_TASKS.md](COMMON_TASKS.md) - How to balance economy
- [copilot-instructions.md](copilot-instructions.md) - Main instructions
