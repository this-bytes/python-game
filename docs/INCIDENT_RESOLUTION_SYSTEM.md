# Incident Resolution System

## Overview

The Incident Resolution System implements interactive, decision-based incident resolution that replaces the simple automatic resolution with engaging player choice mechanics. Players make strategic decisions through multi-stage decision trees that affect resolution outcomes, time, costs, and success rates.

## Core Components

### Resolution Trees (`data/resolution_trees.json`)

Decision trees are stored in JSON format with the following structure:

```json
{
  "ddos_attack": {
    "stages": [
      {
        "stage_id": "containment",
        "prompt": "DDoS attack detected. How do you respond?",
        "decisions": [
          {
            "id": "block_ips",
            "text": "Block attacking IP ranges",
            "effects": {
              "time_multiplier": 0.8,
              "accuracy_check": true,
              "burnout_cost": 5,
              "success_chance": 0.85
            },
            "next_stage": "investigation"
          }
        ],
        "time_limit_seconds": 30.0
      }
    ]
  }
}
```

### Resolution Session

Active resolution sessions track player progress through decision trees:

- **Session State**: Current stage, decisions made, accumulated effects
- **Time Pressure**: SLA deadlines create urgency and affect decision outcomes
- **Specialist Skills**: Level and stats modify decision effectiveness

### Decision Effects

Each decision can modify:
- **Time Multiplier**: Speed up or slow down resolution
- **Success Chance**: Probability of successful resolution
- **Burnout Cost**: Specialist fatigue accumulation
- **Money Cost**: Additional expenses for certain approaches
- **Accuracy Bonus**: Improved precision for complex tasks

## API Usage

### Starting Resolution

```python
from src.core.resolution_system import ResolutionSystem

resolution_system = ResolutionSystem(burnout_system)
session = resolution_system.start_resolution(incident, specialist)
```

### Getting Current Stage Info

```python
stage_info = resolution_system.get_current_stage_info(session)
# Returns: stage_id, prompt, decisions, time_remaining
```

### Making Decisions

```python
success, next_stage, effects = resolution_system.make_decision(
    session, decision_id, specialist
)
```

### Completing Resolution

```python
result = resolution_system.complete_resolution(session, specialist, incident)
# Returns: ResolutionResult with success, time, costs, etc.
```

## Decision Tree Creation

### Adding New Incident Types

1. Add new tree to `data/resolution_trees.json`
2. Use descriptive stage IDs and clear prompts
3. Balance decision effects for strategic depth
4. Test time limits and decision consequences

### Decision Balancing Guidelines

- **Time Multipliers**: 0.5-2.0 range (faster/slower resolution)
- **Success Chances**: 0.6-0.95 range (realistic probabilities)
- **Burnout Costs**: 5-20 points per decision
- **Money Costs**: 0-5000 credits for expensive options

### Stage Design Principles

- **3-5 Stages**: Keep resolution engaging but not overwhelming
- **2-4 Decisions per Stage**: Provide meaningful choices
- **Risk/Reward Balance**: High-risk decisions offer better rewards
- **Specialist Relevance**: Different approaches favor different specialties

## Integration Points

### Burnout System
- Decisions accumulate burnout that affects future performance
- High-pressure situations increase burnout costs
- Recovery mechanics provide strategic depth

### Specialist Progression
- Skill levels modify decision effectiveness
- Specialty matching improves success rates
- Level-appropriate challenges maintain engagement

### Time Pressure Mechanics
- SLA deadlines create urgency
- Time pressure affects decision outcomes
- Late decisions incur penalties

## Testing

Comprehensive test coverage includes:
- Session creation and state management
- Decision execution and effect application
- Time pressure calculations
- Specialist skill modifications
- Error handling for invalid inputs

Run tests with: `pytest tests/test_decision_based_resolution.py`

## Future Enhancements

- **Dynamic Trees**: Context-aware decision options
- **Branching Paths**: Multiple resolution strategies
- **Specialist Abilities**: Unique decision options per specialist
- **Difficulty Scaling**: Adaptive decision trees based on player skill</content>
<parameter name="filePath">/home/localadmin/code/python-game/docs/INCIDENT_RESOLUTION_SYSTEM.md