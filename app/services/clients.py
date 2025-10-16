import asyncio
from typing import List, Dict

from app.services.client import WebSocketClient
from utils.debug import Debug

debug = Debug("WebSocketClients", False)

class WebSocketClients:

    def __init__(self):
        self._clients   : Dict[int, WebSocketClient]    = {}
        self._lock      : asyncio.Lock                  = asyncio.Lock()

    def __repr__(self):
        return f"WebSocketClients({self._clients})"


    async def connectClient(self, websocketClient: WebSocketClient):
        await websocketClient.connect()
        async with self._lock:
            self._clients[websocketClient.id] = websocketClient


    async def disconnectClient(self, websocketClient: WebSocketClient, code: int = None, calledBy:str=None):
        debug.echo(f"[disconnect] {calledBy}: {websocketClient.id}")

        await websocketClient.disconnect(code)
        async with self._lock:
            if websocketClient.id in self._clients:
                del self._clients[websocketClient.id]

    async def disconnectAll(self):
        for client in self._clients.values():
            await self.disconnectClient(client, calledBy="disconnectAll")


    async def broadcastToAll(self, message: str) -> int:
        sent = 0
        for clientId, client in list(self._clients.items()):
            try:
                await client.send_text(message)
                sent += 1
            except Exception:
                # Drop broken connections
                self._clients.pop(clientId, None)
        return sent

    async def count(self) -> int:
        async with self._lock:
            return len(self._clients)

    async def listIds(self) -> List[int]:
        async with self._lock:
            return list(self._clients.keys())


    async def snapshot(self) -> List[WebSocketClient]:
        """Get a stable list of clients to iterate without holding the lock."""
        async with self._lock:
            return list(self._clients.values())

    async def is_connected(self, clientId):
        async with self._lock:
            return clientId in self._clients

