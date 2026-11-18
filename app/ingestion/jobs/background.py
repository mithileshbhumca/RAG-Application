import asyncio
from uuid import uuid4

from app.core.models.contracts import ProcessingRequest


class BackgroundJobExecutor:
    def __init__(self, on_submit: object | None = None):
        self._jobs: dict[str, asyncio.Task[None]] = {}
        self._on_submit = on_submit

    async def submit(self, document_id: str, request: ProcessingRequest) -> str:
        job_id = str(uuid4())
        task = asyncio.create_task(self._run_placeholder(document_id, request))
        self._jobs[job_id] = task
        return job_id

    async def cancel(self, job_id: str) -> None:
        task = self._jobs.get(job_id)
        if task:
            task.cancel()

    async def _run_placeholder(self, document_id: str, request: ProcessingRequest) -> None:
        await asyncio.sleep(0)
