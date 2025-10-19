"""Extensible argument and parameter system for game startup modes.

This module provides command-line argument parsing and game mode configuration
for flexible game initialization.
"""

import argparse
from typing import Optional
from enum import Enum


class GameMode(Enum):
    """Available game startup modes."""
    MENU = "menu"  # Show main menu (default)
    NEW_GAME = "new_game"  # Start new game directly
    CONTINUE = "continue"  # Continue from most recent save
    LOAD_SLOT = "load_slot"  # Load from specific save slot
    TUTORIAL = "tutorial"  # Start tutorial mode


class GameArgs:
    """Parsed game arguments and configuration.
    
    This class encapsulates all startup configuration for the game,
    making it easy to extend with new modes and parameters.
    """
    
    def __init__(
        self,
        mode: GameMode = GameMode.MENU,
        save_slot: Optional[int] = None,
        debug: bool = False,
        headless: bool = False,
        skip_intro: bool = False,
        local_server: bool = False,
        remote_host: Optional[str] = None,
        server_port: int = 5001,
        no_server: bool = False,
        admin_token: Optional[str] = None
    ):
        """Initialize game arguments.
        
        Args:
            mode: Game startup mode
            save_slot: Save slot number for loading (if applicable)
            debug: Enable debug mode
            headless: Run without UI (for testing/backend only)
            skip_intro: Skip intro animations/screens
            local_server: Start local embedded backend server
            remote_host: Connect to remote backend server (hostname/IP)
            server_port: Backend server port (default: 5001)
            no_server: Disable all backend integration
            admin_token: Authentication token for admin operations
        """
        self.mode = mode
        self.save_slot = save_slot
        self.debug = debug
        self.headless = headless
        self.skip_intro = skip_intro
        
        # Backend configuration
        self.local_server = local_server
        self.remote_host = remote_host
        self.server_port = server_port
        self.no_server = no_server
        self.admin_token = admin_token
        
        # Validate backend mode consistency
        if self.local_server and self.remote_host:
            raise ValueError("Cannot use both --local-server and --remote-host simultaneously")
        if self.no_server and (self.local_server or self.remote_host):
            raise ValueError("Cannot use --no-server with --local-server or --remote-host")
    
    def should_show_menu(self) -> bool:
        """Check if main menu should be displayed.
        
        Returns:
            True if menu should be shown
        """
        return self.mode == GameMode.MENU
    
    def should_load_game(self) -> bool:
        """Check if a saved game should be loaded.
        
        Returns:
            True if game should load from save
        """
        return self.mode in (GameMode.CONTINUE, GameMode.LOAD_SLOT)
    
    def should_start_new_game(self) -> bool:
        """Check if a new game should be started.
        
        Returns:
            True if new game should start
        """
        return self.mode == GameMode.NEW_GAME
    
    def should_use_backend(self) -> bool:
        """Check if backend integration should be enabled.
        
        Returns:
            True if backend should be used (local or remote)
        """
        return not self.no_server
    
    def get_backend_mode(self) -> str:
        """Get backend integration mode.
        
        Returns:
            "local" for embedded server, "remote" for remote connection, "none" for disabled
        """
        if self.no_server:
            return "none"
        elif self.local_server:
            return "local"
        elif self.remote_host:
            return "remote"
        else:
            # Default: no backend (can be changed to local if desired)
            return "none"
    
    def get_backend_url(self) -> Optional[str]:
        """Get backend server URL.
        
        Returns:
            Backend URL or None if backend disabled
        """
        if self.no_server:
            return None
        
        if self.remote_host:
            return f"http://{self.remote_host}:{self.server_port}"
        elif self.local_server:
            return f"http://localhost:{self.server_port}"
        
        return None


def parse_game_args() -> GameArgs:
    """Parse command-line arguments for game startup.
    
    Returns:
        GameArgs instance with parsed configuration
    """
    parser = argparse.ArgumentParser(
        description="Cybersecurity Firm Idle/Tycoon/RPG Game",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/main.py                    # Show main menu (default)
  python src/main.py --continue         # Continue from last save
  python src/main.py --new-game         # Start new game directly
  python src/main.py --tutorial         # Start tutorial mode
  python src/main.py --load-slot 3      # Load from save slot 3
  python src/main.py --debug            # Enable debug mode
        """
    )
    
    # Mode selection (mutually exclusive)
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--menu",
        action="store_true",
        help="Show main menu (default)"
    )
    mode_group.add_argument(
        "--new-game",
        action="store_true",
        help="Start a new game directly"
    )
    mode_group.add_argument(
        "--continue",
        action="store_true",
        dest="continue_game",
        help="Continue from most recent save"
    )
    mode_group.add_argument(
        "--load-slot",
        type=int,
        metavar="SLOT",
        help="Load game from specific save slot (0-9)"
    )
    mode_group.add_argument(
        "--tutorial",
        action="store_true",
        help="Start tutorial mode for new players"
    )
    
    # Additional options
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with additional logging"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run without UI (for testing/backend only)"
    )
    parser.add_argument(
        "--skip-intro",
        action="store_true",
        help="Skip intro animations and screens"
    )
    
    # Backend configuration
    backend_group = parser.add_argument_group('Backend Configuration')
    backend_mode = backend_group.add_mutually_exclusive_group()
    
    backend_mode.add_argument(
        "--local-server",
        action="store_true",
        help="Start local embedded backend server (enables admin panel)"
    )
    
    backend_mode.add_argument(
        "--remote-host",
        type=str,
        metavar="HOST",
        help="Connect to remote backend server (e.g., '192.168.1.100' or 'game-server.local')"
    )
    
    backend_mode.add_argument(
        "--no-server",
        action="store_true",
        help="Disable backend integration (standalone mode, no admin panel)"
    )
    
    backend_group.add_argument(
        "--server-port",
        type=int,
        default=5001,
        metavar="PORT",
        help="Backend server port (default: 5001)"
    )
    
    backend_group.add_argument(
        "--admin-token",
        type=str,
        metavar="TOKEN",
        help="Authentication token for admin operations"
    )
    
    args = parser.parse_args()
    
    # Determine mode
    mode = GameMode.MENU  # Default
    save_slot = None
    
    if args.new_game:
        mode = GameMode.NEW_GAME
    elif args.continue_game:
        mode = GameMode.CONTINUE
    elif args.load_slot is not None:
        mode = GameMode.LOAD_SLOT
        save_slot = args.load_slot
        # Validate slot number
        if save_slot < 0 or save_slot >= 10:
            parser.error("Save slot must be between 0 and 9")
    elif args.tutorial:
        mode = GameMode.TUTORIAL
    elif args.menu:
        mode = GameMode.MENU
    
    return GameArgs(
        mode=mode,
        save_slot=save_slot,
        debug=args.debug,
        headless=args.headless,
        skip_intro=args.skip_intro,
        local_server=args.local_server,
        remote_host=args.remote_host,
        server_port=args.server_port,
        no_server=args.no_server,
        admin_token=args.admin_token
    )
