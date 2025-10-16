from fastapi import FastAPI

from .lifespan import lifespan
from .routers import http as http_router
from .routers import ws as ws_router

app = FastAPI(lifespan=lifespan)

app.include_router(http_router.router)
app.include_router(ws_router.router)

