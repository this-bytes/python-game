"""Tests for the game argument system."""

import pytest
from src.utils.game_args import GameArgs, GameMode, parse_game_args
import sys


class TestGameArgs:
    """Tests for GameArgs class."""
    
    def test_initialization_default(self):
        """Test default GameArgs initialization."""
        args = GameArgs()
        assert args.mode == GameMode.MENU
        assert args.save_slot is None
        assert args.debug is False
        assert args.headless is False
        assert args.skip_intro is False
    
    def test_initialization_with_values(self):
        """Test GameArgs initialization with custom values."""
        args = GameArgs(
            mode=GameMode.CONTINUE,
            save_slot=5,
            debug=True,
            headless=True,
            skip_intro=True
        )
        assert args.mode == GameMode.CONTINUE
        assert args.save_slot == 5
        assert args.debug is True
        assert args.headless is True
        assert args.skip_intro is True
    
    def test_should_show_menu(self):
        """Test should_show_menu() method."""
        args_menu = GameArgs(mode=GameMode.MENU)
        args_new = GameArgs(mode=GameMode.NEW_GAME)
        args_continue = GameArgs(mode=GameMode.CONTINUE)
        
        assert args_menu.should_show_menu() is True
        assert args_new.should_show_menu() is False
        assert args_continue.should_show_menu() is False
    
    def test_should_load_game(self):
        """Test should_load_game() method."""
        args_menu = GameArgs(mode=GameMode.MENU)
        args_continue = GameArgs(mode=GameMode.CONTINUE)
        args_load = GameArgs(mode=GameMode.LOAD_SLOT, save_slot=3)
        args_new = GameArgs(mode=GameMode.NEW_GAME)
        
        assert args_menu.should_load_game() is False
        assert args_continue.should_load_game() is True
        assert args_load.should_load_game() is True
        assert args_new.should_load_game() is False
    
    def test_should_start_new_game(self):
        """Test should_start_new_game() method."""
        args_new = GameArgs(mode=GameMode.NEW_GAME)
        args_menu = GameArgs(mode=GameMode.MENU)
        args_continue = GameArgs(mode=GameMode.CONTINUE)
        
        assert args_new.should_start_new_game() is True
        assert args_menu.should_start_new_game() is False
        assert args_continue.should_start_new_game() is False


class TestParseGameArgs:
    """Tests for parse_game_args function."""
    
    def test_parse_default(self, monkeypatch):
        """Test parsing with no arguments (defaults to menu)."""
        monkeypatch.setattr(sys, 'argv', ['main.py'])
        args = parse_game_args()
        
        assert args.mode == GameMode.MENU
        assert args.save_slot is None
        assert args.debug is False
    
    def test_parse_menu_flag(self, monkeypatch):
        """Test parsing with --menu flag."""
        monkeypatch.setattr(sys, 'argv', ['main.py', '--menu'])
        args = parse_game_args()
        
        assert args.mode == GameMode.MENU
    
    def test_parse_new_game(self, monkeypatch):
        """Test parsing with --new-game flag."""
        monkeypatch.setattr(sys, 'argv', ['main.py', '--new-game'])
        args = parse_game_args()
        
        assert args.mode == GameMode.NEW_GAME
        assert args.should_start_new_game() is True
    
    def test_parse_continue(self, monkeypatch):
        """Test parsing with --continue flag."""
        monkeypatch.setattr(sys, 'argv', ['main.py', '--continue'])
        args = parse_game_args()
        
        assert args.mode == GameMode.CONTINUE
        assert args.should_load_game() is True
    
    def test_parse_load_slot(self, monkeypatch):
        """Test parsing with --load-slot flag."""
        monkeypatch.setattr(sys, 'argv', ['main.py', '--load-slot', '5'])
        args = parse_game_args()
        
        assert args.mode == GameMode.LOAD_SLOT
        assert args.save_slot == 5
        assert args.should_load_game() is True
    
    def test_parse_debug_flag(self, monkeypatch):
        """Test parsing with --debug flag."""
        monkeypatch.setattr(sys, 'argv', ['main.py', '--debug'])
        args = parse_game_args()
        
        assert args.debug is True
    
    def test_parse_headless_flag(self, monkeypatch):
        """Test parsing with --headless flag."""
        monkeypatch.setattr(sys, 'argv', ['main.py', '--headless'])
        args = parse_game_args()
        
        assert args.headless is True
    
    def test_parse_skip_intro_flag(self, monkeypatch):
        """Test parsing with --skip-intro flag."""
        monkeypatch.setattr(sys, 'argv', ['main.py', '--skip-intro'])
        args = parse_game_args()
        
        assert args.skip_intro is True
    
    def test_parse_combined_flags(self, monkeypatch):
        """Test parsing with multiple flags combined."""
        monkeypatch.setattr(sys, 'argv', ['main.py', '--new-game', '--debug', '--skip-intro'])
        args = parse_game_args()
        
        assert args.mode == GameMode.NEW_GAME
        assert args.debug is True
        assert args.skip_intro is True
    
    def test_parse_invalid_slot_negative(self, monkeypatch):
        """Test parsing with invalid negative slot number."""
        monkeypatch.setattr(sys, 'argv', ['main.py', '--load-slot', '-1'])
        
        with pytest.raises(SystemExit):
            parse_game_args()
    
    def test_parse_invalid_slot_too_high(self, monkeypatch):
        """Test parsing with slot number that's too high."""
        monkeypatch.setattr(sys, 'argv', ['main.py', '--load-slot', '10'])
        
        with pytest.raises(SystemExit):
            parse_game_args()
    
    def test_mode_flags_mutually_exclusive(self, monkeypatch):
        """Test that mode flags are mutually exclusive."""
        monkeypatch.setattr(sys, 'argv', ['main.py', '--new-game', '--continue'])
        
        with pytest.raises(SystemExit):
            parse_game_args()


class TestGameModeEnum:
    """Tests for GameMode enum."""
    
    def test_game_mode_values(self):
        """Test that GameMode enum has expected values."""
        assert GameMode.MENU.value == "menu"
        assert GameMode.NEW_GAME.value == "new_game"
        assert GameMode.CONTINUE.value == "continue"
        assert GameMode.LOAD_SLOT.value == "load_slot"
    
    def test_game_mode_unique(self):
        """Test that all GameMode values are unique."""
        values = [mode.value for mode in GameMode]
        assert len(values) == len(set(values))
