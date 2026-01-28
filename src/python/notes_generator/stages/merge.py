# -------------------------------------------------------------------------
# File: merge.py
# Description: Merge stage - combine partials by section, deduplicate
# Context: Stage 3 of the VideoToNotes pipeline
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
from notes_generator.prompt_loader import get_merge_prompt


def normalize_section_title(title: str) -> str:
    """
    Normalize a section title for grouping.

    Removes timestamps, emojis, and other prefixes to match related partials.
    Returns the normalized title in lowercase for comparison.
    """
    # Remove emoji markers
    title = re.sub(r'[☁️🎤]+\s*', '', title)
    # Remove timestamp prefixes like [00:22:31] or (00:22:31)
    title = re.sub(r'[\[(]\d{1,2}:\d{2}(?::\d{2})?[\])]\s*', '', title)
    # Remove leading/trailing brackets
    title = re.sub(r'^\[|\]$', '', title)
    # Remove "(continued)" suffix
    title = re.sub(r'\s*\(continued[^)]*\)\s*$', '', title, flags=re.IGNORECASE)
    # Normalize whitespace
    title = re.sub(r'\s+', ' ', title)
    # Return lowercase for grouping
    return title.strip().lower()


def extract_timestamp_seconds(timestamp_range: str) -> Optional[int]:
    """
    Extract the start timestamp in seconds from a timestamp range.

    Args:
        timestamp_range: String like "01:08:04 – 01:11:02"

    Returns:
        Start timestamp in seconds, or None if parsing fails
    """
    if not timestamp_range:
        return None

    match = re.match(r'(\d{1,2}):(\d{2}):?(\d{2})?', timestamp_range)
    if match:
        hours = int(match.group(1))
        minutes = int(match.group(2))
        seconds = int(match.group(3)) if match.group(3) else 0
        return hours * 3600 + minutes * 60 + seconds
    return None


def is_empty_placeholder(partial: SectionPartial) -> bool:
    """
    Check if a partial is just an empty placeholder with no real content.

    Args:
        partial: The partial to check

    Returns:
        True if the partial contains only placeholder text
    """
    content = partial.raw_markdown.lower()
    # Check if the only substantive content is "none in this chunk"
    # Remove the header and check what's left
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    # Filter out header lines (### ...), section headers (**Key Concepts**, etc.)
    content_lines = [
        line for line in lines
        if not line.startswith('#') and not line.startswith('**')
    ]
    # If all content lines are just "- none in this chunk" or similar, it's empty
    non_empty_lines = [
        line for line in content_lines
        if line not in ('- none in this chunk', '- none', 'none in this chunk')
    ]
    return len(non_empty_lines) == 0


def group_partials_by_section(
    partials: List[SectionPartial],
    max_time_gap_minutes: int = 30
) -> Dict[str, List[SectionPartial]]:
    """
    Group partials by their normalized section title.

    Uses timestamp proximity to avoid grouping partials that are too far apart,
    which would indicate they're actually different sections with similar names.

    Args:
        partials: List of all partials from extraction
        max_time_gap_minutes: Maximum time gap between partials to group them

    Returns:
        Dictionary mapping section title to list of partials.
        Uses the original title (with timestamp) for sections that have time gaps.
    """
    max_gap_seconds = max_time_gap_minutes * 60

    # First pass: group by normalized title
    temp_grouped = defaultdict(list)
    for partial in partials:
        normalized = normalize_section_title(partial.section_title)
        temp_grouped[normalized].append(partial)

    # Second pass: split groups with large time gaps
    final_grouped = {}

    for normalized, section_partials in temp_grouped.items():
        # Sort by timestamp
        section_partials.sort(
            key=lambda p: extract_timestamp_seconds(p.timestamp_range) or 0
        )

        # Check for time gaps and split if needed
        current_group = []
        current_group_key = normalized

        for partial in section_partials:
            partial_ts = extract_timestamp_seconds(partial.timestamp_range)

            if not current_group:
                # First partial in group
                current_group.append(partial)
                # Use original title (preserves timestamp context)
                current_group_key = normalize_section_title(partial.section_title)
            else:
                # Check time gap from last partial
                last_ts = extract_timestamp_seconds(current_group[-1].timestamp_range)

                if partial_ts and last_ts and (partial_ts - last_ts) > max_gap_seconds:
                    # Time gap too large - this is a different section
                    # Save current group
                    if current_group:
                        # Add index to key if duplicate
                        key = current_group_key
                        suffix = 1
                        while key in final_grouped:
                            suffix += 1
                            key = f"{current_group_key}_{suffix}"
                        final_grouped[key] = current_group

                    # Start new group with this partial's title
                    current_group = [partial]
                    current_group_key = normalize_section_title(partial.section_title)
                else:
                    # Within time gap - add to current group
                    current_group.append(partial)

        # Save final group
        if current_group:
            key = current_group_key
            suffix = 1
            while key in final_grouped:
                suffix += 1
                key = f"{current_group_key}_{suffix}"
            final_grouped[key] = current_group

    # Sort partials within each group by chunk_id
    for section in final_grouped:
        final_grouped[section].sort(key=lambda p: p.chunk_id)

    return final_grouped


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
        section_title: The section title (may be normalized key)
        partials: List of partials for this section
        section_info: Section metadata from index (level, order)
        model: The model to use for merging
        llm_client: Optional pre-configured LLM client
        section_num: Current section number (for logging)
        total_sections: Total number of sections (for logging)

    Returns:
        MergedSection with combined content
    """
    # Use the original title from the first partial (preserves timestamp info)
    # This helps the assemble stage match to the correct index section
    original_title = partials[0].section_title if partials else section_title

    # If only one partial, no merge needed
    if len(partials) == 1:
        return MergedSection(
            section_title=original_title,
            timestamp_range=partials[0].timestamp_range,
            level=section_info.get("level", 3),
            order=section_info.get("order", 0),
            content=partials[0].raw_markdown
        )

    # Build the prompt from external template
    partials_text = format_partials_for_prompt(partials)
    prompt_template = get_merge_prompt()
    prompt = prompt_template.format(
        section_title=original_title,
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
        section_title=original_title,
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
    # Filter out empty placeholder partials before grouping
    original_count = len(partials)
    filtered_partials = [p for p in partials if not is_empty_placeholder(p)]
    filtered_count = original_count - len(filtered_partials)
    if filtered_count > 0:
        print(f"  Filtered {filtered_count} empty placeholder partials")

    # Group partials by section
    grouped = group_partials_by_section(filtered_partials)

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
