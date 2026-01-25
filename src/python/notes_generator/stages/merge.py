# -------------------------------------------------------------------------
# File: merge.py
# Description: Merge stage - combine partials by section, deduplicate
# Context: Stage 2 of the Exam Notes Generator pipeline
# Author: Greg Tate
# -------------------------------------------------------------------------

"""
Merge Stage

Combines partial notes from extraction stage.
- Groups notes by section
- Deduplicates content
- Uses reasoning model (deepseek-r1)
"""

from typing import List, Dict


def merge_partials(partials: List[str], toc_sections: List[str], model: str = "deepseek-r1") -> Dict[str, str]:
    """
    Merge partial notes by section.

    Args:
        partials: List of partial notes from extraction stage
        toc_sections: List of section headings from TOC
        model: The model to use for merging

    Returns:
        Dictionary mapping section headings to merged content
    """
    # TODO: Implement LLM call for merging
    raise NotImplementedError("Merge stage not yet implemented")


if __name__ == "__main__":
    # Allow running this stage directly for debugging
    print("Merge stage - run with debugger for testing")
