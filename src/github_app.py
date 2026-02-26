# Handles GitHub App authentication for ALL repos

import jwt
import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class GitHubApp:
    """
    GitHub App authenticator
    Gives access to ALL repos where app is installed
    """

    def __init__(self):
        self.app_id      = os.getenv("GITHUB_APP_ID")
        self.private_key = os.getenv("GITHUB_PRIVATE_KEY")

    def _generate_jwt(self) -> str:
        """
        Generate JWT token to authenticate as GitHub App
        Valid for 10 minutes
        """
        now = int(time.time())

        payload = {
            "iat": now - 60,          # Issued at (60 sec ago for clock drift)
            "exp": now + (10 * 60),   # Expires in 10 minutes
            "iss": self.app_id        # Your App ID
        }

        # Sign with private key
        token = jwt.encode(
            payload,
            self.private_key,
            algorithm="RS256"
        )
        return token

    def get_installation_token(self, installation_id: int) -> str:
        """
        Get access token for a specific repo installation
        This token lets us read PRs and post comments on that repo
        """
        jwt_token = self._generate_jwt()

        # Request installation token from GitHub
        url      = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
        headers  = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept":        "application/vnd.github.v3+json"
        }

        response = requests.post(url, headers=headers)
        data     = response.json()

        return data["token"]

    def get_all_installations(self) -> list:
        """
        Get all repos/accounts where this App is installed
        This gives us the list of ALL repos to monitor!
        """
        jwt_token = self._generate_jwt()

        url     = "https://api.github.com/app/installations"
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept":        "application/vnd.github.v3+json"
        }

        response     = requests.get(url, headers=headers)
        installations = response.json()

        return [{
            "installation_id": inst["id"],
            "account":         inst["account"]["login"],
            "repo_count":      inst.get("repository_selection")
        } for inst in installations]