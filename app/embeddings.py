from google import genai
from google.genai import types

from app.config import get_settings

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSION = 768
BATCH_SIZE = 50


def get_embedding_client():
    """Create a Gemini client using application settings."""
    settings = get_settings()

    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    return genai.Client(api_key=settings.gemini_api_key)


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for multiple document chunks in batches."""

    if not texts:
        return []

    if any(not text or not text.strip() for text in texts):
        raise ValueError("Cannot embed empty text")

    client = get_embedding_client()
    all_embeddings = []

    for start in range(0, len(texts), BATCH_SIZE):
        batch = texts[start:start + BATCH_SIZE]

        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=batch,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=EMBEDDING_DIMENSION,
            ),
        )

        if not response.embeddings:
            raise RuntimeError("Gemini returned no embeddings")

        if len(response.embeddings) != len(batch):
            raise RuntimeError("Gemini returned an unexpected number of embeddings")

        for item in response.embeddings:
            values = item.values

            if values is None or len(values) != EMBEDDING_DIMENSION:
                raise RuntimeError("Invalid embedding dimension")

            all_embeddings.append([float(value) for value in values])

    return all_embeddings


def generate_embedding(text: str) -> list[float]:
    """Generate an embedding for one text chunk."""
    return generate_embeddings([text])[0]