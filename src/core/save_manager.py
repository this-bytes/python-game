"""Save/Load System for game state persistence.

This module manages saving and loading game state to/from JSON files,
including metadata, version compatibility, and auto-save functionality.
"""

import os
import json
import time
from typing import Dict, List, Any, Optional, TYPE_CHECKING
from datetime import datetime
from pathlib import Path

from src.utils.logger import GameLogger

if TYPE_CHECKING:
    from src.models.game_state import GameState


class SaveManager:
    """Manages game state persistence through save/load operations.
    
    This class handles serialization of game state to JSON files,
    with support for multiple save slots, auto-save, and version tracking.
    """
    
    GAME_VERSION = "0.2.0"
    MAX_SAVE_SLOTS = 10
    AUTO_SAVE_SLOT = 0
    
    # Class-level annotations for static analysis
    _logger: GameLogger
    _save_dir: str

    def __init__(self, save_dir: Optional[str] = None, logger: Optional[GameLogger] = None):
        """Initialize the save manager.
        
        Args:
            save_dir: Directory for save files (defaults to data/saves/)
            logger: Optional logger for save/load events
        """
        self._logger = logger or GameLogger("save_manager")
        
        # Determine save directory
        if save_dir:
            self._save_dir = save_dir
        else:
            # Allow override via environment variable
            env_save_dir = os.environ.get("SAVE_DIR")
            if env_save_dir:
                self._save_dir = env_save_dir
            else:
                # Find project root relative to this file
                project_root = Path(__file__).parent.parent
                self._save_dir = str(project_root / "data" / "saves")
        
        # Ensure save directory exists
        os.makedirs(self._save_dir, exist_ok=True)
        
        self._logger.info(f"[SAVE_MANAGER] Initialized with save directory: {self._save_dir}")
    
    def save_game(self, game_state: 'GameState', slot: int) -> str:
        """Save game state to a specific slot.
        
        Args:
            game_state: Current game state to save
            slot: Save slot number (0 for auto-save)
            
        Returns:
            Path to saved file
        """
        if slot < 0 or slot >= self.MAX_SAVE_SLOTS:
            raise ValueError(f"Save slot must be between 0 and {self.MAX_SAVE_SLOTS - 1}")
        
        filepath = self._get_save_filepath(slot)
        
        try:
            # Create save data structure
            save_data = {
                "metadata": {
                    "save_time": time.time(),
                    "save_time_formatted": datetime.now().isoformat(),
                    "game_version": self.GAME_VERSION,
                    "slot": slot,
                    "playtime_seconds": game_state.get_game_time_elapsed(),
                    "money": game_state.current_money,
                    "specialist_count": len(game_state.specialists),
                    "prestige_level": getattr(game_state, 'total_prestiges', 0)
                },
                "game_state": game_state.to_dict()
            }
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            self._logger.info(
                f"[SAVE_MANAGER] Game saved to slot {slot}: {filepath}"
            )
            
            return filepath
            
        except Exception as e:
            self._logger.error(f"[SAVE_MANAGER] Failed to save game: {e}")
            raise
    
    def load_game(self, slot: int) -> 'GameState':
        """Load game state from a specific slot.
        
        Args:
            slot: Save slot number
            
        Returns:
            Loaded GameState instance
        """
        if slot < 0 or slot >= self.MAX_SAVE_SLOTS:
            raise ValueError(f"Save slot must be between 0 and {self.MAX_SAVE_SLOTS - 1}")
        
        filepath = self._get_save_filepath(slot)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Save file not found: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Check version compatibility
            metadata = save_data.get("metadata", {})
            saved_version = metadata.get("game_version", "unknown")
            
            if saved_version != self.GAME_VERSION:
                self._logger.warning(
                    f"[SAVE_MANAGER] Loading save from different version: {saved_version} -> {self.GAME_VERSION}"
                )
            
            # Load game state
            from src.models.game_state import GameState
            game_state = GameState.from_dict(save_data["game_state"])
            
            self._logger.info(
                f"[SAVE_MANAGER] Game loaded from slot {slot}: {filepath}"
            )
            
            return game_state
            
        except Exception as e:
            self._logger.error(f"[SAVE_MANAGER] Failed to load game: {e}")
            raise
    
    def list_saves(self) -> List[Dict[str, Any]]:
        """List all save files with metadata.
        
        Returns:
            List of save file information dictionaries
        """
        saves = []
        
        for slot in range(self.MAX_SAVE_SLOTS):
            filepath = self._get_save_filepath(slot)
            
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        save_data = json.load(f)
                    
                    metadata = save_data.get("metadata", {})
                    saves.append({
                        "slot": slot,
                        "filepath": filepath,
                        "exists": True,
                        "metadata": metadata
                    })
                except Exception as e:
                    self._logger.error(
                        f"[SAVE_MANAGER] Failed to read save slot {slot}: {e}"
                    )
                    saves.append({
                        "slot": slot,
                        "filepath": filepath,
                        "exists": True,
                        "error": str(e)
                    })
            else:
                saves.append({
                    "slot": slot,
                    "filepath": filepath,
                    "exists": False
                })
        
        return saves
    
    def delete_save(self, slot: int) -> bool:
        """Delete a save file.
        
        Args:
            slot: Save slot number
            
        Returns:
            True if deleted successfully
        """
        if slot < 0 or slot >= self.MAX_SAVE_SLOTS:
            raise ValueError(f"Save slot must be between 0 and {self.MAX_SAVE_SLOTS - 1}")
        
        filepath = self._get_save_filepath(slot)
        
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                self._logger.info(f"[SAVE_MANAGER] Deleted save slot {slot}")
                return True
            except Exception as e:
                self._logger.error(f"[SAVE_MANAGER] Failed to delete save: {e}")
                raise
        else:
            return False
    
    def auto_save(self, game_state: 'GameState') -> str:
        """Auto-save to slot 0.
        
        Args:
            game_state: Current game state
            
        Returns:
            Path to saved file
        """
        return self.save_game(game_state, self.AUTO_SAVE_SLOT)
    
    def export_save(self, slot: int, export_path: str) -> str:
        """Export a save file to a custom location.
        
        Args:
            slot: Source save slot
            export_path: Destination file path
            
        Returns:
            Path to exported file
        """
        filepath = self._get_save_filepath(slot)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Save file not found: {filepath}")
        
        try:
            # Read save data
            with open(filepath, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Write to export location
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            self._logger.info(
                f"[SAVE_MANAGER] Exported save from slot {slot} to {export_path}"
            )
            
            return export_path
            
        except Exception as e:
            self._logger.error(f"[SAVE_MANAGER] Failed to export save: {e}")
            raise
    
    def import_save(self, import_path: str, slot: int) -> str:
        """Import a save file from a custom location.
        
        Args:
            import_path: Source file path
            slot: Destination save slot
            
        Returns:
            Path to imported file
        """
        if not os.path.exists(import_path):
            raise FileNotFoundError(f"Import file not found: {import_path}")
        
        if slot < 0 or slot >= self.MAX_SAVE_SLOTS:
            raise ValueError(f"Save slot must be between 0 and {self.MAX_SAVE_SLOTS - 1}")
        
        try:
            # Read import data
            with open(import_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Validate structure
            if "metadata" not in save_data or "game_state" not in save_data:
                raise ValueError("Invalid save file format")
            
            # Write to save slot
            filepath = self._get_save_filepath(slot)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            self._logger.info(
                f"[SAVE_MANAGER] Imported save from {import_path} to slot {slot}"
            )
            
            return filepath
            
        except Exception as e:
            self._logger.error(f"[SAVE_MANAGER] Failed to import save: {e}")
            raise
    
    def _get_save_filepath(self, slot: int) -> str:
        """Get filepath for a save slot.
        
        Args:
            slot: Save slot number
            
        Returns:
            Full path to save file
        """
        filename = f"slot_{slot}.json"
        return os.path.join(self._save_dir, filename)
    
    def get_save_directory(self) -> str:
        """Get the save directory path.
        
        Returns:
            Path to save directory
        """
        return self._save_dir
