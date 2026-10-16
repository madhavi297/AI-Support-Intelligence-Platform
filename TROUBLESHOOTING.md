# Troubleshooting Guide: AI Support Intelligence Platform

This guide provides targeted solutions for common setup, runtime, networking, and deployment issues on Windows, VS Code, and cloud hosting.

---

## 1. Windows PowerShell: Script Execution Policy Error

### Symptoms
When running `.\.venv\Scripts\Activate.ps1`, PowerShell returns:
```text
File ...\Activate.ps1 cannot be loaded because running scripts is disabled on this system.
```

### Why It Happens
By default, Windows sets PowerShell's execution policy to `Restricted` to prevent unsigned script execution.

### The Fix (Least Invasive Solution)
Open PowerShell in VS Code and change the execution policy for your **current user session only** (does not affect system security):
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```
Alternatively, bypass execution policy directly when activating:
```powershell
powershell -ExecutionPolicy Bypass -File .\.venv\Scripts\Activate.ps1
```

---

## 2. Python Is Not Recognized as an Internal or External Command

### Symptoms
Running `python --version` returns:
```text
'python' is not recognized as an internal or external command, operable program or batch file.
```

### Why It Happens
Python is installed, but its directory was not added to your Windows system `PATH` environment variable.

### The Fix
1. Try the Windows Python Launcher:
   ```cmd
   py --version
   ```
2. If `py` works, use `py` instead of `python` (e.g., `py -m uvicorn app.main:app`).
3. To add Python to PATH permanently:
   - Search Windows for **"Edit the system environment variables"**.
   - Click **Environment Variables...** > select `Path` under User variables > click **Edit**.
   - Add your Python folder (e.g. `C:\Users\<YourUser>\AppData\Local\Programs\Python\Python311\`) and `...\Python311\Scripts\`.
   - Restart VS Code.

---

## 3. Port 8000 or 8501 Already in Use

### Symptoms
FastAPI or Streamlit crashes on startup with:
```text
[Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000): only one usage of each socket address is normally permitted
```

### Why It Happens
A previous instance of Uvicorn or Streamlit is still running in the background.

### The Fix
Option A: Kill the existing process occupying port 8000 in PowerShell:
```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
```
Option B: Run FastAPI on an alternative port (e.g., 8001):
```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```
*(If you change port to 8001, update the Backend URL in the Streamlit sidebar to `http://127.0.0.1:8001`)*

---

## 4. Frontend Cannot Connect to Backend ("Backend Offline")

### Symptoms
Streamlit sidebar shows `🔴 Backend Offline`, and submitting tickets fails with `ConnectionRefusedError`.

### Why It Happens
The FastAPI backend server is not running, or the Streamlit sidebar has an incorrect backend URL.

### The Fix
1. Ensure the FastAPI backend is running in **Terminal 1**:
   ```powershell
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```
2. Open your browser to `http://127.0.0.1:8000/health`. If it responds with `{"status":"healthy"}`, your backend is alive.
3. In Streamlit (Terminal 2), verify the sidebar input contains:
   `http://127.0.0.1:8000` (no trailing slash).

---

## 5. Model Artifact Missing (`classifier.joblib` Not Found)

### Symptoms
The API logs show:
```text
[ClassifierService] Warning: Model artifact not found at ...\models\classifier.joblib
```

### Why It Happens
The ML model training script has not been executed yet.

### The Fix
Run the model training pipeline:
```powershell
python scripts/train_model.py
```
This trains the TF-IDF + LogisticRegression pipeline on `data/sample_tickets.csv`, computes accuracy metrics, and saves the binary artifact to `models/classifier.joblib`.

---

## 6. OpenAI API Key Missing or Quota Exceeded

### Symptoms
When generating a draft, the API returns a rate limit error or 401 Unauthorized.

### Why It Happens
Either no OpenAI key was provided in `.env`, or the account credit has expired.

### The Fix (Resilient Offline Mode)
Our architecture has built-in offline fallback! Open `.env` and set:
```ini
LLM_PROVIDER=mock
```
Save `.env` and restart FastAPI. The platform will now use the grounded offline mock generator which generates high-quality drafts with real citations, with zero cost and zero network dependencies!

---

## 7. SQLite Database Locked Error

### Symptoms
Submitting tickets yields `sqlite3.OperationalError: database is locked`.

### Why It Happens
Multiple concurrent processes or external database viewer tools (e.g. DB Browser for SQLite) hold an exclusive write lock.

### The Fix
1. Close external database browser software.
2. In `app/database.py`, we use thread-safe connections per request and explicitly close connections immediately after transactions commit.

---

## 8. Git Permission Warnings on Windows User Directory

### Symptoms
Running `git status` reports permission denied warnings on Windows system directories like `Application Data/` or `Cookies/`.

### Why It Happens
The user's home directory (`C:\Users\<User>\`) was accidentally initialized as a Git repository in the past.

### The Fix
We initialized a dedicated Git repository directly inside the project root (`Project1/`):
```powershell
cd C:\Users\Madhavi\Downloads\Project1
git init
```
This isolates the project completely from the user home folder.
