from app.document.models.contracts import DocumentAnalysisResult
from app.processors.base.contracts import DocumentProcessor


class ProcessorRegistry:
    def __init__(self) -> None:
        self._processors: dict[str, DocumentProcessor] = {}

    def register(self, processor: DocumentProcessor) -> None:
        self._processors[processor.name] = processor

    def for_analysis(self, analysis: DocumentAnalysisResult) -> list[DocumentProcessor]:
        return [
            processor
            for name in analysis.recommended_processors
            if (processor := self._processors.get(name)) is not None
            and processor.supports(analysis)
        ]

    def names(self) -> list[str]:
        return sorted(self._processors)
