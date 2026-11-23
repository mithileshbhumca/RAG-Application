# Ingestion module

## Responsibility and implementation

`IngestionOrchestrator` in
[`app/ingestion/orchestrator/orchestrator.py`](../../app/ingestion/orchestrator/orchestrator.py)
coordinates, but does not implement, analysis, extraction, normalization,
enrichment, chunking, embedding, or vector operations. It loads document metadata,
updates a coarse status through those stages, runs supported processors in series,
writes `normalized.json`, creates parent/child chunks, embeds all resulting chunks,
upserts vector records, saves chunk JSON in SQLite, and marks the ingestion
completed or partial if a processor returned partial status.

The API currently calls this orchestrator synchronously. The
`BackgroundJobExecutor` in
[`app/ingestion/jobs/background.py`](../../app/ingestion/jobs/background.py) is a
placeholder: it creates a task that yields once and does not run ingestion.

## Libraries

The module primarily uses the application's typed contracts and adapters. Python
`pathlib` writes normalized artifacts; `asyncio` appears in the job placeholder.

## Alternatives

For development, a synchronous orchestration service is simple. Production
workloads can use a durable queue and worker system, or a workflow engine when
pipelines need retries, long-running steps, and recovery. Keep provider-specific
logic in adapters rather than putting it in the orchestrator.

## Production enhancements

- Persist stage attempts, errors, durations, and retryability; handle cancellation
  and idempotent retries.
- Move long-running work to a durable background queue and return a job ID to the
  API caller.
- Make writes across SQLite, vector storage, and artifact storage recoverable when
  one stage fails after another has committed.
- Avoid loading every embedding input and vector into memory for large documents;
  batch work with bounded concurrency.
- Add resource/time limits for untrusted files and external processors, and
  document cleanup/version replacement semantics.
