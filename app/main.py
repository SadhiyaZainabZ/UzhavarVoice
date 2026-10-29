
import json
import logging
from threading import Lock
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from app.config import Settings, get_settings
from app.database import check_database
from app.llm import chat
from app.schemas import ChatRequest, ChatResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="UzhavarVoice", version="0.2.0")

SettingsDep = Annotated[Settings, Depends(get_settings)]

_usage_lock = Lock()

_usage = {
    "requests": 0,
    "input_tokens": 0,
    "output_tokens": 0,
    "estimated_cost_usd": 0.0,
    "fallback_requests": 0,
}


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

    # Check the database first so its failure is reported correctly.
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
    """Return in-memory LLM usage totals."""
    with _usage_lock:
        return dict(_usage)


def _record_usage(result: dict) -> None:
    """Record successful LLM request usage."""
    with _usage_lock:
        _usage["requests"] += 1
        _usage["input_tokens"] += result["input_tokens"]
        _usage["output_tokens"] += result["output_tokens"]
        _usage["estimated_cost_usd"] += result["estimated_cost_usd"]
        _usage["fallback_requests"] += int(result["fallback_used"])


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(body: ChatRequest, settings: SettingsDep):
    """Generate an agricultural answer using the configured LLM."""
    try:
        result = chat(body.message, settings)
    except Exception as exc:
        # Do not expose API keys or internal error details to clients.
        logger.error(
            "LLM request failed: %s: %s",
            type(exc).__name__,
            exc,
        )
        raise HTTPException(
            status_code=502,
            detail="LLM request failed. Check API container logs.",
        ) from exc

    _record_usage(result)

    if not body.stream:
        return result

    # Sends the completed answer in chunks using Server-Sent Events.
    # This is chunked delivery, not true token-by-token LLM streaming.
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
