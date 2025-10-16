"""Test script to verify idle mechanics work correctly."""

import sys
sys.path.insert(0, '/home/localadmin/python-game')

from src.models.game_state import GameState
from src.core.idle_core import IdleCore
import time

print("=== IDLE MECHANICS TEST ===\n")

# Create game state
print("1. Creating game state...")
game_state = GameState()
print(f"   ✓ Game state initialized")
print(f"   ✓ Specialists: {len(game_state.specialists)}")
print(f"   ✓ Money: ${game_state.current_money}")

# Check IdleCore initialization
print("\n2. Checking IdleCore...")
if hasattr(game_state, '_idle_core') and game_state._idle_core:
    print(f"   ✓ IdleCore initialized")
    print(f"   ✓ Auto-play enabled: {game_state._idle_core.config.enabled}")
else:
    print("   ✗ IdleCore NOT initialized!")
    sys.exit(1)

# Check specialist synergies
print("\n3. Checking specialist synergies...")
for spec in game_state.specialists:
    print(f"   Specialist: {spec.name} ({spec.specialty})")
    if hasattr(spec, 'synergies') and spec.synergies:
        print(f"      ✓ {len(spec.synergies)} synergies:")
        for syn in spec.synergies:
            print(f"         - {syn.threat_type}: {syn.xp_multiplier}x XP, {syn.reward_multiplier}x $")
    else:
        print(f"      ✗ NO synergies!")

# Simulate game loop for 20 seconds with faster time
print("\n4. Running game loop for 20 seconds (10x speed)...")
print("   Watching for auto-assignments...\n")

start_time = time.time()
iterations = 0
assignments_made = 0
incidents_generated = 0

while time.time() - start_time < 20:
    # Update game state with larger delta time (10x speed)
    game_state.update(1.0)  # 1.0 second delta at 10x speed
    iterations += 1
    
    # Track incidents generated
    current_incident_count = len(game_state.incidents)
    if current_incident_count > incidents_generated:
        new_incidents = current_incident_count - incidents_generated
        incidents_generated = current_incident_count
        print(f"   ⚡ {new_incidents} new incident(s) generated! Total: {incidents_generated}")
    
    # Check for new assignments
    for incident in list(game_state.incidents):
        if incident.assigned_specialist_id:
            # Find specialist name
            spec_name = "Unknown"
            for spec in game_state.specialists:
                if spec.id == incident.assigned_specialist_id:
                    spec_name = spec.name
                    break
            print(f"   ✓ Auto-assigned: {incident.incident_type} → {spec_name}")
            assignments_made += 1
            # Remove to avoid duplicate reporting
            game_state.incidents.remove(incident)
    
    time.sleep(0.1)

print(f"\n5. Results:")
print(f"   Total iterations: {iterations}")
print(f"   Incidents generated: {incidents_generated}")
print(f"   Auto-assignments made: {assignments_made}")
print(f"   Current incidents: {len(game_state.incidents)}")
print(f"   Current money: ${game_state.current_money}")
print(f"   Assignments/Incidents ratio: {assignments_made}/{incidents_generated}")

if assignments_made > 0:
    print(f"\n✅ SUCCESS: Auto-assignment system is working!")
else:
    print(f"\n⚠️  WARNING: No auto-assignments made (may need more incidents)")

print("\n=== TEST COMPLETE ===")
