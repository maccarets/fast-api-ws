from fastapi import APIRouter, HTTPException, Depends

from ..deps import getWsClients_http
from ..models.send_body import SendBody
from ..services.clients import WebSocketClients

router = APIRouter()

@router.post("/broadcast-to-all")
async def sendAll(
        body        : SendBody,
        wsClients   : WebSocketClients = Depends(getWsClients_http)
):
    try:
        sent = await wsClients.broadcastToAll(body.message)
        return {"sent": sent}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clients")
async def clients(wsClients: WebSocketClients = Depends(getWsClients_http)):
    try:
        return {"clients": await wsClients.listIds()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
