# Embeddings module

## Responsibility and implementation

The `EmbeddingProvider` protocol in
[`app/embeddings/base/contracts.py`](../../app/embeddings/base/contracts.py)
defines asynchronous document and query embedding methods and typed result/model
metadata.

Two providers are wired through
[`app/api/dependencies.py`](../../app/api/dependencies.py):

- `DeterministicHashEmbeddingProvider` in
  [`app/embeddings/providers/hash.py`](../../app/embeddings/providers/hash.py)
  creates normalized fixed-size vectors from character bytes. It is deterministic
  and lightweight, but it does not encode semantic meaning and is explicitly for
  local demonstration/testing.
- `SentenceTransformerEmbeddingProvider` in
  [`app/embeddings/providers/sentence_transformers.py`](../../app/embeddings/providers/sentence_transformers.py)
  lazily loads a Sentence Transformers model, runs encoding in a worker thread,
  and requests normalized embeddings. The dependency is optional at runtime unless
  selected, despite being declared in the main project dependencies.

The configured provider must produce a consistent vector dimension with the
selected vector collection.

## Libraries

**sentence-transformers** provides the local model adapter. Pydantic types the
provider results; Python `asyncio.to_thread` keeps synchronous model encoding off
the event loop.

## Alternatives

Other options include hosted embedding APIs or alternative local runtimes. Choose
based on language/domain coverage, privacy, latency, throughput, cost, and model
license. Changing models or dimensions requires a deliberate re-embedding and
collection migration plan.

## Production enhancements

- Use a semantically meaningful model; do not use hash vectors for production
  retrieval.
- Pin and record model revisions, dimensions, preprocessing, and normalization.
- Batch work within provider limits, add bounded concurrency, timeouts, retries,
  and metrics.
- Validate the actual model and vector dimension at startup and detect model
  changes before indexing.
- Evaluate retrieval quality on domain-specific queries and document types.
