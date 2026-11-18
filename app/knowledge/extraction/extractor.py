import httpx

from app.knowledge.extraction.contracts import DocumentEnrichment
from app.knowledge.models.contracts import NormalizedDocument
from app.llm.base.contracts import StructuredExtractionRequest
from app.llm.prompts.enrichment import DOCUMENT_ENRICHMENT_TEMPLATE


class KnowledgeExtractor:
    def __init__(self, llm_provider, enabled: bool = False):
        self.llm_provider = llm_provider
        self.enabled = enabled

    async def enrich(self, document: NormalizedDocument) -> DocumentEnrichment:
        if not self.enabled:
            return DocumentEnrichment()

        source_text = "\n\n".join(section.content for section in document.sections)
        source_text = source_text[:12000]
        prompt = DOCUMENT_ENRICHMENT_TEMPLATE.format(document_text=source_text)
        try:
            return await self.llm_provider.extract_structured(
                StructuredExtractionRequest(prompt=prompt),
                DocumentEnrichment,
            )
        except (RuntimeError, ValueError, httpx.HTTPError):
            return DocumentEnrichment()
