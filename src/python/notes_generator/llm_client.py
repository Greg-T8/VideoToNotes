# -------------------------------------------------------------------------
# File: llm_client.py
# Description: GitHub Models client using GitHub CLI authentication
# Context: LLM client for the Exam Notes Generator pipeline
# Author: Greg Tate
# -------------------------------------------------------------------------

"""
GitHub Models Client

Provides LLM access through GitHub Models API using the authenticated
GitHub CLI session. No tokens are stored in code - authentication is
retrieved at runtime via `gh auth token`.

Prerequisites:
    - GitHub CLI installed (gh)
    - Authenticated via `gh auth login`
    - GitHub Models access enabled on your account
"""

import asyncio
import subprocess
from dataclasses import dataclass
from typing import Optional, List, Dict

import httpx


@dataclass
class ChatMessage:
    """A single chat message."""
    role: str  # "system", "user", or "assistant"
    content: str


class GitHubModelsError(Exception):
    """Error from GitHub Models API."""
    pass


class AuthenticationError(GitHubModelsError):
    """GitHub CLI authentication error."""
    pass


def get_github_token() -> str:
    """
    Retrieve GitHub token from the authenticated GitHub CLI session.

    This uses your existing `gh auth login` session - no tokens are
    stored in code or configuration files.

    Returns:
        The GitHub authentication token.

    Raises:
        AuthenticationError: If GitHub CLI is not authenticated.
    """
    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            check=True
        )
        token = result.stdout.strip()

        if not token:
            raise AuthenticationError(
                "No token returned. Run 'gh auth login' to authenticate."
            )

        return token

    except FileNotFoundError:
        raise AuthenticationError(
            "GitHub CLI (gh) not found. Install from https://cli.github.com/"
        )
    except subprocess.CalledProcessError as e:
        raise AuthenticationError(
            f"GitHub CLI authentication failed: {e.stderr.strip()}\n"
            "Run 'gh auth login' to authenticate."
        )


class GitHubModelsClient:
    """
    Client for GitHub Models API.

    Uses the authenticated GitHub CLI session for authentication.
    Supports both chat completions and simple text generation.
    """

    BASE_URL = "https://models.github.ai/inference"

    def __init__(self, timeout: float = 120.0):
        """
        Initialize the GitHub Models client.

        Args:
            timeout: Request timeout in seconds (default: 120s for long generations)
        """
        self._token: Optional[str] = None
        self.timeout = timeout

    @property
    def token(self) -> str:
        """Lazily retrieve and cache the GitHub token."""
        if self._token is None:
            self._token = get_github_token()
        return self._token

    @property
    def headers(self) -> Dict[str, str]:
        """Build request headers with authentication."""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    async def chat(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.2,
        max_tokens: int = 4000
    ) -> str:
        """
        Send a chat completion request.

        Args:
            messages: List of chat messages
            model: Model identifier (e.g., "openai/gpt-4.1-mini")
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response

        Returns:
            The assistant's response content.

        Raises:
            GitHubModelsError: If the API request fails.
        """
        payload = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.BASE_URL}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()

                return data["choices"][0]["message"]["content"]

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    raise AuthenticationError(
                        "Authentication failed. Your token may have expired.\n"
                        "Run 'gh auth login' to re-authenticate."
                    )
                raise GitHubModelsError(
                    f"API request failed ({e.response.status_code}): "
                    f"{e.response.text}"
                )
            except httpx.RequestError as e:
                raise GitHubModelsError(f"Request failed: {e}")

    async def generate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.2,
        max_tokens: int = 4000,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate a response from a simple prompt.

        Args:
            prompt: The user prompt
            model: Model identifier (e.g., "openai/gpt-4.1-mini")
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
            system_prompt: Optional system prompt for context

        Returns:
            The generated response content.
        """
        messages = []

        # Add system prompt if provided
        if system_prompt:
            messages.append(ChatMessage(role="system", content=system_prompt))

        # Add user prompt
        messages.append(ChatMessage(role="user", content=prompt))

        return await self.chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

    def generate_sync(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.2,
        max_tokens: int = 4000,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Synchronous wrapper for generate().

        Args:
            prompt: The user prompt
            model: Model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            system_prompt: Optional system prompt

        Returns:
            The generated response content.
        """
        return asyncio.run(
            self.generate(prompt, model, temperature, max_tokens, system_prompt)
        )


def verify_authentication() -> bool:
    """
    Verify that GitHub CLI is authenticated.

    Returns:
        True if authenticated, False otherwise.
    """
    try:
        get_github_token()
        return True
    except AuthenticationError:
        return False


if __name__ == "__main__":
    # Quick test of authentication
    print("Testing GitHub CLI authentication...")

    if verify_authentication():
        print("✓ GitHub CLI is authenticated")
        print("✓ Ready to use GitHub Models")
    else:
        print("✗ Not authenticated")
        print("  Run 'gh auth login' to authenticate")
