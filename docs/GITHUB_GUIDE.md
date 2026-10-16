# Git and GitHub Publishing Guide

**AI Support Intelligence Platform**

This guide provides step-by-step instructions for staging, committing, and publishing your portfolio project to GitHub safely without exposing secrets.

---

## 1. Verify Git Installation and Identity

Open your terminal in VS Code and check:

```powershell
git --version
```
*(You already have Git `2.51.0` installed)*

Configure your Git username and email if you have not done so already:
```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## 2. Pre-Commit Safety Check: Never Commit Secrets

Before adding files, verify that `.gitignore` properly protects your `.env` and `.db` files:

```powershell
git status
```

**CRITICAL RULE:**
- `.env` must **NOT** appear in the list of untracked files.
- `support_intelligence.db` must **NOT** appear in the list.
- Only `.env.example` should be tracked in version control.

---

## 3. Stage and Create the First Git Commit

Run the following commands in sequence:

```powershell
# 1. Stage all project source files, tests, and documentation
git add .

# 2. Check what is staged
git status

# 3. Create a professional, descriptive commit
git commit -m "feat: complete end-to-end AI Support Intelligence Platform with ML triage and RAG assistant"
```

---

## 4. Create a New GitHub Repository

1. Open your browser and go to [github.com/new](https://github.com/new).
2. Set **Repository name**: `ai-support-intelligence-platform`
3. Description: `Production-ready AI support ticket triage with Scikit-learn text classification, explainable SLA priority heuristics, and RAG-grounded generative LLM assistance.`
4. Visibility: Select **Public**.
5. **Do NOT check** "Add a README file", "Add .gitignore", or "Choose a license" (we already created them locally).
6. Click **Create repository**.

---

## 5. Link Local Repository and Push to GitHub

Copy your GitHub repository URL from the newly created page (e.g. `https://github.com/<your-username>/ai-support-intelligence-platform.git`) and run:

```powershell
# Rename local branch to main
git branch -M main

# Link your GitHub repository as the origin remote
git remote add origin https://github.com/<your-username>/ai-support-intelligence-platform.git

# Push your code to GitHub
git push -u origin main
```

*(If prompted, sign in to your GitHub account in the browser or personal access token prompt).*

---

## 6. Verify Your Repository Online

1. Refresh your GitHub repository page.
2. Verify that:
   - All directories (`app/`, `data/`, `frontend/`, `scripts/`, `tests/`, `docs/`) appear.
   - The root `README.md` renders cleanly with Mermaid diagrams.
   - The `.env` file and `.db` files are **NOT** present.
   - The green commit badge shows all files committed cleanly.
