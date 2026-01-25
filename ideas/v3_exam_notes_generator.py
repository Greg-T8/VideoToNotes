# ============================================================================
# CONFIGURATION - Updated for GitHub Models
# ============================================================================

# GitHub Models API endpoint
GITHUB_MODELS_BASE_URL = "https://models.github.ai/inference"

# Available models from GitHub Models (ranked by recommendation)
MODELS = {
    # Tier 1: Best for exam notes
    "deepseek": "deepseek/deepseek-r1-0528",      # ⭐ RECOMMENDED
    "gpt4.1": "openai/gpt-4.1",                    # Reliable backup
    
    # Tier 2: Strong alternatives  
    "gpt5-mini": "openai/gpt-5-mini",              # Latest OpenAI balanced
    "llama-405b": "meta/meta-llama-3.1-405b-instruct",  # Massive, thorough
    "o3-mini": "openai/o3-mini",                   # Reasoning-optimized
    
    # Tier 3: Fast options (for quick iterations)
    "gpt4.1-mini": "openai/gpt-4.1-mini",          # Fast, good enough
    "phi4-reason": "microsoft/phi-4-reasoning",   # Efficient reasoning
    "deepseek-v3": "deepseek/deepseek-v3-0324",   # Fast DeepSeek
    
    # Experimental
    "gpt5": "openai/gpt-5",                        # If you want bleeding edge
    "grok3": "xai/grok-3",                         # Alternative perspective
}

DEFAULT_MODEL = "deepseek"  # DeepSeek-R1-0528

# Model-specific settings (some models need adjustments)
MODEL_SETTINGS = {
    "deepseek/deepseek-r1-0528": {
        "temperature": 0.2,      # Lower for consistency
        "max_tokens": 4000,
    },
    "openai/gpt-4.1": {
        "temperature": 0.3,
        "max_tokens": 4000,
    },
    "openai/o3-mini": {
        "temperature": 0.2,      # Reasoning models work better with low temp
        "max_tokens": 4000,
    },
    "meta/meta-llama-3.1-405b-instruct": {
        "temperature": 0.3,
        "max_tokens": 4000,
    },
    # Default for unlisted models
    "default": {
        "temperature": 0.3,
        "max_tokens": 4000,
    }
}

def get_model_settings(model_id: str) -> dict:
    """Get optimal settings for a specific model."""
    return MODEL_SETTINGS.get(model_id, MODEL_SETTINGS["default"])