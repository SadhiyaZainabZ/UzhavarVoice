
import json
import logging
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from app.config import Settings, get_settings
from app.database import (
    check_database,
    get_usage_totals,
    initialize_usage_table,
    record_usage,
)
from app.llm import chat
from app.schemas import ChatRequest, ChatResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="UzhavarVoice", version="0.2.0")

SettingsDep = Annotated[Settings, Depends(get_settings)]


@app.on_event("startup")
def startup_event():
    """Initialize persistent usage storage."""
    initialize_usage_table()


@app.get("/health")
def health(settings: SettingsDep) -> dict:
    """Liveness check; does not call the LLM or database."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
    }


@app.get("/ready")
def ready(settings: SettingsDep) -> dict:
    """Check database connectivity and Gemini configuration."""

    if not check_database():
        raise HTTPException(
            status_code=503,
            detail="Database is unavailable",
        )

    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=503,
            detail="Gemini API key is not configured",
        )

    return {
        "status": "ready",
        "database": "connected",
    }


@app.get("/usage")
def usage() -> dict:
    """Return persistent LLM usage totals from PostgreSQL."""
    try:
        return get_usage_totals()
    except Exception as exc:
        logger.error(
            "Could not retrieve usage totals: %s",
            type(exc).__name__,
        )
        raise HTTPException(
            status_code=503,
            detail="Usage data is currently unavailable",
        ) from exc


def _record_usage(result: dict) -> None:
    """Persist successful LLM request usage."""
    record_usage(result)


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(body: ChatRequest, settings: SettingsDep):
    """Generate an agricultural answer using the configured LLM."""
    try:
        result = chat(body.message, settings)
    except Exception as exc:
        logger.error(
            "LLM request failed: %s: %s",
            type(exc).__name__,
            exc,
        )
        raise HTTPException(
            status_code=502,
            detail="LLM request failed. Check API container logs.",
        ) from exc

    try:
        _record_usage(result)
    except Exception as exc:
        logger.error(
            "Could not save usage record: %s",
            type(exc).__name__,
        )
        raise HTTPException(
            status_code=503,
            detail="Chat succeeded but usage logging failed.",
        ) from exc

    if not body.stream:
        return result

    # Sends the completed answer in chunks using Server-Sent Events.
    def event_stream():
        answer = result["answer"]
        chunk_size = 40

        for start in range(0, len(answer), chunk_size):
            chunk = answer[start : start + chunk_size]
            yield f"data: {json.dumps({'text': chunk})}\n\n"

        yield (
            f"data: {json.dumps({'done': True, 'model': result['model']})}\n\n"
        )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
    )
