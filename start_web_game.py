#!/usr/bin/env python3
"""
Start the Cybersecurity Firm game with embedded web server.

This script starts the game in headless mode with an embedded WebSocket server
and static file server, then opens the web UI in your default browser.

Usage:
    python start_web_game.py

The game will be accessible at:
    http://localhost:8000
"""
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def main():
    print("🎮 Starting Cybersecurity Firm Web Game...")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ Error: main.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    print("📡 Starting game server (headless mode with WebSocket support)...")
    print("   - WebSocket server: ws://localhost:8765")
    print("   - Web UI server: http://localhost:8000")
    print()
    
    try:
        # Start the game server
        process = subprocess.Popen(
            [sys.executable, "main.py", "--local-server", "--headless"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Wait a moment for server to start
        print("⏳ Waiting for server to initialize...")
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is not None:
            print("❌ Server failed to start. Check the logs for errors.")
            sys.exit(1)
        
        # Open browser
        url = "http://localhost:8000"
        print(f"🌐 Opening web browser to {url}...")
        webbrowser.open(url)
        
        print()
        print("✅ Game server is running!")
        print()
        print("📖 Instructions:")
        print("   - The game UI should open in your browser automatically")
        print("   - If not, navigate to: http://localhost:8000")
        print("   - Press Ctrl+C in this terminal to stop the server")
        print()
        print("📊 Server logs:")
        print("-" * 60)
        
        # Stream server output
        for line in process.stdout:
            print(line, end='')
            
    except KeyboardInterrupt:
        print()
        print()
        print("🛑 Stopping game server...")
        process.terminate()
        process.wait(timeout=5)
        print("✅ Server stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'process' in locals():
            process.terminate()
        sys.exit(1)


if __name__ == "__main__":
    main()
