# src/github_client.py — Updated for GitHub App (all repos!)

from github import Github, Auth
from src.github_app import GitHubApp
from dotenv import load_dotenv
import os

load_dotenv()

class GitHubClient:
    """
    GitHub client that works with ALL repos
    via GitHub App installation tokens
    """

    def __init__(self):
        self.app = GitHubApp()
        print("✅ GitHub App client initialized!")

    def _get_repo_client(self, installation_id: int):
        """Get authenticated client for a specific repo"""
        token  = self.app.get_installation_token(installation_id)
        client = Github(auth=Auth.Token(token))
        return client

    def get_pr_files(self, repo_name: str,
                     pr_number: int,
                     installation_id: int) -> list:
        """Fetch changed Python files from a PR"""

        client = self._get_repo_client(installation_id)
        repo   = client.get_repo(repo_name)
        pr     = repo.get_pull(pr_number)
        files  = []

        for file in pr.get_files():
            if file.filename.endswith(".py") and file.patch:
                files.append({
                    "filename":  file.filename,
                    "code":      file.patch,
                    "additions": file.additions,
                    "deletions": file.deletions
                })

        print(f"✅ Fetched {len(files)} files from {repo_name} PR #{pr_number}")
        return files

    def post_pr_comment(self, repo_name: str,
                        pr_number: int,
                        comment: str,
                        installation_id: int):
        """Post AI review comment on a PR"""

        client = self._get_repo_client(installation_id)
        repo   = client.get_repo(repo_name)
        pr     = repo.get_pull(pr_number)
        pr.create_issue_comment(comment)

        print(f"✅ Review posted on {repo_name} PR #{pr_number}!")

    def get_pr_info(self, repo_name: str,
                    pr_number: int,
                    installation_id: int) -> dict:
        """Get PR title and author info"""

        client = self._get_repo_client(installation_id)
        repo   = client.get_repo(repo_name)
        pr     = repo.get_pull(pr_number)

        return {
            "title":   pr.title,
            "author":  pr.user.login,
            "url":     pr.html_url,
            "files":   pr.changed_files
        }