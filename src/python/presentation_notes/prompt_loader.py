# -------------------------------------------------------------------------
# File: prompt_loader.py
# Description: Utility for loading prompt templates for presentation notes
# Context: PresentationNotes pipeline - LLM prompt management
# Author: Greg Tate
# -------------------------------------------------------------------------

"""
Prompt Loader for Presentation Notes

Provides utilities for loading LLM prompt templates from the shared
prompts directory.
"""

from pathlib import Path


# Prompts directory relative to this module
# Path: src/python/presentation_notes/prompt_loader.py -> src/prompts/
PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"


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


def get_slide_align_prompt() -> str:
    """Load the slide alignment prompt template."""
    return load_prompt("slide_align")


def get_slide_annotate_prompt() -> str:
    """Load the slide annotation prompt template."""
    return load_prompt("slide_annotate")
