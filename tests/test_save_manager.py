"""Tests for the SaveManager system."""

import pytest
import os
import json
import tempfile
import shutil
from src.core.save_manager import SaveManager
from src.models.game_state import GameState


class TestSaveManager:
    """Tests for SaveManager class."""
    
    @pytest.fixture
    def temp_save_dir(self):
        """Create temporary save directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def save_manager(self, temp_save_dir):
        """Create SaveManager with temporary directory."""
        return SaveManager(save_dir=temp_save_dir)
    
    @pytest.fixture
    def sample_game_state(self):
        """Create a sample game state for testing."""
        # Create a minimal game state
        game_state = GameState()
        game_state.current_money = 10000.0
        game_state.total_money_earned = 25000.0
        return game_state
    
    def test_initialization(self, save_manager, temp_save_dir):
        """Test SaveManager initialization."""
        assert save_manager._save_dir == temp_save_dir
        assert os.path.exists(temp_save_dir)
    
    def test_save_game(self, save_manager, sample_game_state):
        """Test saving game state."""
        slot = 1
        filepath = save_manager.save_game(sample_game_state, slot)
        
        assert os.path.exists(filepath)
        assert "slot_1.json" in filepath
        
        # Verify file contents
        with open(filepath, 'r') as f:
            save_data = json.load(f)
        
        assert "metadata" in save_data
        assert "game_state" in save_data
        assert save_data["metadata"]["slot"] == slot
        assert save_data["metadata"]["money"] == 10000.0
    
    def test_save_game_invalid_slot(self, save_manager, sample_game_state):
        """Test saving with invalid slot number."""
        with pytest.raises(ValueError):
            save_manager.save_game(sample_game_state, -1)
        
        with pytest.raises(ValueError):
            save_manager.save_game(sample_game_state, 100)
    
    def test_load_game(self, save_manager, sample_game_state):
        """Test loading game state."""
        slot = 2
        
        # Save first
        save_manager.save_game(sample_game_state, slot)
        
        # Load
        loaded_state = save_manager.load_game(slot)
        
        assert loaded_state is not None
        assert loaded_state.current_money == sample_game_state.current_money
        assert loaded_state.total_money_earned == sample_game_state.total_money_earned
    
    def test_load_game_not_found(self, save_manager):
        """Test loading non-existent save."""
        with pytest.raises(FileNotFoundError):
            save_manager.load_game(5)
    
    def test_list_saves(self, save_manager, sample_game_state):
        """Test listing all saves."""
        # Initially empty
        saves = save_manager.list_saves()
        assert len(saves) == SaveManager.MAX_SAVE_SLOTS
        assert all(not s['exists'] for s in saves)
        
        # Save to slots 1 and 3
        save_manager.save_game(sample_game_state, 1)
        save_manager.save_game(sample_game_state, 3)
        
        # List again
        saves = save_manager.list_saves()
        assert saves[1]['exists'] is True
        assert saves[3]['exists'] is True
        assert saves[2]['exists'] is False
        
        # Check metadata
        assert 'metadata' in saves[1]
        assert saves[1]['metadata']['slot'] == 1
    
    def test_delete_save(self, save_manager, sample_game_state):
        """Test deleting a save file."""
        slot = 4
        
        # Save first
        save_manager.save_game(sample_game_state, slot)
        assert os.path.exists(save_manager._get_save_filepath(slot))
        
        # Delete
        result = save_manager.delete_save(slot)
        assert result is True
        assert not os.path.exists(save_manager._get_save_filepath(slot))
        
        # Delete non-existent
        result = save_manager.delete_save(slot)
        assert result is False
    
    def test_auto_save(self, save_manager, sample_game_state):
        """Test auto-save functionality."""
        filepath = save_manager.auto_save(sample_game_state)
        
        assert os.path.exists(filepath)
        assert "slot_0.json" in filepath
        
        # Verify it's in slot 0
        with open(filepath, 'r') as f:
            save_data = json.load(f)
        
        assert save_data["metadata"]["slot"] == 0
    
    def test_export_save(self, save_manager, sample_game_state, temp_save_dir):
        """Test exporting save to custom location."""
        slot = 1
        export_path = os.path.join(temp_save_dir, "export_test.json")
        
        # Save first
        save_manager.save_game(sample_game_state, slot)
        
        # Export
        result_path = save_manager.export_save(slot, export_path)
        
        assert os.path.exists(result_path)
        assert result_path == export_path
        
        # Verify contents match
        with open(export_path, 'r') as f:
            export_data = json.load(f)
        
        assert export_data["metadata"]["money"] == 10000.0
    
    def test_import_save(self, save_manager, sample_game_state, temp_save_dir):
        """Test importing save from custom location."""
        # Create a save file manually
        import_path = os.path.join(temp_save_dir, "import_test.json")
        
        save_data = {
            "metadata": {
                "save_time": 1234567890.0,
                "game_version": "0.2.0",
                "slot": 99,
                "money": 50000.0
            },
            "game_state": sample_game_state.to_dict()
        }
        
        with open(import_path, 'w') as f:
            json.dump(save_data, f)
        
        # Import to slot 5
        slot = 5
        result_path = save_manager.import_save(import_path, slot)
        
        assert os.path.exists(result_path)
        
        # Verify it can be loaded
        loaded_state = save_manager.load_game(slot)
        assert loaded_state.current_money == sample_game_state.current_money
    
    def test_import_invalid_file(self, save_manager, temp_save_dir):
        """Test importing invalid save file."""
        import_path = os.path.join(temp_save_dir, "invalid.json")
        
        # Create invalid file
        with open(import_path, 'w') as f:
            json.dump({"invalid": "data"}, f)
        
        with pytest.raises(ValueError):
            save_manager.import_save(import_path, 1)
    
    def test_save_load_round_trip(self, save_manager, sample_game_state):
        """Test complete save/load cycle preserves data."""
        slot = 7
        
        # Modify game state
        sample_game_state.current_money = 99999.99
        sample_game_state.prestige_points = 42
        sample_game_state.total_prestiges = 3
        
        # Save
        save_manager.save_game(sample_game_state, slot)
        
        # Load
        loaded_state = save_manager.load_game(slot)
        
        # Verify all key fields
        assert loaded_state.current_money == 99999.99
        assert loaded_state.prestige_points == 42
        assert loaded_state.total_prestiges == 3
        assert len(loaded_state.specialists) == len(sample_game_state.specialists)
        assert len(loaded_state.clients) == len(sample_game_state.clients)
    
    def test_get_save_directory(self, save_manager, temp_save_dir):
        """Test getting save directory path."""
        assert save_manager.get_save_directory() == temp_save_dir
    
    def test_save_with_metadata(self, save_manager, sample_game_state):
        """Test that save includes proper metadata."""
        slot = 1
        filepath = save_manager.save_game(sample_game_state, slot)
        
        with open(filepath, 'r') as f:
            save_data = json.load(f)
        
        metadata = save_data["metadata"]
        
        # Check all metadata fields exist
        assert "save_time" in metadata
        assert "save_time_formatted" in metadata
        assert "game_version" in metadata
        assert "slot" in metadata
        assert "playtime_seconds" in metadata
        assert "money" in metadata
        assert "specialist_count" in metadata
        assert "prestige_level" in metadata
        
        # Verify values
        assert metadata["game_version"] == SaveManager.GAME_VERSION
        assert metadata["slot"] == slot
        assert metadata["money"] == sample_game_state.current_money
        assert metadata["specialist_count"] == len(sample_game_state.specialists)
