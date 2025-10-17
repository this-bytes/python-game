# Incident Resolution with Burnout Integration

## Overview

This document describes how burnout mechanics integrate into the incident resolution system. Burnout affects specialist performance during incident resolution, making fatigue a critical strategic consideration.

## Integration Points

### 1. Incident Assignment Phase
**Location**: `src/core/idle_core.py` → `AutoAssignmentConfig.respect_fatigue`
**When**: Specialist is being considered for incident assignment
**What**: Don't auto-assign incidents to specialists with burnout > 80% (CRITICAL tier)
**Code Pattern**:
```python
def should_assign_to_specialist(specialist, incident):
    """Check if specialist should be auto-assigned."""
    # Existing checks
    if not specialist.is_available:
        return False
    
    # NEW: Burnout check
    if specialist.burnout_level > 80:  # Critical tier
        return False  # Don't overwork critical specialists
    
    return True
```

### 2. Resolution Time Calculation
**Location**: `src/core/incident_generator.py` or resolution system
**When**: Calculate how long incident will take to resolve
**What**: Apply burnout performance multiplier to resolution time
**Code Pattern**:
```python
def calculate_resolution_time(specialist, incident, base_time):
    """Calculate actual resolution time with burnout penalty."""
    # Base time from incident
    time = base_time
    
    # NEW: Apply burnout multiplier
    burnout_multiplier = specialist.get_performance_multiplier()
    time = time / burnout_multiplier  # Lower multiplier = longer time
    
    return time
```

**Example**:
- Incident base time: 100 seconds
- Specialist burnout: 50% (multiplier = 0.5)
- Actual resolution time: 100 / 0.5 = **200 seconds** (2x slower)

### 3. Success Rate Calculation
**Location**: Incident resolution success check
**When**: Determine if incident resolves successfully
**What**: Apply burnout error chance to success probability
**Code Pattern**:
```python
def calculate_success_rate(specialist, incident):
    """Calculate probability of successful resolution."""
    # Base success rate from incident
    success_rate = incident.base_success_rate
    
    # NEW: Apply burnout error chance
    error_chance = specialist.get_error_chance_from_burnout()
    success_rate = success_rate * (1.0 - error_chance)
    
    return success_rate
```

**Example**:
- Incident base success rate: 90%
- Specialist burnout: 50% (error chance = 0.25)
- Actual success rate: 90% * (1.0 - 0.25) = **67.5%** chance

### 4. Incident Completion Handler
**Location**: Incident resolution completion
**When**: Incident is resolved (successfully or failed)
**What**: Call burnout system to track completion and apply burnout changes
**Code Pattern**:
```python
def complete_incident(specialist, incident, success):
    """Complete incident and update all systems."""
    
    # Existing: Update incident status
    incident.complete_resolution(success)
    
    # NEW: Update burnout system
    if success:
        burnout_system.complete_incident(specialist.id, success=True)
    else:
        burnout_system.complete_incident(specialist.id, success=False)  # Adds trauma
    
    # Existing: Award rewards
    award_xp(specialist, incident)
    award_money(specialist, incident)
```

### 5. Burnout Assignment Tracking
**Location**: When incident assigned to specialist
**When**: Immediately after assignment confirmation
**What**: Register assignment with burnout system
**Code Pattern**:
```python
def assign_incident_to_specialist(specialist, incident):
    """Assign incident to specialist."""
    
    # Existing: Validate and assign
    specialist.current_incident = incident
    incident.assigned_to = specialist.id
    
    # NEW: Track assignment in burnout system
    success, message = burnout_system.assign_incident(
        specialist.id,
        incident_difficulty=incident.difficulty
    )
    
    if not success:
        log.warning(f"Burnout assignment tracking failed: {message}")
```

## Burnout Impact Summary

| Burnout Level | Tier        | Performance | Error Chance | Impact |
|----------------|-------------|-------------|--------------|--------|
| 0-20%         | FRESH       | 1.0x        | 0%           | None |
| 21-40%        | STRESSED    | 0.75x       | 5%           | Slight slowdown |
| 41-60%        | EXHAUSTED   | 0.5x        | 15%          | Halved speed |
| 61-80%        | CRITICAL    | 0.25x       | 30%          | Very slow |
| 81-100%       | BROKEN      | 0.0x        | 50%          | Can't assign |

## Recovery Options

### 1. Rest Day (Free)
- Cost: None
- Recovery: 30% burnout
- Duration: 1 day
- Success rate: 100%
- Use case: Regular maintenance

### 2. Vacation (Paid)
- Cost: 300-1500 money (scales with days)
- Recovery: 30-80% burnout (scales with days 1-5)
- Duration: 1-5 days
- Success rate: 100%
- Use case: Emergency recovery

### 3. Therapy (Paid)
- Cost: 500 money
- Recovery: Clear trauma counter (failed incident accumulation)
- Duration: 1 day
- Success rate: 100%
- Use case: Trauma-specific recovery

## Implementation Priority

### High Priority (Next)
1. ✅ Burnout system core (DONE)
2. ⏳ Incident resolution integration (THIS DOCUMENT)
3. ⏳ UI display of burnout status

### Medium Priority
4. ⏳ Specialist relationships (synergies)
5. ⏳ Advanced recovery mechanics

### Lower Priority
6. ⏳ Burnout-based recruitment quality
7. ⏳ Vacation scheduling UI

## Testing Strategy

### Unit Tests
```python
def test_burnout_multiplier_applied_to_resolution_time():
    """Verify resolution time increases with burnout."""
    specialist = create_specialist(burnout_level=50)
    incident = create_incident(base_resolution_time=100)
    
    actual_time = calculate_resolution_time(specialist, incident)
    
    assert actual_time == 200  # 100 / 0.5 = 200
```

### Integration Tests
```python
def test_full_incident_resolution_with_burnout():
    """Verify complete flow with burnout effects."""
    specialist = create_specialist(burnout_level=40)
    incident = create_incident()
    
    # Assignment
    assign_incident(specialist, incident)
    assert specialist.current_incident == incident
    
    # Verify time increased
    time = calculate_resolution_time(specialist, incident)
    assert time > incident.base_resolution_time
    
    # Verify error chance applied
    success = resolve_incident(specialist, incident)
    # Error chance reduces success probability
```

## Code Examples

### Example 1: Auto-Assignment with Burnout Check
```python
def auto_assign_incidents(specialists, incidents, burnout_system):
    """Automatically assign incidents, respecting burnout."""
    for incident in incidents:
        if incident.assigned_to:
            continue  # Already assigned
        
        # Find best available specialist
        for specialist in specialists:
            # Skip if too fatigued
            if specialist.burnout_level > 80:
                continue
            
            # Check synergy/availability
            if specialist.is_available and specialist.specialty == incident.specialty:
                specialist.current_incident = incident
                burnout_system.assign_incident(specialist.id, incident.difficulty)
                break
```

### Example 2: Resolution Completion with Burnout Updates
```python
def handle_incident_completion(specialist, incident, success, game_state):
    """Complete incident and update all systems."""
    resolution_time = game_state.get_elapsed_time() - incident.assigned_time
    
    # Update incident
    incident.complete_resolution(success)
    specialist.current_incident = None
    
    # Update burnout based on result
    if success:
        # Successful resolution
        game_state.burnout_system.complete_incident(
            specialist.id,
            success=True
        )
    else:
        # Failed resolution adds trauma
        game_state.burnout_system.complete_incident(
            specialist.id,
            success=False
        )
    
    # Award rewards
    xp = calculate_xp(incident, resolution_time, success)
    money = calculate_money(incident, resolution_time, success)
    specialist.xp += xp
    specialist.money += money
    
    # Log event
    log.info(f"Incident {incident.id} completed by {specialist.name}: "
             f"success={success}, burnout={specialist.burnout_level}%")
```

### Example 3: Backend API for Incident Completion
```python
@app.post("/incidents/<incident_id>/complete")
def complete_incident_api(incident_id):
    """Complete an incident and update burnout."""
    data = request.json
    success = data.get("success", False)
    
    # Get incident and specialist
    incident = game_state.get_incident(incident_id)
    specialist = game_state.get_specialist(incident.assigned_to)
    
    if not incident or not specialist:
        return {"error": "Incident or specialist not found"}, 404
    
    # Complete
    handle_incident_completion(specialist, incident, success, game_state)
    
    # Return updated status
    return {
        "incident_id": incident_id,
        "status": "completed",
        "specialist_burnout": specialist.burnout_level,
        "specialist_tier": game_state.burnout_system.get_specialist_status(specialist.id)["tier"]
    }
```

## Next Steps

1. ✅ Burnout system implementation (COMPLETE)
2. ⏳ Add `calculate_resolution_time()` function using burnout multiplier
3. ⏳ Add `calculate_success_rate()` function using error chance
4. ⏳ Integrate into auto-assignment logic to skip critical specialists
5. ⏳ Integrate into incident completion handler
6. ⏳ Create backend API for incident completion with burnout tracking
7. ⏳ Add UI components to display burnout during incident resolution
8. ⏳ Test end-to-end flow with multiple incidents

## Success Criteria

- ✅ Burnout multipliers correctly reduce resolution speed
- ✅ Error chance correctly reduces success rate
- ✅ Auto-assignment skips CRITICAL (81%+) specialists
- ✅ Incident completion updates burnout system
- ✅ Recovery actions properly decrease burnout
- ✅ Integration tests pass
- ✅ Code exemplifies standards (type hints, tests, docstrings)
- ✅ Backend API endpoints functional
