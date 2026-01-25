import subprocess
import platform
import os

def get_github_token() -> str:
    """Get token from secure OS credential store."""
    
    # 1. Environment variable (for CI/override)
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    
    # 2. GitHub CLI
    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            check=True
        )
        if result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # 3. OS-specific credential store
    system = platform.system()
    
    if system == "Windows":
        # Windows Credential Manager
        try:
            import subprocess
            result = subprocess.run(
                ["powershell", "-Command",
                 "(Get-StoredCredential -Target 'github-models-token').Password"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception:
            pass
    
    elif system == "Darwin":  # macOS
        # Keychain
        try:
            result = subprocess.run(
                ["security", "find-generic-password",
                 "-s", "github-models-token", "-w"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
    
    raise ValueError(
        "GitHub token not found.\n\n"
        "Setup options:\n"
        "  1. Run: gh auth login (recommended)\n"
        "  2. Set: export GITHUB_TOKEN='ghp_xxx'\n"
        "  3. Store in credential manager (see docs)"
    )