# Live Deployment Verification Checklist

**AI Support Intelligence Platform**

Use this checklist to verify your live deployment before sending links to hiring managers or demonstrating the platform during interviews.

---

## 1. Backend REST API Health Check

- [ ] **Render Service Status:** Dashboard indicates **Live** with a green dot.
- [ ] **Endpoint `/health`:** Open `https://<your-render-url>/health` in your browser.
  - Expected HTTP Code: `200 OK`
  - Expected Payload:
    ```json
    {
      "status": "healthy",
      "app_name": "AI Support Intelligence Platform",
      "environment": "production",
      "classifier_ready": true,
      "knowledge_base_chunks": 20,
      "llm_provider": "mock"
    }
    ```
- [ ] **Swagger Documentation:** Open `https://<your-render-url>/docs` and verify all endpoints (`/tickets`, `/knowledge`, `/metrics`) are documented interactively.
- [ ] **Metrics Endpoint:** Open `https://<your-render-url>/metrics` and verify empirical test accuracy (81.25%) is returned.

---

## 2. Frontend Streamlit Cloud Verification

- [ ] **Streamlit App Status:** Dashboard loads without Python traceback errors.
- [ ] **Backend Connection:** Sidebar displays `🟢 Backend Connected`.
- [ ] **Ticket Submission Test:**
  - Load sample ticket: *"Billing: Double Charge on Card"*.
  - Click **Submit & Run AI Analysis**.
  - Verified: Predicted Category displays **Billing**.
  - Verified: Priority displays **🟠 High** with rule explanation.
  - Verified: Retrieved Knowledge displays matching sections from `billing_policy.md`.
- [ ] **LLM Grounded Draft Test:**
  - Click **✨ Generate Grounded AI Draft Response**.
  - Verified: Draft contains human review notice, tailored advice, and source citations.
- [ ] **Ticket History Tab:**
  - Switch to **Ticket Management & History** tab.
  - Verified: Newly submitted ticket appears in the data table.
  - Verified: Human agent override form updates status to `resolved`.
- [ ] **Knowledge Base Explorer Tab:**
  - Enter search query: `"SAML SSO login error"`.
  - Verified: Returns Section 4 from `account_security.md` with similarity score.
