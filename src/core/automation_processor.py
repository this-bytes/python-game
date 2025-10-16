"""Automation processing system for handling automation script execution.

This module manages the evaluation and execution of automation scripts during gameplay,
integrating with the game state to provide automated specialist actions.
"""

import time
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from dataclasses import dataclass, field

from ..models.automation_script import AutomationScript
from ..models.specialist import Specialist
from ..models.incident import Incident
from ..utils.logger import GameLogger

if TYPE_CHECKING:
    # Import for type checking only to avoid circular imports at runtime
    from ..models.game_state import GameState


@dataclass
class AutomationResult:
    """Result of an automation script execution."""
    script_id: str
    specialist_id: str
    incident_id: Optional[str]
    effect_type: str
    success: bool
    timestamp: float
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/serialization."""
        return {
            "script_id": self.script_id,
            "specialist_id": self.specialist_id,
            "incident_id": self.incident_id,
            "effect_type": self.effect_type,
            "success": self.success,
            "timestamp": self.timestamp,
            "details": self.details
        }


class AutomationProcessor:
    """Processes automation scripts during game updates.

    This class handles the evaluation and execution of automation scripts,
    checking trigger conditions and applying effects when appropriate.
    """

    def __init__(self, logger: Optional[GameLogger] = None):
        """Initialize the automation processor.

        Args:
            logger: Optional logger for automation events
        """
        self._logger = logger or GameLogger("automation_processor")
        self._last_processing_time = time.time()
        self._processing_interval = 1.0  # Process automation every second

        # Statistics tracking
        self._stats = {
            "total_scripts_evaluated": 0,
            "total_scripts_executed": 0,
            "scripts_executed_by_type": {},
            "execution_failures": 0,
            "last_execution_time": None
        }

    def process_automation(self, game_state: 'GameState', delta_time: float) -> List[AutomationResult]:
        """Process automation scripts for the current game state.

        Args:
            game_state: Current game state
            delta_time: Time elapsed since last update

        Returns:
            List of automation results from this processing cycle
        """
        current_time = time.time()

        # Only process automation at specified intervals to avoid spam
        if current_time - self._last_processing_time < self._processing_interval:
            return []

        self._last_processing_time = current_time
        results = []

        # Get all available automation scripts from specialists
        available_scripts = self._get_available_scripts(game_state)

        if not available_scripts:
            return results

        # Check for automation opportunities
        for script in available_scripts:
            script_results = self._evaluate_and_execute_script(script, game_state)
            results.extend(script_results)

        # Update statistics
        self._stats["total_scripts_evaluated"] += len(available_scripts)
        self._stats["total_scripts_executed"] += len(results)
        if results:
            self._stats["last_execution_time"] = current_time

        return results

    def _get_available_scripts(self, game_state: 'GameState') -> List[AutomationScript]:
        """Get all automation scripts available from specialists.

        Args:
            game_state: Current game state

        Returns:
            List of available automation scripts
        """
        available_scripts = []

        for specialist in game_state.specialists:
            if not specialist.is_available():
                continue  # Busy specialists can't use automation

            # Get scripts this specialist has unlocked
            for script_id in specialist.automation_scripts:
                script = game_state.get_automation_script_by_id(script_id)
                if script and script.can_be_used_by(specialist):
                    available_scripts.append((script, specialist))

        return available_scripts

    def _evaluate_and_execute_script(self, script_specialist_pair: tuple,
                                   game_state: 'GameState') -> List[AutomationResult]:
        """Evaluate and execute a single automation script.

        Args:
            script_specialist_pair: Tuple of (AutomationScript, Specialist)
            game_state: Current game state

        Returns:
            List of automation results (usually 1, but could be more for complex scripts)
        """
        script, specialist = script_specialist_pair
        results = []

        # For auto-assign scripts, check all pending incidents
        if script.effect == "auto_assign":
            for incident in game_state.incidents:
                if incident.status == "pending":
                    if script.evaluate_triggers(specialist, incident):
                        result = self._execute_script(script, specialist, game_state, incident)
                        if result:
                            results.append(result)
                            break  # Only assign one incident per script per cycle

        # For boost scripts, apply continuously if conditions met
        elif script.effect in ["speed_boost", "accuracy_boost", "xp_boost"]:
            # Check if script should be active (using a dummy incident for evaluation)
            should_activate = self._check_boost_conditions(script, specialist, game_state)
            if should_activate:
                result = self._execute_script(script, specialist, game_state)
                if result:
                    results.append(result)

        return results

    def _check_boost_conditions(self, script: AutomationScript, specialist: Specialist,
                              game_state: 'GameState') -> bool:
        """Check if boost automation conditions are met.

        For boost scripts, we check specialty match and availability,
        but don't require a specific incident.

        Args:
            script: The automation script
            specialist: The specialist
            game_state: Current game state

        Returns:
            True if boost should be applied
        """
        conditions = script.trigger_conditions

        # Check specialty_match
        if conditions.specialty_match is not None and conditions.specialty_match:
            # For boost scripts, check if specialist has matching specialty
            if script.specialty != "Any" and not specialist.matches_specialty(script.specialty):
                return False

        # Check specialist_available
        if conditions.specialist_available is not None and conditions.specialist_available:
            if not specialist.is_available():
                return False

        # Check min_accuracy
        if conditions.min_accuracy is not None:
            if specialist.stats.accuracy < conditions.min_accuracy:
                return False

        return True

    def _execute_script(self, script: AutomationScript, specialist: Specialist,
                       game_state: 'GameState', incident: Optional[Incident] = None) -> Optional[AutomationResult]:
        """Execute an automation script.

        Args:
            script: The automation script to execute
            specialist: The specialist executing the script
            game_state: Current game state
            incident: Optional incident for assignment scripts

        Returns:
            AutomationResult if execution occurred, None otherwise
        """
        try:
            # Apply the effect
            effect_result = script.apply_effect(specialist, incident)

            # Create result record
            result = AutomationResult(
                script_id=script.id,
                specialist_id=specialist.id,
                incident_id=incident.id if incident else None,
                effect_type=script.effect,
                success=effect_result["success"],
                timestamp=time.time(),
                details=effect_result["details"]
            )

            # Update statistics
            effect_type = script.effect
            if effect_type not in self._stats["scripts_executed_by_type"]:
                self._stats["scripts_executed_by_type"][effect_type] = 0
            self._stats["scripts_executed_by_type"][effect_type] += 1

            if not effect_result["success"]:
                self._stats["execution_failures"] += 1

            # Log the automation execution
            if effect_result["success"]:
                self._logger.logger.info(
                    f"[AUTOMATION] Script '{script.name}' executed by specialist {specialist.id}: "
                    f"{effect_type} (magnitude: {script.effect_magnitude})"
                )
            else:
                self._logger.logger.warning(
                    f"[AUTOMATION] Script '{script.name}' execution failed: {effect_result['details'].get('error', 'Unknown error')}"
                )

            return result

        except Exception as e:
            self._logger.logger.error(f"[AUTOMATION] Error executing script '{script.id}': {e}")
            self._stats["execution_failures"] += 1
            return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get automation processing statistics.

        Returns:
            Dictionary containing automation statistics
        """
        return self._stats.copy()

    def reset_statistics(self) -> None:
        """Reset automation statistics."""
        self._stats = {
            "total_scripts_evaluated": 0,
            "total_scripts_executed": 0,
            "scripts_executed_by_type": {},
            "execution_failures": 0,
            "last_execution_time": None
        }