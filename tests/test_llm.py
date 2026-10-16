"""
Unit tests for Grounded LLM Response Generator and Offline Fallback.
"""

from app.services.llm_service import get_llm_service
from app.schemas import Citation


def test_llm_grounded_mock_generation():
    llm = get_llm_service()
    cite = Citation(
        source="billing_policy.md",
        section="Section 1: Double Charges",
        score=0.9,
        text="Our billing department initiates an immediate refund for duplicate charges within 3 business days."
    )
    result = llm.generate_draft(
        ticket_code="TCK-9999",
        title="Double Charge",
        description="Charged twice",
        citations=[cite]
    )

    assert result.ticket_code == "TCK-9999"
    assert "AI-Generated Draft" in result.draft_response
    assert "Section 1: Double Charges" in result.draft_response
    assert len(result.citations) == 1


def test_llm_generation_without_citations():
    llm = get_llm_service()
    result = llm.generate_draft(
        ticket_code="TCK-8888",
        title="Unknown topic",
        description="Something completely undocumented",
        citations=[]
    )

    assert result.ticket_code == "TCK-8888"
    assert "does not contain sufficient details" in result.draft_response
    assert "escalated" in result.draft_response.lower()
