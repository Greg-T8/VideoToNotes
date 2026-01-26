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

## Table of Contents with Time Ranges
{toc}

## Transcript Chunk {chunk_id} of {total_chunks}
This chunk covers: {start_ts} – {end_ts}

```
{chunk_text}
```

## Instructions

Create note blocks for sections from the TOC whose time range overlaps with this chunk ({start_ts} – {end_ts}).

### Understanding the TOC Format

Each section shows: `[START_TIME – END_TIME] Section Name`
- **START_TIME**: When this section begins
- **END_TIME**: When this section ends (start of next section)
- **🎤 sections**: Content sections - create detailed notes for these
- **☁️ sections**: PARENT sections - create a brief overview block AND split detailed content into their 🎤 children

### CRITICAL: Match Content to the CORRECT Section by Time

Look at the timestamps IN THE TRANSCRIPT. Match them to the section whose time range contains that timestamp.

**Example**: If TOC shows:
```
## ☁️ [01:18:46 – 01:32:14] Access control options
### 🎤 [01:19:01 – 01:22:17] Account keys
### 🎤 [01:22:17 – 01:23:24] Blob anonymous access
### 🎤 [01:23:24 – 01:26:33] Entra ID integrated RBAC
### 🎤 [01:26:33 – 01:32:14] Shared Access Signatures
```

And transcript at 01:20:30 discusses "storage account keys have two keys for rotation":
- This goes in "🎤 [01:19:01 – 01:22:17] Account keys" (timestamp 01:20:30 is in range 01:19:01–01:22:17)
- Do NOT put detailed content in the parent "☁️ Access control options" - only the overview

### Important Rules

1. **For ☁️ parent sections**: Create a brief overview block with `[PARENT SECTION]` marker that summarizes what topics are covered
2. **For 🎤 content sections**: Create full detailed notes with all key concepts, definitions, facts, examples
3. **Use timestamp ranges to match content** - each piece of content belongs to ONE section
4. **Even short sections (1-3 minutes) need their own note block** - don't skip them
5. **Copy section titles EXACTLY** from the TOC including the marker, timestamps, and name

## Output Format

### For ☁️ PARENT sections (create a brief overview):

### [Copy EXACT section title from TOC: ☁️ [time range] Name]
**[PARENT SECTION]**

This section covers the following topics:
- [List of child topic names covered in this parent section]

**Overview**: [1-2 sentence high-level summary of what this section is about]

---

### For 🎤 CONTENT sections (create detailed notes):

### [Copy EXACT section title from TOC: 🎤 [time range] Name]
**Timestamp**: [actual first mention] – [actual last mention in chunk]

**Key Concepts**
- [main concepts as bullet points]

**Definitions**
- **[Term]**: [definition]

**Key Facts**
- [important facts, numbers, specifications]

**Examples**
- [concrete examples mentioned, or "None in this chunk" if none]

**Key Takeaways 🎯**
- [exam focus points]

---

## IMPORTANT: Output Only Section Blocks

- Output ONLY the note blocks for sections from the TOC
- Do NOT add any commentary, summaries, checklists, or "final notes" sections
- Do NOT output anything after the last section block
- Include BOTH ☁️ parent section blocks AND 🎤 content section blocks
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

    # Pattern to validate section titles (must have 🎤 or ☁️ marker with timestamp)
    valid_section_pattern = re.compile(r'^[🎤☁️]\s*\[[\d:]+\s*[–-]\s*[\d:]+\]')

    for section_text in sections[1:]:  # Skip content before first ###
        lines = section_text.strip().split('\n')
        if not lines:
            continue

        # First line is the section title
        title = lines[0].strip()

        # Skip sections that don't match TOC format (filters out "Final notes", "Final checklist", etc.)
        if not valid_section_pattern.match(title):
            continue

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
        partial.exam_tips = extract_list_section(section_text, "Key Takeaways")

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
