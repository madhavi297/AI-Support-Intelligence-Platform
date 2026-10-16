"""
Vector retrieval engine for RAG pipeline.
Computes cosine similarity between queries and knowledge base chunks.
Returns ranked passages and structured citations.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.config import settings
from app.schemas import Citation
from app.services.document_ingestion import DocumentIngestionService, KnowledgeChunk


class KnowledgeRetrieverService:
    """
    In-memory vector retriever using TF-IDF and Cosine Similarity.
    Provides fast, deterministic, zero-dependency semantic retrieval.
    """

    def __init__(self):
        self.ingestion_service = DocumentIngestionService()
        self.chunks: List[KnowledgeChunk] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.chunk_vectors = None
        self.reindex()

    def reindex(self) -> int:
        """
        Reloads all knowledge base documents and rebuilds the vector index.
        Returns the number of indexed chunks.
        """
        self.chunks = self.ingestion_service.load_and_chunk_documents()
        if not self.chunks:
            self.vectorizer = None
            self.chunk_vectors = None
            return 0

        # Create corpus: combine section title and chunk body for rich context
        corpus = [f"{c.section_title} {c.text}" for c in self.chunks]

        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True
        )
        self.chunk_vectors = self.vectorizer.fit_transform(corpus)
        return len(self.chunks)

    def total_chunks(self) -> int:
        """Returns the total number of indexed knowledge chunks."""
        return len(self.chunks)

    def search(self, query: str, top_k: int = None, threshold: float = None) -> List[Citation]:
        """
        Retrieves top-K knowledge chunks most similar to the query.
        
        Args:
            query: User ticket text or search query
            top_k: Number of passages to return (defaults to settings.TOP_K_RETRIEVAL)
            threshold: Minimum cosine similarity required (defaults to settings.SIMILARITY_THRESHOLD)
            
        Returns:
            List of Citation objects with source, section, score, and text.
        """
        if top_k is None:
            top_k = settings.TOP_K_RETRIEVAL
        if threshold is None:
            threshold = settings.SIMILARITY_THRESHOLD

        if not self.chunks or self.vectorizer is None or self.chunk_vectors is None:
            return []

        query = query.strip()
        if not query:
            return []

        # Vectorize query
        query_vec = self.vectorizer.transform([query])

        # Compute cosine similarity
        similarities = cosine_similarity(query_vec, self.chunk_vectors)[0]

        # Rank indices by descending similarity
        ranked_indices = np.argsort(similarities)[::-1]

        citations: List[Citation] = []
        for idx in ranked_indices:
            score = float(similarities[idx])
            if score < threshold:
                break  # Below similarity threshold

            chunk = self.chunks[idx]
            citations.append(
                Citation(
                    source=chunk.source_doc,
                    section=chunk.section_title,
                    score=round(score, 4),
                    text=chunk.text
                )
            )

            if len(citations) >= top_k:
                break

        return citations


# Global singleton instance
_retriever_instance: Optional[KnowledgeRetrieverService] = None


def get_retriever() -> KnowledgeRetrieverService:
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = KnowledgeRetrieverService()
    return _retriever_instance
