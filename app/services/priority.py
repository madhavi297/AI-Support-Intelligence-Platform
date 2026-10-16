"""
Transparent baseline priority engine for support tickets.
Uses deterministic SLA business rules based on operational impact and urgency indicators.
Explains the exact reasoning for each assigned priority tier.
"""

from typing import Tuple, Dict, Any

# Keyword rules mapped to priority levels and explanations
URGENT_INDICATORS = [
    ("outage", "Production outage or complete service downtime reported"),
    ("down", "Service unavailability reported"),
    ("crash", "Application or worker crash detected"),
    ("fatal", "Fatal runtime exception encountered"),
    ("500 internal", "Internal server 500 error disrupting users"),
    ("502 bad gateway", "Gateway failure impacting service availability"),
    ("503 service", "Service unavailable during operations"),
    ("data loss", "Potential data corruption or loss"),
    ("unauthorized", "Security alert: unauthorized charge or access"),
    ("admin locked", "Administrative account lockout blocking organization"),
    ("saml_invalid", "Enterprise SSO authentication failure blocking all users"),
    ("memory leak", "Critical infrastructure resource exhaustion")
]

HIGH_INDICATORS = [
    ("locked", "Account lockout preventing user access"),
    ("cannot login", "User unable to authenticate into portal"),
    ("password reset", "Authentication reset required"),
    ("2fa", "Two-factor authentication barrier"),
    ("failed payment", "Payment transaction failed"),
    ("card declined", "Payment method declined"),
    ("double charge", "Billing dispute: duplicate charge detected"),
    ("timeout", "Network or database timeout impacting workflow"),
    ("rate limit", "API quota or rate limiting throttling requests"),
    ("latency", "Excessive response latency degrading service")
]

LOW_INDICATORS = [
    ("hours", "General inquiry about business hours"),
    ("demo", "Sales inquiry requesting product demo"),
    ("roadmap", "Product feature roadmap inquiry"),
    ("soc2", "Compliance or certification documentation request"),
    ("tax exempt", "Billing documentation: tax exemption certificate"),
    ("discount", "Pricing discount inquiry"),
    ("whitepaper", "Security or product whitepaper request")
]


class PriorityService:
    """
    Evaluates ticket urgency using transparent SLA heuristic rules.
    Does NOT pretend to be machine learning; provides fully explainable rule audits.
    """

    @staticmethod
    def evaluate_priority(title: str, description: str, category: str = "") -> Dict[str, str]:
        """
        Determines ticket priority level and explains the specific rule trigger.
        
        Args:
            title: Ticket title
            description: Ticket description
            category: Optional predicted category
            
        Returns:
            Dict containing:
                - priority: "Urgent" | "High" | "Medium" | "Low"
                - priority_reason: Human-readable explanation of why priority was assigned
        """
        content = f"{title.lower()} {description.lower()}"

        # 1. Check Urgent triggers
        for keyword, explanation in URGENT_INDICATORS:
            if keyword in content:
                return {
                    "priority": "Urgent",
                    "priority_reason": f"SLA Tier 1 (Urgent): Triggered by keyword '{keyword}' — {explanation}."
                }

        # 2. Check High triggers
        for keyword, explanation in HIGH_INDICATORS:
            if keyword in content:
                return {
                    "priority": "High",
                    "priority_reason": f"SLA Tier 2 (High): Triggered by keyword '{keyword}' — {explanation}."
                }

        # 3. Check Low triggers (mostly general informational inquiries)
        for keyword, explanation in LOW_INDICATORS:
            if keyword in content:
                return {
                    "priority": "Low",
                    "priority_reason": f"SLA Tier 4 (Low): Triggered by keyword '{keyword}' — {explanation}."
                }

        # Category-based default fallbacks
        if category == "General Inquiry":
            return {
                "priority": "Low",
                "priority_reason": "SLA Tier 4 (Low): General inquiries default to standard 48-hour response queue."
            }
        elif category == "Technical Issue":
            return {
                "priority": "Medium",
                "priority_reason": "SLA Tier 3 (Medium): Technical issue without critical outage markers assigned standard triage."
            }
        elif category == "Account Access":
            return {
                "priority": "Medium",
                "priority_reason": "SLA Tier 3 (Medium): Account access request without explicit lockout assigned standard queue."
            }

        return {
            "priority": "Medium",
            "priority_reason": "SLA Tier 3 (Medium): Default baseline priority for standard customer requests."
        }
