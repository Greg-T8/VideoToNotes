# -------------------------------------------------------------------------
# File: validate.py
# Description: Validate stage - check for empty sections and re-extract if needed
# Context: Post-merge validation for the Exam Notes Generator pipeline
# Author: Greg Tate
# -------------------------------------------------------------------------

"""
Validate Stage

Checks merged sections against TOC to find empty sections.
For empty sections, attempts targeted re-extraction from the appropriate chunk.
"""

import asyncio
import re
from typing import List, Set, Tuple, Optional
from dataclasses import asdict

from notes_generator.models import (
    NormalizedIndex,
    IndexSection,
    MergedSection,
    TranscriptChunk,
    SectionPartial
)
from notes_generator.stages.normalize import index_to_toc_string


def get_leaf_sections(index: NormalizedIndex) -> List[IndexSection]:
    """
    Get all leaf sections (🎤 markers) that should have content.

    Leaf sections are those with no children (the 🎤 marked sections
    in the TOC that represent actual content topics).

    Args:
        index: Normalized index structure

    Returns:
        List of sections that need content (those with no children)
    """
    leaf_sections = []

    for section in index.sections:
        # Leaf sections have no children (children is an empty list)
        # Note: children is a List[str] of child titles, not IndexSection objects
        if not section.children:
            if section.level > 1:  # Skip document title (level 1)
                leaf_sections.append(section)

    return leaf_sections


def normalize_title_for_comparison(title: str) -> str:
    """
    Normalize a title for comparison by removing markers, timestamps, etc.
    """
    # Remove emoji markers
    title = re.sub(r'[☁️🎤🎯]+\s*', '', title)
    # Remove timestamp ranges like [00:22:31 – 00:25:00]
    title = re.sub(r'\[[\d:]+\s*[–-]\s*[\d:]+\]\s*', '', title)
    # Remove single timestamps
    title = re.sub(r'[\[(]\d{1,2}:\d{2}(?::\d{2})?[\])]\s*', '', title)
    # Normalize whitespace
    title = re.sub(r'\s+', ' ', title)
    return title.lower().strip()


def find_empty_sections(
    index: NormalizedIndex,
    merged_sections: List[MergedSection]
) -> Tuple[List[IndexSection], Set[str]]:
    """
    Find leaf sections that don't have corresponding merged content.

    Args:
        index: Normalized index structure
        merged_sections: List of merged sections with content

    Returns:
        Tuple of (empty_sections, covered_titles)
    """
    # Get all leaf sections that should have content
    leaf_sections = get_leaf_sections(index)

    # Build set of normalized titles from merged sections
    covered_titles = set()
    for merged in merged_sections:
        norm_title = normalize_title_for_comparison(merged.section_title)
        covered_titles.add(norm_title)

    # Find sections without content
    empty_sections = []
    for section in leaf_sections:
        norm_title = normalize_title_for_comparison(section.title)
        if norm_title not in covered_titles:
            empty_sections.append(section)

    return empty_sections, covered_titles


def timestamp_to_seconds(ts: str) -> int:
    """Convert timestamp string to seconds."""
    parts = ts.split(':')
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    return 0


def find_chunks_for_section(
    section: IndexSection,
    chunks: List[TranscriptChunk]
) -> List[TranscriptChunk]:
    """
    Find transcript chunks that overlap with a section's time range.

    Args:
        section: The section to find chunks for
        chunks: All transcript chunks

    Returns:
        List of chunks that overlap with the section
    """
    if not section.timestamp:
        return []

    # Parse section time range
    section_start = timestamp_to_seconds(section.timestamp)

    # Calculate section end from end_timestamp if available
    if hasattr(section, 'end_timestamp') and section.end_timestamp:
        section_end = timestamp_to_seconds(section.end_timestamp)
    else:
        # Default to 5 minutes after start
        section_end = section_start + 300

    matching_chunks = []
    for chunk in chunks:
        chunk_start = timestamp_to_seconds(chunk.start_timestamp)
        chunk_end = timestamp_to_seconds(chunk.end_timestamp)

        # Check for overlap
        if chunk_start < section_end and chunk_end > section_start:
            matching_chunks.append(chunk)

    return matching_chunks


# Prompt for targeted re-extraction of a specific section
TARGETED_EXTRACT_PROMPT = '''# Targeted Section Extraction

Extract exam notes for ONE SPECIFIC SECTION from this transcript chunk.

## Target Section
**Section**: {section_title}
**Time Range**: {section_start} – {section_end}

## Transcript Chunk
This chunk covers: {chunk_start} – {chunk_end}

```
{chunk_text}
```

## Instructions

Find content in the transcript that falls within the time range {section_start} – {section_end} and create notes for the section "{section_title}".

Look for transcript entries with timestamps between {section_start} and {section_end}. The content may discuss topics like:
- {topic_hints}

## Output Format

### 🎤 [{section_start} – {section_end}] {section_name}
**Timestamp**: [first mention] – [last mention]

**Key Concepts**
- [main concepts as bullet points]

**Definitions**
- **[Term]**: [definition]

**Key Facts**
- [important facts, numbers, specifications]

**Examples**
- [concrete examples or "None in this chunk"]

**Key Takeaways 🎯**
- [exam focus points]

---

If no relevant content is found for this section in the given time range, output:

### 🎤 [{section_start} – {section_end}] {section_name}
**Timestamp**: {section_start}

**Key Concepts**
- [Brief summary based on section title]

---
'''


async def extract_single_section(
    section: IndexSection,
    chunks: List[TranscriptChunk],
    model: str = "gpt-4.1-mini",
    llm_client: Optional[object] = None
) -> Optional[SectionPartial]:
    """
    Extract content for a single empty section by finding the right chunk.

    Args:
        section: The section to extract content for
        chunks: All transcript chunks
        model: The model to use
        llm_client: Optional pre-configured LLM client

    Returns:
        SectionPartial if content was extracted, None otherwise
    """
    # Find chunks that overlap with this section
    matching_chunks = find_chunks_for_section(section, chunks)

    if not matching_chunks:
        return None

    # Use the first matching chunk
    chunk = matching_chunks[0]

    # Build topic hints from section title
    title_words = section.title.lower().split()
    topic_hints = ', '.join(word for word in title_words if len(word) > 3)

    # Build the prompt
    section_end = section.end_timestamp if hasattr(section, 'end_timestamp') and section.end_timestamp else "unknown"

    prompt = TARGETED_EXTRACT_PROMPT.format(
        section_title=section.title,
        section_start=section.timestamp or "00:00:00",
        section_end=section_end,
        section_name=re.sub(r'[☁️🎤]+\s*', '', section.title),
        chunk_start=chunk.start_timestamp,
        chunk_end=chunk.end_timestamp,
        chunk_text=chunk.text,
        topic_hints=topic_hints or section.title
    )

    # Initialize LLM client if not provided
    if llm_client is None:
        from notes_generator.llm_client import GitHubModelsClient
        llm_client = GitHubModelsClient()

    # Call LLM
    context = f"targeted extract: {section.title[:40]}"
    response = await llm_client.generate(
        prompt=prompt,
        model=model,
        context=context
    )

    if not response:
        return None

    # Parse response into a SectionPartial
    # Need timestamp_range field - use section timestamp
    timestamp_range = section.timestamp or "00:00:00"
    if hasattr(section, 'end_timestamp') and section.end_timestamp:
        timestamp_range = f"{section.timestamp} – {section.end_timestamp}"

    return SectionPartial(
        section_title=section.title,
        chunk_id=chunk.chunk_id,
        timestamp_range=timestamp_range,
        raw_markdown=response.strip()
    )


async def validate_and_fill(
    index: NormalizedIndex,
    merged_sections: List[MergedSection],
    chunks: List[TranscriptChunk],
    model: str = "gpt-4.1-mini",
    max_retries: int = 2
) -> List[MergedSection]:
    """
    Validate merged sections and fill in empty ones.

    Args:
        index: Normalized index structure
        merged_sections: List of merged sections
        chunks: Original transcript chunks for re-extraction
        model: Model to use for re-extraction
        max_retries: Maximum number of sections to re-extract

    Returns:
        Updated list of merged sections
    """
    from notes_generator.llm_client import GitHubModelsClient

    # Find empty sections
    empty_sections, _ = find_empty_sections(index, merged_sections)

    if not empty_sections:
        return merged_sections

    print(f"  Found {len(empty_sections)} empty sections, attempting re-extraction...")

    # Limit re-extraction to avoid excessive API calls
    sections_to_fill = empty_sections[:max_retries * 5]  # Process up to 10 sections

    # Initialize LLM client
    llm_client = GitHubModelsClient()

    # Extract content for empty sections
    new_sections = []
    for section in sections_to_fill:
        try:
            partial = await extract_single_section(
                section=section,
                chunks=chunks,
                model=model,
                llm_client=llm_client
            )

            if partial and partial.content:
                # Convert partial to merged section
                new_section = MergedSection(
                    section_title=section.title,
                    timestamp_range=f"{section.timestamp} – {section.end_timestamp}" if hasattr(section, 'end_timestamp') else section.timestamp,
                    content=partial.content
                )
                new_sections.append(new_section)
                print(f"    ✓ Filled: {section.title[:50]}...")
        except Exception as e:
            print(f"    ✗ Failed to fill {section.title[:30]}: {e}")
            continue

    # Combine original and new sections
    result = list(merged_sections)
    result.extend(new_sections)

    return result


def validate_and_fill_sync(
    index: NormalizedIndex,
    merged_sections: List[MergedSection],
    chunks: List[TranscriptChunk],
    model: str = "gpt-4.1-mini"
) -> List[MergedSection]:
    """
    Synchronous wrapper for validate_and_fill.
    """
    return asyncio.run(validate_and_fill(index, merged_sections, chunks, model))


def get_coverage_stats(
    index: NormalizedIndex,
    merged_sections: List[MergedSection]
) -> dict:
    """
    Get statistics about section coverage.

    Returns:
        Dictionary with coverage stats
    """
    leaf_sections = get_leaf_sections(index)
    empty_sections, covered = find_empty_sections(index, merged_sections)

    return {
        "total_leaf_sections": len(leaf_sections),
        "covered_sections": len(leaf_sections) - len(empty_sections),
        "empty_sections": len(empty_sections),
        "coverage_percent": ((len(leaf_sections) - len(empty_sections)) / len(leaf_sections) * 100) if leaf_sections else 100,
        "empty_section_titles": [s.title for s in empty_sections]
    }
