# src/main.py — Updated for GitHub App (all repos!)

from fastapi import FastAPI, Request, Header
from src.ml_analyzer   import MLCodeAnalyzer
from src.github_client import GitHubClient
from src.llm_explainer import LLMExplainer
from dotenv import load_dotenv
import hashlib
import hmac
import os

load_dotenv()

app           = FastAPI(title="AI Code Reviewer — All Repos!")
ml_analyzer   = MLCodeAnalyzer()
github_client = GitHubClient()
llm_explainer = LLMExplainer()

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """
    Verify the request is genuinely from GitHub
    Security check — prevents fake requests!
    """
    if not WEBHOOK_SECRET:
        return True     # Skip check if secret not set

    expected = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature or "")


@app.get("/")
def home():
    return {
        "message": "🤖 AI Code Reviewer is running for ALL repos!",
        "status":  "active"
    }


@app.post("/webhook")
async def github_webhook(
    request: Request,
    x_github_event:    str = Header(None),
    x_hub_signature_256: str = Header(None)
):
    """
    Receives ALL GitHub events from ALL repos
    where your App is installed
    """
    body    = await request.body()
    payload = await request.json()

    # Security: Verify request is from GitHub
    if not verify_webhook_signature(body, x_hub_signature_256):
        print("❌ Invalid webhook signature — rejected!")
        return {"status": "unauthorized"}

    # Handle PR events
    if x_github_event == "pull_request":
        action = payload.get("action", "")

        # Only on PR open or new commits pushed
        if action in ["opened", "synchronize"]:
            pr_number       = payload["number"]
            repo_name       = payload["repository"]["full_name"]
            installation_id = payload["installation"]["id"]

            print(f"\n🔔 PR #{pr_number} in {repo_name}")
            print(f"   Installation ID: {installation_id}")

            # Run AI review
            await run_ai_review(repo_name, pr_number, installation_id)

    # Handle App installation events
    elif x_github_event == "installation":
        action  = payload.get("action")
        account = payload["installation"]["account"]["login"]

        if action == "created":
            print(f"🎉 App installed by: {account}")
        elif action == "deleted":
            print(f"👋 App uninstalled by: {account}")

    return {"status": "processed"}


@app.post("/review/{repo_owner}/{repo_name}/{pr_number}")
async def manual_review(repo_owner: str,
                        repo_name: str,
                        pr_number: int,
                        installation_id: int):
    """
    Manually trigger review for any PR on any repo
    Usage: POST /review/username/reponame/1?installation_id=123
    """
    full_repo_name = f"{repo_owner}/{repo_name}"
    await run_ai_review(full_repo_name, pr_number, installation_id)
    return {
        "status": f"✅ Review completed for {full_repo_name} PR #{pr_number}"
    }


@app.get("/installations")
async def list_installations():
    """
    See all repos/accounts where your App is installed
    Useful for checking which repos are being monitored!
    """
    from src.github_app import GitHubApp
    app_client     = GitHubApp()
    installations  = app_client.get_all_installations()

    return {
        "total_installations": len(installations),
        "installations":       installations
    }


async def run_ai_review(repo_name: str,
                        pr_number: int,
                        installation_id: int):
    """
    Full AI Review Pipeline:
    1. Fetch PR files
    2. ML Analysis
    3. LLM Explanation
    4. Post comment on PR
    """
    print(f"\n🚀 Starting AI Review: {repo_name} PR #{pr_number}")

    try:
        # Step 1: Get PR files from GitHub
        files = github_client.get_pr_files(
            repo_name, pr_number, installation_id
        )

        if not files:
            print("ℹ️ No Python files to review")
            return

        # Step 2: ML Analysis
        print("🤖 Running ML Analysis...")
        analysis_results = []

        for file in files:
            result = ml_analyzer.analyze(file["code"], file["filename"])
            analysis_results.append(result)
            print(f"  ✅ {file['filename']} — Score: {result['quality_score']}/10")

        # Step 3: LLM Explanation
        print("💬 Generating LLM review...")
        review_comment = llm_explainer.generate_review(analysis_results)

        # Step 4: Post on PR
        print("📝 Posting review...")
        github_client.post_pr_comment(
            repo_name, pr_number,
            review_comment, installation_id
        )

        print(f"✅ Review complete for {repo_name} PR #{pr_number}!")

    except Exception as e:
        print(f"❌ Review failed: {e}")