# Chunking module

## Responsibility and implementation

The chunking module converts normalized text and tables into embedding-sized
records. The `ChunkingStrategy` protocol in
[`app/chunking/strategies/base.py`](../../app/chunking/strategies/base.py)
defines the boundary; `HierarchicalChunkingStrategy` is wired by the API
dependencies.

[`app/chunking/strategies/hierarchical.py`](../../app/chunking/strategies/hierarchical.py)
creates a parent for each normalized section and slices its text into overlapping
children. Defaults in
[`app/chunking/models/contracts.py`](../../app/chunking/models/contracts.py) are
500 characters per child and 100 characters of overlap. IDs are deterministic
UUID5-derived strings. Markdown tables become parent chunks with `content_type:
"table"`; the current implementation does not create table child chunks. The
`parent_size` and `strategy` fields are contract/configuration data but are not
used to select another strategy or constrain parent text in this implementation.

## Libraries

**Pydantic** defines configuration and chunk contracts. The implementation uses
Python standard-library `uuid`; splitting is based on character offsets, not
tokens.

## Alternatives

Token-aware splitting can use the tokenizer associated with the embedding model.
Other strategies include recursive separators, sentence/paragraph boundaries,
semantic segmentation, and layout-aware section splitting. Tables can be split by
rows while repeating headers.

## Production enhancements

- Chunk at semantic boundaries and enforce model token limits.
- Preserve page, section, source, and extraction provenance on every child and table
  chunk.
- Split large tables into bounded row groups with repeated headers.
- Add stable version-aware IDs and tests for overlap, Unicode, empty sections,
  large inputs, and table behavior.
- Measure retrieval quality against representative questions before choosing
  chunk sizes or overlap.
