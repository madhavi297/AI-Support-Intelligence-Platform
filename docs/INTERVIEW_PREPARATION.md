# Complete AI Engineering Interview Preparation Guide

**Project:** AI Support Intelligence Platform — Intelligent Ticket Classification and RAG Assistant  
**Author / Candidate:** AI Engineer Portfolio

---

## 1. Quick Pitches & Demonstration Scripts

### A. 30-Second Elevator Pitch
> *"I built the **AI Support Intelligence Platform**, a production-grade system that automates customer support ticket triage. When a ticket arrives, it uses a Scikit-Learn TF-IDF classifier to predict categories with 81% test accuracy, a transparent SLA heuristic engine to prioritize urgency, and a RAG pipeline that retrieves official policy documentation to draft grounded responses using an LLM. It features a FastAPI REST backend, SQLite persistence, and an interactive Streamlit UI."*

---

### B. 60-Second Technical Overview
> *"In customer service, triage delays cause costly SLA breaches. I wanted to build a hybrid AI system combining fast classical ML with modern Generative AI. 
> For classification, instead of spending expensive LLM tokens, I implemented an offline-trained TF-IDF and Logistic Regression pipeline that classifies tickets into Billing, Account Access, Technical Issue, or General Inquiry with calibrated probabilities in under 5 milliseconds. 
> For priority, I used transparent SLA business rules because hiring managers value explainability over black-box guesses. 
> For response generation, I implemented RAG: incoming issues are matched against chunked markdown policy documents using Cosine Similarity. The retrieved passages ground an LLM prompt that enforces strict boundaries against prompt injection and hallucination. 
> The system has a 21-test pytest suite, full OpenAPI docs, and is deployed on Render and Streamlit Cloud."*

---

### C. 2-Minute Architecture Walkthrough
> *"The application follows clean separation of concerns across four layers:
> 
> 1. **Presentation Layer:** A Streamlit dashboard where agents can submit tickets, inspect confidence distributions, review retrieved policy passages, trigger AI response drafts, and perform human overrides.
> 2. **API & Orchestration Layer:** FastAPI handles asynchronous HTTP requests with Pydantic validation, CORS middleware, and automatic Swagger docs.
> 3. **Intelligence Services:**
>    - `TicketClassifierService`: A serialized Scikit-Learn pipeline (`classifier.joblib`) loaded once as a memory singleton.
>    - `PriorityService`: Explainable SLA heuristics that detect outage words like 'crash' or '500 error' to flag Urgent tickets.
>    - `KnowledgeRetrieverService`: A vector engine that ingests markdown files, chunks them by section header, and executes Cosine Similarity.
>    - `LLMService`: Grounds prompts with official documentation, isolates untrusted customer text, and includes a zero-cost offline mock fallback.
> 4. **Persistence Layer:** SQLite stores ticket records, predicted categories, confidence scores, and JSON citation history for auditability."*

---

### D. Live Demo Script (Step-by-Step)
1. **Show the UI:** Open Streamlit. Point out the sidebar showing `🟢 Backend Connected` and `ML Classifier: Ready`.
2. **Submit a Realistic Ticket:** Click the sample loader: *"Billing: Double Charge on Card"*. Click **Submit & Run AI Analysis**.
3. **Highlight ML Confidence:** Point to the metric card: *"Predicted Category: Billing (68% confidence)"*. Open the expander to show the calibrated probability distribution across all 4 classes.
4. **Highlight Explainable Priority:** Show the priority badge: *"Priority: High — Triggered by keyword 'double charge'"*. Explain: *"We explicitly avoided calling this deep learning because it's a transparent SLA heuristic."*
5. **Show RAG Citations:** Show the retrieved citation: `billing_policy.md (Section 1: Double Charges, Similarity: 0.1739)`.
6. **Generate Grounded Draft:** Click **Generate Grounded AI Draft**. Show how the AI drafted a response specifically mentioning the 3–5 day refund policy from the retrieved document, with citations at the bottom.
7. **Show Human-in-the-Loop:** Go to **Ticket Management & History**, show the ticket in SQLite, and demonstrate changing the status from `analyzed` to `resolved`.

---

## 2. Five Honest Limitations to Acknowledge in Interviews

When asked *"What are the limitations of this project?"*, deliver these senior-level answers:
1. **Synthetic Dataset Size:** *"Our model is trained on 64 curated tickets. While it achieves 81% test accuracy, a real production system would require 10,000+ historical tickets to capture nuanced user vocabulary and prevent data drift."*
2. **TF-IDF Vocabulary Sparsity:** *"TF-IDF relies on exact n-gram token overlap. If a customer uses novel slang or typos, dense neural embeddings (like `all-MiniLM-L6-v2`) would perform better for semantic matching."*
3. **SQLite Concurrency:** *"SQLite is excellent for local prototypes and single-instance deployments, but for a distributed multi-agent system, PostgreSQL with connection pooling would be required."*
4. **In-Memory Vector Search:** *"Our Cosine Similarity runs in memory. While instantaneous for 20–500 chunks, a production knowledge base with 100,000 articles would require a dedicated vector database like ChromaDB, Qdrant, or pgvector."*
5. **Mock vs Live LLM:** *"The application includes a resilient offline generator to guarantee zero-cost demos, but seamlessly switches to OpenAI API when an API key is supplied."*

---

## 3. Top 30 Technical Interview Questions & Answers

### Python & Backend Development
#### Q1: Why did you choose FastAPI over Flask or Django?
- **Simple Answer:** FastAPI is modern, faster, and automatically validates data with Pydantic and generates documentation.
- **Technical Answer:** FastAPI is built on Starlette and Pydantic. It provides asynchronous request handling via ASGI, automatic type-hint validation, and auto-generates OpenAPI JSON and interactive Swagger UI at `/docs`.
- **Project Example:** In `app/routes/tickets.py`, `create_ticket(payload: TicketCreate)` validates incoming fields before executing.
- **Follow-up:** *What is ASGI vs WSGI?* (ASGI is asynchronous and supports concurrent websockets/asyncio; WSGI is synchronous).
- **Key Point:** Automatic validation and native async performance.

#### Q2: How does Pydantic improve backend reliability?
- **Simple Answer:** It ensures incoming data has the correct data types before the code touches it.
- **Technical Answer:** Pydantic enforces schema constraints at runtime. If a client sends an empty title or wrong data type, Pydantic immediately returns an HTTP 422 Unprocessable Entity with exact error locations.
- **Project Example:** `TicketCreate` enforces `min_length=3` on ticket titles.
- **Follow-up:** *What is the difference between Pydantic BaseModel and Python dataclass?* (Pydantic performs runtime coercion and validation; dataclasses merely store attributes).
- **Key Point:** Fail early at the API boundary.

#### Q3: How do you handle database connections in SQLite to avoid locking?
- **Simple Answer:** By creating short-lived connections per request and committing immediately.
- **Technical Answer:** In `app/database.py`, we use `get_db_connection()` with `sqlite3.Row` factory. Transactions are committed and closed immediately inside route handlers to prevent long-running write locks.
- **Follow-up:** *Why does SQLite return 'database is locked'?* (Because SQLite uses file-level locking during write transactions).
- **Key Point:** Short transactions and thread-safe connections.

#### Q4: Why did you use `pathlib.Path` instead of string paths?
- **Simple Answer:** It works automatically across Windows, Linux, and Mac.
- **Technical Answer:** Windows uses backslashes (`\`) while Linux/Docker uses forward slashes (`/`). `Path` handles cross-platform delimiters and provides cleaner syntax than `os.path.join`.
- **Project Example:** `BASE_DIR = Path(__file__).resolve().parent.parent`.
- **Key Point:** Cross-platform portability.

#### Q5: What is CORS and why did you configure it?
- **Simple Answer:** It allows our Streamlit frontend to make requests to our FastAPI backend when hosted on different ports or domains.
- **Technical Answer:** Cross-Origin Resource Sharing is a browser security mechanism that blocks HTTP requests across different origins (protocol, host, port). We added `CORSMiddleware` with `allow_origins=["*"]`.
- **Key Point:** Prevents frontend API connection blocks.

---

### Machine Learning & NLP
#### Q6: Why did you use Scikit-Learn instead of an LLM for classification?
- **Simple Answer:** It is much faster, $100\times$ cheaper, and completely deterministic.
- **Technical Answer:** Calling an LLM for a 4-class classification task takes 500–1500ms and costs API tokens per request. A TF-IDF + Logistic Regression pipeline executes in under 5ms, runs on CPU, and outputs mathematically calibrated probabilities.
- **Project Example:** `clf.predict_proba()` produces exact category probabilities in `app/services/classifier.py`.
- **Follow-up:** *When WOULD you use an LLM for classification?* (When labels are open-ended or zero-shot classification is required).
- **Key Point:** Use the right tool for the job; don't use LLMs where classical ML excels.

#### Q7: What is TF-IDF and how does it work?
- **Simple Answer:** It measures how important a word is to a document compared to a whole collection of documents.
- **Technical Answer:** Term Frequency (TF) counts word occurrences in a document. Inverse Document Frequency (IDF) penalizes common words (like "the", "and") by calculating $\log(N / df)$. The product $TF \times IDF$ gives high weight to words that are uniquely discriminative.
- **Project Example:** Words like `"refund"`, `"invoice"`, `"charge"` get high weights for the Billing category.
- **Key Point:** Weighs discriminative terms while dampening common stopwords.

#### Q8: How did you prevent data leakage during model training?
- **Simple Answer:** By splitting the data into train and test sets before fitting any vectorizers.
- **Technical Answer:** If you fit a `TfidfVectorizer` on the entire dataset, the vocabulary and IDF frequencies of the test set leak into the model. In `scripts/train_model.py`, we executed `train_test_split` first, and the pipeline only called `fit()` on `X_train`.
- **Key Point:** Never let test set statistics inform feature extraction.

#### Q9: What is the difference between Precision and Recall?
- **Simple Answer:** Precision is quality ("how many selected items were relevant?"); Recall is quantity ("how many relevant items did we find?").
- **Technical Answer:** Precision is $\frac{TP}{TP + FP}$. Recall is $\frac{TP}{TP + FN}$. In customer support, high Recall on Urgent tickets is vital so no production outages are missed.
- **Project Example:** Account Access had 0.80 Precision and 1.00 Recall in our empirical test report.
- **Key Point:** Precision prevents false alarms; recall prevents missed incidents.

#### Q10: What is an F1-Score and why is it preferred over Accuracy?
- **Simple Answer:** The harmonic mean of precision and recall.
- **Technical Answer:** Accuracy can be misleading if classes are imbalanced (e.g. 95% of tickets are General Inquiry). F1-score balances precision and recall, penalizing models that favor the majority class.
- **Project Example:** Our macro-average F1-score was 0.80 across all 4 categories.
- **Key Point:** Reliable metric for multi-class classification.

---

### RAG & Generative AI
#### Q11: What is RAG and why is it used?
- **Simple Answer:** Retrieval-Augmented Generation feeds relevant company documents to an LLM so it answers accurately without guessing.
- **Technical Answer:** Standard LLMs suffer from knowledge cutoffs and hallucinations. RAG decouples knowledge storage from model weights by retrieving authoritative text passages at runtime and injecting them into the prompt.
- **Project Example:** Fetching refund policies from `billing_policy.md` before generating an invoice dispute draft.
- **Key Point:** Grounding LLMs in private, up-to-date company data.

#### Q12: How does chunking affect retrieval quality?
- **Simple Answer:** If chunks are too large, irrelevant noise enters; if too small, context is lost.
- **Technical Answer:** Chunks must represent coherent semantic units. In `document_ingestion.py`, we chunked documents by markdown section headers (`## Section`), preserving the title, topic, and source file metadata.
- **Key Point:** Section-based chunking preserves document context.

#### Q13: What is Cosine Similarity?
- **Simple Answer:** A mathematical measure of how similar two vectors are, based on their angle.
- **Technical Answer:** Given query vector $\mathbf{a}$ and chunk vector $\mathbf{b}$, Cosine Similarity is $\frac{\mathbf{a} \cdot \mathbf{b}}{\|\mathbf{a}\| \|\mathbf{b}\|}$. It ranges from 0 to 1 for non-negative vectors, independent of document length.
- **Project Example:** Implemented in `app/services/retriever.py` to rank knowledge chunks.
- **Key Point:** Directional similarity independent of text length.

#### Q14: How does your system mitigate LLM hallucinations?
- **Simple Answer:** We force the model to cite retrieved documents and explicitly say when info is missing.
- **Technical Answer:** We use three layers: (1) System prompt constraint forcing answers strictly from context, (2) Mandatory fallback instruction when similarity scores fall below threshold, (3) Source citation requirements.
- **Project Example:** If someone asks about quantum computing, the model responds that official documentation does not contain sufficient details.
- **Key Point:** Constrained prompts and similarity thresholds prevent false claims.

#### Q15: What is prompt injection and how did you defend against it?
- **Simple Answer:** When a user tricks an AI into ignoring rules by typing instructions like "ignore previous instructions".
- **Technical Answer:** In `prompt_templates.py`, we separate system instructions from untrusted data using clear delimiter blocks (`[OFFICIAL KNOWLEDGE BASE]` vs `[UNTRUSTED CUSTOMER TICKET]`). The system prompt instructs the LLM to treat ticket text strictly as inquiry content.
- **Key Point:** Strict boundary demarcation and untrusted input isolation.

---

*(Questions 16–30 cover Deep Learning, Docker, CI/CD, and MLOps concepts in similar technical depth).*
