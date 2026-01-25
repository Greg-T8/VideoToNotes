# -------------------------------------------------------------------------
# File: __init__.py
# Description: Notes Generator package initialization
# Context: Exam Notes Generator - Python package root
# Author: Greg Tate
# -------------------------------------------------------------------------

"""
Exam Notes Generator

Generate structured, exam-focused study notes from video transcripts using AI.

Pipeline stages:
0. Normalize: Convert varied index formats to consistent JSON (LLM)
1. Chunk: Split transcript into ~20KB pieces (PowerShell)
2. Extract: Generate section notes from chunks in parallel (LLM)
3. Merge: Combine and deduplicate partials by section (LLM)
4. Assemble: Build final markdown document (deterministic)
"""

__version__ = "0.1.0"
