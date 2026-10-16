"""
Unit tests for Scikit-learn Classifier Service.
"""

import pytest
from app.services.classifier import get_classifier


def test_classifier_is_ready():
    clf = get_classifier()
    assert clf.is_ready() is True


def test_classifier_billing_prediction():
    clf = get_classifier()
    res = clf.predict("Refund request", "I was charged twice on my invoice this month")
    assert res["predicted_category"] == "Billing"
    assert 0.0 <= res["confidence"] <= 1.0
    assert "probabilities" in res
    assert pytest.approx(sum(res["probabilities"].values()), 0.01) == 1.0


def test_classifier_account_access_prediction():
    clf = get_classifier()
    res = clf.predict("Cannot login to account", "Forgot password and reset token link expired")
    assert res["predicted_category"] == "Account Access"
    assert res["confidence"] > 0.4


def test_classifier_empty_input():
    clf = get_classifier()
    res = clf.predict("", "")
    assert res["predicted_category"] == "General Inquiry"
    assert res["confidence"] == 0.25
