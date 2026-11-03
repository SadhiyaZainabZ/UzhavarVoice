
import asyncio

from app.config import get_settings
from app.llm.factory import create_provider
from app.llm.types import LLMRequest, Message


async def main():
    llm = create_provider(get_settings())

    request = LLMRequest(
        messages=(
            Message(role="user", content="Hello"),
        ),
        model="examate-fake",
    )

    async for chunk in llm.stream(request):
        print(chunk.text)


asyncio.run(main())
