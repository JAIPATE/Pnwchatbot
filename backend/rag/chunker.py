"""Document chunking engine for RAG pipelines with semantic section awareness and sliding windows."""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from backend.rag.parser import ParsedDocument, ParsedSection


@dataclass
class DocumentChunk:
    """A granular chunk of text enriched with retrieval metadata."""
    chunk_id: str
    doc_id: str
    document_title: str
    category: str
    source_url: str
    campus: str  # 'Hammond', 'Westville', or 'Both'
    section_title: str
    chunk_index: int
    content: str
    char_count: int = 0
    token_count_estimate: int = 0
    metadata: Dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.char_count:
            self.char_count = len(self.content)
        if not self.token_count_estimate:
            # Standard heuristic: 1 token ~= 4 chars or words * 1.3
            self.token_count_estimate = max(1, len(self.content) // 4)


class TextChunker:
    """Splits parsed documents into contextual chunks with sliding window overlap."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 80):
        """
        Args:
            chunk_size: Target maximum characters per chunk.
            chunk_overlap: Overlap characters between consecutive chunks.
        """
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, doc: ParsedDocument) -> List[DocumentChunk]:
        """Chunks a ParsedDocument using section-aware segmentation."""
        chunks: List[DocumentChunk] = []
        global_index = 0

        # If document has defined sections, chunk section by section
        if doc.sections:
            for section in doc.sections:
                sec_chunks = self._chunk_text(
                    text=section.content,
                    doc=doc,
                    section_title=section.title,
                    start_index=global_index,
                )
                chunks.extend(sec_chunks)
                global_index += len(sec_chunks)
        else:
            chunks = self._chunk_text(
                text=doc.raw_text,
                doc=doc,
                section_title="General",
                start_index=0,
            )

        return chunks

    def chunk_documents(self, docs: List[ParsedDocument]) -> List[DocumentChunk]:
        """Chunks a collection of documents."""
        all_chunks: List[DocumentChunk] = []
        for doc in docs:
            all_chunks.extend(self.chunk_document(doc))
        return all_chunks

    def _chunk_text(
        self,
        text: str,
        doc: ParsedDocument,
        section_title: str,
        start_index: int = 0,
    ) -> List[DocumentChunk]:
        cleaned = re.sub(r"\s+", " ", text).strip()
        if not cleaned:
            return []

        # If text is small enough, keep as single chunk
        if len(cleaned) <= self.chunk_size:
            return [
                DocumentChunk(
                    chunk_id=f"{doc.doc_id}_c{start_index}",
                    doc_id=doc.doc_id,
                    document_title=doc.title,
                    category=doc.category,
                    source_url=doc.source_url,
                    campus=doc.campus,
                    section_title=section_title,
                    chunk_index=start_index,
                    content=cleaned,
                )
            ]

        # Sentence-based boundary splitting
        sentences = re.split(r"(?<=[.!?])\s+", cleaned)
        chunks: List[DocumentChunk] = []
        current_chunk_sentences: List[str] = []
        current_len = 0
        idx = start_index

        for sent in sentences:
            sent_len = len(sent)
            if current_len + sent_len > self.chunk_size and current_chunk_sentences:
                chunk_str = " ".join(current_chunk_sentences).strip()
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"{doc.doc_id}_c{idx}",
                        doc_id=doc.doc_id,
                        document_title=doc.title,
                        category=doc.category,
                        source_url=doc.source_url,
                        campus=doc.campus,
                        section_title=section_title,
                        chunk_index=idx,
                        content=chunk_str,
                    )
                )
                idx += 1

                # Retain sentences for overlap
                overlap_sentences: List[str] = []
                overlap_len = 0
                for s in reversed(current_chunk_sentences):
                    if overlap_len + len(s) <= self.chunk_overlap:
                        overlap_sentences.insert(0, s)
                        overlap_len += len(s)
                    else:
                        break
                current_chunk_sentences = overlap_sentences + [sent]
                current_len = sum(len(s) for s in current_chunk_sentences) + len(current_chunk_sentences)
            else:
                current_chunk_sentences.append(sent)
                current_len += sent_len + 1

        if current_chunk_sentences:
            chunk_str = " ".join(current_chunk_sentences).strip()
            chunks.append(
                DocumentChunk(
                    chunk_id=f"{doc.doc_id}_c{idx}",
                    doc_id=doc.doc_id,
                    document_title=doc.title,
                    category=doc.category,
                    source_url=doc.source_url,
                    campus=doc.campus,
                    section_title=section_title,
                    chunk_index=idx,
                    content=chunk_str,
                )
            )

        return chunks
