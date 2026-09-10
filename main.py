from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from scalar_fastapi import get_scalar_api_reference

from learning.api.router import master_router
from learning.database.session import create_db_tables


@asynccontextmanager
async def lifespan_handler(app: FastAPI):

    print("Starting server...")

    await create_db_tables()

    print("Database ready")
    print("Server started")

    yield

    print("Server stopped")


app = FastAPI(
    title="Shipment Service",
    version="1.0.0",
    lifespan=lifespan_handler,
    servers=[
        {
            "url": "http://127.0.0.1:8000",
            "description": "Local server",
        }
    ],
)


app.include_router(master_router)


@app.get(
    "/scalar",
    response_class=HTMLResponse,
    include_in_schema=False,
)
def get_scalar_docs():

    return get_scalar_api_reference(
        openapi_url="/openapi.json",
        title="Shipment Service API Reference",
    )