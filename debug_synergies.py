"""Debug script to test synergy generation."""

import sys
sys.path.insert(0, '/home/localadmin/python-game')

from src.models.specialist import Specialist, SpecialistStats
from src.core.idle_core import IdleCore

# Create a specialist
stats = SpecialistStats(speed=1.0, accuracy=80.0, experience_bonus=1.0)
specialist = Specialist(
    id="test_001",
    name="Test Specialist",
    specialty="Network Security",
    level=1,
    xp=0,
    stats=stats
)

print(f"Specialist: {specialist.name}")
print(f"Specialty: {specialist.specialty}")
print(f"Has synergies attr: {hasattr(specialist, 'synergies')}")
print(f"Synergies before: {specialist.synergies}")
print(f"Synergies is empty: {not specialist.synergies}")

# Generate synergies
idle_core = IdleCore()
synergies = idle_core.generate_specialist_synergies(specialist)

print(f"\nGenerated synergies: {synergies}")
print(f"Number of synergies: {len(synergies)}")

for syn in synergies:
    print(f"  - {syn.threat_type}: {syn.xp_multiplier}x XP, {syn.reward_multiplier}x $")

# Assign synergies
specialist.synergies = synergies
print(f"\nSynergies after assignment: {specialist.synergies}")
print(f"Number: {len(specialist.synergies)}")
