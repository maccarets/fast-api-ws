# --- config ---


import asyncio
import logging
import os
import signal
import time
from typing import Union

from fastapi import FastAPI

from app.services.clients import WebSocketClients

# FORCED_SHUTDOWN_AFTER_SEC = 30 * 60   # 30 minutes
FORCED_SHUTDOWN_AFTER_SEC = 3   # 3 cecs
PROGRESS_LOG_EVERY_SEC    = 5         # log every 5s during shutdown wait

log = logging.getLogger("ws-service")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Shared in this worker (each uvicorn worker has its own process & instance)
class ShutdownCoordinator:
    def __init__(self):
        self._shutdown_started                  = False
        self._gate                              = asyncio.Event()
        self._task: Union[asyncio.Task , None]  = None

    def started(self) -> bool:
        return self._shutdown_started

    def gate(self) -> asyncio.Event:
        return self._gate

    def start(self, app: FastAPI):
        print("Shutting down coordinator")
        if self._shutdown_started:
            return
        self._shutdown_started  = True
        self._task              = asyncio.create_task(self._wait_until_safe_to_exit(app), name="graceful_shutdown_waiter")

    async def _wait_until_safe_to_exit(self, app: FastAPI):
        """Wait until no active clients OR timeout (30min). Log progress."""
        webSocketClietns: WebSocketClients = app.state.wsClients

        start           = time.time()
        deadline        = start + FORCED_SHUTDOWN_AFTER_SEC

        # stop accepting NEW connections if you implement such switch in your webSocketClietns (optional)
        # webSocketClietns.freeze_accepting_new()

        print("_wait_until_safe_to_exitr")

        while True:
            print("1")

            active      = await webSocketClietns.count()  # implement a fast, non-async count() in your webSocketClietns; or await if async
            print("2")

            now         = time.time()
            remaining   = max(0, int(deadline - now))
            print("2")

            if active == 0:
                log.info("[shutdown] No active clients → proceeding to exit.")
                break

            if now >= deadline:
                log.warning("[shutdown] Timeout reached (%ss). Forcing exit with %d active client(s).",
                            FORCED_SHUTDOWN_AFTER_SEC, active)
                break

            log.info("[shutdown] Waiting: active=%d, time_left=%ss", active, remaining)
            await asyncio.sleep(PROGRESS_LOG_EVERY_SEC)

        # Optionally close remaining sockets politely
        try:
            print(5)
            for websocketClient in await webSocketClietns.snapshot():  # or await webSocketClietns.listIds()
                try:
                    print(6)

                    await webSocketClietns.disconnectClient(websocketClient, code=1001)  # implement graceful closer
                except Exception:
                    pass
            print(5555)

        except Exception:
            pass

        self._gate.set()
        print(6666)

    @property
    def is_started(self) -> bool:
        return self._shutdown_started




def _install_signal_handlers(app: FastAPI):
    """Ensure we kick off the graceful waiter on SIGINT/SIGTERM."""

    shutdown_coordinator = app.state.shutdown_coordinator


    loop = asyncio.get_running_loop()

    def _trigger(sig_name: str):
        if not shutdown_coordinator.started():
            log.warning("Received %s → starting graceful shutdown (worker PID=%s)", sig_name, str(os.getpid()) if 'os' in globals() else "?")
            shutdown_coordinator.start(app)

    try:
        loop.add_signal_handler(signal.SIGINT, _trigger, "SIGINT")
        loop.add_signal_handler(signal.SIGTERM, _trigger, "SIGTERM")
    except NotImplementedError:
        # Windows or limited envs: signals not available
        pass