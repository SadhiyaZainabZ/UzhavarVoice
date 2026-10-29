
import json
import time

from google import genai
from google.genai import types

from app.config import Settings

# Illustrative default rates; configure current provider rates for cost estimates.
DEFAULT_INPUT_COST_PER_MILLION = 0.0
DEFAULT_OUTPUT_COST_PER_MILLION = 0.0


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
                result = _generate(client, model, message, settings)
                result["fallback_used"] = model_index > 0

                input_rate = float(
                    getattr(
                        settings,
                        "input_cost_per_million",
                        DEFAULT_INPUT_COST_PER_MILLION,
                    )
                )
                output_rate = float(
                    getattr(
                        settings,
                        "output_cost_per_million",
                        DEFAULT_OUTPUT_COST_PER_MILLION,
                    )
                )

                result["estimated_cost_usd"] = (
                    result["input_tokens"] * input_rate
                    + result["output_tokens"] * output_rate
                ) / 1_000_000

                return result

            except Exception as exc:
                last_error = exc
                if attempt < settings.max_retries:
                    time.sleep(min(2**attempt, 4))

    raise RuntimeError(
    f"Both Gemini model attempts failed. "
    f"Last error: {type(last_error).__name__}: {last_error}"
) from last_error
