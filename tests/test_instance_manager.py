"""Tests for GameInstance Manager (multi-client support).

Verifies that the backend can manage multiple game instances and route
admin panel actions to specific instances.
"""
import pytest
from datetime import datetime, timedelta
from backend.services.instance_manager import InstanceManager, GameInstance, instance_manager
from src.models.game_state import GameState
from src.models.specialist import Specialist, SpecialistStats


class TestGameInstance:
    """Test GameInstance class."""
    
    def test_game_instance_initialization(self):
        """Test GameInstance initializes correctly."""
        game_state = GameState()
        instance = GameInstance('test-id-123', game_state, 'Test Client')
        
        assert instance.instance_id == 'test-id-123'
        assert instance.game_state == game_state
        assert instance.client_name == 'Test Client'
        assert instance.connected is True
        assert instance.created_at is not None
    
    def test_game_instance_default_client_name(self):
        """Test GameInstance generates default client name."""
        instance = GameInstance('abc123def', None)
        assert instance.client_name == 'Client-abc123de'
    
    def test_game_instance_update_activity(self):
        """Test activity timestamp updates."""
        instance = GameInstance('test', None)
        original_time = instance.last_activity
        
        import time
        time.sleep(0.1)
        
        instance.update_activity()
        assert instance.last_activity > original_time
    
    def test_game_instance_to_dict(self):
        """Test GameInstance serialization to dict."""
        game_state = GameState()
        game_state.current_money = 10000
        game_state.specialists = []
        
        instance = GameInstance('test-123', game_state, 'Test')
        result = instance.to_dict()
        
        assert result['instance_id'] == 'test-123'
        assert result['client_name'] == 'Test'
        assert result['connected'] is True
        assert result['has_state'] is True
        assert 'state_summary' in result
        assert result['state_summary']['money'] == 10000


class TestInstanceManager:
    """Test InstanceManager class."""
    
    @pytest.fixture
    def manager(self):
        """Create fresh instance manager for each test."""
        return InstanceManager()
    
    def test_create_instance_with_auto_id(self, manager):
        """Test creating instance with auto-generated ID."""
        instance_id = manager.create_instance(client_name='Auto Test')
        
        assert instance_id is not None
        assert len(instance_id) > 0
        assert manager.get_instance(instance_id) is not None
    
    def test_create_instance_with_specific_id(self, manager):
        """Test creating instance with specific ID."""
        instance_id = manager.create_instance(
            instance_id='custom-id-123',
            client_name='Custom Client'
        )
        
        assert instance_id == 'custom-id-123'
        instance = manager.get_instance(instance_id)
        assert instance is not None
        assert instance.client_name == 'Custom Client'
    
    def test_create_instance_with_game_state(self, manager):
        """Test creating instance with GameState."""
        game_state = GameState()
        game_state.current_money = 5000
        
        instance_id = manager.create_instance(game_state=game_state)
        
        retrieved_state = manager.get_game_state(instance_id)
        assert retrieved_state is not None
        assert retrieved_state.current_money == 5000
    
    def test_first_instance_becomes_default(self, manager):
        """Test that first instance is set as default."""
        instance_id = manager.create_instance(client_name='First')
        
        assert manager.get_default_instance_id() == instance_id
        
        # Get instance without ID should return default
        instance = manager.get_instance()
        assert instance.instance_id == instance_id
    
    def test_multiple_instances(self, manager):
        """Test managing multiple instances."""
        id1 = manager.create_instance(client_name='Client 1')
        id2 = manager.create_instance(client_name='Client 2')
        id3 = manager.create_instance(client_name='Client 3')
        
        instances = manager.list_instances()
        assert len(instances) == 3
        
        # Verify each instance is separate
        assert manager.get_instance(id1).client_name == 'Client 1'
        assert manager.get_instance(id2).client_name == 'Client 2'
        assert manager.get_instance(id3).client_name == 'Client 3'
    
    def test_update_game_state(self, manager):
        """Test updating game state for an instance."""
        instance_id = manager.create_instance(client_name='Test')
        
        game_state = GameState()
        game_state.current_money = 15000
        
        result = manager.update_game_state(game_state, instance_id)
        assert result is True
        
        retrieved = manager.get_game_state(instance_id)
        assert retrieved.current_money == 15000
    
    def test_update_game_state_invalid_instance(self, manager):
        """Test updating non-existent instance fails."""
        game_state = GameState()
        result = manager.update_game_state(game_state, 'nonexistent')
        assert result is False
    
    def test_remove_instance(self, manager):
        """Test removing an instance."""
        instance_id = manager.create_instance(client_name='To Remove')
        
        assert manager.get_instance(instance_id) is not None
        
        result = manager.remove_instance(instance_id)
        assert result is True
        
        assert manager.get_instance(instance_id) is None
    
    def test_remove_default_instance_updates_default(self, manager):
        """Test removing default instance sets new default."""
        id1 = manager.create_instance(client_name='First')
        id2 = manager.create_instance(client_name='Second')
        
        assert manager.get_default_instance_id() == id1
        
        manager.remove_instance(id1)
        
        # Default should now be id2
        assert manager.get_default_instance_id() == id2
    
    def test_set_default_instance(self, manager):
        """Test manually setting default instance."""
        id1 = manager.create_instance(client_name='First')
        id2 = manager.create_instance(client_name='Second')
        
        assert manager.get_default_instance_id() == id1
        
        result = manager.set_default_instance(id2)
        assert result is True
        assert manager.get_default_instance_id() == id2
    
    def test_set_default_instance_invalid_id(self, manager):
        """Test setting invalid instance as default fails."""
        result = manager.set_default_instance('nonexistent')
        assert result is False
    
    def test_list_instances(self, manager):
        """Test listing all instances."""
        manager.create_instance(instance_id='id1', client_name='Client 1')
        manager.create_instance(instance_id='id2', client_name='Client 2')
        
        instances = manager.list_instances()
        assert len(instances) == 2
        
        # Verify structure
        for instance_dict in instances:
            assert 'instance_id' in instance_dict
            assert 'client_name' in instance_dict
            assert 'created_at' in instance_dict
            assert 'last_activity' in instance_dict
    
    def test_get_instance_updates_activity(self, manager):
        """Test that getting an instance updates activity timestamp."""
        instance_id = manager.create_instance()
        instance = manager.get_instance(instance_id)
        original_time = instance.last_activity
        
        import time
        time.sleep(0.1)
        
        manager.get_instance(instance_id)
        updated_instance = manager.instances[instance_id]
        
        assert updated_instance.last_activity > original_time
    
    def test_cleanup_inactive_instances(self, manager):
        """Test cleanup of inactive instances."""
        # Create active instance
        active_id = manager.create_instance(client_name='Active')
        
        # Create inactive instance and manually set old activity time
        inactive_id = manager.create_instance(client_name='Inactive')
        inactive_instance = manager.instances[inactive_id]
        inactive_instance.last_activity = datetime.utcnow() - timedelta(hours=2)
        inactive_instance.connected = False
        
        # Cleanup with 1 hour timeout
        manager.cleanup_inactive_instances(timeout_seconds=3600)
        
        # Active should remain, inactive should be removed
        assert manager.get_instance(active_id) is not None
        assert manager.get_instance(inactive_id) is None
    
    def test_instance_isolation(self, manager):
        """Test that instances have isolated game states."""
        # Create two instances with different states
        state1 = GameState()
        state1.current_money = 1000
        id1 = manager.create_instance(game_state=state1, client_name='Client 1')
        
        state2 = GameState()
        state2.current_money = 5000
        id2 = manager.create_instance(game_state=state2, client_name='Client 2')
        
        # Verify isolation
        retrieved1 = manager.get_game_state(id1)
        retrieved2 = manager.get_game_state(id2)
        
        assert retrieved1.current_money == 1000
        assert retrieved2.current_money == 5000
        
        # Modify one state
        retrieved1.current_money = 2000
        
        # Other state should be unaffected
        assert manager.get_game_state(id2).current_money == 5000


class TestInstanceManagerGlobalSingleton:
    """Test global instance_manager singleton."""
    
    def test_global_instance_manager_exists(self):
        """Test that global instance manager is initialized."""
        assert instance_manager is not None
        assert isinstance(instance_manager, InstanceManager)
    
    def test_global_instance_manager_is_singleton(self):
        """Test that imports reference same instance."""
        from backend.services.instance_manager import instance_manager as im2
        assert instance_manager is im2
