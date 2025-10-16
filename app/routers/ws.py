from fastapi import APIRouter, WebSocket, Depends, Path, status
from ..deps import getWsClients_ws
from ..services.clients import WebSocketClients
from ..services.client import WebSocketClient

router = APIRouter()

async def send_ws_error_and_close(ws: WebSocket, code: int, message: str):
    # Accept before sending any data (safe with Starlette/FastAPI)
    await ws.accept()
    await ws.send_json({"type": "error", "code": code, "message": message})
    await ws.close(code=code)

@router.websocket("/ws/{clientId}")
async def websocket_endpoint(
        websocket   : WebSocket,
        clientId    : int               = Path(...),
        wsClients   : WebSocketClients  = Depends(getWsClients_ws),
):
    # 1) Duplicate check BEFORE registering
    if await wsClients.is_connected(clientId):
        await send_ws_error_and_close(
            websocket,
            status.WS_1008_POLICY_VIOLATION,      # 1008 = policy violation
            f"Client {clientId} is already connected"
        )
        return

    wsClient = WebSocketClient(clientId, websocket)

    # 2) Register & accept
    await wsClients.connectClient(wsClient)

    try:
        await wsClient.receive()
    finally:
        await wsClients.disconnectClient(wsClient)
