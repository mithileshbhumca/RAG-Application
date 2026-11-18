from uuid import NAMESPACE_DNS, uuid5

from app.chunking.models.contracts import Chunk, ChunkingConfig, ChunkingResult, ParentChunk
from app.knowledge.models.contracts import NormalizedDocument


class HierarchicalChunkingStrategy:
    name = "hierarchical"

    def chunk(self, document: NormalizedDocument, config: ChunkingConfig) -> ChunkingResult:
        parents = []
        children = []

        for section_index, section in enumerate(document.sections):
            parent_id = self._id(document.document_id, "parent", section_index)
            parent = ParentChunk(
                chunk_id=parent_id,
                document_id=document.document_id,
                section_id=section.section_id,
                content=section.content,
                page_numbers=section.page_numbers,
                heading_context=section.heading,
                metadata={
                    "source_file": document.source_file,
                    "document_type": document.document_type,
                    "extraction_method": section.source.extraction_method,
                    "processor_name": section.source.processor_name,
                },
            )

            text = section.content
            start = 0
            child_index = 0
            while start < len(text):
                end = min(start + config.child_size, len(text))
                child_content = text[start:end]
                child_id = self._id(parent_id, "child", child_index)
                child = Chunk(
                    chunk_id=child_id,
                    document_id=document.document_id,
                    parent_id=parent_id,
                    section_id=section.section_id,
                    content=child_content,
                    page_numbers=section.page_numbers,
                    heading_context=section.heading,
                    metadata=parent.metadata,
                )
                children.append(child)
                parent.child_ids.append(child_id)
                child_index += 1
                if end == len(text):
                    break
                start = max(end - config.overlap, start + 1)

            if not text:
                parent.child_ids = []
            parents.append(parent)

        for table_index, table in enumerate(document.tables):
            table_id = self._id(document.document_id, "table", table_index)
            markdown = str(table.get("markdown", ""))
            if markdown:
                parents.append(ParentChunk(
                    chunk_id=table_id,
                    document_id=document.document_id,
                    content=markdown,
                    content_type="table",
                    metadata={
                        "source_file": document.source_file,
                        "document_type": document.document_type,
                    },
                ))

        return ChunkingResult(parents=parents, children=children)

    @staticmethod
    def _id(*parts: object) -> str:
        identity = "|".join(str(part) for part in parts)
        return "chunk_" + str(uuid5(NAMESPACE_DNS, identity))[:20]
