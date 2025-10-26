"""Minimal WebSocket-based headless game server prototype.

This script implements a small authoritative game loop that serves a JSON
state snapshot on new WS connections and accepts simple action messages from
clients (for example: assign_incident). It broadcasts state patches to all
connected clients.

This is intentionally small and self-contained as a prototype for the
browser-based UI migration. No backwards compatibility is preserved.
"""
import asyncio
import json
import threading
import uuid
from pathlib import Path
from typing import Any, Dict, List, Set, Optional, Callable
import queue as _queue

import websockets

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def _load_json(path: Path) -> Any:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_initial_state() -> Dict[str, Any]:
    """Load initial state from data files (best-effort)."""
    state: Dict[str, Any] = {}

    # Specialists
    specialists_raw = _load_json(DATA_DIR / "specialists.json") or _load_json(DATA_DIR / "specialist_templates.json")
    if isinstance(specialists_raw, dict) and "specialists" in specialists_raw:
        state["specialists"] = specialists_raw["specialists"]
    elif isinstance(specialists_raw, list):
        state["specialists"] = specialists_raw
    else:
        # Fallback: empty list
        state["specialists"] = []

    # Incidents
    incidents_raw = _load_json(DATA_DIR / "incidents.json") or {}
    if isinstance(incidents_raw, dict) and "incident_types" in incidents_raw:
        # convert templates to instances (simple)
        types = incidents_raw["incident_types"]
        # Create a few demo incidents from templates
        incidents: List[Dict[str, Any]] = []
        for i, t in enumerate(types[:10]):
            incidents.append({
                "id": f"inc_demo_{i}",
                "incident_type": t.get("name", t.get("id", "incident")),
                "specialty_required": t.get("specialty_required"),
                "difficulty": (t.get("difficulty_range", [1, 1])[0] if isinstance(t.get("difficulty_range"), list) else 1),
                "assigned_to": None,
            })
        state["incidents"] = incidents
    elif isinstance(incidents_raw, list):
        state["incidents"] = incidents_raw
    else:
        state["incidents"] = []

    # Minimal budget/state
    state["game_time"] = 0
    state["tick"] = 0
    state["money"] = 10000

    return state


CONNECTED: Set[websockets.WebSocketServerProtocol] = set()
STATE = build_initial_state()
STATE_LOCK = threading.Lock()
# Server asyncio loop reference (populated when server starts)
SERVER_LOOP: Optional[asyncio.AbstractEventLoop] = None
# Optional callable to enqueue actions into the authoritative engine
# Should be set by the engine when starting the server so incoming WS
# actions are processed on the engine/game thread safely.
ACTION_ENQUEUE: Optional[Callable[[Dict[str, Any]], None]] = None
# Queue for action results produced by the engine. Engine should put
# result dicts here after processing actions that requested confirmation.
ACTION_RESULT_QUEUE: _queue.Queue = _queue.Queue()
# Mapping from client action id -> websocket connection object.
# Populated when a client requests to wait for an action result. Only
# accessed from the websocket server's asyncio loop.
ACTION_WAITERS: Dict[str, Any] = {}
# Optional admin token for admin actions (set by caller when starting server)
ADMIN_TOKEN: Optional[str] = None


def set_state(new_state: Dict[str, Any]) -> None:
    """Thread-safe setter for authoritative state coming from engine.

    This will replace the in-module STATE and schedule a broadcast to all
    connected websocket clients via the server's asyncio loop.
    """
    global STATE
    with STATE_LOCK:
        # shallow copy to avoid retaining external references
        STATE = dict(new_state)

    # Schedule broadcast on the server loop if available
    if SERVER_LOOP and SERVER_LOOP.is_running():
        try:
            asyncio.run_coroutine_threadsafe(
                broadcast({"event": "state_snapshot", "tick": STATE.get("tick", 0), "data": STATE}),
                SERVER_LOOP,
            )
        except Exception:
            # Best-effort: ignore scheduling errors
            pass


async def broadcast(message: Dict[str, Any]) -> None:
    if not CONNECTED:
        return
    payload = json.dumps(message)
    # debug: show broadcast size/count
    try:
        # Use list() to snapshot connections
        conns = list(CONNECTED)
        # print a lightweight debug line - the server runs in background thread
        print(f"[WS] Broadcasting event={message.get('event')} to {len(conns)} clients")
        try:
            await asyncio.gather(*(ws.send(payload) for ws in conns))
        except Exception as e:
            # Print traceback to help diagnose send failures
            import traceback
            print(f"[WS] Error during broadcast: {e}")
            traceback.print_exc()
    except Exception:
        # Best-effort: ignore send errors
        pass


def find_incident(incident_id: str) -> Dict[str, Any] | None:
    for inc in STATE.get("incidents", []):
        if str(inc.get("id")) == str(incident_id):
            return inc
    return None


def find_specialist(specialist_id: str) -> Dict[str, Any] | None:
    for s in STATE.get("specialists", []):
        if str(s.get("id")) == str(specialist_id):
            return s
    return None


async def handle_action(action: Dict[str, Any], ws: websockets.WebSocketServerProtocol) -> None:
    act = action.get("action")
    cid = action.get("id", str(uuid.uuid4()))

    # Admin action protection: if the action requests admin privileges, require ADMIN_TOKEN
    if (str(act).startswith("admin:") or action.get("admin", False)):
        token = action.get("admin_token")
        if not ADMIN_TOKEN or token != ADMIN_TOKEN:
            await ws.send(json.dumps({"event": "ack", "id": cid, "status": "error", "error": "unauthorized"}))
            return

    if act == "assign_incident":
        data = action.get("data", {})
        specialist_id = data.get("specialist_id")
        incident_id = data.get("incident_id")

        # If the engine provided an enqueue function, delegate handling to it
        if ACTION_ENQUEUE:
            try:
                # If client requested final confirmation, register waiter
                wait_for_result = bool(action.get("wait_for_result", False))
                if wait_for_result:
                    # register waiter mapping so result_dispatcher can reply
                    ACTION_WAITERS[cid] = ws

                ACTION_ENQUEUE({
                    "action": "assign_incident",
                    "incident_id": incident_id,
                    "specialist_id": specialist_id,
                    "_client_action_id": cid,
                })

                # Acknowledge receipt. If wait_for_result is True the final
                # result will be delivered via the action_result event.
                await ws.send(json.dumps({"event": "ack", "id": cid, "status": "received" if wait_for_result else "ok"}))
                return
            except Exception:
                await ws.send(json.dumps({"event": "ack", "id": cid, "status": "error", "error": "enqueue_failed"}))
                # cleanup waiter mapping if set
                if cid in ACTION_WAITERS:
                    ACTION_WAITERS.pop(cid, None)
                return

        # Fallback (prototype behavior): mutate in-module STATE (unsafe for production)
        inc = find_incident(incident_id)
        spec = find_specialist(specialist_id)
        if inc is None or spec is None:
            await ws.send(json.dumps({"event": "ack", "id": cid, "status": "error", "error": "invalid ids"}))
            return

        inc["assigned_to"] = specialist_id
        # broadcast patch
        await broadcast({"event": "state_patch", "tick": STATE.get("tick", 0), "data": {"incidents": [inc]}})
        await ws.send(json.dumps({"event": "ack", "id": cid, "status": "ok"}))
        return

    # Unknown action
    await ws.send(json.dumps({"event": "ack", "id": cid, "status": "error", "error": "unknown_action"}))


async def consumer_handler(ws: websockets.WebSocketServerProtocol) -> None:
    async for message in ws:
        # Debug: log incoming raw messages for diagnosis
        print(f"[WS] Received raw message from client: {message}")
        try:
            obj = json.loads(message)
        except Exception:
            try:
                await ws.send(json.dumps({"event": "error", "error": "invalid_json"}))
            except Exception:
                print("[WS] Failed to send invalid_json error to client")
            continue

        if "action" in obj:
            try:
                await handle_action(obj, ws)
            except Exception as e:
                # Log handler exceptions so we can see why actions may fail
                import traceback
                print(f"[WS] Exception handling action {obj.get('action')}: {e}")
                traceback.print_exc()


async def produce_ticks() -> None:
    while True:
        await asyncio.sleep(1.0)
        STATE["game_time"] += 1
        STATE["tick"] += 1
        # occasionally broadcast heartbeat/state snapshot (every 5 ticks)
        if STATE["tick"] % 5 == 0:
            await broadcast({"event": "state_snapshot", "tick": STATE["tick"], "data": STATE})


async def result_dispatcher() -> None:
    """Coroutine running in the websocket server loop that dispatches
    action results produced by the engine back to waiting clients.
    """
    while True:
        # Non-blocking check for results queued by the engine (from other thread)
        try:
            result = ACTION_RESULT_QUEUE.get_nowait()
        except Exception:
            result = None

        if result:
            client_id = result.get("_client_action_id")
            if client_id:
                ws = ACTION_WAITERS.pop(client_id, None)
                if ws and ws in CONNECTED:
                    try:
                        payload = json.dumps({"event": "action_result", "id": client_id, "result": result})
                        print(f"[WS] Dispatching action_result for client_id={client_id}")
                        await ws.send(payload)
                    except Exception:
                        # If send fails, ignore — client may have disconnected
                        pass
        await asyncio.sleep(0.1)


async def handler(ws: websockets.WebSocketServerProtocol) -> None:
    # New connection: register and send snapshot
    CONNECTED.add(ws)
    print(f"[WS] New connection from client; total connected={len(CONNECTED)}")
    try:
        try:
            payload = json.dumps({"event": "state_snapshot", "tick": STATE.get("tick", 0), "data": STATE})
            print(f"[WS] Sending initial state_snapshot to client (size={len(payload)} bytes)")
            await ws.send(payload)
        except Exception as e:
            print(f"[WS] Failed to send initial state_snapshot: {e}")
            import traceback
            traceback.print_exc()
        consumer_task = asyncio.create_task(consumer_handler(ws))
        await consumer_task
    except websockets.ConnectionClosed:
        pass
    finally:
        CONNECTED.discard(ws)
        print(f"[WS] Connection closed; total connected={len(CONNECTED)}")


async def main(host: str = "0.0.0.0", port: int = 8765) -> None:
    global SERVER_LOOP
    print(f"Starting websocket game server on ws://{host}:{port}")
    SERVER_LOOP = asyncio.get_running_loop()
    server = await websockets.serve(handler, host, port)
    # start heartbeat ticks
    tick_task = asyncio.create_task(produce_ticks())
    # start dispatcher for engine-produced action results
    result_task = asyncio.create_task(result_dispatcher())
    try:
        await server.wait_closed()
    finally:
        tick_task.cancel()
        result_task.cancel()


def start_background_server(host: str = "0.0.0.0", port: int = 8765) -> threading.Thread:
    """Start the websocket server in a background thread.

    Returns the Thread object so callers can join/stop if needed.
    """
    def _run():
        try:
            asyncio.run(main(host=host, port=port))
        except Exception as e:
            # Print full traceback to help diagnose startup failures
            import traceback
            print(f"[WS] WebSocket server thread exiting due to exception: {e}")
            traceback.print_exc()

    t = threading.Thread(target=_run, daemon=True, name="ws-server")
    t.start()
    return t


def start_background_server_with_enqueue(host: str = "0.0.0.0", port: int = 8765, action_enqueue: Optional[Callable[[Dict[str, Any]], None]] = None) -> threading.Thread:
    """Start the websocket server in a background thread and register an action enqueue callback.

    Args:
        host: Host to bind the websocket server
        port: Port to bind
        action_enqueue: Optional callable that accepts an action dict and enqueues it to the engine

    Returns:
        Thread object running the server
    """
    global ACTION_ENQUEUE, ADMIN_TOKEN
    if action_enqueue:
        ACTION_ENQUEUE = action_enqueue
    # ADMIN_TOKEN can be set by caller by passing in via environment or
    # by setting websocket_game.ADMIN_TOKEN after import; start_background
    # helper does not require an explicit admin token parameter to keep
    # the API stable but the caller may set websocket_game.ADMIN_TOKEN
    # before calling this helper.
    return start_background_server(host=host, port=port)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped")
