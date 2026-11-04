import pytest

from app.parser import parse_all_documents


@pytest.fixture(scope="module")
def parsed_records():
    """Parse all documents only once for this test module."""
    return parse_all_documents()


def test_parser_records_have_required_metadata(parsed_records):
    assert len(parsed_records) > 0

    for record in parsed_records:
        assert record["text"].strip()
        assert record["source"]
        assert record["file_type"] in {"html", "pdf"}

        if record["file_type"] == "html":
            assert record["heading"]

        if record["file_type"] == "pdf":
            assert record["page"] is not None
            assert record["page"] >= 1


def test_all_pdf_pages_are_preserved(parsed_records):
    pdf_records = [
        record
        for record in parsed_records
        if record["file_type"] == "pdf"
    ]

    assert len(pdf_records) == 97

    for record in pdf_records:
        assert record["page"] is not None
        assert record["page"] >= 1