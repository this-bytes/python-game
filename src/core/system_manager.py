"""System Manager for orchestrating game systems.

The System Manager handles the lifecycle of all game systems (plugins),
ensuring proper initialization order, update coordination, and save/load.
"""

from typing import Dict, List, Optional, Set
from src.core.game_system import GameSystem
from src.core.feature_manager import get_feature_manager
from src.core.event_bus import get_event_bus
from src.models.game_state import GameState
from src.utils.logger import GameLogger


class SystemManager:
    """Manages the lifecycle of all game systems.
    
    Features:
    - Automatic dependency resolution
    - Feature flag integration
    - Coordinated save/load
    - System enable/disable at runtime
    - Event-driven communication
    
    Example:
        ```python
        manager = SystemManager()
        
        # Register systems
        manager.register_system(IdleCorePlugin())
        manager.register_system(PrestigeSystemPlugin())
        
        # Initialize all
        manager.initialize_all(game_state)
        
        # Update in game loop
        manager.update_all(game_state, delta_time)
        ```
    """
    
    def __init__(self):
        """Initialize the system manager."""
        self._systems: Dict[str, GameSystem] = {}
        self._system_order: List[str] = []
        self._feature_manager = get_feature_manager()
        self._event_bus = get_event_bus()
        self._logger = GameLogger("system_manager")
    
    def register_system(self, system: GameSystem):
        """Register a game system.
        
        Systems are registered but not initialized until initialize_all() is called.
        
        Args:
            system: GameSystem instance to register
        """
        name = system.get_name()
        
        if name in self._systems:
            self._logger.logger.warning(f"[SYSTEM_MANAGER] System '{name}' already registered, replacing")
        
        self._systems[name] = system
        
        # Rebuild initialization order
        self._rebuild_system_order()
        
        self._logger.logger.info(f"[SYSTEM_MANAGER] Registered system: {name}")
    
    def unregister_system(self, system_name: str, game_state: GameState = None):
        """Unregister and shutdown a game system.
        
        Args:
            system_name: Name of system to remove
            game_state: Optional game state for shutdown
        """
        if system_name not in self._systems:
            return
        
        system = self._systems[system_name]
        
        # Shutdown if initialized
        if system.is_initialized() and game_state:
            system.shutdown(game_state)
        
        del self._systems[system_name]
        self._rebuild_system_order()
        
        self._logger.logger.info(f"[SYSTEM_MANAGER] Unregistered system: {system_name}")
    
    def initialize_all(self, game_state: GameState):
        """Initialize all registered systems in dependency order.
        
        Systems with unmet feature flags or dependencies are skipped.
        
        Args:
            game_state: Game state to pass to systems
        """
        self._logger.logger.info("[SYSTEM_MANAGER] Initializing all systems...")
        
        initialized_count = 0
        skipped_count = 0
        
        for system_name in self._system_order:
            system = self._systems[system_name]
            
            # Check feature flag
            feature_id = system.get_feature_id()
            if feature_id and not self._feature_manager.is_enabled(feature_id):
                self._logger.logger.info(
                    f"[SYSTEM_MANAGER] Skipping '{system_name}' (feature '{feature_id}' disabled)"
                )
                skipped_count += 1
                continue
            
            # Check dependencies
            deps_met = self._check_dependencies(system)
            if not deps_met:
                self._logger.logger.warning(
                    f"[SYSTEM_MANAGER] Skipping '{system_name}' (dependencies not met)"
                )
                skipped_count += 1
                continue
            
            # Initialize
            try:
                system.initialize(game_state)
                system.set_initialized(True)
                initialized_count += 1
                self._logger.logger.info(f"[SYSTEM_MANAGER] Initialized: {system_name}")
            except Exception as e:
                self._logger.logger.error(
                    f"[SYSTEM_MANAGER] Failed to initialize '{system_name}': {e}"
                )
                skipped_count += 1
        
        self._logger.logger.info(
            f"[SYSTEM_MANAGER] Initialization complete: "
            f"{initialized_count} initialized, {skipped_count} skipped"
        )
    
    def update_all(self, game_state: GameState, delta_time: float):
        """Update all enabled and initialized systems.
        
        Args:
            game_state: Current game state
            delta_time: Time elapsed since last update (seconds)
        """
        for system_name in self._system_order:
            system = self._systems[system_name]
            
            # Skip if not initialized or not enabled
            if not system.is_initialized() or not system.is_enabled():
                continue
            
            try:
                system.update(game_state, delta_time)
            except Exception as e:
                self._logger.logger.error(
                    f"[SYSTEM_MANAGER] Error updating '{system_name}': {e}"
                )
        
        # Process event bus after all systems update
        self._event_bus.process_events()
    
    def shutdown_all(self, game_state: GameState):
        """Shutdown all systems in reverse order.
        
        Args:
            game_state: Game state for shutdown
        """
        self._logger.logger.info("[SYSTEM_MANAGER] Shutting down all systems...")
        
        # Shutdown in reverse order
        for system_name in reversed(self._system_order):
            system = self._systems[system_name]
            
            if system.is_initialized():
                try:
                    system.shutdown(game_state)
                    self._logger.logger.info(f"[SYSTEM_MANAGER] Shutdown: {system_name}")
                except Exception as e:
                    self._logger.logger.error(
                        f"[SYSTEM_MANAGER] Error shutting down '{system_name}': {e}"
                    )
    
    def save_all(self, game_state: GameState) -> Dict[str, Dict]:
        """Save state from all systems.
        
        Args:
            game_state: Current game state
            
        Returns:
            Dictionary mapping system names to their state data
        """
        system_states = {}
        
        for system_name in self._system_order:
            system = self._systems[system_name]
            
            if system.is_initialized():
                try:
                    state_data = system.save_state(game_state)
                    if state_data:
                        system_states[system_name] = state_data
                except Exception as e:
                    self._logger.logger.error(
                        f"[SYSTEM_MANAGER] Error saving '{system_name}': {e}"
                    )
        
        return system_states
    
    def load_all(self, game_state: GameState, system_states: Dict[str, Dict]):
        """Load state into all systems.
        
        Args:
            game_state: Current game state
            system_states: Dictionary of system names to state data
        """
        for system_name in self._system_order:
            system = self._systems[system_name]
            
            if system.is_initialized() and system_name in system_states:
                try:
                    system.load_state(game_state, system_states[system_name])
                    self._logger.logger.info(f"[SYSTEM_MANAGER] Loaded state: {system_name}")
                except Exception as e:
                    self._logger.logger.error(
                        f"[SYSTEM_MANAGER] Error loading '{system_name}': {e}"
                    )
    
    def get_system(self, system_name: str) -> Optional[GameSystem]:
        """Get a system by name.
        
        Args:
            system_name: Name of system to retrieve
            
        Returns:
            GameSystem instance or None if not found
        """
        return self._systems.get(system_name)
    
    def get_all_systems(self) -> Dict[str, GameSystem]:
        """Get all registered systems.
        
        Returns:
            Dictionary of system names to GameSystem instances
        """
        return self._systems.copy()
    
    def get_initialized_systems(self) -> List[str]:
        """Get names of all initialized systems.
        
        Returns:
            List of system names
        """
        return [
            name for name, system in self._systems.items()
            if system.is_initialized()
        ]
    
    def _rebuild_system_order(self):
        """Rebuild system initialization order based on dependencies.
        
        Uses topological sort to ensure dependencies are initialized first.
        """
        # Build dependency graph
        graph: Dict[str, Set[str]] = {}
        in_degree: Dict[str, int] = {}
        
        for name, system in self._systems.items():
            deps = set(system.get_dependencies())
            graph[name] = deps
            in_degree[name] = len(deps)
        
        # Topological sort (Kahn's algorithm)
        queue = [name for name, degree in in_degree.items() if degree == 0]
        order = []
        
        while queue:
            # Sort to ensure deterministic ordering
            queue.sort()
            current = queue.pop(0)
            order.append(current)
            
            # Reduce in-degree for systems depending on current
            for name, deps in graph.items():
                if current in deps:
                    in_degree[name] -= 1
                    if in_degree[name] == 0:
                        queue.append(name)
        
        # Check for cycles
        if len(order) != len(self._systems):
            self._logger.logger.error(
                "[SYSTEM_MANAGER] Circular dependencies detected in systems!"
            )
            # Fall back to registration order
            order = list(self._systems.keys())
        
        self._system_order = order
    
    def _check_dependencies(self, system: GameSystem) -> bool:
        """Check if all dependencies for a system are met.
        
        Args:
            system: System to check
            
        Returns:
            True if all dependencies are initialized
        """
        for dep_name in system.get_dependencies():
            if dep_name not in self._systems:
                return False
            
            dep_system = self._systems[dep_name]
            if not dep_system.is_initialized():
                return False
        
        return True
