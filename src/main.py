# src/main.py — Fixed with lazy initialization

from fastapi import FastAPI, Request
from dotenv import load_dotenv
import os

# Load env variables FIRST before anything else!
load_dotenv()

app = FastAPI(title="AI Code Reviewer")

# ─────────────────────────────────────────────
# Lazy load — create instances ONLY when needed
# NOT at startup!
# ─────────────────────────────────────────────
_ml_analyzer   = None
_github_client = None
_llm_explainer = None

def get_ml_analyzer():
    global _ml_analyzer
    if _ml_analyzer is None:
        from src.ml_analyzer import MLCodeAnalyzer
        _ml_analyzer = MLCodeAnalyzer()
    return _ml_analyzer

def get_github_client():
    global _github_client
    if _github_client is None:
        from src.github_client import GitHubClient
        _github_client = GitHubClient()
    return _github_client

def get_llm_explainer():
    global _llm_explainer
    if _llm_explainer is None:
        from src.llm_explainer import LLMExplainer
        _llm_explainer = LLMExplainer()
    return _llm_explainer


@app.get("/")
def home():
    return {"message": " AI Code Reviewer is running!"}


@app.post("/webhook")
async def github_webhook(request: Request):
    """GitHub sends PR events here automatically"""
    payload = await request.json()
    action  = payload.get("action", "")

    if action not in ["opened", "synchronize"]:
        return {"status": "ignored"}

    pr_number = payload["number"]
    repo_name = payload["repository"]["full_name"]

    print(f"\n New PR #{pr_number} detected in {repo_name}")
    await run_ai_review(repo_name, pr_number)

    return {"status": "review completed"}


@app.post("/review/{repo_owner}/{repo_name}/{pr_number}")
async def manual_review(repo_owner: str, repo_name: str, pr_number: int):
    """Manually trigger a review — useful for testing!"""
    full_repo_name = f"{repo_owner}/{repo_name}"
    await run_ai_review(full_repo_name, pr_number)
    return {"status": f"Review completed for PR #{pr_number}"}


async def run_ai_review(repo_name: str, pr_number: int):
    """Full AI review pipeline"""
    print(f" Starting AI Review for PR #{pr_number}...")

    # Get instances only when needed
    ml_analyzer   = get_ml_analyzer()
    github_client = get_github_client()
    llm_explainer = get_llm_explainer()

    # Step 1: Get changed files
    files = github_client.get_pr_files(repo_name, pr_number)

    if not files:
        print("No Python files to review")
        return

    # Step 2: ML Analysis
    print(" Running ML Analysis...")
    analysis_results = []

    for file in files:
        result = ml_analyzer.analyze(file["code"], file["filename"])
        analysis_results.append(result)
        print(f"   {file['filename']} — Score: {result['quality_score']}/10")

    # Step 3: LLM Explanation
    print(" Generating Groq LLM explanation...")
    review_comment = llm_explainer.generate_review(analysis_results)

    # Step 4: Post on PR
    print(" Posting review on PR...")
    github_client.post_pr_comment(repo_name, pr_number, review_comment)

    print(f" AI Review Complete for PR #{pr_number}!")