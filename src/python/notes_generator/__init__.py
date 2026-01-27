# -------------------------------------------------------------------------
# File: __init__.py
# Description: Notes Generator package initialization
# Context: VideoToNotes - Python package root
# Author: Greg Tate
# -------------------------------------------------------------------------

"""
VideoToNotes

Generate structured study notes from video transcripts using AI.

Pipeline stages:
0. Normalize: Convert varied index formats to consistent JSON (LLM)
1. Chunk: Split transcript into ~20KB pieces (Python)
2. Extract: Generate notes per section from relevant chunks (LLM)
3. Assemble: Build final markdown document (deterministic)
"""

__version__ = "0.1.0"
