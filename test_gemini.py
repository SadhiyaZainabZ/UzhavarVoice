
import asyncio

from app.config import Settings
from app.llm.factory import create_provider
from app.llm.types import LLMRequest, Message


async def main():
    settings = Settings()
    provider = create_provider(settings)

    request = LLMRequest(
        messages=(
            Message(
                role="user",
                content="Reply with exactly: Gemini connection successful"
            ),
        ),
        model=settings.llm_model,
    )

    print("Testing Gemini connection...")

    try:
        async for chunk in provider.stream(request):
            print(chunk.text, end="", flush=True)

        print("\n\nGemini test completed.")

    except Exception as e:
        print("\nGemini test failed:", type(e).__name__, str(e))


if __name__ == "__main__":
    asyncio.run(main())
