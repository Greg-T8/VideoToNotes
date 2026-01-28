# -------------------------------------------------------------------------
# Program: prompt_loader.py
# Description: Utility for loading prompt templates from markdown files
# Context: VideoToNotes pipeline - LLM prompt management
# Author: Greg Tate
# -------------------------------------------------------------------------
"""
Prompt Loader Module

Provides utilities for loading LLM prompt templates from markdown files.
"""

from pathlib import Path


# Prompts directory relative to this module
PROMPTS_DIR = Path(__file__).parent.parent.parent.parent / "prompts"


def load_prompt(name: str) -> str:
    """
    Load a prompt template from the prompts directory.

    Args:
        name: Name of the prompt file (without .md extension)

    Returns:
        The prompt content as a string

    Raises:
        FileNotFoundError: If the prompt file doesn't exist
    """
    prompt_path = PROMPTS_DIR / f"{name}.md"

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    return prompt_path.read_text(encoding="utf-8")


def get_normalize_prompt() -> str:
    """Load the normalize prompt template."""
    return load_prompt("normalize")


def get_merge_prompt() -> str:
    """Load the merge prompt template."""
    return load_prompt("merge")


def get_extract_prompt() -> str:
    """Load the extract prompt template."""
    return load_prompt("extract")


def get_section_extract_prompt() -> str:
    """Load the section extract prompt template."""
    return load_prompt("section_extract")


def get_targeted_extract_prompt() -> str:
    """Load the targeted extract prompt template."""
    return load_prompt("targeted_extract")
