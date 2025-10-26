"""Main entry point for the Cybersecurity Firm Game.

This module initializes and runs the game, coordinating between the game logic,
user interface, and optional backend services.
"""

# Standard library imports
import os
import sys
import time
from datetime import datetime
from typing import Optional
import threading
import functools

# Third-party imports
import pygame

# Local imports
from src.core.plugins.ability_plugin import AbilityPlugin
from src.core.plugins.achievement_plugin import AchievementSystem
from src.core.plugins.budget_plugin import BudgetPlugin
from src.core.plugins.burnout_plugin import BurnoutPlugin
from src.core.plugins.client_plugin import ClientPlugin
from src.core.plugins.dopamine_plugin import DopaminePlugin
from src.core.plugins.economy_plugin import EconomyPlugin
from src.core.plugins.equipment_plugin import EquipmentPlugin
from src.core.plugins.facility_plugin import FacilityPlugin
from src.core.plugins.game_loop_plugin import GameLoopPlugin
from src.core.plugins.idle_plugin import IdlePlugin
from src.core.plugins.incident_dispatch_plugin import IncidentDispatchPlugin
from src.core.plugins.passive_income_plugin import PassiveIncomePlugin
from src.core.plugins.prestige_plugin import PrestigeSystem
from src.core.plugins.progressive_difficulty_plugin import ProgressiveDifficultyPlugin
from src.core.plugins.relationships_plugin import RelationshipsPlugin
from src.core.plugins.skill_tree_plugin import SkillTreePlugin
from src.core.plugins.sla_plugin import SLAPlugin
from src.core.plugins.team_dynamics_plugin import TeamDynamicsPlugin

from src.core.save_manager import SaveManager
from src.core.system_manager import SystemManager

from src.models.game_state import GameState

from src.ui.game_ui import GameUI
from src.ui.main_menu import MainMenu, MenuAction

from src.utils.backend_integration import (
    initialize_backend_integration,
    connect_to_backend,
)
from src.utils.game_args import parse_game_args, GameMode, GameArgs
from src.utils.json_loader import load_game_data
from src.utils.logger import GameLogger
from src.utils.rich_parameter_system import get_parameter_system
from src.utils.screenshot import initialize_screenshot_utility

# Websocket server integration (headless/local-server mode)
from src.websocket_game import start_background_server, start_background_server_with_enqueue, set_state
import src.websocket_game as websocket_game
import http.server
import socketserver
import webbrowser
import queue


class Game:
    """Main game class coordinating all systems.
    
    Supports both UI and headless modes through optional UI initialization.
    Backend integration is optional and enables live debugging/manipulation.
    """

    def __init__(self, args: GameArgs):
        """Initialize the game.
        
        Args:
            args: Parsed game arguments for initialization
        """
        self.logger = GameLogger("main")
        self.args = args
        self.game_state: Optional[GameState] = None
        self.ui: Optional[GameUI] = None
        self.main_menu: Optional[MainMenu] = None
        self.system_manager: Optional[SystemManager] = None
        self.save_manager: Optional[SaveManager] = None
        self.running = False

        # Development systems
        self.parameter_system = None
        self.screenshot_utility = None
        self.backend_integration = None

        # Game timing
        self.last_update = time.time()
        self.target_fps = 60
        self.frame_time = 1.0 / self.target_fps
        # Headless websocket broadcast accumulator (seconds)
        self._ws_broadcast_acc = 0.0
        
        # Auto-save system
        self.last_auto_save = time.time()
        self.auto_save_interval = 300.0  # Default 5 minutes, will be updated from config

        # Action queue for external inputs (from websocket server)
        self._action_queue = queue.Queue()

        # Menu state
        self.in_menu = args.should_show_menu()
        self.menu_action: Optional[MenuAction] = None

    def initialize(self) -> bool:
        """Initialize all game systems.

        Returns:
            True if initialization successful, False otherwise
        """
        with self.logger.operation("Game Initialization") as op:
            try:
                self.logger.info("[GAME] Initializing Cybersecurity Firm Game...")
                op.add_context('mode', self.args.mode.value if hasattr(self.args.mode, 'value') else str(self.args.mode))

                # Initialize save manager first
                with self.logger.operation("Save Manager Initialization"):
                    self.save_manager = SaveManager()
                    self.logger.info("[GAME] Save manager initialized successfully")
                
                # Check if we should show menu or load game directly
                if self.args.should_show_menu():
                    self.logger.info("[GAME] Starting in menu mode...")
                    result = self._initialize_menu()
                    op.add_context('initialized', 'menu')
                    return result
                elif self.args.should_load_game():
                    self.logger.info("[GAME] Loading saved game...", slot=self.args.save_slot)
                    result = self._initialize_from_save()
                    op.add_context('initialized', 'from_save')
                    return result
                elif self.args.mode == GameMode.TUTORIAL:
                    self.logger.info("[GAME] Starting tutorial mode...")
                    result = self._initialize_tutorial()
                    op.add_context('initialized', 'tutorial')
                    return result
                else:
                    # New game
                    self.logger.info("[GAME] Starting new game...")
                    result = self._initialize_new_game()
                    op.add_context('initialized', 'new_game')
                    return result

            except Exception as e:
                self.logger.error(
                    "[GAME] Failed to initialize game",
                    exception=e,
                    mode=self.args.mode.value if hasattr(self.args.mode, 'value') else str(self.args.mode)
                )
                return False
    
    def _initialize_menu(self) -> bool:
        """Initialize the main menu.
        
        Returns:
            True if menu initialized successfully
        """
        with self.logger.operation("Main Menu Initialization"):
            try:
                # Pygame initialization is handled in main() to keep startup
                # deterministic. If for some reason it isn't initialized yet,
                # initialize it here (defensive).
                if not pygame.get_init():
                    self.logger.debug("[GAME] Pygame not initialized yet; initializing defensively...")
                    pygame.init()
                    self.logger.debug("[GAME] Pygame initialized (defensive)")
                
                # Create main menu
                self.logger.debug("[GAME] Creating main menu...")
                self.main_menu = MainMenu()
                
                # Check if continue is available (slot 0 = auto-save)
                if self.save_manager:
                    saves = self.save_manager.list_saves()
                    auto_save = saves[0] if saves else None
                    continue_available = bool(auto_save and auto_save.get('exists', False))
                    
                    self.main_menu.set_continue_available(continue_available)
                    self.logger.debug("[GAME] Continue option available", available=continue_available)
                
                self.in_menu = True
                self.running = True
                
                self.logger.info("[GAME] Main menu initialized successfully")
                return True
                
            except Exception as e:
                self.logger.error("[GAME] Failed to initialize menu", exception=e)
                return False
    
    def _initialize_from_save(self) -> bool:
        """Initialize game from a saved state.
        
        Returns:
            True if load successful
        """
        try:
            # Determine which slot to load
            if self.args.mode == GameMode.CONTINUE:
                # Load most recent save (auto-save slot 0)
                slot = 0
            else:
                # Load specific slot
                slot = self.args.save_slot

            self.logger.info(f"[GAME] Loading game from slot {slot}...")

            # Defensive: ensure save_manager exists before calling into it
            if not self.save_manager:
                self.logger.warning("[GAME] Save manager not initialized; cannot load save. Starting new game instead.")
                return self._initialize_new_game()

            # Validate slot is provided (static analysis and runtime guard)
            if slot is None:
                self.logger.error("[GAME] No save slot specified for load; starting new game instead")
                return self._initialize_new_game()

            # Load game state
            self.game_state = self.save_manager.load_game(int(slot))

            # Load game data for configuration
            game_data = load_game_data()

            # Initialize UI and systems with loaded state
            return self._initialize_game_systems(game_data)

        except FileNotFoundError:
            self.logger.error("[GAME] Save file not found")
            # Fall back to new game
            self.logger.info("[GAME] Starting new game instead...")
            return self._initialize_new_game()
        except Exception as e:
            self.logger.error(f"[GAME] Failed to load save: {e}")
            return False
    
    def _initialize_new_game(self) -> bool:
        """Initialize a new game.
        
        Returns:
            True if initialization successful
        """
        with self.logger.operation("New Game Initialization"):
            try:
                # Load game data
                with self.logger.operation("Loading Game Configuration"):
                    game_data = load_game_data()
                    self.logger.info("[GAME] Game configuration loaded successfully")

                # Initialize game state with default values
                with self.logger.operation("Creating Game State"):
                    self.game_state = GameState()
                    self.logger.info("[GAME] Game state initialized successfully")
                
                # Initialize UI and systems
                return self._initialize_game_systems(game_data)
                
            except Exception as e:
                self.logger.error("[GAME] Failed to initialize new game", exception=e)
                return False
    
    def _initialize_tutorial(self) -> bool:
        """Initialize tutorial mode.
        
        Returns:
            True if initialization successful
        """
        try:
            # Load game data
            self.logger.info("[GAME] Loading game configuration for tutorial...")
            game_data = load_game_data()

            # Initialize game state with tutorial-specific settings
            self.logger.info("[GAME] Initializing tutorial game state...")
            self.game_state = GameState()
            
            # Mark this as a tutorial session
            # This allows the game to show tutorial-specific UI and guidance
            if not hasattr(self.game_state, 'is_tutorial'):
                self.game_state.is_tutorial = True
            else:
                self.game_state.is_tutorial = True
            
            self.logger.info("[GAME] Tutorial mode enabled")
            
            # Initialize UI and systems
            return self._initialize_game_systems(game_data)
            
        except Exception as e:
            self.logger.error(f"[GAME] Failed to initialize tutorial: {e}")
            return False

    def enqueue_action(self, action: dict) -> None:
        """Enqueue an external action (called by websocket server thread).

        Actions are processed on the main game loop to preserve authoritative
        ordering and thread-safety.
        """
        try:
            self._action_queue.put(action)
        except Exception:
            # Best-effort: ignore enqueue failures to keep game running
            pass
    
    def _initialize_game_systems(self, game_data: dict) -> bool:
        """Initialize UI and game systems (common for both new and loaded games).
        
        Returns:
            True if initialization successful
        """
        with self.logger.operation("Game Systems Initialization"):
            try:
                # Validate game state exists
                if not self.game_state:
                    self.logger.critical("[GAME] Cannot initialize systems: game_state is None!")
                    return False
                
                # Initialize plugin architecture (SystemManager) FIRST
                with self.logger.operation("Plugin Architecture Initialization"):
                    self.logger.debug("[GAME] Creating SystemManager...")
                    self.system_manager = SystemManager()
                    self.logger.info("[GAME] Plugin architecture initialized")
                
                # Register game systems as plugins BEFORE UI initialization
                # This ensures UI can discover all UIProvider plugins immediately
                with self.logger.operation("Plugin Registration"):
                    # REFACTORED: Only register ESSENTIAL plugins for core game loop
                    # Philosophy: "Show the core loop or remove the system"
                    # - If player can't see/interact with it, it shouldn't be running
                    # - Core loop: assign specialists → resolve incidents → manage budget → keep clients happy
                    
                    # ESSENTIAL CORE PLUGINS (functional and visible)
                    plugin_classes = [
                        ("BudgetPlugin", BudgetPlugin),              # Money tracking - NOW HAS UI
                        ("ClientPlugin", ClientPlugin),              # Client management - HAS UI
                        ("IncidentDispatchPlugin", IncidentDispatchPlugin),  # Core gameplay - HAS UI
                        ("SLAPlugin", SLAPlugin),                   # SLA tracking - essential for gameplay
                        ("GameLoopPlugin", GameLoopPlugin),         # Time/phase management
                        ("BurnoutPlugin", BurnoutPlugin),           # Specialist fatigue - HAS UI
                    ]
                    
                    # DISABLED PLUGINS (no UI implementation or not essential to core loop)
                    # These add complexity without visible player value

                    registered = 0
                    for plugin_name, plugin_cls in plugin_classes:
                        try:
                            self.logger.debug(f"[SYSTEM] Instantiating {plugin_name}...")
                            plugin_instance = plugin_cls()
                        except Exception as e:
                            self.logger.error(f"[SYSTEM] Failed to instantiate {plugin_name}: {e}")
                            continue

                        try:
                            self.logger.debug(f"[SYSTEM] Registering {plugin_name}...")
                            self.system_manager.register_system(plugin_instance)
                            registered += 1
                        except Exception as e:
                            self.logger.error(f"[SYSTEM] Failed to register {plugin_name}: {e}")

                    self.logger.info(f"[SYSTEM] Registered {registered} game systems")
                
                # Initialize UI AFTER plugins are registered
                # This allows DashboardManager to discover UIProvider plugins immediately
                with self.logger.operation("UI Initialization"):
                    if self.args.headless:
                        self.ui = None
                        self.logger.info("[GAME] Headless mode: skipping UI initialization")
                    else:
                        self.logger.debug("[GAME] Creating GameUI instance...")
                        self.ui = GameUI(self.game_state, self.system_manager)
                        self.logger.info("[GAME] User interface initialized successfully")
                
                # Initialize all registered systems
                with self.logger.operation("Systems Initialization"):
                    self.logger.debug("[SYSTEM] Initializing all registered systems...")
                    self.system_manager.initialize_all(self.game_state)
                    self.logger.info("[SYSTEM] All systems initialized successfully")

                # If requested, start the embedded websocket server in background
                if self.args.local_server:
                    try:
                        # Web UI connects to websocket on port 8765 by convention
                        ws_port = 8765
                        self.logger.info(f"[WS] Starting embedded websocket server on port {ws_port}")
                        # If ADMIN_TOKEN is set in environment, register it for the WS server
                        try:
                            websocket_game.ADMIN_TOKEN = os.getenv('ADMIN_TOKEN')
                            if websocket_game.ADMIN_TOKEN:
                                self.logger.info("[WS] Admin token set - admin actions will require token")
                        except Exception:
                            pass

                        # NOTE: Static server is started early in main() when local_server is enabled.
                        # Avoid starting another instance here to prevent port conflicts.

                        # Pass our enqueue function so the websocket server can forward actions
                        self._ws_thread = start_background_server_with_enqueue(
                            host="0.0.0.0", port=ws_port, action_enqueue=self.enqueue_action
                        )
                        self.logger.info("[WS] Embedded websocket server started in background thread")

                        # Optionally wait for WS port so web UI can connect immediately
                        try:
                            self._wait_for_port('127.0.0.1', ws_port, timeout=3.0)
                        except Exception:
                            self.logger.debug("[WS] Websocket port did not become available in time; continuing")
                    except Exception as e:
                        self.logger.error("[WS] Failed to start embedded websocket server", exception=e)

                # Load auto-save configuration from game data
                with self.logger.operation("Auto-Save Configuration"):
                    game_config = game_data.get('game_config', {})
                    game_settings = game_config.get('game_settings', {})
                    auto_save_interval = game_settings.get('auto_save_interval_seconds', 300.0)
                    self.auto_save_interval = auto_save_interval
                    self.logger.info(f"[GAME] Auto-save interval set to {auto_save_interval} seconds")

                # Legacy panel connections removed - UI now uses Dashboard Framework
                # All UI is provided through UIProvider interface on plugins

                # Initialize development systems
                with self.logger.operation("Development Systems Initialization"):
                    self.logger.debug("[GAME] Initializing parameter system...")
                    self.parameter_system = get_parameter_system()
                    self.parameter_system.set_logger(self.logger)
                    self.logger.debug("[GAME] Parameter system initialized")

                    if self.ui and self.game_state:
                        self.logger.debug("[GAME] Initializing screenshot utility...")
                        self.screenshot_utility = initialize_screenshot_utility(
                            self.ui, self.game_state, self.logger
                        )
                        self.logger.debug("[GAME] Screenshot utility initialized")
                        
                        # Set screenshot utility on UI for hotkey callbacks
                        self.ui.set_screenshot_utility(self.screenshot_utility)

                # Initialize backend integration
                with self.logger.operation("Backend Integration Initialization"):
                    self.logger.debug("[BACKEND] Creating backend integration...")
                    # Backend runs on port 5001 by default (see backend/config.py)
                    self.backend_integration = initialize_backend_integration(port=5001, logger=self.logger)
                    self.logger.debug("[BACKEND] Backend integration created")

                    # Try to connect to backend if available
                    if self.game_state and self.backend_integration:
                        self.logger.debug("[BACKEND] Attempting to connect to backend...")
                        backend_connected = connect_to_backend(self.game_state)
                        if backend_connected:
                            self.logger.info("[BACKEND] Backend integration connected successfully")
                        else:
                            self.logger.info("[BACKEND] Backend not available, running standalone")

                # Start the game
                self.running = True
                self.in_menu = False
                self.logger.info("[GAME] ✅ Game systems initialization complete!")

                return True
                
            except Exception as e:
                self.logger.error("[GAME] Failed to initialize game systems", exception=e)
                return False

    def run(self) -> None:
        """Run the main game loop."""
        if not self.initialize():
            self.logger.error("[GAME] Game initialization failed. Exiting.")
            sys.exit(1)

        self.logger.info("[GAME] Starting main game loop...")

        try:
            while self.running:
                current_time = time.time()
                delta_time = current_time - self.last_update

                # Limit frame rate
                if delta_time < self.frame_time:
                    time.sleep(self.frame_time - delta_time)
                    continue

                self.last_update = current_time

                # Headless mode: do not poll pygame events
                events = []
                if not self.args.headless:
                    events = pygame.event.get()
                    for event in events:
                        if event.type == pygame.QUIT:
                            self.running = False
                            break

                # Handle menu or game (only if still running)
                if self.running:
                    if self.in_menu:
                        self._run_menu(events, delta_time)
                    else:
                        self._run_game(events, delta_time)

        except KeyboardInterrupt:
            self.logger.info("[GAME] Game interrupted by user")
        except Exception as e:
            import traceback
            self.logger.error(f"[GAME] Unexpected error in game loop: {e}", exception=e)
            # Log full traceback via wrapper's error with exception
            self.logger.error(f"[GAME] Traceback:\n{traceback.format_exc()}")
        finally:
            self.shutdown()
    
    def _run_menu(self, events: list, delta_time: float) -> None:
        """Run the menu loop.
        
        Args:
            events: Pygame events
            delta_time: Time since last update
        """
        if not self.main_menu:
            return
        
        # Handle menu input
        action = self.main_menu.handle_input(events)
        
        if action == MenuAction.EXIT:
            self.running = False
            return
        elif action == MenuAction.NEW_GAME:
            self.logger.info("[GAME] Starting new game from menu...")
            if self._initialize_new_game():
                self.in_menu = False
        elif action == MenuAction.CONTINUE:
            self.logger.info("[GAME] Continuing game from menu...")
            if self._initialize_from_save():
                self.in_menu = False
        elif action == MenuAction.TUTORIAL:
            self.logger.info("[GAME] Starting tutorial from menu...")
            if self._initialize_tutorial():
                self.in_menu = False
        elif action == MenuAction.SETTINGS:
            self.main_menu.show_settings_menu()
        
        # Update and render menu
        self.main_menu.update(delta_time)
        self.main_menu.render()
    
    def _run_game(self, events: list, delta_time: float) -> None:
        """Run the game loop.
        
        Args:
            events: Pygame events
            delta_time: Time since last update
        """
        # Validate critical objects exist before using them
        if not self.game_state:
            self.logger.error("[GAME] game_state is None in _run_game!")
            self.running = False
            return

        if not self.args.headless and not self.ui:
            self.logger.error("[GAME] ui is None in _run_game (non-headless)!")
            self.running = False
            return
        
        # Process queued external actions (from websocket clients)
        try:
            while not self._action_queue.empty():
                action = self._action_queue.get_nowait()
                try:
                    # Handle known action types
                    if action.get("action") == "assign_incident":
                        incident_id = action.get("incident_id")
                        specialist_id = action.get("specialist_id")
                        if incident_id and specialist_id:
                            ok = False
                            try:
                                ok = self.game_state.assign_incident_to_specialist(incident_id, specialist_id)
                            except Exception as e:
                                self.logger.warning("[GAME] Failed to assign incident from queued action", exception=e)
                            self.logger.info(f"[GAME] Queued action assign_incident processed: {incident_id} -> {specialist_id} (ok={ok})")
                            # Immediately publish snapshot so WS clients see the result without waiting
                            try:
                                set_state(self.game_state.to_dict())
                            except Exception:
                                pass
                            # If the action included a client action id, post a result for the websocket server to dispatch
                            client_action_id = action.get("_client_action_id")
                            if client_action_id:
                                try:
                                    websocket_game.ACTION_RESULT_QUEUE.put({
                                        "_client_action_id": client_action_id,
                                        "action": "assign_incident",
                                        "status": "ok" if ok else "error",
                                        "details": {"incident_id": incident_id, "specialist_id": specialist_id},
                                    })
                                except Exception:
                                    pass
                    else:
                        self.logger.debug(f"[GAME] Unknown queued action received: {action.get('action')}")
                except Exception as e:
                    self.logger.error("[GAME] Error processing queued action", exception=e)
        except Exception:
            # Non-fatal: ignore queue processing errors to avoid breaking main loop
            pass

        # Update game state and plugins
        self.game_state.update(delta_time)
        
        # Update all registered plugins/systems
        if self.system_manager:
            self.system_manager.update_all(self.game_state, delta_time)

        # Check for auto-save
        self._check_auto_save(delta_time)

        # Headless: broadcast state periodically to websocket clients
        if self.args.headless:
            try:
                self._ws_broadcast_acc += delta_time
                if self._ws_broadcast_acc >= 1.0:
                    # Best-effort: publish authoritative snapshot to WS clients
                    try:
                        set_state(self.game_state.to_dict())
                    except Exception as e:
                        self.logger.debug("[WS] Failed to publish state snapshot", exception=e)
                    self._ws_broadcast_acc = 0.0
            except Exception:
                # Silently ignore broadcast errors to avoid breaking game loop
                pass
        else:
            # Update UI
            self.ui.handle_input(events)
            self.ui.update(delta_time)

        # Update development systems
        if self.screenshot_utility:
            self.screenshot_utility.update(delta_time)

        # Update backend integration
        # Backend integration runs in background thread, no per-frame update needed

        # Render (only when UI present)
        if not self.args.headless and self.ui:
            self.ui.render()
            pygame.display.flip()

    def _check_auto_save(self, delta_time: float) -> None:
        """Check if auto-save should be triggered.
        
        Args:
            delta_time: Time since last update
        """
        # Update auto-save timer
        self.last_auto_save += delta_time
        
        # Check if it's time to auto-save
        if self.last_auto_save >= self.auto_save_interval:
            self.logger.info("[GAME] Auto-save triggered")
            
            # Perform auto-save
            if self.save_manager and self.game_state:
                try:
                    success = self.save_manager.auto_save(self.game_state)
                    if success:
                        self.logger.info("[GAME] Auto-save completed successfully")
                        # Reset timer
                        self.last_auto_save = 0.0
                    else:
                        self.logger.warning("[GAME] Auto-save failed")
                except Exception as e:
                    self.logger.error(f"[GAME] Auto-save error: {e}")
            else:
                self.logger.warning("[GAME] Cannot auto-save: save_manager or game_state is None")


    def shutdown(self) -> None:
        """Clean shutdown of all systems."""
        self.logger.info("[GAME] Shutting down...")

        # Auto-save before shutdown (if we have a game state)
        if self.game_state and self.save_manager and not self.in_menu:
            try:
                self.logger.info("[GAME] Auto-saving game...")
                self.save_manager.auto_save(self.game_state)
            except Exception as e:
                self.logger.error("[GAME] Auto-save failed", exception=e)

        # Shutdown plugins/systems first
        if self.system_manager and self.game_state:
            self.logger.info("[GAME] Shutting down all game systems...")
            self.system_manager.shutdown_all(self.game_state)

        if self.backend_integration:
            self.backend_integration.disconnect()

        if self.main_menu:
            self.main_menu.shutdown()

        if self.ui:
            self.ui.shutdown()
        if not self.args.headless:
            pygame.quit()
        self.logger.info("[GAME] Game shutdown complete")

    def _wait_for_port(self, host: str, port: int, timeout: float = 3.0) -> None:
        """Wait for a TCP port to be open on host:port up to timeout seconds.

        Raises:
            TimeoutError: if port is not open within timeout
        """
        import socket
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                with socket.create_connection((host, port), timeout=0.5):
                    return
            except Exception:
                time.sleep(0.1)
        raise TimeoutError(f"Port {host}:{port} not open after {timeout}s")


def main():
    """Main entry point."""
    from src.utils.logger import setup_logging
    
    # Setup logging FIRST - this is critical for debugging
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_file = os.path.join('logs', f'game_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    setup_logging(
        log_level=log_level,
        log_file=log_file,
        log_to_console=True,
        use_colors=True
    )
    
    logger = GameLogger("main")
    logger.info("="*60)
    logger.info("[GAME] 🎮 Starting Cybersecurity Firm - Idle/Tycoon/RPG 🎮")
    logger.info("="*60)
    
    try:
        # Parse command-line arguments
        with logger.operation("Parsing Command-Line Arguments"):
            args = parse_game_args()

            # User preference: default to local embedded server unless explicit remote or no-server provided
            if not args.remote_host and not args.no_server and not args.local_server:
                args.local_server = True
                # When running an embedded server we run headless by default
                args.headless = True

            # Enforce: embedded local server => headless engine and skip menu to avoid opening legacy Pygame window
            if args.local_server:
                args.headless = True
                if args.mode == GameMode.MENU:
                    # Skip interactive menu in embedded-server mode; start new game directly
                    args.mode = GameMode.NEW_GAME

            # If we are running a local embedded server, start the static file server early
            # so the UI is available immediately (before game systems initialize).
            if args.local_server:
                try:
                    # Pick a static HTTP port (prefer 8000, fall back to next few)
                    static_port = 8000
                    repo_root = os.path.dirname(os.path.abspath(__file__))
                    ui_dir = os.path.join(repo_root, 'ui', 'game')
                    if os.path.isdir(ui_dir):
                        # Try a small range of ports to avoid conflict
                        chosen_port = None
                        for candidate in range(static_port, static_port + 10):
                            try:
                                # Try binding to candidate to test availability, then close
                                test_handler = functools.partial(
                                    http.server.SimpleHTTPRequestHandler,
                                    directory=ui_dir
                                )
                                # Use a one-off server instance to check bind; if success, run real server
                                class _ThreadingTCPServer(socketserver.ThreadingTCPServer):
                                    allow_reuse_address = True
                                httpd = _ThreadingTCPServer(("0.0.0.0", candidate), test_handler)
                                httpd.server_close()  # Release test bind immediately
                                chosen_port = candidate
                                break
                            except OSError:
                                continue

                        if chosen_port is None:
                            # If all candidates fail, fall back to 8000 and hope for the best
                            chosen_port = static_port

                        def _start_static_early(port: int):
                            handler = functools.partial(
                                http.server.SimpleHTTPRequestHandler,
                                directory=ui_dir
                            )
                            class ThreadingHTTPServer(socketserver.ThreadingTCPServer):
                                allow_reuse_address = True
                            with ThreadingHTTPServer(("0.0.0.0", port), handler) as httpd:
                                logger.info(f"[STATIC-EARLY] Serving web UI at http://0.0.0.0:{port}")
                                httpd.serve_forever()

                        t_static_early = threading.Thread(target=lambda: _start_static_early(chosen_port), daemon=True, name="static-server-early")
                        t_static_early.start()
                        # Best-effort: open browser after a short delay so server has time to bind
                        try:
                            time.sleep(0.1)
                            webbrowser.open(f'http://localhost:{chosen_port}/index.html')
                        except Exception:
                            pass
                    else:
                        logger.warning(f"[STATIC-EARLY] ui/game directory not found at {ui_dir}; static UI will not be served.")
                except Exception:
                    # Do not raise - static server is optional
                    pass

            logger.info(
                "[GAME] Arguments parsed",
                mode=args.mode.value if hasattr(args.mode, 'value') else str(args.mode),
                backend_mode=args.get_backend_mode()
            )
        
        # Initialize Pygame (only when not running headless)
        with logger.operation("Pygame Initialization"):
            if not args.headless:
                pygame.init()
                pygame.display.set_caption("Cybersecurity Firm - Idle/Tycoon/RPG")
                logger.info("[GAME] Pygame initialized successfully")
            else:
                logger.info("[GAME] Headless mode requested; skipping Pygame initialization")

        # Create and run game
        logger.info("[GAME] Creating game instance...")
        game = Game(args)

        # If local embedded server requested, start it when game systems are initialized
        # The Game class will start the server in _initialize_game_systems when appropriate
        logger.info("[GAME] Starting game...")
        game.run()

        logger.info("[GAME] Game exited normally")

    except KeyboardInterrupt:
        logger.info("[GAME] Game interrupted by user (Ctrl+C)")
    except Exception as e:
        logger.critical("[GAME] FATAL ERROR - Game crashed!", exception=e)
        sys.exit(1)


if __name__ == "__main__":
    main()
