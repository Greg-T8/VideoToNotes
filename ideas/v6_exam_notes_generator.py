import subprocess
import os

def get_github_token() -> str:
    """Get token from GitHub CLI (most secure for local use)."""
    
    # 1. Check environment variable first (for CI/automation)
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    
    # 2. Use GitHub CLI's stored token
    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            check=True
        )
        token = result.stdout.strip()
        if token:
            return token
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    raise ValueError(
        "GitHub token not found.\n"
        "Options:\n"
        "  1. Run: gh auth login\n"
        "  2. Set: export GITHUB_TOKEN='ghp_xxx'\n"
        "  3. Create .env file with: GITHUB_TOKEN=ghp_xxx"
    )