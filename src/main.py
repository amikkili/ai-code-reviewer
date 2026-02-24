# src/main.py
# The main FastAPI server — connects everything together!

from fastapi import FastAPI, Request
from src.ml_analyzer   import MLCodeAnalyzer
from src.github_client import GitHubClient
from src.llm_explainer import LLMExplainer
from dotenv import load_dotenv
import os

load_dotenv()

app            = FastAPI(title="AI Code Reviewer")
ml_analyzer    = MLCodeAnalyzer()
github_client  = GitHubClient()
llm_explainer  = LLMExplainer()

@app.get("/")
def home():
    return {"message": "AI Code Reviewer is running!"}


@app.post("/webhook")
async def github_webhook(request: Request):
    """
    GitHub sends events here automatically
    Triggers on every PR open or update
    """
    payload = await request.json()
    action  = payload.get("action", "")

    # Only trigger on PR open or new commits pushed
    if action not in ["opened", "synchronize"]:
        return {"status": "ignored"}

    pr_number = payload["number"]
    repo_name = payload["repository"]["full_name"]

    print(f"\n New PR #{pr_number} detected in {repo_name}")

    # Run the full AI review pipeline
    await run_ai_review(repo_name, pr_number)

    return {"status": "review completed"}


@app.post("/review/{repo_name}/{pr_number}")
async def manual_review(repo_name: str, pr_number: int):
    """
    Manually trigger a review for any PR
    Useful for testing!
    Call: POST /review/yourusername/ai-code-reviewer/1
    """
    await run_ai_review(repo_name, pr_number)
    return {"status": f"Review completed for PR #{pr_number}"}


async def run_ai_review(repo_name: str, pr_number: int):
    """
    The full AI review pipeline:
    1. Fetch PR files from GitHub
    2. Run ML analysis on each file
    3. Generate LLM explanation
    4. Post comment on PR
    """
    print(f"Starting AI Review for PR #{pr_number}...")

    # Step 1: Get changed files from GitHub
    files = github_client.get_pr_files(repo_name, pr_number)

    if not files:
        print("No Python files to review")
        return

    # Step 2: ML Analysis on each file
    print("Running ML Analysis...")
    analysis_results = []

    for file in files:
        result = ml_analyzer.analyze(file["code"], file["filename"])
        analysis_results.append(result)
        print(f" {file['filename']} — Score: {result['quality_score']}/10")

    # Step 3: LLM generates explanation
    print("Generating LLM explanation...")
    review_comment = llm_explainer.generate_review(analysis_results)

    # Step 4: Post comment on the PR
    print("Posting review on PR...")
    github_client.post_pr_comment(repo_name, pr_number, review_comment)

    print(f"AI Review Complete for PR #{pr_number}!")