# src/github_client.py
# Connects to YOUR GitHub — fetches PRs and posts comments

from github import Github
from dotenv import load_dotenv
import os

load_dotenv()

class GitHubClient:
    """Handles all GitHub API interactions"""

    def __init__(self):
        token = os.getenv("GITHUB_TOKEN")
        self.client = Github(token)
        print("Connected to GitHub!")

    def get_pr_files(self, repo_name: str, pr_number: int) -> list:
        """Fetch all changed files from a Pull Request"""
        repo  = self.client.get_repo(repo_name)
        pr    = repo.get_pull(pr_number)
        files = []

        for file in pr.get_files():
            # Only analyze Python files
            if file.filename.endswith(".py") and file.patch:
                files.append({
                    "filename": file.filename,
                    "code":     file.patch,         # The actual code changes
                    "additions": file.additions,
                    "deletions": file.deletions
                })

        print(f"Fetched {len(files)} Python files from PR #{pr_number}")
        return files

    def post_pr_comment(self, repo_name: str, 
                         pr_number: int, comment: str):
        """Post AI review comment on the Pull Request"""
        repo    = self.client.get_repo(repo_name)
        pr      = repo.get_pull(pr_number)
        pr.create_issue_comment(comment)
        print(f"AI review posted on PR #{pr_number}!")

    def get_open_prs(self, repo_name: str) -> list:
        """Get all open PRs in a repository"""
        repo = self.client.get_repo(repo_name)
        prs  = repo.get_pulls(state='open')

        return [{
            "number": pr.number,
            "title":  pr.title,
            "author": pr.user.login,
            "url":    pr.html_url
        } for pr in prs]