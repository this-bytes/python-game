"""Entrypoint to run the websocket headless game prototype.

Usage:
    python run_ws_game.py

This will start the asyncio websockets server on port 8765. The small
browser UI in `web_ui/index.html` can connect to it (open that file in a
browser and it will connect to ws://localhost:8765).
"""
import asyncio
from src.websocket_game import main


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Stopped')
