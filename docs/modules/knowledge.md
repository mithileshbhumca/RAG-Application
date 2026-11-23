# Knowledge module

## Responsibility and implementation

The knowledge module converts processor outputs into normalized document records
and optionally extracts structured metadata.

[`app/knowledge/normalization/normalizer.py`](../../app/knowledge/normalization/normalizer.py)
turns each processor text block into a `DocumentSection` with a
`SourceReference` containing document ID, source path, page, section, processor,
and extraction method. It carries tables and images forward as dictionaries with
processor and extraction-method fields. It does not currently interpret image
contents, infer figure captions, or structurally extract PDF tables.

[`app/knowledge/extraction/extractor.py`](../../app/knowledge/extraction/extractor.py)
optionally sends up to 12,000 characters of joined section text to a configured
LLM for `DocumentEnrichment`. The prompt in
[`app/llm/prompts/enrichment.py`](../../app/llm/prompts/enrichment.py) treats
document text as untrusted. When disabled, it returns an empty enrichment. It also
currently returns empty enrichment for selected provider/validation errors, so
failure is not fully observable in ingestion status.

## Libraries

**Pydantic** defines normalized content and source contracts. **httpx** is used by
the extractor to recognize provider HTTP errors.

## Alternatives

Normalization can remain an application-owned contract while each format uses
separate extraction adapters. Structured metadata may use deterministic rules or
an LLM with schema validation. Do not expose third-party parser objects beyond
their adapters.

## Production enhancements

- Replace untyped content dictionaries with validated table, image, and layout
  contracts, including bounding boxes and page provenance.
- Make enrichment failures and skipped work visible in logs/status while keeping
  enrichment non-blocking when policy allows.
- Bound prompt size by tokens and redact sensitive content as required.
- Add OCR/layout and vision-derived figure descriptions only as explicit,
  optional processors with source/model provenance.
- Treat all extracted text as untrusted data; do not follow embedded instructions.
