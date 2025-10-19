"""Main entry point for the Cybersecurity Firm Game.

This module initializes and runs the game, coordinating between the game logic,
user interface, and optional backend services.
"""

import sys
import time
import pygame
import os
from datetime import datetime
from typing import Optional

# Add parent directory to path so src imports work
sys.path.insert(0, '/home/localadmin/code/python-game')

# Change to project root directory so relative paths work
# os.chdir('/home/localadmin/code/python-game')

from src.models.game_state import GameState
from src.ui.game_ui import GameUI
from src.ui.main_menu import MainMenu, MenuAction
from src.utils.logger import GameLogger
from src.utils.json_loader import load_game_data
from src.utils.rich_parameter_system import get_parameter_system
from src.utils.screenshot import initialize_screenshot_utility
from src.utils.backend_integration import initialize_backend_integration, connect_to_backend
from src.utils.game_args import parse_game_args, GameMode, GameArgs
from src.core.save_manager import SaveManager
from src.core.system_manager import SystemManager
from src.core.plugins.idle_plugin import IdlePlugin
from src.core.plugins.prestige_plugin import PrestigeSystem
from src.core.plugins.achievement_plugin import AchievementSystem
from src.core.plugins.burnout_plugin import BurnoutPlugin
from src.core.plugins.relationships_plugin import RelationshipsPlugin
from src.core.plugins.dopamine_plugin import DopaminePlugin
from src.core.plugins.equipment_plugin import EquipmentPlugin
from src.core.plugins.ability_plugin import AbilityPlugin
from src.core.plugins.passive_income_plugin import PassiveIncomePlugin


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
                self.logger.error("[GAME] Failed to initialize game", exception=e, 
                                mode=self.args.mode.value if hasattr(self.args.mode, 'value') else str(self.args.mode))
                return False
    
    def _initialize_menu(self) -> bool:
        """Initialize the main menu.
        
        Returns:
            True if menu initialized successfully
        """
        with self.logger.operation("Main Menu Initialization"):
            try:
                # Initialize Pygame if not already done
                if not pygame.get_init():
                    self.logger.debug("[GAME] Initializing Pygame...")
                    pygame.init()
                    self.logger.debug("[GAME] Pygame initialized")
                else:
                    self.logger.debug("[GAME] Pygame already initialized")
                
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
            
            self.logger.logger.info(f"[GAME] Loading game from slot {slot}...")
            
            # Load game state
            self.game_state = self.save_manager.load_game(slot)
            
            # Initialize UI and systems with loaded state
            return self._initialize_game_systems()
            
        except FileNotFoundError:
            self.logger.logger.error("[GAME] Save file not found")
            # Fall back to new game
            self.logger.logger.info("[GAME] Starting new game instead...")
            return self._initialize_new_game()
        except Exception as e:
            self.logger.logger.error(f"[GAME] Failed to load save: {e}")
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
                return self._initialize_game_systems()
                
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
            self.logger.logger.info("[GAME] Loading game configuration for tutorial...")
            game_data = load_game_data()

            # Initialize game state with tutorial-specific settings
            self.logger.logger.info("[GAME] Initializing tutorial game state...")
            self.game_state = GameState()
            
            # Mark this as a tutorial session
            # This allows the game to show tutorial-specific UI and guidance
            if not hasattr(self.game_state, 'is_tutorial'):
                self.game_state.is_tutorial = True
            else:
                self.game_state.is_tutorial = True
            
            self.logger.logger.info("[GAME] Tutorial mode enabled")
            
            # Initialize UI and systems
            return self._initialize_game_systems()
            
        except Exception as e:
            self.logger.logger.error(f"[GAME] Failed to initialize tutorial: {e}")
            return False
    
    def _initialize_game_systems(self) -> bool:
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
                
                # Initialize UI
                with self.logger.operation("UI Initialization"):
                    self.logger.debug("[GAME] Creating GameUI instance...")
                    self.ui = GameUI(self.game_state)
                    self.logger.info("[GAME] User interface initialized successfully")

                # Initialize plugin architecture (SystemManager)
                with self.logger.operation("Plugin Architecture Initialization"):
                    self.logger.debug("[GAME] Creating SystemManager...")
                    self.system_manager = SystemManager()
                    self.logger.info("[GAME] Plugin architecture initialized")
                
                # Register game systems as plugins
                with self.logger.operation("Plugin Registration"):
                    plugins = [
                        ("IdlePlugin", IdlePlugin()),
                        ("PrestigeSystem", PrestigeSystem()),
                        ("AchievementSystem", AchievementSystem()),
                        ("BurnoutPlugin", BurnoutPlugin()),
                        ("RelationshipsPlugin", RelationshipsPlugin()),
                        ("DopaminePlugin", DopaminePlugin()),
                        ("EquipmentPlugin", EquipmentPlugin()),
                        ("AbilityPlugin", AbilityPlugin()),
                        ("PassiveIncomePlugin", PassiveIncomePlugin()),
                    ]
                    
                    for plugin_name, plugin_instance in plugins:
                        self.logger.debug(f"[SYSTEM] Registering {plugin_name}...")
                        self.system_manager.register_system(plugin_instance)
                    
                    self.logger.info(f"[SYSTEM] Registered {len(plugins)} game systems")
                
                # Initialize all registered systems
                with self.logger.operation("Systems Initialization"):
                    self.logger.debug("[SYSTEM] Initializing all registered systems...")
                    self.system_manager.initialize_all(self.game_state)
                    self.logger.info("[SYSTEM] All systems initialized successfully")

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
            self.logger.logger.error("[GAME] Game initialization failed. Exiting.")
            sys.exit(1)

        self.logger.logger.info("[GAME] Starting main game loop...")

        try:
            while self.running:
                current_time = time.time()
                delta_time = current_time - self.last_update

                # Limit frame rate
                if delta_time < self.frame_time:
                    time.sleep(self.frame_time - delta_time)
                    continue

                self.last_update = current_time

                # Handle events
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT:
                        self.running = False
                        break

                # Handle menu or game
                if self.in_menu:
                    self._run_menu(events, delta_time)
                else:
                    self._run_game(events, delta_time)

        except KeyboardInterrupt:
            self.logger.logger.info("[GAME] Game interrupted by user")
        except Exception as e:
            import traceback
            self.logger.logger.error(f"[GAME] Unexpected error in game loop: {e}")
            self.logger.logger.error(f"[GAME] Traceback:\n{traceback.format_exc()}")
        finally:
            self.shutdown()
    
    def _run_menu(self, events, delta_time: float) -> None:
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
            self.logger.logger.info("[GAME] Starting new game from menu...")
            if self._initialize_new_game():
                self.in_menu = False
        elif action == MenuAction.CONTINUE:
            self.logger.logger.info("[GAME] Continuing game from menu...")
            if self._initialize_from_save():
                self.in_menu = False
        elif action == MenuAction.TUTORIAL:
            self.logger.logger.info("[GAME] Starting tutorial from menu...")
            if self._initialize_tutorial():
                self.in_menu = False
        elif action == MenuAction.SETTINGS:
            self.main_menu.show_settings_menu()
        
        # Update and render menu
        self.main_menu.update(delta_time)
        self.main_menu.render()
    
    def _run_game(self, events, delta_time: float) -> None:
        """Run the game loop.
        
        Args:
            events: Pygame events
            delta_time: Time since last update
        """
        # Validate critical objects exist before using them
        if not self.game_state:
            self.logger.logger.error("[GAME] game_state is None in _run_game!")
            self.running = False
            return
        
        if not self.ui:
            self.logger.logger.error("[GAME] ui is None in _run_game!")
            self.running = False
            return
        
        # Update game state and plugins
        self.game_state.update(delta_time)
        
        # Update all registered plugins/systems
        if self.system_manager:
            self.system_manager.update_all(self.game_state, delta_time)

        # Update UI
        actions = self.ui.handle_input(events)
        self.ui.update(delta_time)

        # Process any game actions from UI
        for action in actions:
            self._handle_game_action(action)

        # Update development systems
        if self.screenshot_utility:
            self.screenshot_utility.update(delta_time)

        # Update backend integration
        # Backend integration runs in background thread, no per-frame update needed

        # Render
        if self.ui:
            self.ui.render()

        pygame.display.flip()

    def _handle_game_action(self, action) -> None:
        """Handle game actions from the UI.

        Args:
            action: The action to process
        """
        # This will be expanded as we implement more UI interactions
        # For now, just log the action
        self.logger.logger.debug(f"[GAME] Processing action: {action}")

    def shutdown(self) -> None:
        """Clean shutdown of all systems."""
        self.logger.logger.info("[GAME] Shutting down...")
        
        # Auto-save before shutdown (if we have a game state)
        if self.game_state and self.save_manager and not self.in_menu:
            try:
                self.logger.logger.info("[GAME] Auto-saving game...")
                self.save_manager.auto_save(self.game_state)
            except Exception as e:
                self.logger.logger.error(f"[GAME] Auto-save failed: {e}")

        # Shutdown plugins/systems first
        if self.system_manager and self.game_state:
            self.logger.logger.info("[GAME] Shutting down all game systems...")
            self.system_manager.shutdown_all(self.game_state)

        if self.backend_integration:
            self.backend_integration.disconnect()
        
        if self.main_menu:
            self.main_menu.shutdown()

        if self.ui:
            self.ui.shutdown()

        pygame.quit()
        self.logger.logger.info("[GAME] Game shutdown complete")


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
            logger.info("[GAME] Arguments parsed", mode=args.mode.value if hasattr(args.mode, 'value') else str(args.mode))
        
        # Initialize Pygame
        with logger.operation("Pygame Initialization"):
            pygame.init()
            pygame.display.set_caption("Cybersecurity Firm - Idle/Tycoon/RPG")
            logger.info("[GAME] Pygame initialized successfully")

        # Create and run game
        logger.info("[GAME] Creating game instance...")
        game = Game(args)
        
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
