import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import config
from app.services.clients import WebSocketClients
from app.shutdown.coordinator import ShutdownCoordinator, _install_signal_handlers

log = logging.getLogger(config.APP_NAME)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create the per-worker singleton
    app.state.wsClients            = WebSocketClients()
    app.state.shutdown_coordinator = ShutdownCoordinator()

    _install_signal_handlers(app)


    log.info("WS service started (per-worker singleton initialised).")
    try:
        yield

    finally:
        # Ensure manager is fully cleaned up
        try:
            await app.state.wsClients.disconnectAll()
        except Exception:
            pass
