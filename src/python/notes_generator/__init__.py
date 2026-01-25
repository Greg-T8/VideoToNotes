# -------------------------------------------------------------------------
# File: __init__.py
# Description: Notes Generator package initialization
# Context: Exam Notes Generator - Python package root
# Author: Greg Tate
# -------------------------------------------------------------------------

"""
Exam Notes Generator

A three-stage pipeline for generating structured notes from video transcripts:
1. Extract: Process transcript chunks into structured notes (parallel, fast model)
2. Merge: Combine partials by section, deduplicate (reasoning model)
3. Assemble: Build final document from TOC (deterministic)
"""

__version__ = "0.1.0"
