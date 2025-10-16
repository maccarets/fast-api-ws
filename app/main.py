import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .services.clients import WebSocketClients
from .routers import http as http_router
from .routers import ws as ws_router
from .shutdown.coordinator import _install_signal_handlers, ShutdownCoordinator

log = logging.getLogger("ws-service")
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create the per-worker singleton
    app.state.wsClients     = WebSocketClients()
    shutdown_coordinator    = app.state.shutdown_coordinator  = ShutdownCoordinator()

    log.info("WS service started (per-worker singleton initialised).")
    try:
        print("yield")
        yield
    finally:
        print(43223432)
        # If no signal triggered us yet, start graceful waiter now
        if not shutdown_coordinator.started():
            shutdown_coordinator.start(app)

        # Block shutdown until waiter decides it's time (no clients or timeout)
        print(54321)
        await shutdown_coordinator.gate().wait()

        log.info("Worker shutdown complete.")
        # Optionally: ensure manager is fully cleaned up
        try:
            await app.state.wsClients.disconnectAll()

        except Exception:
            pass


app = FastAPI(lifespan=lifespan)
app.include_router(http_router.router)
app.include_router(ws_router.router)
