#!/usr/bin/env python3
"""Standalone backend server startup script.

This script starts the backend API server with a live GameState instance
for live debugging and manipulation during development.
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.app import BackendApp
from backend.config import BackendConfig
from src.models.game_state import GameState

def main():
    """Start the backend server."""
    print("=" * 60)
    print("🚀 Cybersecurity Firm - Backend API Server")
    print("=" * 60)
    print()
    print("Initializing game state...")
    
    # Create game state
    try:
        game_state = GameState()
        print(f"✅ Game state initialized:")
        print(f"   - Specialists: {len(game_state.specialists)}")
        print(f"   - Clients: {len(game_state.clients)}")
        print(f"   - Automation Scripts: {len(game_state.automation_scripts)}")
        print(f"   - Starting Money: ${game_state.current_money:.2f}")
    except Exception as e:
        print(f"❌ Failed to initialize game state: {e}")
        sys.exit(1)
    
    print()
    print("Starting backend server...")
    print(f"   Host: {BackendConfig.HOST}")
    print(f"   Port: {BackendConfig.PORT}")
    print(f"   Debug: {BackendConfig.DEBUG}")
    print()
    print("=" * 60)
    print(f"🌐 Admin Dashboard: http://localhost:{BackendConfig.PORT}/admin")
    print(f"📡 API Endpoints: http://localhost:{BackendConfig.PORT}/api/*")
    print(f"❤️  Health Check: http://localhost:{BackendConfig.PORT}/health")
    print("=" * 60)
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    # Create and run backend app
    backend = BackendApp(game_state)
    
    try:
        backend.run()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down backend server...")
        print("Goodbye!")

if __name__ == "__main__":
    main()
