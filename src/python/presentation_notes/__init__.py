# -------------------------------------------------------------------------
# File: __init__.py
# Description: Presentation Notes package initialization
# Context: VideoToNotes - slide presentation to notes pipeline
# Author: Greg Tate
# -------------------------------------------------------------------------

"""
PresentationNotes

Generate structured study notes from slide presentations (PDF) with
accompanying video/audio recordings.

Pipeline stages:
0. Extract:   Render PDF pages as images and extract text per slide (Python)
1. Transcribe: Extract and transcribe audio from video (PowerShell/spx)
2. Align:     Map transcript segments to slides using LLM (LLM)
3. Annotate:  Generate detailed notes per slide from transcript + slide text (LLM)
4. Assemble:  Build final markdown with embedded slide images (deterministic)
"""

__version__ = "0.1.0"
