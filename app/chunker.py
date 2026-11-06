def chunk_records(
    records: list[dict],
    chunk_size: int = 1800,
    overlap: int = 250,
) -> list[dict]:
    """Group parsed records and split them into overlapping chunks."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size")

    grouped = {}

    for record in records:
        text = record.get("text", "").strip()

        if not text:
            continue

        key = (
            record["source"],
            record["file_type"],
            record.get("page"),
            record.get("heading") or "General",
            record["extraction_method"],
        )

        grouped.setdefault(key, []).append(text)

    chunks = []

    for key, texts in grouped.items():
        source, file_type, page, heading, extraction_method = key
        content = "\n".join(texts).strip()

        start = 0

        while start < len(content):
            end = min(start + chunk_size, len(content))

            # Prefer splitting at a word boundary.
            if end < len(content):
                boundary = content.rfind(" ", start, end)

                if boundary > start:
                    end = boundary

            chunk_text = content[start:end].strip()

            if chunk_text:
                chunks.append({
                    "text": chunk_text,
                    "source": source,
                    "file_type": file_type,
                    "page": page,
                    "heading": heading,
                    "extraction_method": extraction_method,
                })

            if end >= len(content):
                break

            start = end - overlap

    return chunks
