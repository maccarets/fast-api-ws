import asyncio
import logging
import os
import signal
import time
from typing import Union

from fastapi import FastAPI

from app.config import config
from app.services.clients import WebSocketClients


log = logging.getLogger(config.APP_NAME)


# Shared in this worker (each uvicorn worker has its own process & instance)
class ShutdownCoordinator:
    def __init__(self):
        self._shutdown_started                  = False
        self._task: Union[asyncio.Task , None]  = None

    @property
    def started(self) -> bool:
        return self._shutdown_started


    def start(self, app: FastAPI):
        if self._shutdown_started:
            return

        self._shutdown_started  = True
        self._task              = asyncio.create_task(self._waitUntilSafeToExit(app), name="graceful_shutdown_waiter")

    async def _waitUntilSafeToExit(self, app: FastAPI):
        """Wait until no active clients OR timeout (30min). Log progress."""

        webSocketClietns: WebSocketClients = app.state.wsClients

        start           = time.time()
        deadline        = start + config.FORCED_SHUTDOWN_AFTER_SEC

        while True:

            active      = await webSocketClietns.count()  # implement a fast, non-async count() in your webSocketClietns; or await if async
            now         = time.time()
            remaining   = max(0, int(deadline - now))

            if active == 0:
                log.info("[shutdown] No active clients → proceeding to exit.")
                break

            if now >= deadline:
                log.warning("[shutdown] Timeout reached (%ss). Forcing exit with %d active client(s).",
                            config.FORCED_SHUTDOWN_AFTER_SEC, active)
                break

            log.info("[shutdown] Waiting: active=%d, time_left=%ss", active, remaining)
            await asyncio.sleep(config.PROGRESS_LOG_EVERY_SEC)


        log.info("[shutdown] Force disconnect clients %s", await webSocketClietns.listIds())

        # Optionally close remaining sockets politely
        for websocketClient in await webSocketClietns.snapshot():  # or await webSocketClietns.listIds()

            await webSocketClietns.disconnectClient(websocketClient, code=1001, calledBy="Coordinator")  # implement graceful closer
            log.info("[shutdown] Force disconnected client %s", websocketClient)


        # and crucially, tell uvicorn to begin graceful shutdown:
        app.state.server.handle_exit(getattr(signal, "SIGINT"), None)



def _install_signal_handlers(app: FastAPI):
    """Ensure we kick off the graceful waiter on SIGINT/SIGTERM."""

    shutdown_coordinator    = app.state.shutdown_coordinator
    loop                    = asyncio.get_running_loop()

    def _trigger(sig_name: str):
        if not shutdown_coordinator.started:
            log.warning("Received %s → starting graceful shutdown (worker PID=%s)", sig_name, str(os.getpid()) if 'os' in globals() else "?")
            shutdown_coordinator.start(app)

    try:
        loop.add_signal_handler(signal.SIGINT, _trigger, "SIGINT")
        loop.add_signal_handler(signal.SIGTERM, _trigger, "SIGTERM")
    except NotImplementedError:
        # Windows or limited envs: signals not available
        pass