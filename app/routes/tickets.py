"""
FastAPI route handlers for support ticket management and AI processing.
Provides endpoints for ticket creation, listing, ML analysis, human overrides, and LLM drafting.
"""

import json
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.database import get_db_connection, row_to_dict
from app.schemas import (
    TicketCreate,
    TicketUpdate,
    TicketResponse,
    TicketAnalysisResult,
    DraftResponseRequest,
    DraftResponseResult,
    Citation
)
from app.services.classifier import get_classifier
from app.services.priority import PriorityService
from app.services.retriever import get_retriever
from app.services.llm_service import get_llm_service

router = APIRouter(prefix="/tickets", tags=["Tickets"])


def _generate_ticket_code(cursor) -> str:
    """Generates sequential ticket codes such as TCK-1001."""
    cursor.execute("SELECT MAX(id) FROM tickets")
    max_id = cursor.fetchone()[0]
    next_id = (max_id or 0) + 1
    return f"TCK-{1000 + next_id}"


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(payload: TicketCreate):
    """
    Submits a new customer support ticket and persists it to SQLite.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    ticket_code = _generate_ticket_code(cursor)
    now = datetime.utcnow().isoformat()

    cursor.execute("""
        INSERT INTO tickets (ticket_code, title, description, priority, status, citations, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (ticket_code, payload.title.strip(), payload.description.strip(), "Medium", "open", "[]", now, now))

    ticket_id = cursor.lastrowid
    conn.commit()

    cursor.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    row = cursor.fetchone()
    conn.close()

    return row_to_dict(row)


@router.get("", response_model=List[TicketResponse])
def list_tickets(status_filter: Optional[str] = Query(None, description="Filter by status (open, analyzed, resolved)")):
    """
    Retrieves all support tickets ordered by most recent first.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if status_filter:
        cursor.execute("SELECT * FROM tickets WHERE status = ? ORDER BY id DESC", (status_filter,))
    else:
        cursor.execute("SELECT * FROM tickets ORDER BY id DESC")

    rows = cursor.fetchall()
    conn.close()

    return [row_to_dict(row) for row in rows]


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int):
    """
    Fetches a single support ticket by its database ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID {ticket_id} not found."
        )

    return row_to_dict(row)


@router.post("/{ticket_id}/analyze", response_model=TicketAnalysisResult)
def analyze_ticket(ticket_id: int):
    """
    Runs end-to-end AI intelligence on a ticket:
    1. Scikit-learn category prediction & confidence score
    2. Transparent SLA priority heuristic evaluation
    3. RAG vector similarity search over official documentation
    Persists predictions and citations to SQLite.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticket ID {ticket_id} not found.")

    ticket = row_to_dict(row)

    # 1. ML Classification
    classifier = get_classifier()
    clf_res = classifier.predict(ticket["title"], ticket["description"])
    category = clf_res["predicted_category"]
    confidence = clf_res["confidence"]
    probabilities = clf_res["probabilities"]

    # 2. Priority Heuristic
    priority_res = PriorityService.evaluate_priority(ticket["title"], ticket["description"], category)
    priority = priority_res["priority"]
    priority_reason = priority_res["priority_reason"]

    # 3. RAG Retrieval
    retriever = get_retriever()
    query = f"{ticket['title']} {ticket['description']}"
    citations = retriever.search(query=query)

    # Persist analysis results to SQLite
    now = datetime.utcnow().isoformat()
    citations_json = json.dumps([c.model_dump() for c in citations])

    cursor.execute("""
        UPDATE tickets
        SET category = ?, confidence = ?, priority = ?, priority_reason = ?, citations = ?, updated_at = ?
        WHERE id = ?
    """, (category, confidence, priority, priority_reason, citations_json, now, ticket_id))

    conn.commit()
    conn.close()

    return TicketAnalysisResult(
        ticket_code=ticket["ticket_code"],
        predicted_category=category,
        confidence=confidence,
        probabilities=probabilities,
        priority=priority,
        priority_reason=priority_reason,
        relevant_knowledge=citations
    )


@router.post("/{ticket_id}/draft-response", response_model=DraftResponseResult)
def generate_ticket_draft(ticket_id: int, payload: DraftResponseRequest = None):
    """
    Generates a policy-grounded support draft response using retrieved knowledge base context.
    Persists the suggested draft to the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticket ID {ticket_id} not found.")

    ticket = row_to_dict(row)

    # Ensure ticket has citations; if not, retrieve now
    citations_data = ticket.get("citations", [])
    if not citations_data:
        retriever = get_retriever()
        citations = retriever.search(f"{ticket['title']} {ticket['description']}")
    else:
        citations = [Citation(**c) if isinstance(c, dict) else c for c in citations_data]

    custom_instructions = payload.custom_instructions if payload else None

    # Generate grounded response
    llm = get_llm_service()
    draft_result = llm.generate_draft(
        ticket_code=ticket["ticket_code"],
        title=ticket["title"],
        description=ticket["description"],
        citations=citations,
        custom_instructions=custom_instructions
    )

    # Persist draft to SQLite
    now = datetime.utcnow().isoformat()
    citations_json = json.dumps([c.model_dump() for c in citations])

    cursor.execute("""
        UPDATE tickets
        SET suggested_response = ?, citations = ?, status = 'analyzed', updated_at = ?
        WHERE id = ?
    """, (draft_result.draft_response, citations_json, now, ticket_id))

    conn.commit()
    conn.close()

    return draft_result


@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket(ticket_id: int, payload: TicketUpdate):
    """
    Enables human support agents to review, correct category/priority, or update ticket status.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticket ID {ticket_id} not found.")

    now = datetime.utcnow().isoformat()
    updates = []
    values = []

    if payload.category is not None:
        updates.append("category = ?")
        values.append(payload.category)
    if payload.priority is not None:
        updates.append("priority = ?")
        values.append(payload.priority)
    if payload.status is not None:
        updates.append("status = ?")
        values.append(payload.status)

    if updates:
        updates.append("updated_at = ?")
        values.append(now)
        values.append(ticket_id)
        cursor.execute(f"UPDATE tickets SET {', '.join(updates)} WHERE id = ?", tuple(values))
        conn.commit()

    cursor.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    updated_row = cursor.fetchone()
    conn.close()

    return row_to_dict(updated_row)
