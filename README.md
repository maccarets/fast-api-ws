## FastAPI WebSocket Service

A small FastAPI service providing a WebSocket endpoint for client connections and HTTP endpoints to inspect and broadcast messages to connected clients. It also includes coordinated, graceful shutdown logic.

### Setup

1) Create and activate a virtual environment (recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2) Install dependencies

```bash
pip install -r requirements.txt
```

3) Run the server (reload enabled for local dev)

```bash
python server.py
```

The app starts on `http://127.0.0.1:8000`.

Environment variables (optional):
- `FORCED_SHUTDOWN_AFTER_SEC` (default: 1800) – max wait before forcing shutdown
- `PROGRESS_LOG_EVERY_SEC` (default: 5) – interval for progress logs during shutdown
- `LOG_LEVEL` (default: INFO)

### Endpoints

#### WebSocket
- `GET ws://127.0.0.1:8000/ws/{clientId}`
  - Path params:
    - `clientId` (int): Unique ID for the client connection.
  - Behavior:
    - Rejects duplicate connections for the same `clientId` with a `1008` policy violation.
    - Rejects new connections once graceful shutdown has started.
    - Echoes received text messages as `"Server echo: {message}"`.

#### HTTP
- `POST /broadcast-to-all`
  - Body: `{ "message": "<string>" }`
  - Sends the text to all currently connected WebSocket clients.
  - Response: `{ "sent": <number_of_clients_sent_to> }`

- `GET /clients`
  - Lists the IDs of currently connected clients.
  - Response: `{ "clients": [<clientId>, ...] }`

### How to test the WebSocket endpoint

Using `websocat`:
```bash
websocat ws://127.0.0.1:8000/ws/1
```
Type a message and you should receive an echo: `Server echo: <your message>`.


Broadcast to all connected clients via HTTP:
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello, clients!"}' \
  http://127.0.0.1:8000/broadcast-to-all
```

List clients via HTTP:
```bash
curl http://127.0.0.1:8000/clients
```

### Graceful shutdown

The app installs signal handlers for `SIGINT` and `SIGTERM`. On the first signal:

- A `ShutdownCoordinator` starts a background task that periodically checks the number of active WebSocket clients.
- New WebSocket connections are rejected while shutdown is in progress.
- The coordinator waits until either:
  - there are no active clients, or
  - the timeout `FORCED_SHUTDOWN_AFTER_SEC` expires.
- Remaining clients are closed politely (code `1001`), and then the underlying server is instructed to exit (`app.state.server.handle_exit(...)`).

On final app shutdown (lifespan teardown), the service also attempts to disconnect any remaining clients to ensure cleanup.


