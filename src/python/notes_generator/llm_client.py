# -------------------------------------------------------------------------
# File: llm_client.py
# Description: LLM client supporting GitHub Models and Azure OpenAI providers
# Context: LLM client for the VideoToNotes pipeline
# Author: Greg Tate
# -------------------------------------------------------------------------

"""
LLM Client (GitHub Models + Azure OpenAI)

Provides LLM access through two providers:

1. GitHub Models (default) - Uses GitHub CLI authentication
   Prerequisites:
       - GitHub CLI installed (gh)
       - Authenticated via `gh auth login`
       - GitHub Models access enabled on your account

2. Azure OpenAI - Uses Azure CLI token (DefaultAzureCredential)
   Prerequisites:
       - Azure CLI installed (az)
       - Authenticated via `az login`
       - Azure OpenAI endpoint and deployment name

Use create_llm_client() factory to create the appropriate client.
"""

import asyncio
import os
import random
import subprocess
from dataclasses import dataclass
from typing import Optional, List, Dict

import httpx


# Retry configuration
MAX_RETRIES = 5
INITIAL_BACKOFF = 2.0  # seconds
MAX_BACKOFF = 60.0  # seconds
BACKOFF_MULTIPLIER = 2.0
JITTER_FACTOR = 0.25  # 25% random jitter


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
        max_tokens: int = 4000,
        context: Optional[str] = None
    ) -> str:
        """
        Send a chat completion request with automatic retry on rate limits.

        Args:
            messages: List of chat messages
            model: Model identifier (e.g., "openai/gpt-4.1-mini")
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
            context: Optional context string for logging (e.g., "chunk 3/14")

        Returns:
            The assistant's response content.

        Raises:
            GitHubModelsError: If the API request fails after all retries.
        """
        # Determine if this is a reasoning model (o1, o3, o4 series)
        is_reasoning_model = any(
            x in model.lower() for x in ['/o1', '/o3', '/o4', 'o1-', 'o3-', 'o4-']
        )

        # Build payload - reasoning models use different parameters
        payload = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
        }

        if is_reasoning_model:
            # Reasoning models use max_completion_tokens and don't support temperature
            payload["max_completion_tokens"] = max_tokens
        else:
            # Standard models use max_tokens and temperature
            payload["temperature"] = temperature
            payload["max_tokens"] = max_tokens

        last_error = None
        backoff = INITIAL_BACKOFF

        for attempt in range(MAX_RETRIES):
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
                    status_code = e.response.status_code

                    # Handle authentication errors immediately
                    if status_code == 401:
                        raise AuthenticationError(
                            "Authentication failed. Your token may have expired.\n"
                            "Run 'gh auth login' to re-authenticate."
                        )

                    # Handle rate limiting with retry
                    if status_code == 429:
                        last_error = e

                        # Check for Retry-After header
                        retry_after = e.response.headers.get("Retry-After")
                        if retry_after:
                            try:
                                wait_time = float(retry_after)
                            except ValueError:
                                wait_time = backoff
                        else:
                            # Calculate exponential backoff with jitter
                            jitter = random.uniform(-JITTER_FACTOR, JITTER_FACTOR) * backoff
                            wait_time = min(backoff + jitter, MAX_BACKOFF)

                        if attempt < MAX_RETRIES - 1:
                            ctx = f" [{context}]" if context else ""
                            print(f"  Rate limited{ctx}. Waiting {wait_time:.1f}s before retry {attempt + 2}/{MAX_RETRIES}...")
                            await asyncio.sleep(wait_time)
                            backoff = min(backoff * BACKOFF_MULTIPLIER, MAX_BACKOFF)
                            continue

                    # Non-retryable error
                    raise GitHubModelsError(
                        f"API request failed ({status_code}): "
                        f"{e.response.text}"
                    )

                except httpx.RequestError as e:
                    last_error = e

                    # Network errors are retryable
                    if attempt < MAX_RETRIES - 1:
                        jitter = random.uniform(-JITTER_FACTOR, JITTER_FACTOR) * backoff
                        wait_time = min(backoff + jitter, MAX_BACKOFF)
                        ctx = f" [{context}]" if context else ""
                        print(f"  Network error{ctx}. Waiting {wait_time:.1f}s before retry {attempt + 2}/{MAX_RETRIES}...")
                        await asyncio.sleep(wait_time)
                        backoff = min(backoff * BACKOFF_MULTIPLIER, MAX_BACKOFF)
                        continue

                    raise GitHubModelsError(f"Request failed: {e}")

        # All retries exhausted
        raise GitHubModelsError(
            f"API request failed after {MAX_RETRIES} retries: {last_error}"
        )

    async def generate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.2,
        max_tokens: int = 4000,
        system_prompt: Optional[str] = None,
        context: Optional[str] = None
    ) -> str:
        """
        Generate a response from a simple prompt.

        Args:
            prompt: The user prompt
            model: Model identifier (e.g., "openai/gpt-4.1-mini")
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
            system_prompt: Optional system prompt for context
            context: Optional context string for logging (e.g., "chunk 3/14")

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
            max_tokens=max_tokens,
            context=context
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


# =========================================================================
# Azure OpenAI Client
# =========================================================================


def get_azure_token() -> str:
    """
    Retrieve an Azure AD token for Cognitive Services using the Azure CLI.

    Returns:
        The Azure AD bearer token.

    Raises:
        AuthenticationError: If Azure CLI is not authenticated.
    """
    try:
        result = subprocess.run(
            [
                "az", "account", "get-access-token",
                "--resource", "https://cognitiveservices.azure.com",
                "--query", "accessToken",
                "-o", "tsv"
            ],
            capture_output=True,
            text=True,
            check=True
        )
        token = result.stdout.strip()

        if not token:
            raise AuthenticationError(
                "No token returned. Run 'az login' to authenticate."
            )

        return token

    except FileNotFoundError:
        raise AuthenticationError(
            "Azure CLI (az) not found. Install from https://aka.ms/installazurecli"
        )
    except subprocess.CalledProcessError as e:
        raise AuthenticationError(
            f"Azure CLI authentication failed: {e.stderr.strip()}\n"
            "Run 'az login' to authenticate."
        )


class AzureOpenAIClient:
    """
    Client for Azure OpenAI API.

    Uses Azure CLI token authentication (passwordless). The endpoint
    and deployment name are provided from the Terraform outputs.
    """

    def __init__(
        self,
        endpoint: str,
        deployment: str,
        api_version: str = "2024-12-01-preview",
        timeout: float = 120.0
    ):
        """
        Initialize the Azure OpenAI client.

        Args:
            endpoint: Azure OpenAI endpoint URL
            deployment: Model deployment name
            api_version: Azure OpenAI API version
            timeout: Request timeout in seconds
        """
        self.endpoint = endpoint.rstrip("/")
        self.deployment = deployment
        self.api_version = api_version
        self.timeout = timeout
        self._token: Optional[str] = None

    @property
    def token(self) -> str:
        """Lazily retrieve and cache the Azure AD token."""
        if self._token is None:
            self._token = get_azure_token()
        return self._token

    @property
    def headers(self) -> Dict[str, str]:
        """Build request headers with Azure AD authentication."""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    @property
    def chat_url(self) -> str:
        """Build the chat completions URL for this deployment."""
        return (
            f"{self.endpoint}/openai/deployments/{self.deployment}"
            f"/chat/completions?api-version={self.api_version}"
        )

    async def chat(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.2,
        max_tokens: int = 4000,
        context: Optional[str] = None
    ) -> str:
        """
        Send a chat completion request to Azure OpenAI.

        The model parameter is accepted for interface compatibility but
        the deployment name from the constructor is used instead.

        Args:
            messages: List of chat messages
            model: Ignored (deployment name is used)
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
            context: Optional context string for logging

        Returns:
            The assistant's response content.
        """
        # Build payload (Azure OpenAI does not need the model field)
        payload = {
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        last_error = None
        backoff = INITIAL_BACKOFF

        for attempt in range(MAX_RETRIES):
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                try:
                    response = await client.post(
                        self.chat_url,
                        headers=self.headers,
                        json=payload
                    )
                    response.raise_for_status()
                    data = response.json()

                    return data["choices"][0]["message"]["content"]

                except httpx.HTTPStatusError as e:
                    status_code = e.response.status_code

                    # Handle authentication errors - refresh token and retry
                    if status_code == 401:
                        self._token = None
                        if attempt < MAX_RETRIES - 1:
                            ctx = f" [{context}]" if context else ""
                            print(f"  Token expired{ctx}. Refreshing...")
                            continue
                        raise AuthenticationError(
                            "Azure authentication failed. Run 'az login' to re-authenticate."
                        )

                    # Handle rate limiting with retry
                    if status_code == 429:
                        last_error = e
                        retry_after = e.response.headers.get("Retry-After")
                        if retry_after:
                            try:
                                wait_time = float(retry_after)
                            except ValueError:
                                wait_time = backoff
                        else:
                            jitter = random.uniform(-JITTER_FACTOR, JITTER_FACTOR) * backoff
                            wait_time = min(backoff + jitter, MAX_BACKOFF)

                        if attempt < MAX_RETRIES - 1:
                            ctx = f" [{context}]" if context else ""
                            print(f"  Rate limited{ctx}. Waiting {wait_time:.1f}s before retry {attempt + 2}/{MAX_RETRIES}...")
                            await asyncio.sleep(wait_time)
                            backoff = min(backoff * BACKOFF_MULTIPLIER, MAX_BACKOFF)
                            continue

                    raise GitHubModelsError(
                        f"Azure OpenAI request failed ({status_code}): "
                        f"{e.response.text}"
                    )

                except httpx.RequestError as e:
                    last_error = e
                    if attempt < MAX_RETRIES - 1:
                        jitter = random.uniform(-JITTER_FACTOR, JITTER_FACTOR) * backoff
                        wait_time = min(backoff + jitter, MAX_BACKOFF)
                        ctx = f" [{context}]" if context else ""
                        print(f"  Network error{ctx}. Waiting {wait_time:.1f}s before retry {attempt + 2}/{MAX_RETRIES}...")
                        await asyncio.sleep(wait_time)
                        backoff = min(backoff * BACKOFF_MULTIPLIER, MAX_BACKOFF)
                        continue
                    raise GitHubModelsError(f"Request failed: {e}")

        raise GitHubModelsError(
            f"Azure OpenAI request failed after {MAX_RETRIES} retries: {last_error}"
        )

    async def generate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.2,
        max_tokens: int = 4000,
        system_prompt: Optional[str] = None,
        context: Optional[str] = None
    ) -> str:
        """
        Generate a response from a simple prompt.

        Args:
            prompt: The user prompt
            model: Ignored (deployment name is used)
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
            system_prompt: Optional system prompt for context
            context: Optional context string for logging

        Returns:
            The generated response content.
        """
        messages = []

        if system_prompt:
            messages.append(ChatMessage(role="system", content=system_prompt))

        messages.append(ChatMessage(role="user", content=prompt))

        return await self.chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            context=context
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
            model: Ignored (deployment name is used)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            system_prompt: Optional system prompt

        Returns:
            The generated response content.
        """
        return asyncio.run(
            self.generate(prompt, model, temperature, max_tokens, system_prompt)
        )


# =========================================================================
# Factory
# =========================================================================


def create_llm_client(
    provider: str = "github",
    azure_endpoint: Optional[str] = None,
    azure_deployment: Optional[str] = None,
    timeout: float = 120.0
):
    """
    Create the appropriate LLM client based on the selected provider.

    Args:
        provider: "github" for GitHub Models or "azure" for Azure OpenAI
        azure_endpoint: Azure OpenAI endpoint (required when provider is "azure")
        azure_deployment: Azure model deployment name (required when provider is "azure")
        timeout: Request timeout in seconds

    Returns:
        A GitHubModelsClient or AzureOpenAIClient instance.

    Raises:
        ValueError: If Azure provider is selected without required parameters.
    """
    if provider.lower() == "azure":
        # Resolve endpoint and deployment from parameters or environment
        endpoint = azure_endpoint or os.environ.get("AZURE_OPENAI_ENDPOINT")
        deployment = azure_deployment or os.environ.get("AZURE_OPENAI_DEPLOYMENT")

        if not endpoint:
            raise ValueError(
                "Azure provider requires --azure-endpoint or "
                "AZURE_OPENAI_ENDPOINT environment variable."
            )
        if not deployment:
            raise ValueError(
                "Azure provider requires --azure-deployment or "
                "AZURE_OPENAI_DEPLOYMENT environment variable."
            )

        return AzureOpenAIClient(
            endpoint=endpoint,
            deployment=deployment,
            timeout=timeout
        )

    # Default to GitHub Models
    return GitHubModelsClient(timeout=timeout)


if __name__ == "__main__":
    # Quick test of authentication
    print("Testing GitHub CLI authentication...")

    if verify_authentication():
        print("✓ GitHub CLI is authenticated")
        print("✓ Ready to use GitHub Models")
    else:
        print("✗ Not authenticated")
        print("  Run 'gh auth login' to authenticate")
