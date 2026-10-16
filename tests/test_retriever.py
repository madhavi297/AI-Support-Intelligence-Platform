"""
Unit tests for RAG Document Ingestion and Vector Retriever.
"""

from app.services.retriever import get_retriever
from app.services.document_ingestion import DocumentIngestionService


def test_document_ingestion():
    service = DocumentIngestionService()
    chunks = service.load_and_chunk_documents()
    assert len(chunks) >= 4
    for c in chunks:
        assert c.source_doc.endswith(".md")
        assert len(c.text) > 10


def test_vector_retriever_search():
    retriever = get_retriever()
    results = retriever.search("duplicate charge on my credit card invoice", top_k=2)
    assert len(results) > 0
    top = results[0]
    assert "billing" in top.source.lower()
    assert top.score > 0.05


def test_vector_retriever_empty_query():
    retriever = get_retriever()
    results = retriever.search("")
    assert results == []
