# -------------------------------------------------------------------------
# File: merge.py
# Description: Merge stage - combine partials by section, deduplicate
# Context: Stage 3 of the Exam Notes Generator pipeline
# Author: Greg Tate
# -------------------------------------------------------------------------

"""
Merge Stage

Combines partial notes from extraction stage.
- Groups notes by section
- Deduplicates content
- Merges timestamps (earliest start to latest end)
- Uses reasoning model (deepseek-r1)
"""

import asyncio
import re
from collections import defaultdict
from typing import List, Dict, Optional

from notes_generator.models import (
    NormalizedIndex,
    SectionPartial,
    MergedSection
)


# Prompt template for section merging
MERGE_PROMPT = '''# Section Merge

Merge these partial notes into ONE coherent, comprehensive section.

## Section: {section_title}

## Partial Notes from Different Transcript Chunks:
{partials}

## Merge Instructions

### 1. Timestamp Handling
- Final timestamp: [earliest start] – [latest end]
- If there's a gap > 5 minutes between partials, note it as "(continued at [timestamp])"

### 2. Key Concepts
- Combine all bullet points across partials
- REMOVE exact duplicates (identical phrasing)
- KEEP near-duplicates if they add nuance (merge into one refined bullet)
- Order logically: foundational concepts first, advanced concepts later

### 3. Definitions
- If the same term is defined multiple times, keep the MOST COMPLETE definition
- If definitions conflict, include both with clarification: "(also described as: ...)"

### 4. Key Facts
- Remove redundant facts (same information, different words)
- Keep all UNIQUE facts
- If facts appear to contradict, flag with: "⚠️ Verify: mentioned as both X and Y"
- Order by dependency (prerequisite facts first)

### 5. Examples
- Keep ALL unique examples (examples are high-value for exams)
- Remove only exact duplicate examples
- Preserve code snippets, CLI commands, and configuration samples exactly

### 6. Exam Tips 🎯
- Combine all tips, remove duplicates
- Prioritize actionable tips ("Remember to..." > "This is important")
- Consolidate similar tips into stronger combined tips

## Rules

- Do NOT add information not present in the source partials
- Do NOT infer or expand beyond what's provided
- Do NOT summarize or lose detail
- Output in the standard format with ### heading

## Output Format

### {section_title}
**Timestamp**: [merged timestamp range]

**Key Concepts**
- [merged concepts]

**Definitions**
- **[Term]**: [merged definition]

**Key Facts**
- [merged facts]

**Examples**
- [merged examples]

**Exam Tips 🎯**
- [merged tips]
'''


def group_partials_by_section(
    partials: List[SectionPartial]
) -> Dict[str, List[SectionPartial]]:
    """
    Group partials by their section title.

    Args:
        partials: List of all partials from extraction

    Returns:
        Dictionary mapping section title to list of partials
    """
    grouped = defaultdict(list)

    for partial in partials:
        grouped[partial.section_title].append(partial)

    # Sort partials within each group by chunk_id
    for section in grouped:
        grouped[section].sort(key=lambda p: p.chunk_id)

    return dict(grouped)


def format_partials_for_prompt(partials: List[SectionPartial]) -> str:
    """
    Format partials for inclusion in the merge prompt.

    Args:
        partials: List of partials for a single section

    Returns:
        Formatted string for prompt
    """
    sections = []

    for partial in partials:
        sections.append(f"--- From Chunk {partial.chunk_id} ---\n{partial.raw_markdown}")

    return "\n\n".join(sections)


async def merge_section(
    section_title: str,
    partials: List[SectionPartial],
    section_info: dict,
    model: str = "deepseek-r1",
    llm_client: Optional[object] = None
) -> MergedSection:
    """
    Merge partials for a single section.

    Args:
        section_title: The section title
        partials: List of partials for this section
        section_info: Section metadata from index (level, order)
        model: The model to use for merging
        llm_client: Optional pre-configured LLM client

    Returns:
        MergedSection with combined content
    """
    # If only one partial, no merge needed
    if len(partials) == 1:
        return MergedSection(
            section_title=section_title,
            timestamp_range=partials[0].timestamp_range,
            level=section_info.get("level", 3),
            order=section_info.get("order", 0),
            content=partials[0].raw_markdown
        )

    # Build the prompt
    partials_text = format_partials_for_prompt(partials)
    prompt = MERGE_PROMPT.format(
        section_title=section_title,
        partials=partials_text
    )

    # Initialize LLM client if not provided
    if llm_client is None:
        from notes_generator.llm_client import GitHubModelsClient
        llm_client = GitHubModelsClient()

    response = await llm_client.generate(
        prompt=prompt,
        model=model,
        temperature=0.1,  # Low temperature for consistent merging
        max_tokens=8000
    )

    # Extract timestamp range from response
    timestamp_match = re.search(
        r'\*\*Timestamp\*\*:\s*(.+?)(?:\n|$)',
        response
    )
    timestamp_range = timestamp_match.group(1).strip() if timestamp_match else ""

    return MergedSection(
        section_title=section_title,
        timestamp_range=timestamp_range,
        level=section_info.get("level", 3),
        order=section_info.get("order", 0),
        content=response
    )


async def merge_all_sections(
    partials: List[SectionPartial],
    index: NormalizedIndex,
    model: str = "deepseek-r1",
    llm_client: Optional[object] = None,
    max_concurrent: int = 3
) -> List[MergedSection]:
    """
    Merge all section partials.

    Args:
        partials: List of all partials from extraction
        index: Normalized index for section metadata
        model: The model to use for merging
        llm_client: Optional pre-configured LLM client
        max_concurrent: Maximum concurrent API calls

    Returns:
        List of MergedSection objects
    """
    # Group partials by section
    grouped = group_partials_by_section(partials)

    # Build section info lookup
    section_info = {
        s.title: {"level": s.level, "order": s.order}
        for s in index.sections
    }

    # Create semaphore for concurrency control
    semaphore = asyncio.Semaphore(max_concurrent)

    async def merge_with_semaphore(
        title: str,
        section_partials: List[SectionPartial]
    ) -> MergedSection:
        async with semaphore:
            info = section_info.get(title, {"level": 3, "order": 0})
            return await merge_section(
                section_title=title,
                partials=section_partials,
                section_info=info,
                model=model,
                llm_client=llm_client
            )

    # Run merges
    tasks = [
        merge_with_semaphore(title, section_partials)
        for title, section_partials in grouped.items()
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Collect results
    merged_sections = []
    for result in results:
        if isinstance(result, Exception):
            print(f"Warning: Merge failed: {result}")
            continue
        merged_sections.append(result)

    # Sort by order
    merged_sections.sort(key=lambda s: s.order)

    return merged_sections


def merge_all_sections_sync(
    partials: List[SectionPartial],
    index: NormalizedIndex,
    model: str = "deepseek-r1",
    llm_client: Optional[object] = None
) -> List[MergedSection]:
    """
    Synchronous wrapper for merge_all_sections.

    Args:
        partials: List of all partials from extraction
        index: Normalized index for section metadata
        model: The model to use for merging
        llm_client: Optional pre-configured LLM client

    Returns:
        List of MergedSection objects
    """
    return asyncio.run(merge_all_sections(partials, index, model, llm_client))


if __name__ == "__main__":
    # Allow running this stage directly for debugging
    print("Merge stage - run with debugger for testing")
