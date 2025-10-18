"""API Tests for Relationships Endpoints.

Tests the relationships system API endpoints:
- GET /specialists/<id>/relationships
- GET /specialists/relationships/list-all
- POST /specialists/relationships/team-synergy
- POST /specialists/relationships/create
- POST /specialists/relationships/delete
"""
import pytest
import json
from datetime import datetime
from src.models.game_state import GameState
from src.models.specialist import Specialist, SpecialistStats
from src.core.relationships_system import RelationshipsSystem, RelationshipType


@pytest.fixture
def game_state_for_api():
    """Create game state for API testing."""
    game_state = GameState()
    return game_state


@pytest.fixture
def test_specialists_api(game_state_for_api):
    """Create test specialists."""
    specialist_a = Specialist(
        id="spec_001",
        name="Alice",
        specialty="Network Security",
        level=1,
        xp=0,
        stats=SpecialistStats(speed=100.0, accuracy=90.0, experience_bonus=1.0)
    )
    specialist_b = Specialist(
        id="spec_002",
        name="Bob",
        specialty="Malware Analysis",
        level=1,
        xp=0,
        stats=SpecialistStats(speed=95.0, accuracy=95.0, experience_bonus=1.1)
    )
    specialist_c = Specialist(
        id="spec_003",
        name="Charlie",
        specialty="Cryptography",
        level=1,
        xp=0,
        stats=SpecialistStats(speed=90.0, accuracy=100.0, experience_bonus=1.2)
    )
    
    game_state_for_api.specialists = [specialist_a, specialist_b, specialist_c]
    return [specialist_a, specialist_b, specialist_c]


@pytest.fixture
def client_api(game_state_for_api):
    """Create Flask test client."""
    from backend.app import create_app
    
    app = create_app(game_state_for_api)
    return app.test_client()


class TestGetSpecialistRelationships:
    """Tests for GET /specialists/<id>/relationships endpoint."""
    
    def test_get_relationships_for_specialist(self, client_api, game_state_for_api, test_specialists_api):
        """Verify endpoint returns specialist relationships."""
        specialist_a, specialist_b, specialist_c = test_specialists_api
        
        # Create friendship between A and B
        game_state_for_api._relationships_system.create_friendship("spec_001", "spec_002", 80)
        
        # Get relationships
        response = client_api.get('/api/specialists/spec_001/relationships')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["specialist_id"] == "spec_001"
        assert data["data"]["friend_count"] >= 1
    
    def test_get_relationships_nonexistent_specialist(self, client_api):
        """Verify endpoint returns 404 for nonexistent specialist."""
        response = client_api.get('/api/specialists/nonexistent/relationships')
        
        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False
        assert "not found" in data["message"].lower()
    
    def test_get_relationships_no_relationships(self, client_api, test_specialists_api):
        """Verify endpoint returns 0 relationships for isolated specialist."""
        response = client_api.get('/api/specialists/spec_001/relationships')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["friend_count"] == 0
        assert data["data"]["rival_count"] == 0


class TestListAllRelationships:
    """Tests for GET /specialists/relationships/list-all endpoint."""
    
    def test_list_all_relationships_empty(self, client_api, test_specialists_api):
        """Verify endpoint returns empty list when no relationships."""
        response = client_api.get('/api/specialists/relationships/list-all')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["count"] == 0
        assert data["data"] == []
    
    def test_list_all_relationships_with_friendships(self, client_api, game_state_for_api, test_specialists_api):
        """Verify endpoint returns all relationships."""
        # Create multiple relationships
        game_state_for_api._relationships_system.create_friendship("spec_001", "spec_002", 75)
        game_state_for_api._relationships_system.create_rivalry("spec_002", "spec_003", -70)
        
        response = client_api.get('/api/specialists/relationships/list-all')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["count"] >= 2
        
        # Verify relationships are listed
        relationships = data["data"]
        assert any(r["specialist_a"] == "spec_001" for r in relationships)
        assert any(r["type"] in ["FRIENDLY", "RIVAL"] for r in relationships)


class TestTeamSynergy:
    """Tests for POST /specialists/relationships/team-synergy endpoint."""
    
    def test_team_synergy_neutral_team(self, client_api, test_specialists_api):
        """Verify endpoint returns 1.0 synergy for team with no relationships."""
        response = client_api.post('/api/specialists/relationships/team-synergy', 
            json={"team_ids": ["spec_001", "spec_002", "spec_003"]},
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["synergy_multiplier"] == 1.0
        assert data["data"]["synergy_type"] == "neutral"
    
    def test_team_synergy_friendly_team(self, client_api, game_state_for_api, test_specialists_api):
        """Verify endpoint returns >1.0 synergy for friendly team."""
        # Create friendships
        game_state_for_api._relationships_system.create_friendship("spec_001", "spec_002", 80)
        game_state_for_api._relationships_system.create_friendship("spec_002", "spec_003", 75)
        
        response = client_api.post('/api/specialists/relationships/team-synergy',
            json={"team_ids": ["spec_001", "spec_002", "spec_003"]},
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["synergy_multiplier"] > 1.0
        assert data["data"]["synergy_type"] == "positive"
    
    def test_team_synergy_rival_team(self, client_api, game_state_for_api, test_specialists_api):
        """Verify endpoint returns <1.0 synergy for rival team."""
        # Create rivalries
        game_state_for_api._relationships_system.create_rivalry("spec_001", "spec_002", -85)
        game_state_for_api._relationships_system.create_rivalry("spec_002", "spec_003", -80)
        
        response = client_api.post('/api/specialists/relationships/team-synergy',
            json={"team_ids": ["spec_001", "spec_002", "spec_003"]},
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["synergy_multiplier"] < 1.0
        assert data["data"]["synergy_type"] == "negative"
    
    def test_team_synergy_invalid_specialist(self, client_api):
        """Verify endpoint returns 404 for nonexistent specialist in team."""
        response = client_api.post('/api/specialists/relationships/team-synergy',
            json={"team_ids": ["spec_001", "nonexistent"]},
            content_type='application/json'
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False
        assert "not found" in data["message"].lower()
    
    def test_team_synergy_empty_team(self, client_api):
        """Verify endpoint returns 400 for empty team."""
        response = client_api.post('/api/specialists/relationships/team-synergy',
            json={"team_ids": []},
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False


class TestCreateRelationship:
    """Tests for POST /specialists/relationships/create endpoint."""
    
    def test_create_friendship(self, client_api, game_state_for_api):
        """Verify endpoint creates friendship."""
        response = client_api.post('/api/specialists/relationships/create',
            json={
                "specialist_a_id": "spec_001",
                "specialist_b_id": "spec_002",
                "type": "FRIENDLY",
                "intensity": 80
            },
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["type"] == "friendship"
        assert data["data"]["intensity"] == 80
    
    def test_create_rivalry(self, client_api):
        """Verify endpoint creates rivalry."""
        response = client_api.post('/api/specialists/relationships/create',
            json={
                "specialist_a_id": "spec_001",
                "specialist_b_id": "spec_002",
                "type": "RIVAL",
                "intensity": -75
            },
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["type"] == "rivalry"
        assert data["data"]["intensity"] == -75
    
    def test_create_relationship_missing_parameters(self, client_api):
        """Verify endpoint returns 400 for missing parameters."""
        response = client_api.post('/api/specialists/relationships/create',
            json={
                "specialist_a_id": "spec_001"
            },
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
    
    def test_create_relationship_self_relationship(self, client_api):
        """Verify endpoint returns 400 for self-relationship."""
        response = client_api.post('/api/specialists/relationships/create',
            json={
                "specialist_a_id": "spec_001",
                "specialist_b_id": "spec_001",
                "type": "FRIENDLY"
            },
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "same specialist" in data["message"].lower()
    
    def test_create_relationship_nonexistent_specialist(self, client_api):
        """Verify endpoint returns 404 for nonexistent specialist."""
        response = client_api.post('/api/specialists/relationships/create',
            json={
                "specialist_a_id": "spec_001",
                "specialist_b_id": "nonexistent",
                "type": "FRIENDLY"
            },
            content_type='application/json'
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False
        assert "not found" in data["message"].lower()
    
    def test_create_relationship_invalid_type(self, client_api):
        """Verify endpoint returns 400 for invalid relationship type."""
        response = client_api.post('/api/specialists/relationships/create',
            json={
                "specialist_a_id": "spec_001",
                "specialist_b_id": "spec_002",
                "type": "INVALID"
            },
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False


class TestDeleteRelationship:
    """Tests for POST /specialists/relationships/delete endpoint."""
    
    def test_delete_relationship(self, client_api, game_state_for_api):
        """Verify endpoint deletes relationship."""
        # Create relationship first
        game_state_for_api._relationships_system.create_friendship("spec_001", "spec_002", 80)
        
        # Delete it
        response = client_api.post('/api/specialists/relationships/delete',
            json={
                "specialist_a_id": "spec_001",
                "specialist_b_id": "spec_002"
            },
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["deleted_type"] == "FRIENDLY"
        assert data["data"]["deleted_intensity"] == 80
    
    def test_delete_nonexistent_relationship(self, client_api):
        """Verify endpoint returns 404 when relationship doesn't exist."""
        response = client_api.post('/api/specialists/relationships/delete',
            json={
                "specialist_a_id": "spec_001",
                "specialist_b_id": "spec_002"
            },
            content_type='application/json'
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False
        assert "no relationship" in data["message"].lower()
    
    def test_delete_relationship_missing_parameters(self, client_api):
        """Verify endpoint returns 400 for missing parameters."""
        response = client_api.post('/api/specialists/relationships/delete',
            json={
                "specialist_a_id": "spec_001"
            },
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False


class TestEndToEndRelationshipsAPI:
    """End-to-end relationship API tests."""
    
    def test_complete_relationship_workflow(self, client_api, game_state_for_api, test_specialists_api):
        """Verify complete workflow: create, list, calculate synergy, delete."""
        # Create friendships
        response = client_api.post('/api/specialists/relationships/create',
            json={
                "specialist_a_id": "spec_001",
                "specialist_b_id": "spec_002",
                "type": "FRIENDLY",
                "intensity": 85
            },
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # List all relationships
        response = client_api.get('/api/specialists/relationships/list-all')
        assert response.status_code == 200
        assert response.get_json()["count"] > 0
        
        # Get team synergy
        response = client_api.post('/api/specialists/relationships/team-synergy',
            json={"team_ids": ["spec_001", "spec_002"]},
            content_type='application/json'
        )
        assert response.status_code == 200
        synergy_before = response.get_json()["data"]["synergy_multiplier"]
        assert synergy_before > 1.0
        
        # Delete relationship
        response = client_api.post('/api/specialists/relationships/delete',
            json={
                "specialist_a_id": "spec_001",
                "specialist_b_id": "spec_002"
            },
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # Verify synergy back to neutral (allow floating point error and calculation variance)
        response = client_api.post('/api/specialists/relationships/team-synergy',
            json={"team_ids": ["spec_001", "spec_002"]},
            content_type='application/json'
        )
        assert response.status_code == 200
        synergy_after = response.get_json()["data"]["synergy_multiplier"]
        assert abs(synergy_after - 1.0) < 0.1  # Allow reasonable tolerance for calculation variance
    
    def test_multiple_team_synergy_calculations(self, client_api, game_state_for_api):
        """Verify synergy calculation with mixed relationships."""
        # Mix friendships and rivalries
        game_state_for_api._relationships_system.create_friendship("spec_001", "spec_002", 75)
        game_state_for_api._relationships_system.create_rivalry("spec_002", "spec_003", -70)
        game_state_for_api._relationships_system.create_friendship("spec_001", "spec_003", 60)
        
        # Calculate full team synergy
        response = client_api.post('/api/specialists/relationships/team-synergy',
            json={"team_ids": ["spec_001", "spec_002", "spec_003"]},
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        # Should be close to neutral since friendships and rivalries offset
        assert 0.85 <= data["data"]["synergy_multiplier"] <= 1.15
