"""
Interactive Streamlit Frontend for AI Support Intelligence Platform.
Connects directly to the FastAPI REST backend for real-time ticket triage,
ML classification, RAG retrieval, and grounded LLM response drafting.
"""

import os
import requests
import streamlit as st
import pandas as pd

# Configure Streamlit page
st.set_page_config(
    page_title="AI Support Intelligence Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Determine default backend URL from environment or default to local FastAPI port
DEFAULT_API_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000")


# ---------------------------------------------------------
# Sidebar: System Connection & Configuration
# ---------------------------------------------------------
st.sidebar.title("🛠️ Platform Settings")
api_base_url = st.sidebar.text_input("Backend REST API URL", value=DEFAULT_API_URL).rstrip("/")

# Health Check
try:
    health_resp = requests.get(f"{api_base_url}/health", timeout=3)
    if health_resp.status_code == 200:
        health_data = health_resp.json()
        st.sidebar.success("🟢 Backend Connected")
        st.sidebar.caption(f"**Environment:** `{health_data.get('environment')}`")
        st.sidebar.caption(f"**ML Classifier:** `{'Ready' if health_data.get('classifier_ready') else 'Offline'}`")
        st.sidebar.caption(f"**RAG Chunks:** `{health_data.get('knowledge_base_chunks')}`")
        st.sidebar.caption(f"**LLM Provider:** `{health_data.get('llm_provider')}`")
    else:
        st.sidebar.warning(f"🟡 Backend returned status {health_resp.status_code}")
except Exception:
    st.sidebar.error("🔴 Backend Offline")
    st.sidebar.info("Run `python -m uvicorn app.main:app --port 8000` to start backend.")

st.sidebar.markdown("---")
st.sidebar.subheader("📋 Sample Ticket Loader")

SAMPLE_TICKETS = {
    "Select a sample ticket...": ("", ""),
    "💳 Billing: Double Charge on Card": (
        "Double charge on credit card",
        "I noticed two identical charges of $49.99 on my Visa statement for this month. Please refund one payment immediately."
    ),
    "🔐 Access: Locked Out of Account": (
        "Account locked after failed login attempts",
        "My account has been locked due to 5 incorrect password attempts. I need urgent login access for a client demo."
    ),
    "🚨 Technical: Server 500 Outage": (
        "REST API returning 500 Internal Server Error",
        "POST /api/v1/orders is failing with HTTP 500 and message Database connection pool exhausted error."
    ),
    "❓ General: Operating Hours & SLA": (
        "What are your standard support operating hours?",
        "Can you tell me what hours your technical support team is available and what is the SLA for enterprise accounts?"
    )
}

selected_sample = st.sidebar.selectbox("Load Sample Incident:", list(SAMPLE_TICKETS.keys()))
sample_title, sample_desc = SAMPLE_TICKETS[selected_sample]

st.sidebar.markdown("---")
st.sidebar.caption("AI Support Intelligence Platform v1.0.0 | Portfolio Project")


# ---------------------------------------------------------
# Main Application Header
# ---------------------------------------------------------
st.title("🤖 AI Support Intelligence Platform")
st.markdown(
    "Intelligent Ticket Classification, Explainable Priority Heuristics, and "
    "**RAG-Grounded** Generative Support Assistant."
)

tab1, tab2, tab3, tab4 = st.tabs([
    "📥 Submit & Analyze Ticket",
    "📊 Ticket Management & History",
    "📚 Knowledge Base & RAG Search",
    "📈 ML Model Evaluation & Architecture"
])


# ---------------------------------------------------------
# TAB 1: Submit & Analyze Ticket
# ---------------------------------------------------------
with tab1:
    st.subheader("Create New Customer Ticket")
    
    col1, col2 = st.columns([2, 1])

    with col1:
        with st.form("new_ticket_form"):
            ticket_title = st.text_input(
                "Ticket Title / Subject",
                value=sample_title,
                placeholder="e.g., Cannot login to account"
            )
            ticket_description = st.text_area(
                "Detailed Description",
                value=sample_desc,
                height=150,
                placeholder="Explain the issue in detail..."
            )
            submit_btn = st.form_submit_button("🚀 Submit & Run AI Analysis", use_container_width=True)

    with col2:
        st.info(
            "💡 **What happens on submit?**\n\n"
            "1. **Store:** Persisted to SQLite.\n"
            "2. **Classify:** Scikit-Learn TF-IDF classifier predicts category with calibrated probabilities.\n"
            "3. **Priority:** Transparent SLA rules determine urgency level.\n"
            "4. **RAG:** Vector similarity retrieves matching policy documents.\n"
            "5. **Draft:** LLM creates an evidence-grounded response draft."
        )

    if submit_btn:
        if not ticket_title.strip() or not ticket_description.strip():
            st.error("Please enter both ticket title and description.")
        else:
            with st.spinner("Submitting ticket and executing AI analysis pipeline..."):
                try:
                    # 1. Create ticket
                    create_resp = requests.post(
                        f"{api_base_url}/tickets",
                        json={"title": ticket_title, "description": ticket_description},
                        timeout=5
                    )
                    if create_resp.status_code != 201:
                        st.error(f"Error creating ticket: {create_resp.text}")
                    else:
                        ticket = create_resp.json()
                        ticket_id = ticket["id"]
                        ticket_code = ticket["ticket_code"]

                        # 2. Analyze ticket
                        analyze_resp = requests.post(f"{api_base_url}/tickets/{ticket_id}/analyze", timeout=10)
                        if analyze_resp.status_code != 200:
                            st.error(f"Error analyzing ticket: {analyze_resp.text}")
                        else:
                            analysis = analyze_resp.json()
                            st.session_state["current_ticket_id"] = ticket_id
                            st.session_state["current_ticket_code"] = ticket_code
                            st.session_state["current_analysis"] = analysis
                            st.success(f"Ticket **{ticket_code}** created and analyzed successfully!")
                except Exception as e:
                    st.error(f"Failed to connect to backend: {e}")

    # Display analysis results if available
    if "current_analysis" in st.session_state:
        analysis = st.session_state["current_analysis"]
        ticket_id = st.session_state.get("current_ticket_id")
        ticket_code = st.session_state.get("current_ticket_code")

        st.markdown("---")
        st.subheader(f"🔍 AI Triage Results for Ticket `{ticket_code}`")

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric(
                label="Predicted Category",
                value=analysis["predicted_category"],
                delta=f"{analysis['confidence'] * 100:.1f}% Confidence"
            )
        with m2:
            priority_val = analysis["priority"]
            p_color = {
                "Urgent": "🔴 Urgent",
                "High": "🟠 High",
                "Medium": "🔵 Medium",
                "Low": "🟢 Low"
            }.get(priority_val, priority_val)
            st.metric(label="Assigned Priority", value=p_color)
        with m3:
            st.metric(label="Retrieved Citations", value=f"{len(analysis['relevant_knowledge'])} passages")

        st.caption(f"**Priority Reasoning:** {analysis['priority_reason']}")

        # Class Probability Breakdown
        with st.expander("📊 View Machine Learning Class Probabilities", expanded=False):
            probs_df = pd.DataFrame(
                list(analysis["probabilities"].items()),
                columns=["Category", "Probability"]
            ).sort_values(by="Probability", ascending=False)
            st.dataframe(probs_df, use_container_width=True, hide_index=True)
            st.bar_chart(probs_df.set_index("Category"))

        # Retrieved Knowledge Passages
        st.subheader("📚 Grounding Evidence (RAG Vector Search)")
        if not analysis["relevant_knowledge"]:
            st.warning("⚠️ No relevant knowledge base documents matched above the similarity threshold.")
        else:
            for idx, cite in enumerate(analysis["relevant_knowledge"], 1):
                with st.expander(f"Source {idx}: {cite['source']} — {cite['section']} (Similarity: {cite['score']:.4f})", expanded=(idx == 1)):
                    st.markdown(cite["text"])

        # Grounded LLM Response Draft Section
        st.markdown("---")
        st.subheader("🤖 LLM Grounded Response Generator")

        custom_prompt_input = st.text_input(
            "Optional Operator Guidance for LLM (e.g. 'Polite apology for inconvenience')",
            key="custom_llm_guidance"
        )

        if st.button("✨ Generate Grounded AI Draft Response", use_container_width=True):
            with st.spinner("Generating policy-grounded draft with citations..."):
                try:
                    draft_resp = requests.post(
                        f"{api_base_url}/tickets/{ticket_id}/draft-response",
                        json={"custom_instructions": custom_prompt_input},
                        timeout=15
                    )
                    if draft_resp.status_code == 200:
                        st.session_state["current_draft"] = draft_resp.json()
                    else:
                        st.error(f"Error generating draft: {draft_resp.text}")
                except Exception as e:
                    st.error(f"Backend call failed: {e}")

        if "current_draft" in st.session_state:
            draft_data = st.session_state["current_draft"]
            st.markdown(draft_data["draft_response"])
            st.caption(f"**Generation Provider:** `{draft_data['provider_used']}` | **Fallback Active:** `{draft_data['is_fallback']}`")


# ---------------------------------------------------------
# TAB 2: Ticket Management & History
# ---------------------------------------------------------
with tab2:
    st.subheader("Support Ticket Management & History")

    if st.button("🔄 Refresh Tickets List"):
        st.rerun()

    try:
        tickets_resp = requests.get(f"{api_base_url}/tickets", timeout=5)
        if tickets_resp.status_code == 200:
            tickets_list = tickets_resp.json()
            if not tickets_list:
                st.info("No tickets recorded yet. Create one in the 'Submit & Analyze' tab.")
            else:
                df = pd.DataFrame(tickets_list)[["id", "ticket_code", "title", "category", "priority", "status", "created_at"]]
                st.dataframe(df, use_container_width=True, hide_index=True)

                st.markdown("---")
                st.subheader("👨‍💼 Human Agent Review & Override")
                selected_ticket_id = st.selectbox(
                    "Select Ticket to Inspect or Override:",
                    options=[t["id"] for t in tickets_list],
                    format_func=lambda x: next(f"{t['ticket_code']}: {t['title'][:40]}" for t in tickets_list if t["id"] == x)
                )

                selected_ticket = next(t for t in tickets_list if t["id"] == selected_ticket_id)
                st.write(f"**Description:** {selected_ticket['description']}")
                if selected_ticket.get("suggested_response"):
                    with st.expander("📄 View Stored AI Draft"):
                        st.markdown(selected_ticket["suggested_response"])

                with st.form("override_form"):
                    col_cat, col_pri, col_stat = st.columns(3)
                    with col_cat:
                        new_cat = st.selectbox("Category", ["Billing", "Account Access", "Technical Issue", "General Inquiry"], index=["Billing", "Account Access", "Technical Issue", "General Inquiry"].index(selected_ticket.get("category") or "General Inquiry"))
                    with col_pri:
                        new_pri = st.selectbox("Priority", ["Low", "Medium", "High", "Urgent"], index=["Low", "Medium", "High", "Urgent"].index(selected_ticket.get("priority") or "Medium"))
                    with col_stat:
                        new_stat = st.selectbox("Status", ["open", "analyzed", "resolved", "closed"], index=["open", "analyzed", "resolved", "closed"].index(selected_ticket.get("status") or "open"))

                    update_btn = st.form_submit_button("💾 Save Human Review Updates")
                    if update_btn:
                        patch_resp = requests.patch(
                            f"{api_base_url}/tickets/{selected_ticket_id}",
                            json={"category": new_cat, "priority": new_pri, "status": new_stat},
                            timeout=5
                        )
                        if patch_resp.status_code == 200:
                            st.success("Ticket updated successfully!")
                            st.rerun()
                        else:
                            st.error(f"Error updating ticket: {patch_resp.text}")
        else:
            st.error(f"Failed to fetch tickets: {tickets_resp.text}")
    except Exception as e:
        st.error(f"Backend communication error: {e}")


# ---------------------------------------------------------
# TAB 3: Knowledge Base & RAG Search
# ---------------------------------------------------------
with tab3:
    st.subheader("📚 Knowledge Base Explorer & Direct RAG Query")
    st.markdown("Test vector similarity search directly without creating a support ticket.")

    search_query = st.text_input("Enter search query or policy question:", placeholder="e.g., refund policy for downtime")
    top_k_val = st.slider("Max Passages to Retrieve (Top-K):", min_value=1, max_value=5, value=3)

    if st.button("🔎 Search Knowledge Base"):
        if not search_query.strip():
            st.warning("Please enter a query.")
        else:
            with st.spinner("Executing vector search..."):
                try:
                    search_resp = requests.get(
                        f"{api_base_url}/knowledge/search",
                        params={"query": search_query, "top_k": top_k_val},
                        timeout=5
                    )
                    if search_resp.status_code == 200:
                        results = search_resp.json()
                        if not results:
                            st.warning("No knowledge chunks met the minimum similarity threshold.")
                        else:
                            for idx, res in enumerate(results, 1):
                                st.markdown(f"### {idx}. {res['source']} — {res['section']}")
                                st.caption(f"Cosine Similarity Score: `{res['score']:.4f}`")
                                st.info(res["text"])
                    else:
                        st.error(f"Search failed: {search_resp.text}")
                except Exception as e:
                    st.error(f"Error querying knowledge base: {e}")

    st.markdown("---")
    st.subheader("📊 Ingested Knowledge Base Statistics")
    try:
        stats_resp = requests.get(f"{api_base_url}/knowledge/stats", timeout=5)
        if stats_resp.status_code == 200:
            stats = stats_resp.json()
            c1, c2 = st.columns(2)
            c1.metric("Total Indexed Chunks", stats["total_chunks"])
            c2.metric("Source Documents", stats["total_documents"])
            st.write("**Ingested Document Files:**")
            for doc in stats["documents"]:
                st.markdown(f"- 📄 `{doc}`")
    except Exception:
        st.caption("Knowledge stats currently unavailable.")


# ---------------------------------------------------------
# TAB 4: ML Model Evaluation & Architecture
# ---------------------------------------------------------
with tab4:
    st.subheader("📈 Machine Learning Model Performance & Metrics")
    st.markdown(
        "Empirical evaluation results of the **TF-IDF + Logistic Regression** text classifier "
        "trained on the 64-ticket stratified dataset."
    )

    try:
        metrics_resp = requests.get(f"{api_base_url}/metrics", timeout=5)
        if metrics_resp.status_code == 200:
            metrics_data = metrics_resp.json()
            if "accuracy" in metrics_data:
                col_acc, col_total, col_train, col_test = st.columns(4)
                col_acc.metric("Test Accuracy", f"{metrics_data['accuracy'] * 100:.1f}%")
                col_total.metric("Total Dataset", f"{metrics_data['total_samples']} tickets")
                col_train.metric("Training Split", f"{metrics_data['train_samples']} tickets")
                col_test.metric("Test Split", f"{metrics_data['test_samples']} tickets")

                st.markdown("#### Classification Report per Category")
                report_dict = metrics_data["classification_report"]
                classes = metrics_data["classes"]
                
                table_rows = []
                for cls in classes:
                    if cls in report_dict:
                        table_rows.append({
                            "Category": cls,
                            "Precision": f"{report_dict[cls]['precision']:.2f}",
                            "Recall": f"{report_dict[cls]['recall']:.2f}",
                            "F1-Score": f"{report_dict[cls]['f1-score']:.2f}",
                            "Support (Test Count)": report_dict[cls]['support']
                        })
                st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

                st.markdown("#### Confusion Matrix")
                cm_df = pd.DataFrame(
                    metrics_data["confusion_matrix"],
                    index=[f"Actual: {c}" for c in classes],
                    columns=[f"Pred: {c}" for c in classes]
                )
                st.dataframe(cm_df, use_container_width=True)
            else:
                st.info(metrics_data.get("message", "Metrics not ready."))
    except Exception as e:
        st.error(f"Could not load ML metrics: {e}")

    st.markdown("---")
    st.subheader("🏛️ System Architecture Workflow")
    st.markdown("""
    ```text
    [User / Support Agent]
              │
              ▼
    [Streamlit UI Dashboard] ──HTTP POST──► [FastAPI REST Backend]
                                                    │
                 ┌──────────────────────────────────┴──────────────────────────────────┐
                 ▼                                  ▼                                  ▼
        [SQLite Database]              [Scikit-learn Classifier]             [RAG Vector Retriever]
     (Persistent Tickets/Audit)         (TF-IDF + Logistic Reg)               (Cosine Similarity)
                 │                                  │                                  │
                 │                                  ▼                                  ▼
                 │                         Category & Probabilities            Relevant Documents
                 │                                  │                                  │
                 └──────────────────────────────────┼──────────────────────────────────┘
                                                    │
                                                    ▼
                                         [LLM Service & Grounding]
                                       (OpenAI or Offline Fallback)
                                                    │
                                                    ▼
                                        [Evidence-Grounded Draft]
    ```
    """)
