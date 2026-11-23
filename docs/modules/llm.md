# LLM module

## Responsibility and implementation

The LLM module separates contracts and prompts from provider adapters.
[`app/llm/base/contracts.py`](../../app/llm/base/contracts.py) defines text
generation and structured extraction requests, a generic Pydantic schema-based
response contract, and a `VisionProvider`/`VisionRequest` interface.

[`app/llm/providers/ollama.py`](../../app/llm/providers/ollama.py) is the
implemented provider. It calls Ollama's `/api/generate` endpoint using **httpx**,
requests non-streaming output, and validates structured results with Pydantic.
[`app/llm/providers/disabled.py`](../../app/llm/providers/disabled.py) is the
disabled text provider. The vision protocol has no concrete implementation and is
not wired into ingestion. Current LLM use is optional metadata enrichment, not
retrieval-based question answering or image explanation.

## Libraries

**httpx** performs asynchronous HTTP calls. **Pydantic** defines and validates
request/response schemas.

## Alternatives

Keep the provider contract independent from a vendor, then implement an adapter for
the chosen hosted or local model. Select models based on privacy, supported input
modalities, context length, quality, latency, cost, and operational constraints.
An image-Q&A feature requires a vision-capable adapter and a retrieval path that
selects the relevant image.

## Production enhancements

- Add provider-specific timeouts, bounded retries, rate limits, and telemetry.
- Validate structured outputs robustly and surface failures rather than silently
  converting them to success-shaped empty data.
- Apply prompt-injection defenses: document content is untrusted data, not
  instructions.
- Add token budgeting, sensitive-data controls, and model/version provenance.
- Implement vision separately behind the existing typed boundary if image
  questions become a product requirement.
