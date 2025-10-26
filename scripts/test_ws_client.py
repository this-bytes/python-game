"""Simple test WebSocket client to verify the embedded server.

Run this while the game is running to confirm the server accepts
connections and sends the initial state snapshot.

Usage:
    python scripts/test_ws_client.py --host localhost --port 8765
"""
import asyncio
import websockets
import json
import argparse

async def run(host: str, port: int):
    uri = f"ws://{host}:{port}"
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as ws:
            print("Connected. Waiting for first message...")
            msg = await ws.recv()
            try:
                obj = json.loads(msg)
                print("Received:", json.dumps(obj, indent=2)[:2000])
            except Exception:
                print("Received non-JSON message:", msg)
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    asyncio.run(run(args.host, args.port))
