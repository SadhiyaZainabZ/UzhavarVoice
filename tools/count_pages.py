from pathlib import Path

from pypdf import PdfReader

root = Path(__file__).resolve().parent.parent
raw_dir = root / "data" / "raw"

if not raw_dir.exists():
    raise SystemExit("data/raw folder not found.")

total = 0

for file in sorted(raw_dir.rglob("*")):
    if not file.is_file():
        continue

    if file.suffix.lower() in (".html", ".htm"):
        total += 1
        print(f"{file.name}: 1 file")
    elif file.suffix.lower() == ".pdf":
        try:
            pages = len(PdfReader(str(file)).pages)
            total += pages
            print(f"{file.name}: {pages} pages")
        except Exception as error:
            print(f"{file.name}: could not read PDF: {error}")

print("-" * 35)
print(f"Total count: {total}")
print(f"Requirement of 50 or more: {'MET' if total >= 50 else 'NOT MET'}")
