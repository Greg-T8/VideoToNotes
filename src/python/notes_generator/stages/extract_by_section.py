# -------------------------------------------------------------------------
# File: extract_by_section.py
# Description: Section-based extraction - extract notes per section time range
# Context: Alternative extraction approach for the Exam Notes Generator pipeline
# Author: Greg Tate
# -------------------------------------------------------------------------

"""
Section-Based Extraction

Instead of extracting from chunks and merging, this approach:
1. Iterates through each leaf section (🎤 sections)
2. Finds transcript content that falls within the section's time range
3. Extracts notes specifically for that section
4. Produces one MergedSection per section directly (no merge stage needed)

This ensures every section gets attention and avoids empty sections.
"""

import asyncio
import json
import re
from pathlib import Path
from typing import List, Optional

from notes_generator.models import (
    NormalizedIndex,
    IndexSection,
    TranscriptChunk,
    MergedSection
)


# Prompt for section-specific extraction
SECTION_EXTRACT_PROMPT = '''# Section Notes Extraction

Extract exam-focused study notes for ONE SPECIFIC SECTION from the transcript content below.

## Target Section
**Title**: {section_title}
**Time Range**: {section_start} – {section_end}

## Transcript Content
This content covers the time range for this section:

```
{transcript_content}
```

## Instructions

Create comprehensive exam notes for the section "{section_title}" based on the transcript content above.

Focus on:
- Key concepts and definitions
- Important facts, numbers, and specifications
- Practical examples mentioned
- Exam tips and things to remember

## Output Format

### {section_header}
**Timestamp**: {section_start} – {section_end}

**Key Concepts**
- [main concepts as bullet points]

**Definitions**
- **[Term]**: [definition]

**Key Facts**
- [important facts, numbers, specifications]

**Examples**
- [concrete examples mentioned, or "None mentioned"]

**Key Takeaways 🎯**
- [exam focus points and things to remember]

---

IMPORTANT:
- Only include content that was actually discussed in the transcript
- Do not invent information not present in the transcript
- If the transcript content is sparse, create concise notes accordingly
'''


def timestamp_to_seconds(ts: str) -> int:
    """
    Convert timestamp string to total seconds.

    Args:
        ts: Timestamp in HH:MM:SS or MM:SS format

    Returns:
        Total seconds
    """
    if not ts:
        return 0

    parts = ts.split(':')
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    return 0


def seconds_to_timestamp(seconds: int) -> str:
    """
    Convert seconds to HH:MM:SS timestamp.

    Args:
        seconds: Total seconds

    Returns:
        Timestamp string in HH:MM:SS format
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def get_leaf_sections(index: NormalizedIndex) -> List[IndexSection]:
    """
    Get all leaf sections (🎤 markers) that should have content.

    Leaf sections are those without children - the actual content sections.

    Args:
        index: Normalized index structure

    Returns:
        List of leaf sections in order
    """
    leaf_sections = []

    for section in index.sections:
        # Leaf sections have no children (children is an empty list)
        # Note: children is a List[str] of child titles, not IndexSection objects
        if not section.children:
            # Skip document title (level 1)
            if section.level > 1:
                leaf_sections.append(section)

    return leaf_sections


def extract_transcript_for_timerange(
    transcript_text: str,
    start_seconds: int,
    end_seconds: int,
    buffer_seconds: int = 30
) -> str:
    """
    Extract transcript lines that fall within a time range.

    The transcript is in consolidated format with periods like:
        00:01:03-00:01:19
        Text content here...

    Args:
        transcript_text: Full transcript text with timestamps
        start_seconds: Start of range in seconds
        end_seconds: End of range in seconds
        buffer_seconds: Extra seconds to include before/after for context

    Returns:
        Transcript content within the time range
    """
    lines = transcript_text.split('\n')
    selected_lines = []

    # Apply buffer
    start_with_buffer = max(0, start_seconds - buffer_seconds)
    end_with_buffer = end_seconds + buffer_seconds

    # Pattern to match consolidated timestamp ranges: HH:MM:SS-HH:MM:SS or MM:SS-MM:SS
    timestamp_pattern = re.compile(r'^(\d{1,2}:\d{2}(?::\d{2})?)-(\d{1,2}:\d{2}(?::\d{2})?)$')

    current_start_seconds = 0
    current_end_seconds = 0
    in_range = False

    for line in lines:
        match = timestamp_pattern.match(line.strip())

        if match:
            # This is a timestamp line - update current position
            current_start_seconds = timestamp_to_seconds(match.group(1))
            current_end_seconds = timestamp_to_seconds(match.group(2))

            # Check if this period overlaps with our target range
            in_range = (current_start_seconds < end_with_buffer and
                       current_end_seconds > start_with_buffer)

            if in_range:
                selected_lines.append(line)
        else:
            # This is content - include if we're in range
            if in_range and line.strip():
                selected_lines.append(line)

    return '\n'.join(selected_lines)


def load_full_transcript(chunks: List[TranscriptChunk]) -> str:
    """
    Combine all chunks into full transcript text.

    Args:
        chunks: List of transcript chunks

    Returns:
        Full transcript text
    """
    return '\n'.join(chunk.text for chunk in chunks)


def sanitize_filename(title: str) -> str:
    """
    Create a safe filename from a section title.

    Args:
        title: Section title

    Returns:
        Sanitized filename string
    """
    # Remove emojis and special chars
    clean = re.sub(r'[☁️🎤]+\s*', '', title)
    # Replace unsafe chars with underscores
    clean = re.sub(r'[<>:"/\\|?*\[\]]', '_', clean)
    # Collapse multiple underscores/spaces
    clean = re.sub(r'[\s_]+', '_', clean)
    # Limit length
    return clean.strip('_')[:60]


def write_section_file(
    section: MergedSection,
    output_dir: Path
) -> Path:
    """
    Write a single section's content to a file.

    File format: {order:03d}_{sanitized_title}.md
    Also writes a metadata .json file alongside.

    Args:
        section: The merged section with content
        output_dir: Directory to write files to

    Returns:
        Path to the written markdown file
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create filename with order prefix for proper sorting
    safe_name = sanitize_filename(section.section_title)
    base_name = f"{section.order:03d}_{safe_name}"
    md_path = output_dir / f"{base_name}.md"
    json_path = output_dir / f"{base_name}.json"

    # Write markdown content
    md_path.write_text(section.content, encoding='utf-8')

    # Write metadata JSON for reassembly
    metadata = {
        "section_title": section.section_title,
        "timestamp_range": section.timestamp_range,
        "level": section.level,
        "order": section.order,
        "content_file": md_path.name
    }
    json_path.write_text(json.dumps(metadata, indent=2), encoding='utf-8')

    return md_path


def load_section_files(sections_dir: Path) -> List[MergedSection]:
    """
    Load all section files from a directory.

    Reads the .json metadata files and corresponding .md content files.

    Args:
        sections_dir: Directory containing section files

    Returns:
        List of MergedSection objects in order
    """
    sections = []

    # Find all JSON metadata files
    json_files = sorted(sections_dir.glob("*.json"))

    for json_path in json_files:
        metadata = json.loads(json_path.read_text(encoding='utf-8'))
        md_path = sections_dir / metadata["content_file"]

        if md_path.exists():
            content = md_path.read_text(encoding='utf-8')
            section = MergedSection(
                section_title=metadata["section_title"],
                timestamp_range=metadata["timestamp_range"],
                level=metadata["level"],
                order=metadata["order"],
                content=content
            )
            sections.append(section)

    # Sort by order
    sections.sort(key=lambda s: s.order)
    return sections


async def extract_section_notes(
    section: IndexSection,
    transcript_text: str,
    model: str = "gpt-4.1-mini",
    llm_client: Optional[object] = None
) -> Optional[MergedSection]:
    """
    Extract notes for a single section from the transcript.

    Args:
        section: The section to extract notes for
        transcript_text: Full transcript text
        model: The model to use
        llm_client: Optional pre-configured LLM client

    Returns:
        MergedSection with extracted notes, or None if no content found
    """
    # Calculate time range
    start_seconds = timestamp_to_seconds(section.timestamp or "00:00:00")

    if section.end_timestamp:
        end_seconds = timestamp_to_seconds(section.end_timestamp)
    else:
        # Default to 5 minutes after start if no end timestamp
        end_seconds = start_seconds + 300

    # Extract transcript content for this section's time range
    transcript_content = extract_transcript_for_timerange(
        transcript_text,
        start_seconds,
        end_seconds
    )

    # Skip if no content found
    if not transcript_content.strip():
        return None

    # Build section header (clean up emojis for output)
    clean_title = re.sub(r'[☁️🎤]+\s*', '', section.title).strip()
    section_header = f"🎤 [{section.timestamp} – {section.end_timestamp or '??:??:??'}] {clean_title}"

    # Build the prompt
    prompt = SECTION_EXTRACT_PROMPT.format(
        section_title=section.title,
        section_start=section.timestamp or "00:00:00",
        section_end=section.end_timestamp or "unknown",
        section_header=section_header,
        transcript_content=transcript_content
    )

    # Initialize LLM client if not provided
    if llm_client is None:
        from notes_generator.llm_client import GitHubModelsClient
        llm_client = GitHubModelsClient()

    # Call LLM
    context = f"section: {clean_title[:40]}"
    response = await llm_client.generate(
        prompt=prompt,
        model=model,
        context=context
    )

    if not response:
        return None

    # Create MergedSection directly
    # Determine level from section.level
    return MergedSection(
        section_title=section.title,
        timestamp_range=f"{section.timestamp} – {section.end_timestamp or 'unknown'}",
        level=section.level,
        order=section.order,
        content=response.strip()
    )


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


async def extract_all_sections(
    index: NormalizedIndex,
    chunks: List[TranscriptChunk],
    model: str = "gpt-4.1-mini",
    llm_client: Optional[object] = None,
    max_concurrent: int = 2,  # Reduced to avoid rate limits with many sections
    progress_callback: Optional[callable] = None,
    sections_output_dir: Optional[Path] = None
) -> List[MergedSection]:
    """
    Extract notes for all sections from the transcript.

    Args:
        index: Normalized index structure
        chunks: List of transcript chunks
        model: The model to use for extraction
        llm_client: Optional pre-configured LLM client
        max_concurrent: Maximum concurrent API calls
        progress_callback: Optional callback for progress updates
        sections_output_dir: Optional directory to write individual section files

    Returns:
        List of MergedSection objects for all sections
    """
    # Get leaf sections that need content
    leaf_sections = get_leaf_sections(index)
    total_sections = len(leaf_sections)

    # Load full transcript
    transcript_text = load_full_transcript(chunks)

    # Get inter-request delay based on model
    # Increase delay for section-based extraction since we make more calls
    request_delay = _get_request_delay(model) * 2

    # Create semaphore for concurrency control
    semaphore = asyncio.Semaphore(max_concurrent)

    # Initialize LLM client once for all requests
    if llm_client is None:
        from notes_generator.llm_client import GitHubModelsClient
        llm_client = GitHubModelsClient()

    # Process counter for progress tracking
    processed_count = 0

    async def extract_with_semaphore(
        section: IndexSection,
        section_num: int
    ) -> Optional[MergedSection]:
        nonlocal processed_count
        async with semaphore:
            # Add delay between requests to avoid rate limits
            await asyncio.sleep(request_delay)

            result = await extract_section_notes(
                section=section,
                transcript_text=transcript_text,
                model=model,
                llm_client=llm_client
            )

            # Write section file if output directory provided
            if result is not None and sections_output_dir is not None:
                write_section_file(result, sections_output_dir)

            # Progress update
            processed_count += 1
            if processed_count % 10 == 0 or processed_count == total_sections:
                print(f"  Progress: {processed_count}/{total_sections} sections...")

            return result

    # Run extractions in parallel with limited concurrency
    tasks = [
        extract_with_semaphore(section, idx)
        for idx, section in enumerate(leaf_sections, start=1)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Collect successful results
    merged_sections = []
    for result in results:
        if isinstance(result, Exception):
            print(f"Warning: Extraction failed: {result}")
            continue
        if result is not None:
            merged_sections.append(result)

    return merged_sections


def extract_all_sections_sync(
    index: NormalizedIndex,
    chunks: List[TranscriptChunk],
    model: str = "gpt-4.1-mini",
    llm_client: Optional[object] = None,
    progress_callback: Optional[callable] = None,
    sections_output_dir: Optional[Path] = None
) -> List[MergedSection]:
    """
    Synchronous wrapper for extract_all_sections.

    Args:
        index: Normalized index structure
        chunks: List of transcript chunks
        model: The model to use for extraction
        llm_client: Optional pre-configured LLM client
        progress_callback: Optional callback for progress updates
        sections_output_dir: Optional directory to write individual section files

    Returns:
        List of MergedSection objects for all sections
    """
    return asyncio.run(
        extract_all_sections(
            index=index,
            chunks=chunks,
            model=model,
            llm_client=llm_client,
            progress_callback=progress_callback,
            sections_output_dir=sections_output_dir
        )
    )


if __name__ == "__main__":
    print("Extract by Section stage - run with debugger for testing")
