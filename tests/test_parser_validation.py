from app import parser


def test_parser_records_have_required_metadata(tmp_path, monkeypatch):
    html_file = tmp_path / "sample.html"

    html_file.write_text(
        """
        <html>
            <body>
                <main>
                    <h1>Paddy Cultivation</h1>
                    <p>Paddy requires sufficient water.</p>
                    <h2>Irrigation</h2>
                    <p>Maintain suitable water levels.</p>
                </main>
            </body>
        </html>
        """,
        encoding="utf-8",
    )

    monkeypatch.setattr(parser, "RAW_DIR", tmp_path)

    records = parser.parse_all_documents(tmp_path)

    assert len(records) > 0

    for record in records:
        assert record["text"].strip()
        assert record["source"]
        assert record["file_type"] == "html"
        assert record["heading"]


def test_parser_preserves_html_headings(tmp_path, monkeypatch):
    html_file = tmp_path / "sample.html"

    html_file.write_text(
        """
        <html>
            <body>
                <main>
                    <h1>Paddy Cultivation</h1>
                    <p>Paddy needs water.</p>
                    <h2>Irrigation</h2>
                    <p>Maintain water levels.</p>
                </main>
            </body>
        </html>
        """,
        encoding="utf-8",
    )

    monkeypatch.setattr(parser, "RAW_DIR", tmp_path)

    records = parser.parse_all_documents(tmp_path)
    headings = {record["heading"] for record in records}

    assert "Paddy Cultivation" in headings
    assert "Irrigation" in headings

