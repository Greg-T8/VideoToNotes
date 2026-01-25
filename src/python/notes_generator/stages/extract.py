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

## Table of Contents (EXACT section titles to use)
{toc}

## Transcript Chunk {chunk_id} of {total_chunks}
Timestamps: {start_ts} – {end_ts}

```
{chunk_text}
```

## Instructions

Analyze this transcript and create INDIVIDUAL note blocks for EACH LEAF SECTION (🎤 sections) from the TOC above.

## ⚠️ CRITICAL RULES - READ CAREFULLY

### Rule 1: NEVER CREATE NOTE BLOCKS FOR PARENT SECTIONS (☁️)
- Parent sections are marked with ☁️ - DO NOT create any note blocks for them
- ONLY create note blocks for 🎤 sections
- If you see content that seems like it belongs to a ☁️ parent, put it in the most relevant 🎤 child instead
- Examples of parent sections you must SKIP:
  - ☁️ ML Studio → put content in its children like 🎤 Azure Machine Learning Service
  - ☁️ Follow Alongs → put content in its children like 🎤 Setup, 🎤 AutoML
  - ☁️ Congitive Services → put content in its children
- If you create ANY note block for a ☁️ section, that is WRONG

### Rule 2: CREATE SEPARATE BLOCKS FOR EACH CHILD
- If the transcript discusses Transformers, Tokenization, AND Embeddings:
  - Create THREE separate note blocks
  - One for each 🎤 leaf section
  - Do NOT create one big block for the ☁️ parent

### Rule 3: MATCH CONTENT TO MOST SPECIFIC SECTION
- "Tokens are split into subwords" → goes to 🎤 Tokenization (not parent)
- "Attention mechanism allows focus" → goes to 🎤 Attention (not parent)
- "Embeddings represent words as vectors" → goes to 🎤 Embeddings (not parent)

### Rule 4: SPLIT RELATED SIBLING SECTIONS
- When you see multiple 🎤 sections with similar names, they are SEPARATE topics
- Example: "Form Recognizer", "Form Recognizer Custom Models", "Form Recognizer Prebuilt Models"
  - These are THREE separate 🎤 sections, not one
  - Content about custom models goes to "Form Recognizer Custom Models"
  - Content about prebuilt/pre-built models goes to "Form Recognizer Prebuilt Models"
  - Only general Form Recognizer overview goes to "Form Recognizer"
- Example: "Computer Vision", "Computer Vision AI", "Custom Vision"
  - These are separate sections - split content appropriately

### Rule 5: USE EXACT SECTION TITLES FROM TOC (WITH TIMESTAMPS)
- Copy the ENTIRE section title from the TOC exactly as written
- Section titles include the marker (🎤), timestamp in brackets, AND the name
- CORRECT: `### 🎤 [02:35:02] Computer Vision`
- WRONG: `### 🎤 Computer Vision AI` (missing timestamp, wrong name)
- WRONG: `### Computer Vision` (missing marker and timestamp)
- The TOC above shows the ONLY valid titles - use them exactly
- If content matches timestamp 02:35:02, use title `🎤 [02:35:02] Computer Vision`
- Do NOT make up titles or omit any parts

## Output Format

For EACH applicable 🎤 section, use this EXACT format:

### [EXACT Section Title from TOC - copy the 🎤 section title verbatim]
**Timestamp**: [first timestamp] – [last timestamp]

**Key Concepts**
- [main concepts as bullet points]

**Definitions**
- **[Term]**: [definition]

**Key Facts**
- [important facts, numbers, specifications]

**Examples**
- [concrete examples mentioned]

**Exam Tips 🎯**
- [exam focus points]

## Additional Rules

1. **ONE TOPIC PER BLOCK**: Each note block covers ONE specific section from the TOC
2. **EXACT TITLES**: Copy section titles EXACTLY from the TOC including marker and timestamp - no modifications
3. **PREFER 🎤 OVER ☁️**: Always match content to 🎤 sections, almost never ☁️ sections
4. Use `###` for section titles ONLY
5. Use bold (`**text**`) for subsection headers within each note block
6. Be technically precise — preserve exact values
7. If a subsection (like Key Facts) has no content, write "- None in this chunk"
8. If content doesn't match any TOC section, skip it
9. **ONLY OUTPUT SECTIONS WITH CONTENT**: Do NOT create note blocks for sections whose content is not in this chunk. If the section timestamp is outside this chunk's time range, do NOT output anything for it.
10. **MATCH BY TIMESTAMP**: Use the chunk's timestamp range ({start_ts} – {end_ts}) to identify which TOC sections are covered. Only create notes for sections whose timestamps fall within or near this range.
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

    # Initialize LLM client if not provided
    if llm_client is None:
        from notes_generator.llm_client import GitHubModelsClient
        llm_client = GitHubModelsClient()

    # Build context for logging
    context = f"extract chunk {chunk.chunk_id}/{total_chunks}"

    response = await llm_client.generate(
        prompt=prompt,
        model=model,
        temperature=0.2,
        max_tokens=8000,
        context=context
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


def _get_request_delay(model: str) -> float:
    """
    Get inter-request delay based on model type.

    Reasoning models have lower rate limits (500 RPM vs 5000 RPM),
    so we add longer delays to avoid hitting limits.
    """
    if any(f"/{prefix}" in model or model.startswith(prefix)
           for prefix in ("o1", "o3", "o4")):
        return 0.5  # 500ms for reasoning models
    else:
        return 0.15  # 150ms for standard models


async def extract_all_chunks(
    chunks: List[TranscriptChunk],
    index: NormalizedIndex,
    model: str = "gpt-4.1-mini",
    llm_client: Optional[object] = None,
    max_concurrent: int = 4
) -> List[SectionPartial]:
    """
    Extract notes from all chunks in parallel.

    Args:
        chunks: List of transcript chunks
        index: Normalized index for context
        model: The model to use for extraction
        llm_client: Optional pre-configured LLM client
        max_concurrent: Maximum concurrent API calls (default 4 to avoid rate limits)

    Returns:
        List of all SectionPartial objects from all chunks
    """
    total_chunks = len(chunks)

    # Get inter-request delay based on model
    request_delay = _get_request_delay(model)

    # Create semaphore for concurrency control
    semaphore = asyncio.Semaphore(max_concurrent)

    async def extract_with_semaphore(chunk: TranscriptChunk) -> List[SectionPartial]:
        async with semaphore:
            # Add delay between requests to avoid rate limits
            await asyncio.sleep(request_delay)

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
