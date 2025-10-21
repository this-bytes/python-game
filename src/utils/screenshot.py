"""Enhanced Screenshot Utility for UI Development and Testing.

This module provides a comprehensive screenshot system for game development,
with configurable output directories, automatic timestamping, event-based capture,
and integration with the rich parameter system for development workflows.
"""

import sys
import pygame
import os
from datetime import datetime
from typing import Optional, Dict, Any, List

# Add parent directory to path so src imports work
sys.path.insert(0, '/home/localadmin/code/python-game')

from src.utils.logger import GameLogger
from src.ui.game_ui import GameUI
from src.models.game_state import GameState
from src.utils.rich_parameter_system import get_parameter_system


class ScreenshotUtility:
    """Enhanced utility to capture screenshots of the game window."""

    def __init__(self, game_ui: GameUI, game_state: GameState, logger: GameLogger):
        """Initialize the screenshot utility.

        Args:
            game_ui: The game UI instance
            game_state: The current game state
            logger: Logger instance for logging
        """
        self.game_ui = game_ui
        self.game_state = game_state
        self.logger = logger

        # Screenshot configuration
        self.screenshot_count = 0
        self.event_screenshots: Dict[str, int] = {}
        self.output_dir = "screenshots"
        self.auto_screenshot_timer = 0.0

        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)

        # Parameter system integration
        self.param_system = get_parameter_system()
        self.param_system.set_logger(logger)

        self.logger.logger.info(f"[SCREENSHOT] Screenshot utility initialized. Output dir: {self.output_dir}")

    def update(self, delta_time: float) -> None:
        """Update screenshot utility (called every frame).

        Args:
            delta_time: Time elapsed since last update
        """
        # Auto-screenshot functionality
        if self.param_system.get_parameter("auto_screenshot"):
            self.auto_screenshot_timer += delta_time
            interval = self.param_system.get_parameter("screenshot_interval")

            if self.auto_screenshot_timer >= interval:
                self.capture_screenshot("auto")
                self.auto_screenshot_timer = 0.0

    def capture_screenshot(self, prefix: str = "") -> str:
        """Capture a screenshot of the current game window.

        Args:
            prefix: Optional prefix for the filename

        Returns:
            Path to the captured screenshot
        """
        try:
            # Create screenshot surface
            screenshot_surface = pygame.Surface(self.game_ui.screen.get_size())
            screenshot_surface.blit(self.game_ui.screen, (0, 0))

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if prefix:
                filename = f"{prefix}_{timestamp}_{self.screenshot_count:04d}.png"
            else:
                filename = f"screenshot_{timestamp}_{self.screenshot_count:04d}.png"

            filepath = os.path.join(self.output_dir, filename)

            # Save screenshot
            pygame.image.save(screenshot_surface, filepath)
            self.screenshot_count += 1

            self.logger.logger.info(f"[SCREENSHOT] Captured screenshot: {filepath}")
            return filepath

        except Exception as e:
            self.logger.logger.error(f"[SCREENSHOT] Failed to capture screenshot: {e}")
            return ""

    def capture_event_screenshot(self, event_name: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Capture a screenshot for a specific event.

        Args:
            event_name: Name of the event triggering the screenshot
            metadata: Optional metadata to include in filename

        Returns:
            Path to the captured screenshot
        """
        try:
            # Create screenshot surface
            screenshot_surface = pygame.Surface(self.game_ui.screen.get_size())
            screenshot_surface.blit(self.game_ui.screen, (0, 0))

            # Generate filename with event info
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Track event screenshots
            if event_name not in self.event_screenshots:
                self.event_screenshots[event_name] = 0
            self.event_screenshots[event_name] += 1

            event_count = self.event_screenshots[event_name]

            # Build filename with metadata
            filename_parts = [event_name, timestamp, f"{event_count:03d}"]

            if metadata:
                # Add key metadata to filename (keep it reasonable length)
                meta_parts = []
                for key, value in metadata.items():
                    if isinstance(value, (str, int, float)) and len(str(value)) < 20:
                        meta_parts.append(f"{key}_{value}")
                    if len(meta_parts) >= 3:  # Limit metadata parts
                        break
                filename_parts.extend(meta_parts)

            filename = "_".join(filename_parts) + ".png"
            filepath = os.path.join(self.output_dir, filename)

            # Save screenshot
            pygame.image.save(screenshot_surface, filepath)

            self.logger.logger.info(f"[SCREENSHOT] Captured event screenshot: {filepath}")
            return filepath

        except Exception as e:
            self.logger.logger.error(f"[SCREENSHOT] Failed to capture event screenshot: {e}")
            return ""

    def capture_ui_state_screenshot(self, ui_state: str) -> str:
        """Capture a screenshot of a specific UI state.

        Args:
            ui_state: Description of the current UI state

        Returns:
            Path to the captured screenshot
        """
        metadata = {
            "ui_state": ui_state.replace(" ", "_"),
            "panels_open": len(self.game_ui.panels) if hasattr(self.game_ui, 'panels') else 0,
            "specialists": len(self.game_state.specialists),
            "incidents": len(self.game_state.incidents) if hasattr(self.game_state, 'incidents') else 0
        }

        return self.capture_event_screenshot("ui_state", metadata)

    def capture_game_state_screenshot(self) -> str:
        """Capture a screenshot with current game state info.

        Returns:
            Path to the captured screenshot
        """
        metadata = {
            "money": int(self.game_state.current_money),
            "specialists": len(self.game_state.specialists),
            "reputation": getattr(self.game_state, 'reputation', 0),
            "time": int(getattr(self.game_state, 'game_time', 0))
        }

        return self.capture_event_screenshot("game_state", metadata)

    def capture_panel_screenshot(self, panel_name: str) -> str:
        """Capture a screenshot focused on a specific panel.

        Args:
            panel_name: Name of the panel to capture

        Returns:
            Path to the captured screenshot
        """
        # Find the panel
        target_panel = None
        if hasattr(self.game_ui, 'panels'):
            for panel in self.game_ui.panels:
                if hasattr(panel, 'title') and panel.title.lower().replace(" ", "_") == panel_name.lower():
                    target_panel = panel
                    break

        if target_panel:
            metadata = {
                "panel": panel_name,
                "panel_visible": getattr(target_panel, 'visible', True),
                "panel_minimized": (
                    getattr(target_panel, 'state', None) == "minimized"
                    if hasattr(target_panel, 'state') else False
                )
            }
        else:
            metadata = {"panel": panel_name, "panel_found": False}

        return self.capture_event_screenshot("panel_focus", metadata)

    def get_screenshot_stats(self) -> Dict[str, Any]:
        """Get statistics about captured screenshots.

        Returns:
            Dictionary with screenshot statistics
        """
        total_files = len([f for f in os.listdir(self.output_dir)
                          if f.endswith('.png') and os.path.isfile(os.path.join(self.output_dir, f))])

        return {
            "total_screenshots": self.screenshot_count,
            "total_files": total_files,
            "output_directory": self.output_dir,
            "event_types": list(self.event_screenshots.keys()),
            "event_counts": self.event_screenshots.copy(),
            "auto_screenshot_enabled": self.param_system.get_parameter("auto_screenshot"),
            "screenshot_interval": self.param_system.get_parameter("screenshot_interval")
        }

    def cleanup_old_screenshots(self, keep_days: int = 7) -> int:
        """Clean up old screenshots older than specified days.

        Args:
            keep_days: Number of days of screenshots to keep

        Returns:
            Number of files deleted
        """
        import time as time_module

        deleted_count = 0
        cutoff_time = time_module.time() - (keep_days * 24 * 60 * 60)

        try:
            for filename in os.listdir(self.output_dir):
                if filename.endswith('.png'):
                    filepath = os.path.join(self.output_dir, filename)
                    if os.path.getmtime(filepath) < cutoff_time:
                        os.remove(filepath)
                        deleted_count += 1

            if deleted_count > 0:
                self.logger.logger.info(f"[SCREENSHOT] Cleaned up {deleted_count} old screenshots")

        except Exception as e:
            self.logger.logger.error(f"[SCREENSHOT] Failed to cleanup screenshots: {e}")

        return deleted_count

    def set_output_directory(self, output_dir: str) -> bool:
        """Set the output directory for screenshots.

        Args:
            output_dir: New output directory path

        Returns:
            True if directory was set successfully
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            self.output_dir = output_dir
            self.logger.logger.info(f"[SCREENSHOT] Output directory set to: {output_dir}")
            return True
        except Exception as e:
            self.logger.logger.error(f"[SCREENSHOT] Failed to set output directory: {e}")
            return False


# Global screenshot utility instance
_screenshot_utility = None


def get_screenshot_utility() -> Optional[ScreenshotUtility]:
    """Get the global screenshot utility instance.

    Returns:
        ScreenshotUtility instance or None if not initialized
    """
    return _screenshot_utility


def initialize_screenshot_utility(game_ui: GameUI, game_state: GameState, logger: GameLogger) -> ScreenshotUtility:
    """Initialize the global screenshot utility.

    Args:
        game_ui: Game UI instance
        game_state: Game state instance
        logger: Logger instance

    Returns:
        ScreenshotUtility instance
    """
    global _screenshot_utility
    _screenshot_utility = ScreenshotUtility(game_ui, game_state, logger)
    return _screenshot_utility


def capture_screenshot(prefix: str = "") -> str:
    """Capture a screenshot using the global utility.

    Args:
        prefix: Optional prefix for filename

    Returns:
        Path to captured screenshot or empty string if failed
    """
    if _screenshot_utility:
        return _screenshot_utility.capture_screenshot(prefix)
    return ""


def capture_event_screenshot(event_name: str, metadata: Optional[Dict[str, Any]] = None) -> str:
    """Capture an event screenshot using the global utility.

    Args:
        event_name: Event name
        metadata: Optional metadata

    Returns:
        Path to captured screenshot or empty string if failed
    """
    if _screenshot_utility:
        return _screenshot_utility.capture_event_screenshot(event_name, metadata)
    return ""
