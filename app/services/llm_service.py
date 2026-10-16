"""
LLM Generation Service with Grounded Generation and Offline Fallback.
Supports OpenAI API and guaranteed offline mock generation for interview demonstrations.
"""

import json
import requests
from typing import List, Dict, Any, Tuple
from app.config import settings
from app.schemas import Citation, DraftResponseResult
from app.services.prompt_templates import SYSTEM_PROMPT, format_user_prompt


class LLMService:
    """
    Manages prompt formatting, LLM provider integration, and resilient offline fallbacks.
    """

    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self.api_key = settings.LLM_API_KEY
        self.model_name = settings.LLM_MODEL_NAME

    def generate_draft(
        self,
        ticket_code: str,
        title: str,
        description: str,
        citations: List[Citation],
        custom_instructions: str = None
    ) -> DraftResponseResult:
        """
        Generates a contextual support response draft based on retrieved citations.
        """
        # If provider is explicitly set to mock, or no API key is provided
        if self.provider == "mock" or not self.api_key:
            return self._generate_mock_draft(ticket_code, title, description, citations, custom_instructions)

        if self.provider == "openai":
            try:
                return self._call_openai(ticket_code, title, description, citations, custom_instructions)
            except Exception as e:
                print(f"[LLMService] OpenAI call failed: {e}. Engaging offline fallback.")
                fallback_res = self._generate_mock_draft(ticket_code, title, description, citations, custom_instructions)
                fallback_res.is_fallback = True
                fallback_res.provider_used = f"offline-fallback (OpenAI failed: {str(e)[:50]})"
                return fallback_res

        # Fallback for unrecognized provider
        return self._generate_mock_draft(ticket_code, title, description, citations, custom_instructions)

    def _call_openai(
        self,
        ticket_code: str,
        title: str,
        description: str,
        citations: List[Citation],
        custom_instructions: str = None
    ) -> DraftResponseResult:
        """Calls OpenAI Chat Completions API with system grounding."""
        user_prompt = format_user_prompt(title, description, citations, custom_instructions)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,  # Low temperature for factual grounding
            "max_tokens": 600
        }

        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=20
        )
        resp.raise_for_status()
        data = resp.json()
        raw_text = data["choices"][0]["message"]["content"].strip()

        # Prepend human review notice if not present
        if "[AI-Generated Draft - Requires Human Review]" not in raw_text:
            final_text = f"> **[AI-Generated Draft - Requires Human Review]**\n\n{raw_text}"
        else:
            final_text = raw_text

        return DraftResponseResult(
            ticket_code=ticket_code,
            draft_response=final_text,
            citations=citations,
            provider_used=f"openai ({self.model_name})",
            is_fallback=False
        )

    def _generate_mock_draft(
        self,
        ticket_code: str,
        title: str,
        description: str,
        citations: List[Citation],
        custom_instructions: str = None
    ) -> DraftResponseResult:
        """
        High-quality, grounded offline draft generator.
        Assembles a professional support response directly from retrieved citations.
        Guaranteed to work without API keys or internet access.
        """
        banner = "> **[AI-Generated Draft - Requires Human Review]**\n\n"
        greeting = "Hello,\n\nThank you for contacting customer support. We have reviewed your request regarding your recent inquiry.\n\n"

        if not citations:
            body = (
                "Our official knowledge base documentation does not contain sufficient details "
                "to fully resolve this specific issue automatically. \n\n"
                "I have escalated your ticket to our senior tier support engineering team for a comprehensive "
                "manual investigation. A specialist will follow up with you shortly.\n\n"
                "Thank you for your patience while we investigate this matter."
            )
            citations_footer = "\n\n---\n*Citations: No direct knowledge-base match found. Escalated for specialist review.*"
        else:
            top_citation = citations[0]
            body = (
                f"Based on our official **{top_citation.section}** guidelines, here is the relevant guidance to resolve your issue:\n\n"
            )
            
            # Extract actionable sentences from top retrieved knowledge
            sentences = [s.strip() for s in top_citation.text.split(".") if len(s.strip()) > 15]
            for s in sentences[:3]:
                body += f"- {s}.\n"

            if len(citations) > 1:
                body += f"\nAdditionally, please note per our **{citations[1].section}**:\n"
                sec_sentences = [s.strip() for s in citations[1].text.split(".") if len(s.strip()) > 15]
                if sec_sentences:
                    body += f"- {sec_sentences[0]}.\n"

            body += (
                "\nIf you need any additional assistance or if this does not fully address your issue, "
                "please reply directly to this message."
            )

            citations_footer = "\n\n---\n**Referenced Official Sources:**\n"
            for c in citations:
                citations_footer += f"- `{c.source}`: {c.section} (Relevance Score: {c.score:.2f})\n"

        closing = "\n\nBest regards,\nCustomer Support Operations Team"
        full_draft = banner + greeting + body + closing + citations_footer

        return DraftResponseResult(
            ticket_code=ticket_code,
            draft_response=full_draft,
            citations=citations,
            provider_used="offline-grounded-mock",
            is_fallback=False
        )


# Global singleton instance
_llm_instance: LLMService = None


def get_llm_service() -> LLMService:
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMService()
    return _llm_instance
