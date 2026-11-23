# Document module

## Responsibility and implementation

The document module classifies a stored file and estimates basic processing needs.
`DocumentAnalyzer` in
[`app/document/analyzer/analyzer.py`](../../app/document/analyzer/analyzer.py)
uses the source path suffix to assign a format. For PDFs it uses PyMuPDF to count
pages, native text characters, embedded images, and drawing objects. It uses
thresholds on aggregate native text to decide whether the PDF is scanned, estimates
text density, and recommends processor names. For image files it uses Pillow to
read dimensions and marks the input as scanned.

[`app/document/models/contracts.py`](../../app/document/models/contracts.py)
defines the Pydantic result and dimensions contracts. At present, `contains_tables`
is not detected and remains false; drawing presence only raises layout complexity
to medium and does not prove a table exists. Scanned status is document-wide, not
page-specific.

## Libraries

- **PyMuPDF** (`pymupdf`) inspects PDF text, pages, images, drawings, and geometry.
- **Pillow** (`PIL`) reads image dimensions.
- **Pydantic** types the analysis result.

## Alternatives

PyMuPDF is a good local PDF foundation. A specialized layout/document AI service
can identify reading order, tables, figures, and page regions, but adds network,
cost, privacy, and provider dependencies.

## Production enhancements

- Detect scanned/text/image content per page rather than using an aggregate
  document-level threshold.
- Track image and text regions with bounding boxes; detect tables using a dedicated
  layout/table stage instead of inferring them from drawings.
- Handle encrypted, malformed, oversized, and adversarial PDFs with explicit
  resource limits and observable errors.
- Keep analysis deterministic and test mixed, scanned, empty, and rotated pages.
- Preserve the media type and content validation result alongside extension-based
  classification.
