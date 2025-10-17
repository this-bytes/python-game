"""Idle Core - True Idle Game Mechanics with Strategic Depth

This system makes the game a REAL idle game:
1. Auto-assigns incidents to specialists automatically (always on)
2. Specialist synergies for strategic player intervention
3. Threat-type multipliers (like Balatro's card synergies)
4. Ability timing system for manual intervention
5. Strategic depth without requiring constant clicking
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import random


class ThreatType(Enum):
    """Specific threat types that specialists can have multipliers for."""
    DDOS = "DDoS Attack"
    MALWARE = "Malware Infection"
    PHISHING = "Phishing Campaign"
    DATA_BREACH = "Data Breach"
    RANSOMWARE = "Ransomware"
    SQL_INJECTION = "SQL Injection"
    XSS = "Cross-Site Scripting"
    ZERO_DAY = "Zero-Day Exploit"
    INSIDER_THREAT = "Insider Threat"
    APT = "Advanced Persistent Threat"


@dataclass
class SpecialistSynergy:
    """Synergy bonuses for matching specialist to incident type."""
    threat_type: str
    xp_multiplier: float = 1.0
    speed_multiplier: float = 1.0
    reward_multiplier: float = 1.0
    success_rate_bonus: float = 0.0
    
    def get_display_string(self) -> str:
        """Get human-readable synergy description."""
        bonuses = []
        if self.xp_multiplier > 1.0:
            bonuses.append(f"{self.xp_multiplier}x XP")
        if self.speed_multiplier > 1.0:
            bonuses.append(f"{self.speed_multiplier}x Speed")
        if self.reward_multiplier > 1.0:
            bonuses.append(f"{self.reward_multiplier}x Reward")
        if self.success_rate_bonus > 0:
            bonuses.append(f"+{int(self.success_rate_bonus*100)}% Success")
        
        return f"{self.threat_type}: " + ", ".join(bonuses)


@dataclass
class AutoAssignmentConfig:
    """Configuration for automatic incident assignment."""
    enabled: bool = True
    prefer_synergies: bool = True  # Prioritize synergy matches
    balance_workload: bool = True  # Spread work across specialists
    respect_fatigue: bool = True  # Don't overwork tired specialists
    difficulty_threshold: int = 5  # Auto-assign up to this difficulty (1-5 = all)
    
    # Smart assignment priorities
    priority_order: List[str] = field(default_factory=lambda: [
        "synergy",  # Match specialist synergies first
        "specialty",  # Then match specialty
        "availability",  # Then check availability
        "success_rate",  # Then highest success rate
        "fatigue"  # Finally consider fatigue
    ])


class IdleCore:
    """Core idle game mechanics - auto-assignment with strategic depth."""
    
    def __init__(self):
        self.config = AutoAssignmentConfig()
        
        # Track auto-assignment statistics
        self.stats = {
            "total_auto_assigned": 0,
            "synergy_matches": 0,
            "specialty_matches": 0,
            "suboptimal_assignments": 0,
            "manual_overrides": 0
        }
    
    def auto_assign_incidents(self, game_state) -> List[Dict]:
        """Automatically assign pending incidents to available specialists.
        
        This is the CORE of the idle game - it runs constantly.
        Respects burnout: skips CRITICAL (81%+) specialists.
        
        Args:
            game_state: Current game state
            
        Returns:
            List of assignment results
        """
        if not self.config.enabled:
            return []
        
        assignments = []
        pending_incidents = [inc for inc in game_state.incidents if inc.status == "pending"]
        available_specialists = [spec for spec in game_state.specialists if spec.is_available()]
        
        if not pending_incidents or not available_specialists:
            return []
        
        # Sort incidents by urgency (SLA time remaining)
        pending_incidents.sort(key=lambda inc: inc.get_time_remaining())
        
        for incident in pending_incidents:
            # Check if difficulty is within auto-assignment threshold
            if incident.difficulty > self.config.difficulty_threshold:
                continue
            
            # Find best specialist for this incident
            best_match = self._find_best_specialist_match(
                incident, available_specialists, game_state
            )
            
            if best_match:
                specialist, match_info = best_match
                
                # BURNOUT CHECK: Skip CRITICAL specialists (81%+)
                if self.config.respect_fatigue and specialist.burnout_level > 80:
                    continue
                
                # Perform assignment
                success = game_state.assign_incident_to_specialist(incident.id, specialist.id)
                
                if success:
                    assignments.append({
                        "incident_id": incident.id,
                        "specialist_id": specialist.id,
                        "match_quality": match_info["quality"],
                        "synergy_active": match_info["synergy_active"],
                        "bonuses": match_info["bonuses"],
                        "auto_assigned": True
                    })
                    
                    self.stats["total_auto_assigned"] += 1
                    if match_info["synergy_active"]:
                        self.stats["synergy_matches"] += 1
                    elif match_info["specialty_match"]:
                        self.stats["specialty_matches"] += 1
                    else:
                        self.stats["suboptimal_assignments"] += 1
                    
                    # Remove from available specialists
                    available_specialists.remove(specialist)
                    
                    if not available_specialists:
                        break  # No more specialists available
        
        return assignments
    
    def _find_best_specialist_match(self, incident, specialists, game_state) -> Optional[Tuple]:
        """Find the best specialist match for an incident.
        
        This implements the strategic depth - synergies, specialties, etc.
        
        Returns:
            (specialist, match_info) or None
        """
        if not specialists:
            return None
        
        scored_specialists = []
        
        for specialist in specialists:
            score = 0
            match_info = {
                "quality": "poor",
                "synergy_active": False,
                "specialty_match": False,
                "bonuses": {}
            }
            
            # Check for synergy match (HIGHEST PRIORITY)
            synergy = self._check_synergy(specialist, incident)
            if synergy:
                score += 1000  # Massive priority for synergies
                match_info["synergy_active"] = True
                match_info["bonuses"] = {
                    "xp_mult": synergy.xp_multiplier,
                    "speed_mult": synergy.speed_multiplier,
                    "reward_mult": synergy.reward_multiplier,
                    "success_bonus": synergy.success_rate_bonus
                }
                match_info["quality"] = "synergy"
            
            # Check specialty match
            if specialist.specialty == incident.specialty_required:
                score += 100
                match_info["specialty_match"] = True
                if not synergy:
                    match_info["quality"] = "good"
            
            # Calculate success probability
            success_prob = specialist.calculate_success_probability(incident.difficulty)
            score += success_prob * 50  # Up to 50 points for success rate
            
            # Penalize fatigue
            if self.config.respect_fatigue and hasattr(specialist, 'fatigue'):
                fatigue_penalty = specialist.fatigue * 20
                score -= fatigue_penalty
            
            # Bonus for being underutilized (workload balancing)
            if self.config.balance_workload:
                if specialist.assigned_incident_id is None:
                    score += 10
            
            scored_specialists.append((specialist, score, match_info))
        
        if not scored_specialists:
            return None
        
        # Return specialist with highest score
        scored_specialists.sort(key=lambda x: x[1], reverse=True)
        best = scored_specialists[0]
        
        return (best[0], best[2])
    
    def _check_synergy(self, specialist, incident) -> Optional[SpecialistSynergy]:
        """Check if specialist has synergy with incident type.
        
        This is where the strategic depth comes from - matching specialists
        to specific threat types gives massive bonuses.
        """
        if not hasattr(specialist, 'synergies'):
            return None
        
        # Check if specialist has synergy for this incident type
        for synergy in specialist.synergies:
            if synergy.threat_type == incident.incident_type:
                return synergy
        
        return None
    
    def suggest_manual_intervention(self, game_state) -> List[Dict]:
        """Suggest incidents where manual assignment would give better synergies.
        
        This creates strategic depth - the game auto-plays, but the player
        can intervene for bonus multipliers (like Balatro).
        
        Returns:
            List of suggestions: {incident, specialist, synergy_bonus}
        """
        suggestions = []
        
        pending_incidents = [inc for inc in game_state.incidents if inc.status == "pending"]
        available_specialists = [spec for spec in game_state.specialists if spec.is_available()]
        
        for incident in pending_incidents:
            # Find specialists with synergy for this incident
            synergy_specialists = []
            
            for specialist in available_specialists:
                synergy = self._check_synergy(specialist, incident)
                if synergy:
                    synergy_specialists.append({
                        "specialist": specialist,
                        "synergy": synergy,
                        "bonuses": {
                            "xp_mult": synergy.xp_multiplier,
                            "speed_mult": synergy.speed_multiplier,
                            "reward_mult": synergy.reward_multiplier
                        }
                    })
            
            if synergy_specialists:
                # Sort by total bonus
                synergy_specialists.sort(
                    key=lambda x: (
                        x["synergy"].xp_multiplier +
                        x["synergy"].speed_multiplier +
                        x["synergy"].reward_multiplier
                    ),
                    reverse=True
                )
                
                best = synergy_specialists[0]
                suggestions.append({
                    "incident": incident,
                    "specialist": best["specialist"],
                    "synergy": best["synergy"],
                    "bonuses": best["bonuses"],
                    "priority": "high" if incident.get_time_remaining() < 60 else "medium"
                })
        
        return suggestions
    
    def apply_synergy_bonuses(self, specialist, incident, game_state):
        """Apply synergy bonuses when incident is resolved.
        
        This is called during incident resolution to apply the actual bonuses.
        """
        synergy = self._check_synergy(specialist, incident)
        if not synergy:
            return None
        
        bonuses = {
            "xp_multiplier": synergy.xp_multiplier,
            "speed_multiplier": synergy.speed_multiplier,
            "reward_multiplier": synergy.reward_multiplier,
            "success_rate_bonus": synergy.success_rate_bonus,
            "synergy_name": synergy.threat_type
        }
        
        return bonuses
    
    def generate_specialist_synergies(self, specialist, num_synergies: int = 2) -> List[SpecialistSynergy]:
        """Generate random synergies for a specialist based on their specialty.
        
        This adds strategic depth - each specialist has unique synergy bonuses.
        """
        specialty_to_threats = {
            "Network Security": [
                ThreatType.DDOS.value,
                ThreatType.SQL_INJECTION.value,
                ThreatType.XSS.value
            ],
            "Malware Analysis": [
                ThreatType.MALWARE.value,
                ThreatType.RANSOMWARE.value,
                ThreatType.ZERO_DAY.value
            ],
            "Digital Forensics": [
                ThreatType.DATA_BREACH.value,
                ThreatType.INSIDER_THREAT.value,
                ThreatType.APT.value
            ],
            "Application Security": [
                ThreatType.SQL_INJECTION.value,
                ThreatType.XSS.value,
                ThreatType.ZERO_DAY.value
            ],
            "Cloud Security": [
                ThreatType.DATA_BREACH.value,
                ThreatType.DDOS.value,
                ThreatType.RANSOMWARE.value
            ],
            "Threat Intelligence": [
                ThreatType.PHISHING.value,
                ThreatType.APT.value,
                ThreatType.INSIDER_THREAT.value
            ],
            "Incident Response": [
                ThreatType.DATA_BREACH.value,
                ThreatType.RANSOMWARE.value,
                ThreatType.APT.value
            ]
        }
        
        possible_threats = specialty_to_threats.get(specialist.specialty, [
            ThreatType.MALWARE.value,
            ThreatType.PHISHING.value,
            ThreatType.DDOS.value
        ])
        
        # Generate synergies
        synergies = []
        selected_threats = random.sample(possible_threats, min(num_synergies, len(possible_threats)))
        
        for threat in selected_threats:
            # Randomize bonuses
            xp_mult = random.choice([1.5, 2.0, 2.5])
            speed_mult = random.choice([1.3, 1.5, 1.8])
            reward_mult = random.choice([1.2, 1.5, 1.8])
            success_bonus = random.choice([0.1, 0.15, 0.2])
            
            synergy = SpecialistSynergy(
                threat_type=threat,
                xp_multiplier=xp_mult,
                speed_multiplier=speed_mult,
                reward_multiplier=reward_mult,
                success_rate_bonus=success_bonus
            )
            synergies.append(synergy)
        
        return synergies
    
    def toggle_auto_assignment(self) -> bool:
        """Toggle auto-assignment on/off.
        
        Returns:
            New state (True = enabled, False = disabled)
        """
        self.config.enabled = not self.config.enabled
        return self.config.enabled
    
    def set_difficulty_threshold(self, threshold: int):
        """Set the maximum difficulty for auto-assignment.
        
        Args:
            threshold: 1-5, incidents above this won't be auto-assigned
        """
        self.config.difficulty_threshold = max(1, min(5, threshold))
