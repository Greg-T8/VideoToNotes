# -------------------------------------------------------------------------
# File: __init__.py
# Description: Stages package initialization
# Context: PresentationNotes - pipeline stages
# Author: Greg Tate
# -------------------------------------------------------------------------

"""
Pipeline stages for PresentationNotes.

Stages:
- extract_slides: Render PDF pages as images and extract text (Python)
- parse_transcript: Parse SRT transcript into timestamped segments (Python)
- align: Map transcript segments to slides (LLM)
- annotate: Generate detailed notes per slide (LLM)
- assemble: Build final markdown with embedded slide images (Python)
"""
