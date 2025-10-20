"""Skill tree plugin for specialist progression.

This plugin integrates the skill tree system with the game's plugin architecture.
"""

import logging
from typing import Dict, Any, Optional

from src.core.game_system import GameSystem
from src.core.skill_tree_system import SkillTreeSystem
from src.core.event_bus import get_event_bus
from src.models.game_state import GameState

logger = logging.getLogger(__name__)


class SkillTreePlugin(GameSystem):
    """Plugin for managing specialist skill trees and progression."""

    def __init__(self):
        """Initialize the skill tree plugin."""
        super().__init__()
        self.skill_tree_system: Optional[SkillTreeSystem] = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def get_name(self) -> str:
        """Get the unique name of this system.

        Returns:
            System name
        """
        return "skill_tree"

    def initialize(self, game_state: GameState) -> bool:
        """Initialize the skill tree plugin.

        Args:
            game_state: Current game state

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.skill_tree_system = SkillTreeSystem()
            success = self.skill_tree_system.initialize(game_state)

            if success:
                self.logger.info("Skill tree plugin initialized successfully")
                return True
            else:
                self.logger.error("Failed to initialize skill tree system")
                return False

        except Exception as e:
            self.logger.error(f"Failed to initialize skill tree plugin: {e}")
            return False

    def update(self, game_state: GameState, delta_time: float) -> None:
        """Update the skill tree plugin.

        Args:
            game_state: Current game state
            delta_time: Time elapsed since last update
        """
        if self.skill_tree_system:
            self.skill_tree_system.update(delta_time)

    def shutdown(self, game_state: GameState) -> None:
        """Shutdown the skill tree plugin.

        Args:
            game_state: Current game state
        """
        if self.skill_tree_system:
            self.skill_tree_system.shutdown()
        self.logger.info("Skill tree plugin shut down")

    def save_state(self, game_state: GameState) -> Dict:
        """Save the current state of the skill tree plugin.

        Args:
            game_state: Current game state

        Returns:
            Dictionary containing plugin state
        """
        if self.skill_tree_system:
            return self.skill_tree_system.save_state()
        return {}

    def load_state(self, game_state: GameState, state: Dict) -> None:
        """Load the state of the skill tree plugin.

        Args:
            game_state: Current game state
            state: Dictionary containing plugin state
        """
        if self.skill_tree_system:
            self.skill_tree_system.load_state(state)

    def get_skill_tree_system(self) -> Optional[SkillTreeSystem]:
        """Get the skill tree system instance.

        Returns:
            The skill tree system instance
        """
        return self.skill_tree_system