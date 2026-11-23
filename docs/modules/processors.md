# Processors module

## Responsibility and implementation

Processors are format-specific adapters. `ProcessingRequest`,
`ProcessingResult`, and the `DocumentProcessor` protocol are defined in
[`app/processors/base/contracts.py`](../../app/processors/base/contracts.py).
The registry selects processors by the names recommended by document analysis and
their `supports()` checks.

- [`text/text_processor.py`](../../app/processors/text/text_processor.py):
  PyMuPDF extracts PDF text blocks and page/bounding-box data; `python-docx` reads
  DOCX paragraphs; `python-pptx` reads slide text; other supported paths use UTF-8
  text reading.
- [`tables/table_processor.py`](../../app/processors/tables/table_processor.py):
  `openpyxl` reads XLSX worksheets into Markdown-like table data. Despite accepting
  PDF and DOCX in `supports()`, those formats currently return no tables.
- [`images/image_processor.py`](../../app/processors/images/image_processor.py):
  PyMuPDF extracts embedded PDF images to artifacts; Pillow saves uploaded images.
  This extracts image files but does not describe their visual content.
- [`ocr/ocr_processor.py`](../../app/processors/ocr/ocr_processor.py):
  renders PDF pages with PyMuPDF and invokes the external Tesseract executable.
  Missing Tesseract returns a partial result and warning.
- [`layout/layout_processor.py`](../../app/processors/layout/layout_processor.py):
  emits a basic document-level placeholder, not a real layout or reading-order
  analysis.

## Libraries

The adapters use **PyMuPDF**, **python-docx**, **python-pptx**, **openpyxl**, and
**Pillow**. OCR requires the external **Tesseract** program, called through
Python's `subprocess`.

## Alternatives

Alternative OCR engines include PaddleOCR and managed document-intelligence
services. Layout/table extraction can use specialized local libraries or managed
APIs. Compare languages, table structure, accuracy, latency, deployment, privacy,
and cost before selecting one. Keep each choice behind a processor contract.

## Production enhancements

- Detect capabilities per page and report confidence, warnings, and processing
  errors.
- Implement PDF table extraction and preserve table cells, page, and bounding box.
- Associate captions and figure regions; add optional OCR or vision description
  processors when needed.
- Enforce subprocess timeouts, output-size limits, safe temporary-file cleanup, and
  resource limits for untrusted documents.
- Test mixed native/scanned pages, rotated layouts, malformed files, and extraction
  quality on representative real documents.
