"""
Unit tests for Transparent SLA Priority Service.
"""

from app.services.priority import PriorityService


def test_priority_urgent_on_outage():
    res = PriorityService.evaluate_priority("Production Outage", "The API is down with 500 internal server error")
    assert res["priority"] == "Urgent"
    assert "SLA Tier 1" in res["priority_reason"]


def test_priority_high_on_lockout():
    res = PriorityService.evaluate_priority("Account Locked", "Cannot login after failed attempts, reset 2fa please")
    assert res["priority"] == "High"
    assert "SLA Tier 2" in res["priority_reason"]


def test_priority_low_on_roadmap_or_hours():
    res = PriorityService.evaluate_priority("Office Hours", "What are your support operating hours and roadmap?")
    assert res["priority"] == "Low"
    assert "SLA Tier 4" in res["priority_reason"]


def test_priority_default_medium():
    res = PriorityService.evaluate_priority("General question", "How do I update my profile settings?")
    assert res["priority"] == "Medium"
