# WebSocket Protocol - Headless Game Prototype

This document describes the simple JSON protocol used by the headless
WebSocket prototype server (`src/websocket_game.py`) and the browser UI
prototype in `web_ui/index.html`.

Server -> Client
- event: `state_snapshot`
  - Sent on client connect and periodically. Payload: `{ tick: int, data: { ...full state... } }`

- event: `state_patch`
  - Sent to describe small updates. Payload: `{ tick: int, data: { incidents: [...], specialists?: [...] } }`

- event: `ack`
  - Sent in response to client actions: `{ id: <client_action_id>, status: 'ok'|'error', error?: '...' }`

Client -> Server
- action: `assign_incident`
  - Example:
    ```json
    {
      "action": "assign_incident",
      "id": "client_action_123",
      "data": { "incident_id": "inc_demo_1", "specialist_id": "spec_42" }
    }
    ```

Notes & Recommendations
- The prototype uses plain JSON to keep things simple. For production, consider
  delta patching, protobuf, or other efficient encodings for large state.
- Always correlate acks with the client-supplied `id` so the UI can show
  optimistic updates and reconcile if the server rejects the action.
- On reconnect, the client should request a fresh `state_snapshot`.
