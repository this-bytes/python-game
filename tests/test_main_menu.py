"""Tests for the main menu UI component."""

import pytest
import pygame
from unittest.mock import MagicMock, patch
from src.ui.main_menu import MainMenu, MenuAction


@pytest.fixture
def mock_pygame():
    """Mock pygame initialization."""
    with patch('pygame.init'):
        with patch('pygame.display.set_mode') as mock_display:
            mock_surface = MagicMock()
            mock_display.return_value = mock_surface
            with patch('pygame.font.SysFont') as mock_font:
                mock_font.return_value = MagicMock()
                yield mock_surface


class TestMainMenu:
    """Tests for MainMenu class."""
    
    def test_initialization(self, mock_pygame):
        """Test MainMenu initialization."""
        menu = MainMenu()
        
        assert menu.width == 1280
        assert menu.height == 720
        assert menu.selected_action is None
        assert menu.continue_available is False
        assert len(menu.buttons) == 4
    
    def test_initialization_custom_size(self, mock_pygame):
        """Test MainMenu initialization with custom size."""
        menu = MainMenu(width=1920, height=1080)
        
        assert menu.width == 1920
        assert menu.height == 1080
    
    def test_set_continue_available(self, mock_pygame):
        """Test setting continue availability."""
        menu = MainMenu()
        
        # Initially should be unavailable
        assert menu.continue_available is False
        assert menu.continue_button.enabled is False
        
        # Enable continue
        menu.set_continue_available(True)
        assert menu.continue_available is True
        assert menu.continue_button.enabled is True
        
        # Disable continue
        menu.set_continue_available(False)
        assert menu.continue_available is False
        assert menu.continue_button.enabled is False
    
    def test_handle_input_quit_event(self, mock_pygame):
        """Test handling pygame QUIT event."""
        menu = MainMenu()
        
        quit_event = pygame.event.Event(pygame.QUIT)
        action = menu.handle_input([quit_event])
        
        assert action == MenuAction.EXIT
    
    def test_handle_input_escape_key(self, mock_pygame):
        """Test handling ESC key press."""
        menu = MainMenu()
        
        escape_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        action = menu.handle_input([escape_event])
        
        assert action == MenuAction.EXIT
    
    def test_handle_input_enter_new_game(self, mock_pygame):
        """Test handling ENTER key when continue unavailable."""
        menu = MainMenu()
        menu.set_continue_available(False)
        
        enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        action = menu.handle_input([enter_event])
        
        assert action == MenuAction.NEW_GAME
    
    def test_handle_input_enter_continue(self, mock_pygame):
        """Test handling ENTER key when continue available."""
        menu = MainMenu()
        menu.set_continue_available(True)
        
        enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        action = menu.handle_input([enter_event])
        
        assert action == MenuAction.CONTINUE
    
    def test_handle_input_no_events(self, mock_pygame):
        """Test handling empty event list."""
        menu = MainMenu()
        
        action = menu.handle_input([])
        
        assert action is None
    
    def test_update(self, mock_pygame):
        """Test menu update logic."""
        menu = MainMenu()
        
        initial_offset = menu.pulse_offset
        menu.update(0.1)
        
        # Pulse offset should have changed
        assert menu.pulse_offset != initial_offset
    
    def test_shutdown(self, mock_pygame):
        """Test menu shutdown."""
        menu = MainMenu()
        
        # Should not raise any exceptions
        menu.shutdown()


class TestMenuAction:
    """Tests for MenuAction enum."""
    
    def test_menu_action_values(self):
        """Test MenuAction enum values."""
        assert MenuAction.NEW_GAME.value == "new_game"
        assert MenuAction.CONTINUE.value == "continue"
        assert MenuAction.SETTINGS.value == "settings"
        assert MenuAction.EXIT.value == "exit"
        assert MenuAction.LOAD_SLOT.value == "load_slot"
    
    def test_menu_action_unique(self):
        """Test that all MenuAction values are unique."""
        values = [action.value for action in MenuAction]
        assert len(values) == len(set(values))
