# UzhavarVoice Dataset

## Purpose
This dataset supports UzhavarVoice, an agricultural assistance project focused on banana and paddy cultivation information for farmers.

## Data Source
- Source: Tamil Nadu Agricultural University (TNAU) Agritech Portal
- Website: https://agritech.tnau.ac.in/
- Collection date: 2026-10-23
- Topics: Banana cultivation, irrigation, pests and diseases, paddy cultivation, rice ecosystems, and Tamil agricultural resources.
- Languages: English and Tamil-oriented sources. The language of each file must be verified before use.

## Collection Summary
- HTML files collected: 20
- PDF files collected: 2
- Total files: 22
- PDF pages: 97
- Counting result: 117 units using `python tools/count_pages.py` (each HTML file counts as one unit and each PDF page counts individually).

## File Inventory
The file-level inventory, source URLs, download dates, byte sizes, and SHA-256 hashes are recorded in `data/manifest.csv`.

All downloaded files are stored in `data/raw/`. The raw dataset should not be committed to Git.

## Licence and Terms
The source is the TNAU Agritech Portal. The applicable licence, copyright conditions, and reuse terms have not yet been fully verified for every downloaded file. These must be checked before redistribution or public reuse.

Collection must respect the source website's terms and `robots.txt`. Restricted URLs must not be downloaded in violation of those restrictions.

## Extraction and Validation Notes
- `Brochure-tamil.pdf` did not yield extractable text during the initial check and may be scanned or image-based.
- Text extraction from `Tamil Manual Final Book.pdf` requires validation before the content is used.
- HTML content, language labels, file integrity, and relevance should be checked before ingestion.
- Any inaccessible, broken, or restricted sources should be documented rather than silently treated as successful downloads.

## Rebuilding the Dataset
1. Review the source URLs listed in `urls.txt`.
2. Check the source terms and `robots.txt` before downloading.
3. Run the downloader from the project root:

   `python .\tests\tools\download.py .\urls.txt`

4. Review `data/manifest.csv` and verify the downloaded files.
5. Count the collected HTML files and PDF pages:

   `python tools/count_pages.py`

## Sample Data
The permitted sample files belong in `data/sample/`. Add 2–3 suitable files only after checking the applicable terms. The sample folder has not yet been populated with these files.