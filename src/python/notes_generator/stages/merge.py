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
MERGE_PROMPT = '''# Section Merge Task

Merge these partial notes into ONE coherent, comprehensive section.

## Section: {section_title}

## Partial Notes from Different Transcript Chunks:
{partials}

## Merge Instructions

### CRITICAL: Timestamp Validation
- Calculate the time span: [latest end] - [earliest start]
- If the span is > 30 minutes, something is WRONG - the partials may be from different topics
- In that case, keep ONLY the content that most directly relates to the section title
- Reasonable timestamp spans: 1-15 minutes for most sections

### Output Format (REQUIRED)
You MUST output in this EXACT format:

### {section_title}
**Timestamp**: [earliest start] – [latest end]

**Key Concepts**
- [merged concepts as bullet points]

**Definitions**
- **[Term]**: [definition]

**Key Facts**
- [merged facts]

**Examples**
- [merged examples]

**Exam Tips 🎯**
- [merged tips]

### Merge Rules

1. **Key Concepts**: Combine all bullet points, remove exact duplicates, keep near-duplicates if they add nuance
2. **Definitions**: Keep the most complete definition for each term
3. **Key Facts**: Remove redundant facts, keep unique ones
4. **Examples**: Keep ALL unique examples (high value for exams)
5. **Exam Tips**: Combine tips, prioritize actionable ones

### Quality Rules

- Do NOT add information not in the source partials
- Do NOT summarize or lose detail
- Every section MUST have a **Timestamp** line
- Omit subsections that have no content (don't write "None")
'''


def normalize_section_title(title: str) -> str:
    """
    Normalize a section title for grouping.

    Removes timestamps, emojis, and other prefixes to match related partials.
    """
    # Remove emoji markers
    title = re.sub(r'[☁️🎤]+\s*', '', title)
    # Remove timestamp prefixes like [00:22:31] or (00:22:31)
    title = re.sub(r'[\[(]\d{1,2}:\d{2}(?::\d{2})?[\])]\s*', '', title)
    # Remove leading/trailing brackets
    title = re.sub(r'^\[|\]$', '', title)
    # Remove "(continued)" suffix
    title = re.sub(r'\s*\(continued[^)]*\)\s*$', '', title, flags=re.IGNORECASE)
    return title.strip()


def group_partials_by_section(
    partials: List[SectionPartial]
) -> Dict[str, List[SectionPartial]]:
    """
    Group partials by their normalized section title.

    Args:
        partials: List of all partials from extraction

    Returns:
        Dictionary mapping normalized section title to list of partials
    """
    grouped = defaultdict(list)

    for partial in partials:
        # Normalize the title for grouping
        normalized = normalize_section_title(partial.section_title)
        grouped[normalized].append(partial)

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
    model: str = "gpt-4.1-mini",
    llm_client: Optional[object] = None,
    section_num: int = 0,
    total_sections: int = 0
) -> MergedSection:
    """
    Merge partials for a single section.

    Args:
        section_title: The section title
        partials: List of partials for this section
        section_info: Section metadata from index (level, order)
        model: The model to use for merging
        llm_client: Optional pre-configured LLM client
        section_num: Current section number (for logging)
        total_sections: Total number of sections (for logging)

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

    # Build context for logging
    context = f"merge section {section_num}/{total_sections}: {section_title[:30]}"

    response = await llm_client.generate(
        prompt=prompt,
        model=model,
        temperature=0.1,  # Low temperature for consistent merging
        max_tokens=8000,
        context=context
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


def _is_reasoning_model(model: str) -> bool:
    """Check if model is a reasoning model (o1, o3, o4 series)."""
    return any(f"/{prefix}" in model or model.startswith(prefix)
               for prefix in ("o1", "o3", "o4"))


def _get_request_delay(model: str) -> float:
    """
    Get inter-request delay based on model type.

    Reasoning models have lower rate limits (500 RPM vs 5000 RPM),
    so we add longer delays to avoid hitting limits.
    """
    if _is_reasoning_model(model):
        # o3-mini: 500 RPM = ~8 requests/second max
        # Use 500ms delay to stay well under limit
        return 0.5
    else:
        # gpt-4.1-mini: 5000 RPM = ~83 requests/second max
        # Use 150ms delay for safety margin
        return 0.15


async def merge_all_sections(
    partials: List[SectionPartial],
    index: NormalizedIndex,
    model: str = "gpt-4.1-mini",
    llm_client: Optional[object] = None,
    max_concurrent: int = 5
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

    # Adjust concurrency for reasoning models (lower rate limits)
    if _is_reasoning_model(model):
        max_concurrent = min(max_concurrent, 3)
        print(f"  Using reduced concurrency ({max_concurrent}) for reasoning model")

    # Get inter-request delay
    request_delay = _get_request_delay(model)

    # Create semaphore for concurrency control
    semaphore = asyncio.Semaphore(max_concurrent)

    # Total sections for logging
    total_sections = len(grouped)

    async def merge_with_semaphore(
        title: str,
        section_partials: List[SectionPartial],
        section_num: int
    ) -> MergedSection:
        async with semaphore:
            # Add delay between requests to avoid rate limits
            await asyncio.sleep(request_delay)

            info = section_info.get(title, {"level": 3, "order": 0})
            return await merge_section(
                section_title=title,
                partials=section_partials,
                section_info=info,
                model=model,
                llm_client=llm_client,
                section_num=section_num,
                total_sections=total_sections
            )

    # Run merges
    tasks = [
        merge_with_semaphore(title, section_partials, idx + 1)
        for idx, (title, section_partials) in enumerate(grouped.items())
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
    model: str = "gpt-4.1-mini",
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
