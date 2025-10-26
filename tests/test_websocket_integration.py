#!/usr/bin/env python3
"""
Integration test for WebSocket game server.

Tests:
- Server startup
- WebSocket connection
- State snapshot reception
- Incident assignment
"""
import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path

import websockets


async def test_websocket():
    """Test WebSocket connection and basic functionality."""
    print("Connecting to WebSocket server...")
    
    try:
        async with websockets.connect('ws://localhost:8765') as ws:
            print("✅ Connected successfully")
            
            # Test 1: Receive initial state snapshot
            print("\nTest 1: Receiving initial state snapshot...")
            message = await asyncio.wait_for(ws.recv(), timeout=5.0)
            data = json.loads(message)
            
            assert data.get('event') == 'state_snapshot', "Expected state_snapshot event"
            assert 'data' in data, "Missing data field"
            assert 'specialists' in data['data'], "Missing specialists"
            assert 'incidents' in data['data'], "Missing incidents"
            print(f"✅ Received state snapshot with {len(data['data']['specialists'])} specialists and {len(data['data']['incidents'])} incidents")
            
            # Test 2: Send incident assignment action
            specialists = data['data']['specialists']
            incidents = data['data']['incidents']
            
            if specialists and incidents:
                print("\nTest 2: Assigning incident to specialist...")
                action = {
                    'action': 'assign_incident',
                    'id': 'test_' + str(int(time.time())),
                    'data': {
                        'incident_id': incidents[0]['id'],
                        'specialist_id': specialists[0]['id']
                    },
                    'wait_for_result': True
                }
                
                await ws.send(json.dumps(action))
                print(f"✅ Sent assignment request")
                
                # Wait for acknowledgment
                ack_message = await asyncio.wait_for(ws.recv(), timeout=5.0)
                ack = json.loads(ack_message)
                assert ack.get('event') in ['ack', 'action_result'], "Expected ack or action_result"
                print(f"✅ Received acknowledgment: {ack.get('status', 'unknown')}")
            else:
                print("⚠️  Skipping assignment test (no specialists or incidents)")
            
            print("\n✅ All tests passed!")
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run integration tests."""
    print("="*60)
    print("WebSocket Game Server Integration Test")
    print("="*60)
    
    # Check if server is already running
    print("\nChecking if server is running...")
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8765))
        sock.close()
        
        if result == 0:
            print("✅ Server is already running")
            server_started = False
        else:
            print("Server not running. Starting server...")
            # Start server
            server_process = subprocess.Popen(
                [sys.executable, 'main.py', '--local-server', '--headless'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(5)  # Wait for server to start
            print("✅ Server started")
            server_started = True
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return 1
    
    # Run tests
    try:
        success = asyncio.run(test_websocket())
        
        if server_started:
            print("\nStopping server...")
            server_process.terminate()
            server_process.wait(timeout=5)
            print("✅ Server stopped")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        if server_started:
            server_process.terminate()
        return 1
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        if server_started:
            server_process.terminate()
        return 1


if __name__ == '__main__':
    sys.exit(main())
