"""Incident resolution system with decision-based gameplay and burnout integration."""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple, List
import random
import time
import json
import logging
from src.core.burnout_system import BurnoutSystem
from src.models.specialist import Specialist
from src.models.incident import Incident

logger = logging.getLogger(__name__)


@dataclass
class ResolutionDecision:
    """A decision made during incident resolution."""
    decision_id: str
    stage_id: str
    timestamp: Optional[float] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class ResolutionSession:
    """Active resolution session with decision state."""
    incident_id: str
    specialist_id: str
    tree_id: str
    current_stage: str
    decisions_made: List[ResolutionDecision]
    start_time: float
    time_pressure_multiplier: float = 1.0
    total_burnout_cost: float = 0.0
    total_money_cost: int = 0
    
    @property
    def elapsed_time(self) -> float:
        """Time elapsed since session start."""
        return time.time() - self.start_time
    
    @property
    def current_stage_time_limit(self) -> float:
        """Get time limit for current stage with pressure multiplier."""
        # This would be loaded from the tree config
        base_limit = 30.0  # Default fallback
        return base_limit * self.time_pressure_multiplier


@dataclass
class ResolutionResult:
    """Result of incident resolution attempt."""
    success: bool
    resolution_time: float
    base_time: float
    burnout_multiplier: float
    error_chance: float
    actual_success_rate: float
    specialist_id: str
    incident_id: str
    decisions_made: Optional[List[ResolutionDecision]] = None
    total_burnout_cost: float = 0.0
    total_money_cost: int = 0
    
    def __post_init__(self):
        if self.decisions_made is None:
            self.decisions_made = []


class ResolutionSystem:
    """Decision-based incident resolution with burnout penalties."""

    def __init__(self, burnout_system: BurnoutSystem, config_path: str = "data/resolution_trees.json"):
        self.burnout_system = burnout_system
        self.resolution_trees = self._load_resolution_trees(config_path)
        
    def _load_resolution_trees(self, config_path: str) -> Dict:
        """Load resolution trees from JSON config."""
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
            logger.info(f"Loaded resolution trees from {config_path}")
            return data.get("resolution_trees", {})
        except FileNotFoundError:
            logger.warning(f"Resolution trees config not found: {config_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in resolution trees config: {e}")
            return {}

    def start_resolution(
        self, 
        incident: Incident, 
        specialist: Specialist
    ) -> ResolutionSession:
        """
        Start decision-based incident resolution.
        
        Args:
            incident: Incident to resolve
            specialist: Specialist resolving it
            
        Returns:
            ResolutionSession with initial state
        """
        # Map incident type to tree ID
        tree_id = self._get_tree_id_for_incident(incident)
        
        if tree_id not in self.resolution_trees:
            logger.warning(f"No resolution tree found for incident type: {incident.incident_type}")
            # Fallback to simple resolution
            return self._create_simple_session(incident, specialist)
        
        tree = self.resolution_trees[tree_id]
        first_stage = tree["stages"][0]["stage_id"]
        
        session = ResolutionSession(
            incident_id=incident.id,
            specialist_id=specialist.id,
            tree_id=tree_id,
            current_stage=first_stage,
            decisions_made=[],
            start_time=time.time(),
            time_pressure_multiplier=self._calculate_time_pressure(incident)
        )
        
        logger.info(f"Started resolution session for incident {incident.id} with tree {tree_id}")
        return session
    
    def _get_tree_id_for_incident(self, incident: Incident) -> str:
        """Map incident type to resolution tree ID."""
        type_mapping = {
            "DDoS Attack": "ddos_attack",
            "Malware Infection": "malware_infection", 
            "Phishing": "phishing_attack",
            "Data Breach": "data_breach",
            "Ransomware": "ransomware_attack"
        }
        return type_mapping.get(incident.incident_type, "ddos_attack")  # Default fallback
    
    def _calculate_time_pressure(self, incident: Incident) -> float:
        """Calculate time pressure multiplier based on SLA urgency."""
        urgency = incident.get_sla_urgency()
        if urgency == "critical":
            return 0.7  # 30% less time
        elif urgency == "warning":
            return 0.85  # 15% less time
        else:
            return 1.0  # Normal time
    
    def _create_simple_session(self, incident: Incident, specialist: Specialist) -> ResolutionSession:
        """Create simple fallback session when no tree is available."""
        return ResolutionSession(
            incident_id=incident.id,
            specialist_id=specialist.id,
            tree_id="simple",
            current_stage="complete",
            decisions_made=[],
            start_time=time.time(),
            time_pressure_multiplier=1.0
        )
    
    def get_current_stage_info(self, session: ResolutionSession) -> Dict:
        """
        Get information about the current resolution stage.
        
        Args:
            session: Active resolution session
            
        Returns:
            Dict with stage prompt, decisions, and time remaining
        """
        if session.tree_id == "simple":
            return {
                "stage_id": "complete",
                "prompt": "Resolve incident using standard procedures.",
                "decisions": [
                    {
                        "id": "resolve_standard",
                        "text": "Resolve using standard procedures",
                        "effects": {
                            "time_multiplier": 1.0,
                            "success_chance": 0.85
                        }
                    }
                ],
                "time_limit_seconds": 60.0,
                "time_remaining": 60.0 - session.elapsed_time
            }
        
        tree = self.resolution_trees.get(session.tree_id)
        if not tree:
            return {}
        
        # Find current stage
        current_stage_data = None
        for stage in tree["stages"]:
            if stage["stage_id"] == session.current_stage:
                current_stage_data = stage
                break
        
        if not current_stage_data:
            return {}
        
        time_limit = current_stage_data.get("time_limit_seconds", 30.0) * session.time_pressure_multiplier
        time_remaining = max(0, time_limit - session.elapsed_time)
        
        return {
            "stage_id": session.current_stage,
            "prompt": current_stage_data["prompt"],
            "decisions": current_stage_data["decisions"],
            "time_limit_seconds": time_limit,
            "time_remaining": time_remaining
        }
    
    def make_decision(
        self, 
        session: ResolutionSession, 
        decision_id: str,
        specialist: Specialist
    ) -> Tuple[bool, Optional[str], Dict]:
        """
        Make a decision in the current resolution stage.
        
        Args:
            session: Active resolution session
            decision_id: ID of the decision to make
            specialist: Specialist making the decision
            
        Returns:
            (success, next_stage_or_complete, decision_effects)
        """
        stage_info = self.get_current_stage_info(session)
        if not stage_info or "decisions" not in stage_info:
            return False, None, {}
        
        # Find the decision
        decision_data = None
        for decision in stage_info["decisions"]:
            if decision["id"] == decision_id:
                decision_data = decision
                break
        
        if not decision_data:
            return False, None, {}
        
        # Check time limit
        if stage_info["time_remaining"] <= 0:
            logger.warning(f"Decision made after time limit for session {session.incident_id}")
            # Apply time penalty
            decision_data = self._apply_time_penalty(decision_data)
        
        # Apply specialist skill checks
        decision_data = self._apply_specialist_skills(decision_data, specialist)
        
        # Record the decision
        decision_record = ResolutionDecision(
            decision_id=decision_id,
            stage_id=session.current_stage
        )
        session.decisions_made.append(decision_record)
        
        # Apply decision effects
        effects = decision_data.get("effects", {})
        session.total_burnout_cost += effects.get("burnout_cost", 0)
        session.total_money_cost += effects.get("money_cost", 0)
        
        # Check if resolution is complete
        if decision_data.get("resolution_complete", False):
            return True, "complete", effects
        
        # Move to next stage
        next_stage = decision_data.get("next_stage")
        if next_stage:
            session.current_stage = next_stage
            return True, next_stage, effects
        
        return False, None, effects
    
    def _apply_time_penalty(self, decision_data: Dict) -> Dict:
        """Apply penalty for decisions made after time limit."""
        modified = decision_data.copy()
        effects = modified.get("effects", {}).copy()
        
        # Reduce success chance and increase burnout
        effects["success_chance"] = effects.get("success_chance", 0.8) * 0.8
        effects["burnout_cost"] = effects.get("burnout_cost", 0) + 5
        
        modified["effects"] = effects
        return modified
    
    def _apply_specialist_skills(self, decision_data: Dict, specialist: Specialist) -> Dict:
        """Apply specialist skills and accuracy to decision."""
        modified = decision_data.copy()
        effects = modified.get("effects", {}).copy()
        
        # Accuracy check: if required, apply specialist accuracy
        if effects.get("accuracy_check", False):
            accuracy_bonus = (specialist.stats.accuracy - 50) / 100.0  # -0.5 to +0.5
            effects["success_chance"] = effects.get("success_chance", 0.8) + accuracy_bonus
        
        # Accuracy bonus: direct addition
        if "accuracy_bonus" in effects:
            bonus = effects["accuracy_bonus"] / 100.0  # Convert to decimal
            effects["success_chance"] = effects.get("success_chance", 0.8) + bonus
        
        # Clamp success chance
        effects["success_chance"] = max(0.1, min(0.99, effects.get("success_chance", 0.8)))
        
        modified["effects"] = effects
        return modified
    
    def complete_resolution(
        self,
        session: ResolutionSession,
        specialist: Specialist,
        incident: Incident
    ) -> ResolutionResult:
        """
        Complete the resolution and calculate final outcome.
        
        Args:
            session: Completed resolution session
            specialist: Specialist who resolved
            incident: Incident being resolved
            
        Returns:
            ResolutionResult with final outcome
        """
        # Calculate aggregate effects from all decisions
        total_time_mult = 1.0
        total_success_chance = 0.8  # Base chance
        total_burnout_cost = session.total_burnout_cost
        total_money_cost = session.total_money_cost
        
        for decision in session.decisions_made:
            # Get decision effects (would need to store or recalculate)
            # For now, use simplified calculation
            total_time_mult *= 1.0  # Would be calculated from decisions
            total_success_chance = max(total_success_chance, 0.7)  # Simplified
        
        # Apply burnout effects
        burnout_mult = specialist.get_performance_multiplier()
        error_chance = specialist.get_error_chance_from_burnout()
        final_success_chance = total_success_chance * (1.0 - error_chance)
        
        # Determine success
        success = random.random() < final_success_chance
        
        # Calculate resolution time
        base_time = 100.0  # Base resolution time
        actual_time = base_time * total_time_mult / burnout_mult
        
        # Apply burnout costs
        specialist.burnout_level = min(100.0, specialist.burnout_level + total_burnout_cost)
        
        result = ResolutionResult(
            success=success,
            resolution_time=actual_time,
            base_time=base_time,
            burnout_multiplier=burnout_mult,
            error_chance=error_chance,
            actual_success_rate=final_success_chance,
            specialist_id=specialist.id,
            incident_id=incident.id,
            decisions_made=session.decisions_made,
            total_burnout_cost=total_burnout_cost,
            total_money_cost=total_money_cost
        )
        
        logger.info(f"Completed resolution for incident {incident.id}: success={success}, time={actual_time:.1f}s")
        return result

    def complete_incident(
        self,
        specialist: Specialist,
        incident: Incident,
        success: bool,
        base_time: float = 100.0
    ) -> Dict:
        """Complete incident using simple resolution (fallback for non-decision-based incidents).

        Args:
            specialist: Specialist who resolved it
            incident: Incident being completed
            success: Whether resolution succeeded
            base_time: Base resolution time

        Returns:
            Status dict with updates
        """
        # Calculate resolution metrics
        multiplier = specialist.get_performance_multiplier()
        error_chance = specialist.get_error_chance_from_burnout()
        actual_time = base_time / multiplier if multiplier > 0 else float('inf')

        incident.complete_resolution(success)

        self.burnout_system.complete_incident(
            specialist.id,
            success=success
        )

        return {
            'incident_id': incident.id,
            'specialist_id': specialist.id,
            'success': success,
            'resolution_time': actual_time,
            'burnout_level': specialist.burnout_level,
            'burnout_tier': self.burnout_system.get_specialist_status(
                specialist.id
            )['tier'],
            'performance_multiplier': multiplier,
            'error_chance': error_chance
        }

    def attempt_resolution(
        self,
        specialist: Specialist,
        incident: Incident,
        base_time: float = 100.0,
        base_success_rate: float = 0.9
    ) -> ResolutionResult:
        """Attempt to resolve incident with burnout effects (convenience method).

        This method provides backward compatibility for simple resolution.
        For decision-based resolution, use start_resolution() instead.

        Args:
            specialist: Resolving specialist
            incident: Incident being resolved
            base_time: Base resolution time (seconds)
            base_success_rate: Base success probability

        Returns:
            ResolutionResult with outcome and metrics
        """
        multiplier = specialist.get_performance_multiplier()
        if multiplier <= 0.0:
            return ResolutionResult(
                success=False,
                resolution_time=float('inf'),
                base_time=base_time,
                burnout_multiplier=multiplier,
                error_chance=specialist.get_error_chance_from_burnout(),
                actual_success_rate=0.0,
                specialist_id=specialist.id,
                incident_id=incident.id
            )

        error_chance = specialist.get_error_chance_from_burnout()
        actual_time = base_time / multiplier
        success_rate = base_success_rate * (1.0 - error_chance)
        success = random.random() < success_rate

        return ResolutionResult(
            success=success,
            resolution_time=actual_time,
            base_time=base_time,
            burnout_multiplier=multiplier,
            error_chance=error_chance,
            actual_success_rate=success_rate,
            specialist_id=specialist.id,
            incident_id=incident.id
        )

    def calculate_resolution_time(
        self,
        specialist: Specialist,
        incident: Incident,
        base_time: float
    ) -> Tuple[float, float]:
        """Calculate actual resolution time with burnout multiplier.

        Args:
            specialist: Resolving specialist
            incident: Incident being resolved
            base_time: Base resolution time in seconds

        Returns:
            (actual_resolution_time, burnout_multiplier)

        Examples:
            - Burnout 0% (multiplier 1.0): base_time = 100s → 100s
            - Burnout 50% (multiplier 0.5): base_time = 100s → 200s
            - Burnout 80% (multiplier 0.25): base_time = 100s → 400s
            - Burnout 100% (multiplier 0.0): Can't resolve
        """
        multiplier = specialist.get_performance_multiplier()

        if multiplier <= 0.0:
            return float('inf'), 0.0

        actual_time = base_time / multiplier
        return actual_time, multiplier

    def calculate_success_rate(
        self,
        specialist: Specialist,
        incident: Incident,
        base_success_rate: float = 0.9
    ) -> float:
        """Calculate success rate with burnout error chance.

        Args:
            specialist: Resolving specialist
            incident: Incident being resolved
            base_success_rate: Base success probability (default 0.9 = 90%)

        Returns:
            Actual success probability (0.0 to 1.0)

        Examples:
            - Base 90%, Burnout 0% (error 0%): 90%
            - Base 90%, Burnout 50% (error 25%): 90% * (1 - 0.25) = 67.5%
            - Base 90%, Burnout 100% (error 50%): 90% * (1 - 0.50) = 45%
        """
        error_chance = specialist.get_error_chance_from_burnout()
        actual_rate = base_success_rate * (1.0 - error_chance)
        return max(0.0, min(1.0, actual_rate))
