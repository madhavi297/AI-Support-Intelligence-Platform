# Comprehensive Testing and Verification Guide

**AI Support Intelligence Platform**

This guide documents the full testing protocol, functional user journeys, empirical ML evaluation results, and automated test suite execution.

---

## 1. Automated Test Suite Execution (Pytest)

All unit and integration tests were executed using `pytest`.

### Command Executed:
```powershell
pytest -v
```

### Measured Test Run Output:
```text
============================= test session starts =============================
platform win32 -- Python 3.11.0, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Madhavi\Downloads\Project1
collected 21 items

tests/test_api.py::test_get_health PASSED                                [  4%]
tests/test_api.py::test_create_and_get_ticket PASSED                     [  9%]
tests/test_api.py::test_ticket_not_found PASSED                          [ 14%]
tests/test_api.py::test_ticket_validation_error PASSED                   [ 19%]
tests/test_api.py::test_analyze_and_draft_ticket_flow PASSED             [ 23%]
tests/test_api.py::test_human_override_patch PASSED                      [ 28%]
tests/test_api.py::test_knowledge_search_endpoint PASSED                 [ 33%]
tests/test_api.py::test_ml_metrics_endpoint PASSED                       [ 38%]
tests/test_classifier.py::test_classifier_is_ready PASSED                [ 42%]
tests/test_classifier.py::test_classifier_billing_prediction PASSED      [ 47%]
tests/test_classifier.py::test_classifier_account_access_prediction PASSED [ 52%]
tests/test_classifier.py::test_classifier_empty_input PASSED             [ 57%]
tests/test_llm.py::test_llm_grounded_mock_generation PASSED              [ 61%]
tests/test_llm.py::test_llm_generation_without_citations PASSED          [ 66%]
tests/test_priority.py::test_priority_urgent_on_outage PASSED            [ 71%]
tests/test_priority.py::test_priority_high_on_lockout PASSED             [ 76%]
tests/test_priority.py::test_priority_low_on_roadmap_or_hours PASSED     [ 80%]
tests/test_priority.py::test_priority_default_medium PASSED              [ 85%]
tests/test_retriever.py::test_document_ingestion PASSED                  [ 90%]
tests/test_retriever.py::test_vector_retriever_search PASSED             [ 95%]
tests/test_retriever.py::test_vector_retriever_empty_query PASSED        [100%]

======================== 21 passed, 1 warning in 2.30s ========================
```

### Summary:
- **Total Tests:** 21
- **Passed:** 21 (100%)
- **Failed:** 0
- **Duration:** 2.30 seconds

---

## 2. Machine Learning Empirical Evaluation

The text classification model was trained and evaluated on `data/sample_tickets.csv` using a 75/25 stratified train/test split.

### Dataset Profile:
- **Total Samples:** 64 tickets
- **Class Balance:** Exactly 16 tickets per class (Billing, Account Access, Technical Issue, General Inquiry)
- **Training Set:** 48 samples
- **Test Set:** 16 unseen samples

### Empirical Classification Results:
- **Overall Test Accuracy:** **81.25% (0.8125)**

| Category | Precision | Recall | F1-Score | Support (Test Count) |
| :--- | :---: | :---: | :---: | :---: |
| **Account Access** | 0.80 | 1.00 | 0.89 | 4 |
| **Billing** | 0.67 | 1.00 | 0.80 | 4 |
| **General Inquiry** | 1.00 | 0.50 | 0.67 | 4 |
| **Technical Issue** | 1.00 | 0.75 | 0.86 | 4 |
| **Macro Average** | **0.87** | **0.81** | **0.80** | 16 |
| **Weighted Average** | **0.87** | **0.81** | **0.80** | 16 |

### Confusion Matrix:
*(Rows = Actual Label, Columns = Predicted Label)*

```text
Labels: [Account Access, Billing, General Inquiry, Technical Issue]

Actual \ Pred       AccAccess  Billing  GenInq  TechIssue
Account Access          4         0        0        0
Billing                 0         4        0        0
General Inquiry         0         2        2        0
Technical Issue         1         0        0        3
```

### What These Metrics Prove vs. Limitations:
1. **What it proves:** TF-IDF with sublinear term frequency weighting and Logistic Regression effectively identifies domain-specific terminology (e.g. `credit card`, `refund`, `invoice`, `password`, `login`, `2fa`, `500 error`) and generalizes well to unseen test splits.
2. **Limitations to acknowledge in interviews:**
   - 64 samples is a small synthetic dataset designed for prototype validation. In production, a dataset of 5,000–50,000 real customer tickets would be needed.
   - Domain vocabulary shifts (e.g. new product features or slang) require continuous model retraining (MLOps concept: *data drift*).

---

## 3. End-to-End Functional User Journeys

### Journey 1: Create and Analyze a High-Priority Billing Ticket
1. **Action:** User submits ticket:
   - *Title:* `"Double charge on credit card"`
   - *Description:* `"I noticed two identical charges of $49.99 on my Visa statement for this month. Please refund one immediately."`
2. **FastAPI Processing:**
   - Ticket persisted in SQLite as `TCK-1001`.
   - ML Classifier predicts: `Billing` with **68.4% confidence**.
   - Priority Service triggers: `"SLA Tier 2 (High): Triggered by keyword 'double charge' — duplicate charge detected."`
   - RAG Retriever extracts: `billing_policy.md` (Section 1: Double Charges and Duplicate Transactions, Cosine Similarity: `0.1739`).
3. **LLM Response Draft Generation:**
   - Draft acknowledges duplicate charge policy and specifies standard 3–5 business day refund window.
   - Includes citations: `- billing_policy.md: Section 1: Double Charges and Duplicate Transactions`.

### Journey 2: Outage Alert Triggers Urgent Priority
1. **Action:** User submits:
   - *Title:* `"REST API returning 500 Internal Server Error"`
   - *Description:* `"POST /orders is failing with HTTP 500 and database connection pool exhausted crash."`
2. **Result:**
   - Predicted Category: `Technical Issue`
   - Priority Assigned: `🔴 Urgent` (Reason: `Triggered by keyword 'crash' — Application or worker crash detected`).

### Journey 3: Undocumented Query Fallback Behavior
1. **Action:** User submits an unsupported query:
   - *Title:* `"How do I configure quantum computing nodes?"`
   - *Description:* `"We want to connect quantum qubits to our account."`
2. **RAG Vector Search:**
   - No chunks pass the similarity threshold (`0.10`).
3. **LLM Output:**
   - The model does **NOT** hallucinate a quantum computing policy.
   - It outputs: *"Our official support documentation does not contain sufficient details to fully resolve this specific inquiry. I have escalated this ticket to our senior tier support engineering team."*

---

## 4. How to Run the Verification Checks Yourself

1. **Verify Backend Health:**
   ```powershell
   curl http://127.0.0.1:8000/health
   ```
2. **Run Pytest Test Suite:**
   ```powershell
   pytest -v
   ```
3. **Inspect Real ML Metrics:**
   ```powershell
   curl http://127.0.0.1:8000/metrics
   ```
4. **Launch Streamlit Dashboard:**
   ```powershell
   streamlit run frontend/streamlit_app.py
   ```
