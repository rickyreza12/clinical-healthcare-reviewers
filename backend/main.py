from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from backend.api.error_handlers import install_error_handlers
from backend.api.routes.review import router
from backend.semantic.settings import semantic_settings
from backend.observability.phoenix import configure_phoenix, shutdown_phoenix


load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    semantic_settings()
    configure_phoenix()
    try:
        yield
    finally:
        shutdown_phoenix()


app = FastAPI(title="Clinical Document Review Assistant", version="1.0.0", lifespan=lifespan)
app.include_router(router)
install_error_handlers(app)


@app.get("/health")
def health():
    return {"status": "ok"}
