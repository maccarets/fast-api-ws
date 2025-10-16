from fastapi import WebSocket, WebSocketDisconnect

from utils.debug import Debug

debug = Debug("WsClient", True)

class WebSocketClient:
    def __init__(self, id: int, websocket:WebSocket):
        self._websocket : WebSocket = websocket
        self.id         : int       = id

    def __repr__(self):
        return f"<WebSocketClient: {self.id}>"

    async def connect(self):
        debug.echo(f"connect()")
        await self._websocket.accept()

    async def disconnect(self, code:int=None):
        debug.echo(f"disconnect()")
        await self._websocket.close(code=code)

    async def send_text(self, message: str):
        debug.echo(f"send_text({message})")
        await self._websocket.send_text(message)

    async def receive(self):
        try:
            while True:
                # Receive message from client
                message = await self._websocket.receive_text()
                debug.echo(f"received: ({message})")

                # Send a response back
                await self._websocket.send_text(f"Server echo: {message}")

        except WebSocketDisconnect:
            print("Client disconnected")

