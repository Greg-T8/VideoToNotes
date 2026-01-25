# -------------------------------------------------------------------------
# File: extract.py
# Description: Extract stage - process transcript chunks into structured notes
# Context: Stage 1 of the Exam Notes Generator pipeline
# Author: Greg Tate
# -------------------------------------------------------------------------

"""
Extract Stage

Processes 20KB transcript chunks into structured notes.
- Runs in parallel for speed
- Uses fast model (gpt-4.1-mini)
- Outputs partial notes per chunk
"""

from pathlib import Path
from typing import List


def extract_from_chunk(chunk_text: str, toc_context: str, model: str = "gpt-4.1-mini") -> str:
    """
    Extract structured notes from a single transcript chunk.

    Args:
        chunk_text: The transcript chunk text
        toc_context: Table of contents for context
        model: The model to use for extraction

    Returns:
        Structured notes extracted from the chunk
    """
    # TODO: Implement LLM call
    raise NotImplementedError("Extract stage not yet implemented")


def extract_all_chunks(chunks_path: Path, toc_path: Path, model: str = "gpt-4.1-mini") -> List[str]:
    """
    Extract notes from all chunks in parallel.

    Args:
        chunks_path: Path to the transcript.zip file
        toc_path: Path to the contents.md file
        model: The model to use for extraction

    Returns:
        List of partial notes from each chunk
    """
    # TODO: Implement parallel extraction
    raise NotImplementedError("Extract stage not yet implemented")


if __name__ == "__main__":
    # Allow running this stage directly for debugging
    print("Extract stage - run with debugger for testing")
