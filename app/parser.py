from pathlib import Path

import pytesseract
from bs4 import BeautifulSoup
from pdf2image import convert_from_path
from pypdf import PdfReader

RAW_DIR = Path("data/raw")

TESSERACT_CMD = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

POPPLER_PATH = (
    r"C:\Users\Admin\Downloads\Release-26.09.0-0"
    r"\poppler-26.09.0\Library\bin"
)

OCR_LANGUAGE = "tam+eng"
OCR_DPI = 300


def is_valid_text(text: str) -> bool:
    """Check whether extracted PDF text is reasonably readable."""
    if not text or not text.strip():
        return False

    replacement_count = (
        text.count("\x00") + text.count("\ufffd")
    )

    return (
        replacement_count == 0
        and len(text.strip()) >= 30
    )


def parse_html(file_path: Path) -> list[dict]:
    """Extract HTML text while preserving section headings and labels."""

    records = []

    soup = BeautifulSoup(
        file_path.read_text(
            encoding="utf-8",
            errors="replace",
        ),
        "html.parser",
    )

    # Remove unnecessary elements.
    for tag in soup(
        [
            "script",
            "style",
            "noscript",
            "nav",
            "header",
            "footer",
            "aside",
        ]
    ):
        tag.decompose()

    # Remove common navigation and sidebar elements.
    for tag in soup.select(
        ".menu, .navigation, .navbar, .sidebar, "
        "#menu, #navigation, #sidebar, "
        "#templatemo_header, #templatemo_sidebar"
    ):
        tag.decompose()

    # Select the actual TNAU content area.
    content = (
        soup.find(id="templatemo_content")
        or soup.find("main")
        or soup.find("article")
        or soup.body
        or soup
    )

    current_heading = "General"

    elements = content.find_all(
        [
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "p",
            "li",
        ]
    )

    for element in elements:
        text = element.get_text(" ", strip=True)

        if not text or len(text) < 3:
            continue

        # Standard HTML headings.
        if element.name in {
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
        }:
            heading_text = text.rstrip(":").strip()

            if heading_text:
                current_heading = heading_text

            continue

        # Standalone bold paragraph headings.
        if element.name == "p":
            bold_label = element.find(
                ["strong", "b"],
                recursive=False,
            )

            if (
                bold_label
                and len(element.find_all(["strong", "b"])) == 1
                and bold_label.get_text(" ", strip=True) == text
            ):
                heading_text = text.rstrip(":").strip()

                if heading_text:
                    current_heading = heading_text

                continue

        # Bold labels inside list items.
        if element.name == "li":
            label = element.find(
                ["strong", "b"],
                recursive=False,
            )

            if label:
                label_text = label.get_text(
                    " ",
                    strip=True,
                )

                label_text = label_text.rstrip(":").strip()

                # Use the label only if it contains actual text.
                item_heading = label_text or current_heading

            else:
                item_heading = current_heading

        else:
            item_heading = current_heading

        # Final fallback: every HTML record must have a heading.
        final_heading = (
            item_heading
            or current_heading
            or "General"
        )

        records.append(
            {
                "text": text,
                "source": file_path.name,
                "file_type": "html",
                "page": None,
                "heading": final_heading,
                "extraction_method": "html",
            }
        )

    return records


def extract_pdf_ocr(
    file_path: Path,
    page_number: int,
) -> str:
    """Extract Tamil and English text from one PDF page using OCR."""

    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

    images = convert_from_path(
        str(file_path),
        first_page=page_number,
        last_page=page_number,
        dpi=OCR_DPI,
        poppler_path=POPPLER_PATH,
    )

    if not images:
        return ""

    return pytesseract.image_to_string(
        images[0],
        lang=OCR_LANGUAGE,
    ).strip()


def parse_pdf(file_path: Path) -> list[dict]:
    """Extract PDF text, using OCR for unreliable text encoding."""

    records = []

    reader = PdfReader(str(file_path))

    # This PDF has corrupted Tamil Unicode mappings.
    force_ocr = (
        file_path.name == "Tamil%20Manual%20Final%20Book.pdf"
    )

    for page_number, page in enumerate(
        reader.pages,
        start=1,
    ):
        text = page.extract_text() or ""
        method = "text"

        # Use OCR when text extraction is unreliable.
        if force_ocr or not is_valid_text(text):
            try:
                text = extract_pdf_ocr(
                    file_path,
                    page_number,
                )

                method = "ocr"

            except Exception as error:
                print(
                    f"OCR failed: {file_path.name}, "
                    f"page {page_number}: {error}"
                )

                continue

        if not text.strip():
            print(
                f"Empty page skipped: "
                f"{file_path.name}, page {page_number}"
            )

            continue

        records.append(
            {
                "text": text.strip(),
                "source": file_path.name,
                "file_type": "pdf",
                "page": page_number,
                "heading": None,
                "extraction_method": method,
            }
        )

    return records


def parse_document(file_path: Path) -> list[dict]:
    """Parse a supported HTML or PDF document."""

    suffix = file_path.suffix.lower()

    if suffix in {".html", ".htm"}:
        return parse_html(file_path)

    if suffix == ".pdf":
        return parse_pdf(file_path)

    return []


def parse_all_documents(
    directory: Path = RAW_DIR,
) -> list[dict]:
    """Parse all supported documents in a directory."""

    all_records = []

    if not directory.exists():
        print(f"Directory not found: {directory}")
        return all_records

    for file_path in sorted(directory.iterdir()):
        if not file_path.is_file():
            continue

        try:
            records = parse_document(file_path)

            all_records.extend(records)

            ocr_count = sum(
                record["extraction_method"] == "ocr"
                for record in records
            )

            print(
                f"{file_path.name}: "
                f"{len(records)} records extracted "
                f"({ocr_count} OCR)"
            )

        except Exception as error:
            print(
                f"ERROR: {file_path.name}: {error}"
            )

    return all_records


if __name__ == "__main__":
    records = parse_all_documents()

    print("\nParsing completed")

    print(
        f"Total records extracted: {len(records)}"
    )

    html_records = [
        record
        for record in records
        if record["file_type"] == "html"
    ]

    pdf_records = [
        record
        for record in records
        if record["file_type"] == "pdf"
    ]

    print(
        f"HTML records: {len(html_records)}"
    )

    print(
        f"PDF records: {len(pdf_records)}"
    )

    print(
        "PDF records using OCR:",
        sum(
            record["extraction_method"] == "ocr"
            for record in pdf_records
        ),
    )

    print(
        "PDF records using text extraction:",
        sum(
            record["extraction_method"] == "text"
            for record in pdf_records
        ),
    )

    missing_headings = [
        record
        for record in html_records
        if not record["heading"]
    ]

    missing_sources = [
        record
        for record in records
        if not record["source"]
    ]

    missing_pdf_pages = [
        record
        for record in pdf_records
        if not record["page"]
    ]

    print(
        "HTML records with missing headings:",
        len(missing_headings),
    )

    print(
        "Records with missing sources:",
        len(missing_sources),
    )

    print(
        "PDF records with missing page numbers:",
        len(missing_pdf_pages),
    )