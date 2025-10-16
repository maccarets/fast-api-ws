from fastapi import Request
from starlette.websockets import WebSocket

from .services.clients import WebSocketClients

def getWsClients_http(request: Request) -> WebSocketClients:
    """Get WebSocket clients manager for HTTP routes."""
    return request.app.state.wsClients


def getWsClients_ws(websocket: WebSocket) -> WebSocketClients:
    """Get WebSocket clients manager for WebSocket routes."""
    return websocket.app.state.wsClients