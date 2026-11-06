
import time
from pathlib import Path

from google.genai.errors import ClientError

from app.chunker import chunk_records
from app.database import (
    get_existing_chunk_hashes,
    initialize_document_chunks_table,
    store_document_chunks,
)
from app.embeddings import BATCH_SIZE, generate_embeddings
from app.parser import parse_all_documents

RAW_DIR = Path("data/raw")
CHUNK_SIZE = 1800
CHUNK_OVERLAP = 250
BATCH_DELAY = 65
MAX_RETRIES = 5


def main():
    print("\n=== UzhavarVoice Document Ingestion ===")

    if not RAW_DIR.exists():
        raise FileNotFoundError(f"Dataset directory not found: {RAW_DIR}")

    files = [
        path for path in RAW_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in {".html", ".pdf"}
    ]

    print(f"\nSource files found: {len(files)}")

    print("\nStep 1: Parsing documents...")
    records = parse_all_documents(RAW_DIR)
    print(f"Parsed records: {len(records)}")

    actual_pdf_pages = sum(
        1 for record in records
        if record.get("file_type") == "pdf"
    )
    print(f"Extracted PDF pages: {actual_pdf_pages}")

    print("\nStep 2: Creating chunks...")
    chunks = chunk_records(
        records,
        chunk_size=CHUNK_SIZE,
        overlap=CHUNK_OVERLAP,
    )
    print(f"Generated chunks: {len(chunks)}")

    print("\nStep 3: Checking database...")
    initialize_document_chunks_table()

    existing_hashes = get_existing_chunk_hashes(chunks)

    pending_chunks = []

    import hashlib

    for chunk in chunks:
        content_hash = hashlib.sha256(
            (
                chunk["source"]
                + str(chunk.get("page"))
                + str(chunk.get("heading"))
                + chunk["text"]
            ).encode("utf-8")
        ).hexdigest()

        if content_hash not in existing_hashes:
            pending_chunks.append(chunk)

    print(f"Already stored: {len(existing_hashes)}")
    print(f"Remaining chunks: {len(pending_chunks)}")

    print("\nStep 4: Generating embeddings and storing...")

    total_inserted = 0

    for start in range(0, len(pending_chunks), BATCH_SIZE):
        batch = pending_chunks[start:start + BATCH_SIZE]

        for attempt in range(MAX_RETRIES):
            try:
                texts = [chunk["text"] for chunk in batch]
                embeddings = generate_embeddings(texts)

                inserted = store_document_chunks(batch, embeddings)
                total_inserted += inserted

                print(
                    f"Processed {min(start + len(batch), len(pending_chunks))}"
                    f"/{len(pending_chunks)} remaining chunks"
                    f" | Inserted: {inserted}"
                )
                break

            except ClientError as error:
                if error.code != 429 or attempt == MAX_RETRIES - 1:
                    raise

                wait_time = 65 * (attempt + 1)

                print(
                    f"Gemini rate limit reached. "
                    f"Waiting {wait_time} seconds before retry..."
                )
                time.sleep(wait_time)

        if start + BATCH_SIZE < len(pending_chunks):
            print(f"Waiting {BATCH_DELAY} seconds for quota...")
            time.sleep(BATCH_DELAY)

    print("\n=== Ingestion Complete ===")
    print(f"Source files: {len(files)}")
    print(f"Extracted PDF pages: {actual_pdf_pages}")
    print(f"Generated chunks: {len(chunks)}")
    print(f"Previously stored: {len(existing_hashes)}")
    print(f"New chunks stored: {total_inserted}")
    print(f"Total stored: {len(existing_hashes) + total_inserted}")


if __name__ == "__main__":
    main()
