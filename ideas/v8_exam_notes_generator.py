# ============================================================================
# SECURE TOKEN HANDLING
# ============================================================================

import subprocess
import os
from pathlib import Path

def get_github_token() -> str:
    """
    Get GitHub token securely. Priority:
    1. GITHUB_TOKEN environment variable
    2. GitHub CLI (gh auth token)
    3. .env file in current directory
    4. ~/.config/gh-models/.env
    """
    
    # 1. Environment variable (CI/CD or explicit override)
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        print("   🔑 Using token from GITHUB_TOKEN environment variable")
        return token
    
    # 2. GitHub CLI (recommended for local use)
    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        token = result.stdout.strip()
        if token:
            print("   🔑 Using token from GitHub CLI")
            return token
    except subprocess.CalledProcessError:
        pass  # gh not authenticated
    except FileNotFoundError:
        pass  # gh not installed
    except subprocess.TimeoutExpired:
        pass  # gh hanging
    
    # 3. .env file in current directory
    env_file = Path(".env")
    if env_file.exists():
        token = _parse_env_file(env_file)
        if token:
            print("   🔑 Using token from .env file")
            return token
    
    # 4. User config directory
    config_file = Path.home() / ".config" / "gh-models" / ".env"
    if config_file.exists():
        token = _parse_env_file(config_file)
        if token:
            print("   🔑 Using token from ~/.config/gh-models/.env")
            return token
    
    # No token found
    raise ValueError(
        "\n❌ GitHub token not found!\n\n"
        "Setup (choose one):\n\n"
        "  Option A - GitHub CLI (recommended):\n"
        "    gh auth login\n\n"
        "  Option B - Environment variable:\n"
        "    export GITHUB_TOKEN='ghp_xxxx'\n\n"
        "  Option C - .env file (add to .gitignore!):\n"
        "    echo 'GITHUB_TOKEN=ghp_xxxx' > .env\n"
    )

def _parse_env_file(path: Path) -> str | None:
    """Parse GITHUB_TOKEN from .env file."""
    for line in path.read_text().splitlines():
        line = line.strip()
        if line.startswith("#") or not line:
            continue
        if line.startswith("GITHUB_TOKEN="):
            value = line.split("=", 1)[1].strip()
            # Remove quotes if present
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            return value
    return None

def create_client() -> AsyncOpenAI:
    """Create OpenAI-compatible client for GitHub Models."""
    token = get_github_token()
    return AsyncOpenAI(api_key=token, base_url=GITHUB_MODELS_BASE_URL)