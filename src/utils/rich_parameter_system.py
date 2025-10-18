"""Rich Parameter System for Game Development.

This module provides a comprehensive parameter system for development features,
debug modes, game configuration, and runtime toggles to enhance the development
workflow and testing capabilities.
"""

import json
import os
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import time


class ParameterType(Enum):
    """Types of parameters supported by the system."""
    BOOLEAN = "boolean"
    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    CHOICE = "choice"
    COLOR = "color"


class ParameterCategory(Enum):
    """Categories for organizing parameters."""
    DEBUG = "debug"
    UI = "ui"
    GAMEPLAY = "gameplay"
    PERFORMANCE = "performance"
    BACKEND = "backend"
    DEVELOPMENT = "development"


@dataclass
class ParameterDefinition:
    """Definition of a parameter with its properties."""
    name: str
    type: ParameterType
    category: ParameterCategory
    default_value: Any
    description: str
    choices: Optional[list] = None  # For CHOICE type
    min_value: Optional[float] = None  # For numeric types
    max_value: Optional[float] = None  # For numeric types
    hot_reloadable: bool = True  # Can be changed at runtime
    callback: Optional[Callable] = None  # Called when parameter changes


@dataclass
class ParameterState:
    """Current state of a parameter."""
    definition: ParameterDefinition
    current_value: Any
    last_modified: float = field(default_factory=time.time)


class RichParameterSystem:
    """Rich parameter system for game development and configuration."""

    def __init__(self, config_file: str = "data/dev_parameters.json"):
        """Initialize the parameter system.

        Args:
            config_file: Path to the parameter configuration file
        """
        self.config_file = config_file
        self.parameters: Dict[str, ParameterState] = {}
        self.parameter_definitions: Dict[str, ParameterDefinition] = {}
        self.logger = None  # Will be set by game

        # Create config directory if it doesn't exist
        os.makedirs(os.path.dirname(config_file), exist_ok=True)

        # Initialize default parameters
        self._initialize_default_parameters()

        # Load saved parameters
        self._load_parameters()

    def _initialize_default_parameters(self):
        """Initialize default parameter definitions."""
        defaults = [
            # Debug Parameters
            ParameterDefinition(
                name="debug_mode",
                type=ParameterType.BOOLEAN,
                category=ParameterCategory.DEBUG,
                default_value=False,
                description="Enable debug mode with additional logging and visual indicators",
                hot_reloadable=True
            ),
            ParameterDefinition(
                name="show_fps",
                type=ParameterType.BOOLEAN,
                category=ParameterCategory.DEBUG,
                default_value=False,
                description="Display FPS counter in the top-right corner",
                hot_reloadable=True
            ),
            ParameterDefinition(
                name="show_collision_boxes",
                type=ParameterType.BOOLEAN,
                category=ParameterCategory.DEBUG,
                default_value=False,
                description="Show collision boxes for UI elements",
                hot_reloadable=True
            ),
            ParameterDefinition(
                name="log_level",
                type=ParameterType.CHOICE,
                category=ParameterCategory.DEBUG,
                default_value="INFO",
                description="Logging level for the application",
                choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                hot_reloadable=True
            ),

            # UI Parameters
            ParameterDefinition(
                name="ui_scale",
                type=ParameterType.FLOAT,
                category=ParameterCategory.UI,
                default_value=1.0,
                description="Global UI scaling factor",
                min_value=0.5,
                max_value=2.0,
                hot_reloadable=False
            ),
            ParameterDefinition(
                name="auto_screenshot",
                type=ParameterType.BOOLEAN,
                category=ParameterCategory.UI,
                default_value=False,
                description="Automatically capture screenshots on UI changes",
                hot_reloadable=True
            ),
            ParameterDefinition(
                name="screenshot_interval",
                type=ParameterType.INTEGER,
                category=ParameterCategory.UI,
                default_value=30,
                description="Interval in seconds for automatic screenshots",
                min_value=5,
                max_value=300,
                hot_reloadable=True
            ),
            ParameterDefinition(
                name="theme_override",
                type=ParameterType.CHOICE,
                category=ParameterCategory.UI,
                default_value="default",
                description="Override the current UI theme",
                choices=["default", "dark", "light", "high_contrast"],
                hot_reloadable=True
            ),

            # Gameplay Parameters
            ParameterDefinition(
                name="god_mode",
                type=ParameterType.BOOLEAN,
                category=ParameterCategory.GAMEPLAY,
                default_value=False,
                description="Enable god mode with unlimited resources",
                hot_reloadable=True
            ),
            ParameterDefinition(
                name="fast_forward_time",
                type=ParameterType.FLOAT,
                category=ParameterCategory.GAMEPLAY,
                default_value=1.0,
                description="Time multiplier for faster gameplay testing",
                min_value=0.1,
                max_value=10.0,
                hot_reloadable=True
            ),
            ParameterDefinition(
                name="disable_random_events",
                type=ParameterType.BOOLEAN,
                category=ParameterCategory.GAMEPLAY,
                default_value=False,
                description="Disable random events for consistent testing",
                hot_reloadable=True
            ),
            ParameterDefinition(
                name="auto_resolve_incidents",
                type=ParameterType.BOOLEAN,
                category=ParameterCategory.GAMEPLAY,
                default_value=False,
                description="Automatically resolve all incidents",
                hot_reloadable=True
            ),

            # Performance Parameters
            ParameterDefinition(
                name="max_fps",
                type=ParameterType.INTEGER,
                category=ParameterCategory.PERFORMANCE,
                default_value=60,
                description="Maximum frames per second",
                min_value=30,
                max_value=240,
                hot_reloadable=False
            ),
            ParameterDefinition(
                name="vsync",
                type=ParameterType.BOOLEAN,
                category=ParameterCategory.PERFORMANCE,
                default_value=True,
                description="Enable vertical sync",
                hot_reloadable=False
            ),
            ParameterDefinition(
                name="low_quality_mode",
                type=ParameterType.BOOLEAN,
                category=ParameterCategory.PERFORMANCE,
                default_value=False,
                description="Reduce quality for better performance",
                hot_reloadable=True
            ),

            # Backend Parameters
            ParameterDefinition(
                name="backend_enabled",
                type=ParameterType.BOOLEAN,
                category=ParameterCategory.BACKEND,
                default_value=True,
                description="Enable backend API server",
                hot_reloadable=False
            ),
            ParameterDefinition(
                name="backend_port",
                type=ParameterType.INTEGER,
                category=ParameterCategory.BACKEND,
                default_value=5000,
                description="Port for backend API server",
                min_value=1024,
                max_value=65535,
                hot_reloadable=False
            ),
            ParameterDefinition(
                name="live_state_sync",
                type=ParameterType.BOOLEAN,
                category=ParameterCategory.BACKEND,
                default_value=True,
                description="Sync backend with live game state",
                hot_reloadable=True
            ),

            # Development Parameters
            ParameterDefinition(
                name="dev_hot_reload",
                type=ParameterType.BOOLEAN,
                category=ParameterCategory.DEVELOPMENT,
                default_value=True,
                description="Enable hot reloading of game assets",
                hot_reloadable=True
            ),
            ParameterDefinition(
                name="dev_save_interval",
                type=ParameterType.INTEGER,
                category=ParameterCategory.DEVELOPMENT,
                default_value=60,
                description="Auto-save interval in seconds",
                min_value=10,
                max_value=3600,
                hot_reloadable=True
            ),
            ParameterDefinition(
                name="dev_test_mode",
                type=ParameterType.BOOLEAN,
                category=ParameterCategory.DEVELOPMENT,
                default_value=False,
                description="Enable test mode with predefined scenarios",
                hot_reloadable=True
            )
        ]

        for param_def in defaults:
            self.parameter_definitions[param_def.name] = param_def
            self.parameters[param_def.name] = ParameterState(
                definition=param_def,
                current_value=param_def.default_value
            )

    def _load_parameters(self):
        """Load saved parameter values from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    saved_data = json.load(f)

                for param_name, param_value in saved_data.items():
                    if param_name in self.parameters:
                        self.set_parameter(param_name, param_value, save=False)

                if self.logger:
                    self.logger.logger.info(f"[PARAMS] Loaded {len(saved_data)} saved parameters")

            except Exception as e:
                if self.logger:
                    self.logger.logger.warning(f"[PARAMS] Failed to load parameters: {e}")

    def _save_parameters(self):
        """Save current parameter values to file."""
        try:
            save_data = {}
            for name, state in self.parameters.items():
                save_data[name] = state.current_value

            with open(self.config_file, 'w') as f:
                json.dump(save_data, f, indent=2)

            if self.logger:
                self.logger.logger.debug(f"[PARAMS] Saved {len(save_data)} parameters")

        except Exception as e:
            if self.logger:
                self.logger.logger.error(f"[PARAMS] Failed to save parameters: {e}")

    def set_logger(self, logger):
        """Set the logger instance.

        Args:
            logger: Logger instance
        """
        self.logger = logger

    def get_parameter(self, name: str) -> Any:
        """Get the current value of a parameter.

        Args:
            name: Parameter name

        Returns:
            Current parameter value
        """
        if name not in self.parameters:
            raise ValueError(f"Parameter '{name}' not found")

        return self.parameters[name].current_value

    def set_parameter(self, name: str, value: Any, save: bool = True) -> bool:
        """Set the value of a parameter.

        Args:
            name: Parameter name
            value: New value
            save: Whether to save to file

        Returns:
            True if parameter was set successfully
        """
        if name not in self.parameters:
            if self.logger:
                self.logger.logger.warning(f"[PARAMS] Parameter '{name}' not found")
            return False

        param_state = self.parameters[name]
        param_def = param_state.definition

        # Validate value
        if not self._validate_parameter_value(param_def, value):
            if self.logger:
                self.logger.logger.warning(f"[PARAMS] Invalid value '{value}' for parameter '{name}'")
            return False

        # Set value
        old_value = param_state.current_value
        param_state.current_value = value
        param_state.last_modified = time.time()

        # Call callback if provided
        if param_def.callback:
            try:
                param_def.callback(old_value, value)
            except Exception as e:
                if self.logger:
                    self.logger.logger.error(f"[PARAMS] Callback error for '{name}': {e}")

        # Save if requested
        if save:
            self._save_parameters()

        if self.logger:
            self.logger.logger.info(f"[PARAMS] Set {name} = {value}")

        return True

    def _validate_parameter_value(self, param_def: ParameterDefinition, value: Any) -> bool:
        """Validate a parameter value.

        Args:
            param_def: Parameter definition
            value: Value to validate

        Returns:
            True if value is valid
        """
        try:
            if param_def.type == ParameterType.BOOLEAN:
                return isinstance(value, bool)
            elif param_def.type == ParameterType.INTEGER:
                if not isinstance(value, int):
                    return False
                if param_def.min_value is not None and value < param_def.min_value:
                    return False
                if param_def.max_value is not None and value > param_def.max_value:
                    return False
                return True
            elif param_def.type == ParameterType.FLOAT:
                if not isinstance(value, (int, float)):
                    return False
                if param_def.min_value is not None and value < param_def.min_value:
                    return False
                if param_def.max_value is not None and value > param_def.max_value:
                    return False
                return True
            elif param_def.type == ParameterType.STRING:
                return isinstance(value, str)
            elif param_def.type == ParameterType.CHOICE:
                return value in param_def.choices
            elif param_def.type == ParameterType.COLOR:
                # Basic color validation (hex color)
                if isinstance(value, str) and value.startswith('#'):
                    return len(value) == 7  # #RRGGBB format
                return False
            else:
                return True  # Unknown type, accept
        except:
            return False

    def get_parameters_by_category(self, category: ParameterCategory) -> Dict[str, Any]:
        """Get all parameters in a specific category.

        Args:
            category: Parameter category

        Returns:
            Dictionary of parameter names to values
        """
        result = {}
        for name, state in self.parameters.items():
            if state.definition.category == category:
                result[name] = state.current_value
        return result

    def get_all_parameters(self) -> Dict[str, Any]:
        """Get all current parameter values.

        Returns:
            Dictionary of all parameter names to values
        """
        return {name: state.current_value for name, state in self.parameters.items()}

    def reset_parameter(self, name: str) -> bool:
        """Reset a parameter to its default value.

        Args:
            name: Parameter name

        Returns:
            True if parameter was reset successfully
        """
        if name not in self.parameters:
            return False

        default_value = self.parameters[name].definition.default_value
        return self.set_parameter(name, default_value)

    def reset_all_parameters(self):
        """Reset all parameters to their default values."""
        for name in self.parameters.keys():
            self.reset_parameter(name)

        if self.logger:
            self.logger.logger.info("[PARAMS] Reset all parameters to defaults")

    def get_parameter_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a parameter.

        Args:
            name: Parameter name

        Returns:
            Dictionary with parameter information or None if not found
        """
        if name not in self.parameters:
            return None

        state = self.parameters[name]
        param_def = state.definition

        return {
            "name": name,
            "type": param_def.type.value,
            "category": param_def.category.value,
            "description": param_def.description,
            "current_value": state.current_value,
            "default_value": param_def.default_value,
            "choices": param_def.choices,
            "min_value": param_def.min_value,
            "max_value": param_def.max_value,
            "hot_reloadable": param_def.hot_reloadable,
            "last_modified": state.last_modified
        }

    def get_all_parameter_info(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed information about all parameters.

        Returns:
            Dictionary of parameter names to info dictionaries
        """
        result = {}
        for name in self.parameters.keys():
            info = self.get_parameter_info(name)
            if info:
                result[name] = info
        return result


# Global parameter system instance
_parameter_system = None


def get_parameter_system() -> RichParameterSystem:
    """Get the global parameter system instance.

    Returns:
        RichParameterSystem instance
    """
    global _parameter_system
    if _parameter_system is None:
        _parameter_system = RichParameterSystem()
    return _parameter_system


def get_parameter(name: str) -> Any:
    """Get a parameter value from the global system.

    Args:
        name: Parameter name

    Returns:
        Parameter value
    """
    return get_parameter_system().get_parameter(name)


def set_parameter(name: str, value: Any) -> bool:
    """Set a parameter value in the global system.

    Args:
        name: Parameter name
        value: New value

    Returns:
        True if successful
    """
    return get_parameter_system().set_parameter(name, value)