"""
Document Ingestion and Chunking service for RAG pipeline.
Parses markdown knowledge-base articles into structured chunks with rich metadata.
"""

import re
from pathlib import Path
from typing import List, Dict, Any
from app.config import settings


class KnowledgeChunk:
    """Represents a chunk of text from the knowledge base."""
    def __init__(self, chunk_id: str, source_doc: str, section_title: str, text: str):
        self.chunk_id = chunk_id
        self.source_doc = source_doc
        self.section_title = section_title
        self.text = text.strip()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "source_doc": self.source_doc,
            "section_title": self.section_title,
            "text": self.text
        }


class DocumentIngestionService:
    """
    Ingests markdown documents from data/knowledge_base/ and splits them into clean chunks.
    """

    def __init__(self, kb_dir: Path = settings.KNOWLEDGE_BASE_DIR):
        self.kb_dir = kb_dir

    def load_and_chunk_documents(self) -> List[KnowledgeChunk]:
        """
        Reads all markdown files in the knowledge base directory and splits
        them based on markdown section headers (## Header).
        
        Returns:
            List of KnowledgeChunk objects with source metadata.
        """
        chunks: List[KnowledgeChunk] = []
        if not self.kb_dir.exists():
            print(f"[DocumentIngestion] Knowledge base directory does not exist: {self.kb_dir}")
            return chunks

        md_files = list(self.kb_dir.glob("*.md"))
        print(f"[DocumentIngestion] Found {len(md_files)} knowledge base files.")

        chunk_counter = 1
        for file_path in md_files:
            filename = file_path.name
            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception as e:
                print(f"[DocumentIngestion] Error reading {filename}: {e}")
                continue

            # Split document by markdown section headers (## Header)
            sections = re.split(r'\n(?=##\s+)', content)
            doc_title = filename

            # First section might have document title (# Title)
            for idx, sec in enumerate(sections):
                lines = sec.strip().split("\n")
                if not lines:
                    continue

                # Detect header
                first_line = lines[0].strip()
                if first_line.startswith("#"):
                    header = first_line.lstrip("#").strip()
                    body = "\n".join(lines[1:]).strip()
                else:
                    header = f"General Overview - Part {idx + 1}"
                    body = sec.strip()

                if body:
                    chunk_id = f"CHK-{chunk_counter:03d}"
                    chunks.append(
                        KnowledgeChunk(
                            chunk_id=chunk_id,
                            source_doc=filename,
                            section_title=header,
                            text=body
                        )
                    )
                    chunk_counter += 1

        print(f"[DocumentIngestion] Successfully ingested {len(chunks)} chunks across {len(md_files)} documents.")
        return chunks
