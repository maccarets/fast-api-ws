from fastapi import Request
from starlette.websockets import WebSocket

from .services.clients import WebSocketClients

# For HTTP routes
def getWsClients_http(request: Request) -> WebSocketClients:
    return request.app.state.wsClients  # created in lifespan


# For WebSocket routes
def getWsClients_ws(websocket: WebSocket) -> WebSocketClients:
    return websocket.app.state.wsClients