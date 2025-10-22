"""
SystemCoordinator - System management layer.

Coordinates all internal game systems and time-based updates.
Extracts system management logic from the monolithic GameState class.
"""

from typing import Dict, Any, List
import logging

from src.core.state_manager import StateManager
from src.core.game_logic import GameLogic

logger = logging.getLogger(__name__)


class SystemCoordinator:
    """
    Coordinates all internal game systems and time-based updates.

    This layer manages the internal systems that operate on game state,
    including incident generation, automation processing, and dopamine mechanics.
    It separates system coordination from business logic and data storage.
    """

    def __init__(self, state_manager: StateManager, game_logic: GameLogic, game_config: Dict[str, Any]):
        """
        Initialize SystemCoordinator with dependencies.

        Args:
            state_manager: StateManager for data access
            game_logic: GameLogic for business rules
            game_config: Game configuration dictionary
        """
        self.state_manager = state_manager
        self.game_logic = game_logic
        self.game_config = game_config

        # System state
        self._last_incident_generation = 0.0
        self._last_automation_processing = 0.0
        self._last_dopamine_update = 0.0

        # Configuration
        self.incident_generation_interval = game_config.get("game_settings", {}).get("incident_generation_interval", 60.0)
        self.automation_processing_interval = game_config.get("game_settings", {}).get("automation_processing_interval", 30.0)
        self.dopamine_update_interval = game_config.get("game_settings", {}).get("dopamine_update_interval", 10.0)

        logger.info("SystemCoordinator initialized")

    def update(self, delta_time: float) -> None:
        """
        Update all internal systems based on time elapsed.

        Args:
            delta_time: Time elapsed since last update in seconds
        """
        # Update incident generation
        self._last_incident_generation += delta_time
        if self._last_incident_generation >= self.incident_generation_interval:
            self._generate_incidents()
            self._last_incident_generation = 0.0

        # Update automation processing
        self._last_automation_processing += delta_time
        if self._last_automation_processing >= self.automation_processing_interval:
            self._process_automation()
            self._last_automation_processing = 0.0

        # Update dopamine system
        self._last_dopamine_update += delta_time
        if self._last_dopamine_update >= self.dopamine_update_interval:
            self._update_dopamine()
            self._last_dopamine_update = 0.0

    def _generate_incidents(self) -> None:
        """
        Generate new incidents based on client profiles and current game state.

        This is a placeholder for the incident generation system.
        In the full implementation, this would:
        - Check each client's incident rate
        - Generate incidents based on industry threat profiles
        - Apply random variance and current game conditions
        """
        logger.debug("Generating incidents...")

        # Placeholder: Generate one test incident per client
        for client in self.state_manager.get_all_clients():
            if client.is_active:
                # This would be replaced with proper incident generation logic
                logger.debug(f"Would generate incidents for client {client.client_id}")

    def _process_automation(self) -> None:
        """
        Process automation scripts for specialists.

        This is a placeholder for the automation processing system.
        In the full implementation, this would:
        - Check each specialist's unlocked automation scripts
        - Execute eligible automation actions
        - Apply cooldowns and resource costs
        """
        logger.debug("Processing automation scripts...")

        # Placeholder: Process automation for specialists
        for specialist in self.state_manager.get_all_specialists():
            # This would be replaced with proper automation logic
            logger.debug(f"Would process automation for specialist {specialist.name}")

    def _update_dopamine(self) -> None:
        """
        Update dopamine/reward system.

        This is a placeholder for the dopamine system.
        In the full implementation, this would:
        - Track player actions and progress
        - Provide feedback and rewards
        - Update achievement progress
        """
        logger.debug("Updating dopamine system...")

        # Placeholder: Update dopamine mechanics
        # This would be replaced with proper dopamine logic

    def force_incident_generation(self) -> None:
        """
        Force immediate incident generation (for testing/debugging).
        """
        logger.info("Forcing incident generation")
        self._generate_incidents()
        self._last_incident_generation = 0.0

    def force_automation_processing(self) -> None:
        """
        Force immediate automation processing (for testing/debugging).
        """
        logger.info("Forcing automation processing")
        self._process_automation()
        self._last_automation_processing = 0.0

    def force_dopamine_update(self) -> None:
        """
        Force immediate dopamine update (for testing/debugging).
        """
        logger.info("Forcing dopamine update")
        self._update_dopamine()
        self._last_dopamine_update = 0.0

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get current status of all systems.

        Returns:
            Dictionary with system status information
        """
        return {
            "incident_generation": {
                "last_update": self._last_incident_generation,
                "interval": self.incident_generation_interval,
                "next_update_in": self.incident_generation_interval - self._last_incident_generation
            },
            "automation_processing": {
                "last_update": self._last_automation_processing,
                "interval": self.automation_processing_interval,
                "next_update_in": self.automation_processing_interval - self._last_automation_processing
            },
            "dopamine_update": {
                "last_update": self._last_dopamine_update,
                "interval": self.dopamine_update_interval,
                "next_update_in": self.dopamine_update_interval - self._last_dopamine_update
            }
        }