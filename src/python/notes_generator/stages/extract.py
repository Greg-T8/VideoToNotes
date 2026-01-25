# -------------------------------------------------------------------------
# File: extract.py
# Description: Extract stage - process transcript chunks into structured notes
# Context: Stage 2 of the Exam Notes Generator pipeline
# Author: Greg Tate
# -------------------------------------------------------------------------

"""
Extract Stage

Processes 20KB transcript chunks into structured notes.
- Runs in parallel for speed
- Uses fast model (gpt-4.1-mini)
- Maps transcript segments to TOC sections
- Outputs partial notes per chunk
"""

import asyncio
import json
import re
from pathlib import Path
from typing import List, Optional

from notes_generator.models import (
    NormalizedIndex,
    TranscriptChunk,
    SectionPartial
)
from notes_generator.stages.normalize import index_to_toc_string


# Prompt template for chunk extraction
EXTRACT_PROMPT = '''# Chunk Processing

Generate exam-focused study notes from this transcript chunk.

## Table of Contents
{toc}

## Transcript Chunk {chunk_id} of {total_chunks}
Timestamps: {start_ts} – {end_ts}

```
{chunk_text}
```

## Instructions

Map each portion of this transcript to the appropriate TOC section based on timestamps.
For EACH section that has content in this chunk, generate notes in this EXACT format:

### [Section Title from TOC]
**Timestamp**: [first timestamp] – [last timestamp in this chunk for this section]

**Key Concepts**
- [main concepts as bullet points]

**Definitions**
- **[Term]**: [definition]

**Key Facts**
- [important facts, numbers, specifications]

**Examples**
- [concrete examples, commands, configurations mentioned]

**Exam Tips 🎯**
- [what to remember for the exam, common pitfalls]

## Rules

1. Use `###` for section titles ONLY
2. Use bold (`**text**`) for subsection headers
3. Include ALL content from the transcript — no information loss
4. If content spans multiple sections, create separate note blocks for each
5. Be technically precise — preserve exact values, commands, configurations
6. If a subsection has no content (e.g., no examples), write "- None in this chunk"
7. Timestamps should reflect the actual time range covered in this chunk for each section
8. Only generate notes for sections that have content in THIS chunk
'''


async def extract_from_chunk(
    chunk: TranscriptChunk,
    index: NormalizedIndex,
    total_chunks: int,
    model: str = "gpt-4.1-mini",
    llm_client: Optional[object] = None
) -> List[SectionPartial]:
    """
    Extract structured notes from a single transcript chunk.

    Args:
        chunk: The transcript chunk to process
        index: Normalized index for context
        total_chunks: Total number of chunks being processed
        model: The model to use for extraction
        llm_client: Optional pre-configured LLM client

    Returns:
        List of SectionPartial objects extracted from this chunk
    """
    # Build TOC context
    toc_context = index_to_toc_string(index)

    # Build the prompt
    prompt = EXTRACT_PROMPT.format(
        toc=toc_context,
        chunk_id=chunk.chunk_id,
        total_chunks=total_chunks,
        start_ts=chunk.start_timestamp,
        end_ts=chunk.end_timestamp,
        chunk_text=chunk.text
    )

    # Call LLM
    if llm_client is None:
        # TODO: Initialize default LLM client
        raise NotImplementedError("LLM client initialization not yet implemented")

    response = await llm_client.generate(
        prompt=prompt,
        model=model,
        temperature=0.2,
        max_tokens=8000
    )

    # Parse response into SectionPartials
    partials = parse_extraction_response(response, chunk.chunk_id)

    return partials


def parse_extraction_response(response: str, chunk_id: int) -> List[SectionPartial]:
    """
    Parse LLM extraction response into SectionPartial objects.

    Args:
        response: Raw markdown response from LLM
        chunk_id: The chunk ID for provenance

    Returns:
        List of SectionPartial objects
    """
    partials = []

    # Split by ### headings
    sections = re.split(r'^###\s+', response, flags=re.MULTILINE)

    for section_text in sections[1:]:  # Skip content before first ###
        lines = section_text.strip().split('\n')
        if not lines:
            continue

        # First line is the section title
        title = lines[0].strip()

        # Extract timestamp range
        timestamp_match = re.search(
            r'\*\*Timestamp\*\*:\s*(.+?)(?:\n|$)',
            section_text
        )
        timestamp_range = timestamp_match.group(1).strip() if timestamp_match else ""

        # Create partial with raw markdown
        partial = SectionPartial(
            section_title=title,
            chunk_id=chunk_id,
            timestamp_range=timestamp_range,
            raw_markdown=f"### {section_text}"
        )

        # Parse structured content
        partial.key_concepts = extract_list_section(section_text, "Key Concepts")
        partial.definitions = extract_definitions(section_text)
        partial.key_facts = extract_list_section(section_text, "Key Facts")
        partial.examples = extract_list_section(section_text, "Examples")
        partial.exam_tips = extract_list_section(section_text, "Exam Tips")

        partials.append(partial)

    return partials


def extract_list_section(text: str, header: str) -> List[str]:
    """
    Extract bullet points from a section.

    Args:
        text: The section text
        header: The header to look for (e.g., "Key Concepts")

    Returns:
        List of bullet point contents
    """
    # Find the section
    pattern = rf'\*\*{re.escape(header)}\*\*.*?\n((?:[-•]\s+.+\n?)+)'
    match = re.search(pattern, text, re.IGNORECASE)

    if not match:
        return []

    # Extract bullet points
    bullets = re.findall(r'^[-•]\s+(.+)$', match.group(1), re.MULTILINE)

    return [b.strip() for b in bullets if b.strip() and b.strip().lower() != "none in this chunk"]


def extract_definitions(text: str) -> dict:
    """
    Extract definitions from a section.

    Args:
        text: The section text

    Returns:
        Dictionary of term -> definition
    """
    definitions = {}

    # Pattern: - **Term**: Definition
    pattern = r'^[-•]\s+\*\*(.+?)\*\*:\s*(.+)$'
    matches = re.findall(pattern, text, re.MULTILINE)

    for term, definition in matches:
        definitions[term.strip()] = definition.strip()

    return definitions


async def extract_all_chunks(
    chunks: List[TranscriptChunk],
    index: NormalizedIndex,
    model: str = "gpt-4.1-mini",
    llm_client: Optional[object] = None,
    max_concurrent: int = 5
) -> List[SectionPartial]:
    """
    Extract notes from all chunks in parallel.

    Args:
        chunks: List of transcript chunks
        index: Normalized index for context
        model: The model to use for extraction
        llm_client: Optional pre-configured LLM client
        max_concurrent: Maximum concurrent API calls

    Returns:
        List of all SectionPartial objects from all chunks
    """
    total_chunks = len(chunks)

    # Create semaphore for concurrency control
    semaphore = asyncio.Semaphore(max_concurrent)

    async def extract_with_semaphore(chunk: TranscriptChunk) -> List[SectionPartial]:
        async with semaphore:
            return await extract_from_chunk(
                chunk=chunk,
                index=index,
                total_chunks=total_chunks,
                model=model,
                llm_client=llm_client
            )

    # Run extractions in parallel
    tasks = [extract_with_semaphore(chunk) for chunk in chunks]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Collect all partials
    all_partials = []
    for result in results:
        if isinstance(result, Exception):
            print(f"Warning: Extraction failed: {result}")
            continue
        all_partials.extend(result)

    return all_partials


def extract_all_chunks_sync(
    chunks: List[TranscriptChunk],
    index: NormalizedIndex,
    model: str = "gpt-4.1-mini",
    llm_client: Optional[object] = None
) -> List[SectionPartial]:
    """
    Synchronous wrapper for extract_all_chunks.

    Args:
        chunks: List of transcript chunks
        index: Normalized index for context
        model: The model to use for extraction
        llm_client: Optional pre-configured LLM client

    Returns:
        List of all SectionPartial objects from all chunks
    """
    return asyncio.run(extract_all_chunks(chunks, index, model, llm_client))


if __name__ == "__main__":
    # Allow running this stage directly for debugging
    print("Extract stage - run with debugger for testing")
