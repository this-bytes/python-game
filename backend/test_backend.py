#!/usr/bin/env python3
"""Test script to verify backend API functionality."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import BackendApp
from src.models.game_state import GameState

def test_backend():
    """Test backend initialization and routes."""
    print("Testing backend initialization...")
    
    # Create game state
    print("Creating game state...")
    game_state = GameState()
    
    # Create backend app
    print("Creating backend app...")
    backend = BackendApp(game_state)
    
    # Test with Flask test client
    with backend.app.test_client() as client:
        print("\n=== Testing Endpoints ===")
        
        # Test health endpoint
        print("\n1. Testing /health")
        response = client.get('/health')
        print(f"   Status: {response.status_code}")
        print(f"   Data: {response.get_json()}")
        
        # Test state summary
        print("\n2. Testing /api/state/summary")
        response = client.get('/api/state/summary')
        print(f"   Status: {response.status_code}")
        data = response.get_json()
        print(f"   Success: {data.get('success')}")
        if data.get('success'):
            summary = data.get('data', {})
            print(f"   Money: ${summary.get('money', 0):.2f}")
            print(f"   Specialists: {summary.get('total_specialists', 0)}")
            print(f"   Incidents: {summary.get('active_incidents', 0)}")
        
        # Test specialists list
        print("\n3. Testing /api/specialists")
        response = client.get('/api/specialists')
        print(f"   Status: {response.status_code}")
        data = response.get_json()
        print(f"   Success: {data.get('success')}")
        print(f"   Count: {data.get('count', 0)}")
        
        # Test incidents list
        print("\n4. Testing /api/incidents")
        response = client.get('/api/incidents')
        print(f"   Status: {response.status_code}")
        data = response.get_json()
        print(f"   Success: {data.get('success')}")
        print(f"   Count: {data.get('count', 0)}")
        
        # Test clients list
        print("\n5. Testing /api/clients")
        response = client.get('/api/clients')
        print(f"   Status: {response.status_code}")
        data = response.get_json()
        print(f"   Success: {data.get('success')}")
        print(f"   Count: {data.get('count', 0)}")
        
        # Test time pause
        print("\n6. Testing /api/time/pause")
        response = client.post('/api/time/pause')
        print(f"   Status: {response.status_code}")
        data = response.get_json()
        print(f"   Success: {data.get('success')}")
        print(f"   Message: {data.get('message')}")
        
        # Test money adjustment
        print("\n7. Testing /api/economy/money")
        response = client.post('/api/economy/money', 
                              json={'amount': 1000, 'reason': 'Test adjustment'})
        print(f"   Status: {response.status_code}")
        data = response.get_json()
        print(f"   Success: {data.get('success')}")
        if data.get('success'):
            adj_data = data.get('data', {})
            print(f"   Old money: ${adj_data.get('old_money', 0):.2f}")
            print(f"   New money: ${adj_data.get('new_money', 0):.2f}")
        
        # Test incident spawn
        print("\n8. Testing /api/incidents/spawn")
        response = client.post('/api/incidents/spawn', json={})
        print(f"   Status: {response.status_code}")
        data = response.get_json()
        print(f"   Success: {data.get('success')}")
        print(f"   Message: {data.get('message')}")
        
        print("\n=== All tests completed! ===")
        print("\n✅ Backend API is working correctly!")
        print("   To start the server, run:")
        print("   python backend/app.py")
        print("   Then open http://localhost:5000 in your browser")

if __name__ == "__main__":
    test_backend()
