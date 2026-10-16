"""
FastAPI route handlers for Knowledge Base and RAG inspection.
Allows searching documents, viewing indexed chunks, and triggering index rebuilds.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Query, status
from app.schemas import Citation
from app.services.retriever import get_retriever

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base & RAG"])


@router.get("/search", response_model=List[Citation])
def search_knowledge(
    query: str = Query(..., min_length=2, description="Search terms to query against knowledge base"),
    top_k: int = Query(3, ge=1, le=10, description="Max passages to retrieve")
):
    """
    Performs vector similarity search over ingested support policies and FAQs.
    """
    retriever = get_retriever()
    return retriever.search(query=query, top_k=top_k)


@router.get("/stats")
def get_knowledge_stats():
    """
    Returns indexing statistics, chunk count, and unique document sources.
    """
    retriever = get_retriever()
    chunks = retriever.chunks
    sources = sorted(list(set(c.source_doc for c in chunks)))

    return {
        "total_chunks": len(chunks),
        "total_documents": len(sources),
        "documents": sources,
        "sample_sections": [f"{c.source_doc} -> {c.section_title}" for c in chunks[:5]]
    }


@router.post("/reindex")
def reindex_knowledge():
    """
    Rebuilds the vector index from markdown files in data/knowledge_base/.
    """
    retriever = get_retriever()
    count = retriever.reindex()
    return {
        "status": "success",
        "message": f"Successfully reindexed {count} knowledge chunks."
    }
