
import json
import logging
import time

from google import genai
from google.genai import types

from app.config import Settings
from app.cost import log_call

logger = logging.getLogger(__name__)


def _generate(client, model: str, message: str, settings: Settings) -> dict:
    response = client.models.generate_content(
        model=model,
        contents=message,
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are a helpful agricultural information assistant. "
                "Answer clearly and safely. Return JSON only with one string field named answer."
            ),
            response_mime_type="application/json",
            response_schema={
                "type": "OBJECT",
                "properties": {"answer": {"type": "STRING"}},
                "required": ["answer"],
            },
            http_options=types.HttpOptions(
                timeout=int(settings.request_timeout * 1000)
            ),
        ),
    )

    payload = json.loads(response.text or "{}")
    usage = response.usage_metadata

    input_tokens = getattr(usage, "prompt_token_count", 0) or 0
    output_tokens = getattr(usage, "candidates_token_count", 0) or 0

    return {
        "answer": str(payload.get("answer", "")),
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }


def chat(message: str, settings: Settings) -> dict:
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    client = genai.Client(api_key=settings.gemini_api_key)
    models = [settings.gemini_model, settings.fallback_model]
    last_error = None

    for model_index, model in enumerate(models):
        for attempt in range(settings.max_retries + 1):
            try:
                start_time = time.perf_counter()

                result = _generate(client, model, message, settings)

                latency_ms = (time.perf_counter() - start_time) * 1000
                result["fallback_used"] = model_index > 0

                input_rate = settings.input_cost_per_million
                output_rate = settings.output_cost_per_million

                result["estimated_cost_usd"] = (
                    result["input_tokens"] * input_rate
                    + result["output_tokens"] * output_rate
                ) / 1_000_000

                try:
                    log_call(
                        settings.cost_log_path,
                        provider="gemini",
                        model=model,
                        usage={
                            "input_tokens": result["input_tokens"],
                            "output_tokens": result["output_tokens"],
                        },
                        latency_ms=latency_ms,
                        price_in_per_m=input_rate,
                        price_out_per_m=output_rate,
                        ok=True,
                        fallback_used=result["fallback_used"],
                    )
                except Exception as log_error:
                    logger.warning(
                        "Cost logging failed: %s",
                        type(log_error).__name__,
                    )

                return result

            except Exception as exc:
                last_error = exc

                if attempt < settings.max_retries:
                    time.sleep(min(2**attempt, 4))

    raise RuntimeError(
        f"Both Gemini model attempts failed. "
        f"Last error: {type(last_error).__name__}: {last_error}"
    ) from last_error
