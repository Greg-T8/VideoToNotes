# -------------------------------------------------------------------------
# File: __init__.py
# Description: Stages package initialization
# Context: VideoToNotes - pipeline stages
# Author: Greg Tate
# -------------------------------------------------------------------------

"""
Pipeline stages for VideoToNotes.

Stages:
- normalize: Convert varied index formats to JSON (LLM)
- chunk: Split transcript into ~20KB pieces (Python)
- extract: Generate section notes from chunks (LLM)
- merge: Combine and deduplicate partials (LLM)
- assemble: Build final markdown document
"""

from notes_generator.stages.normalize import normalize_index, normalize_index_sync
from notes_generator.stages.chunk import chunk_transcript, load_chunks_from_zip
from notes_generator.stages.extract import extract_from_chunk, extract_all_chunks
from notes_generator.stages.merge import merge_section, merge_all_sections
from notes_generator.stages.assemble import assemble_document

__all__ = [
    "normalize_index",
    "normalize_index_sync",
    "chunk_transcript",
    "load_chunks_from_zip",
    "extract_from_chunk",
    "extract_all_chunks",
    "merge_section",
    "merge_all_sections",
    "assemble_document",
]
