# -------------------------------------------------------------------------
# File: normalize.py
# Description: Normalize stage - convert varied index formats to JSON
# Context: Stage 0 of the VideoToNotes pipeline
# Author: Greg Tate
# -------------------------------------------------------------------------

"""
Normalize Stage

Converts varied index/TOC formats into a consistent JSON structure using an LLM.
This handles different formatting styles like:
- ☁️ Section / 🎤 (HH:MM:SS) Topic
- MM:SS - Topic
- ## Section / ### Subsection patterns

The LLM intelligently detects hierarchy and normalizes timestamps.
"""

import json
from pathlib import Path
from typing import Optional

from notes_generator.models import NormalizedIndex, IndexSection


# Prompt template for index normalization
NORMALIZE_PROMPT = '''# Index Normalization

Convert this index/table of contents into a structured JSON format.

## Raw Index Content
```
{raw_index}
```

## Instructions

1. **Identify the hierarchy**: Detect parent-child relationships between sections.
   - Look for visual groupings (icons, indentation, heading markers)
   - Parent sections typically have no timestamp or a broader scope
   - Child sections have specific timestamps and detailed topics

2. **Extract timestamps**: Find all timestamps and normalize to HH:MM:SS format.
   - MM:SS → 00:MM:SS
   - HH:MM:SS stays as-is
   - If no timestamp, use "00:00:00"

3. **Determine heading levels**:
   - Level 2 (##): Top-level sections/categories
   - Level 3 (###): Subsections under a category
   - Level 4 (####): Detailed topics (if present)

4. **Preserve order**: Keep the original document order (1-indexed).

5. **Infer video title**: Extract or infer the video/course title from context.

## Output Format

Return ONLY valid JSON (no markdown code fences, no explanation):

{{
  "title": "Video or Course Title",
  "sections": [
    {{
      "title": "Section Name",
      "timestamp": "00:00:00",
      "level": 2,
      "order": 1,
      "parent": null,
      "children": ["Child Section 1", "Child Section 2"]
    }},
    {{
      "title": "Child Section 1",
      "timestamp": "00:12:51",
      "level": 3,
      "order": 2,
      "parent": "Section Name",
      "children": []
    }}
  ]
}}

## Rules

- Every section must have: title, timestamp, level, order, parent, children
- Parent is null for top-level sections, otherwise the parent's title
- Children is an array of child section titles (empty array if none)
- Timestamps must be exactly HH:MM:SS format
- Order starts at 1 and increments for each section
- Output ONLY the JSON object, nothing else
'''


async def normalize_index(
    index_path: Path,
    model: str = "gpt-4.1-mini",
    llm_client: Optional[object] = None
) -> NormalizedIndex:
    """
    Normalize an index file into a structured format.

    Args:
        index_path: Path to the raw index file
        model: LLM model to use for normalization
        llm_client: Optional pre-configured LLM client

    Returns:
        NormalizedIndex with consistent structure
    """
    # Read raw index content
    raw_content = index_path.read_text(encoding="utf-8")

    # Build the prompt
    prompt = NORMALIZE_PROMPT.format(raw_index=raw_content)

    # Initialize LLM client if not provided
    if llm_client is None:
        from notes_generator.llm_client import GitHubModelsClient
        llm_client = GitHubModelsClient()

    response = await llm_client.generate(
        prompt=prompt,
        model=model,
        temperature=0.1,  # Low temperature for consistent parsing
        max_tokens=16000  # Larger for complex indexes
    )

    # Parse JSON response
    try:
        data = json.loads(response)
    except json.JSONDecodeError as e:
        # Try to extract JSON from response if wrapped in markdown
        import re

        # Remove markdown code fences if present
        cleaned = re.sub(r'^```(?:json)?\s*', '', response, flags=re.MULTILINE)
        cleaned = re.sub(r'\s*```$', '', cleaned, flags=re.MULTILINE)

        # Try to find the JSON object
        json_match = re.search(r'\{[\s\S]*\}', cleaned)
        if json_match:
            try:
                data = json.loads(json_match.group())
            except json.JSONDecodeError:
                # Try to fix common JSON issues
                fixed = json_match.group()
                # Fix trailing commas
                fixed = re.sub(r',(\s*[}\]])', r'\1', fixed)
                # Fix unquoted keys (simple cases)
                fixed = re.sub(r'(\{|\,)\s*(\w+)\s*:', r'\1"\2":', fixed)
                try:
                    data = json.loads(fixed)
                except json.JSONDecodeError as e2:
                    raise ValueError(f"Failed to parse LLM response as JSON after cleanup: {e2}\nResponse preview: {response[:500]}")
        else:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}\nResponse preview: {response[:500]}")

    # Convert to NormalizedIndex
    normalized = NormalizedIndex.from_dict(data)

    # Try to extract URL from contents.json if it exists alongside the index file
    contents_json_path = index_path.parent / "contents.json"
    if contents_json_path.exists():
        try:
            contents_data = json.loads(contents_json_path.read_text(encoding="utf-8"))
            if "url" in contents_data:
                normalized.url = contents_data["url"]
            if "uploadDate" in contents_data:
                # Format YYYYMMDD to YYYY-MM-DD
                raw_date = contents_data["uploadDate"]
                if len(raw_date) == 8:
                    normalized.upload_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:8]}"
                else:
                    normalized.upload_date = raw_date
        except (json.JSONDecodeError, IOError):
            pass  # Ignore errors reading contents.json

    # Check if source is a flat list (all items at same indentation)
    # If so, flatten the normalized structure to remove incorrect hierarchy
    normalized = _flatten_if_source_is_flat(normalized, raw_content)

    # Post-process: Calculate end_timestamp for each section
    normalized = _calculate_end_timestamps(normalized)

    return normalized


def _flatten_if_source_is_flat(index: NormalizedIndex, raw_index: str) -> NormalizedIndex:
    """
    Check if the source index is a flat list and flatten the normalized result.

    The LLM sometimes infers hierarchy based on topic relationships even when
    the source is clearly a flat list. This function detects flat sources and
    flattens the result.

    Args:
        index: Normalized index (possibly with incorrect hierarchy)
        raw_index: Original raw index text

    Returns:
        Flattened index if source was flat, otherwise unchanged
    """
    # Check if source is flat: look for consistent bullet/dash patterns without indentation
    lines = [l for l in raw_index.strip().split('\n') if l.strip()]

    # Count lines that look like flat list items (timestamps with no leading whitespace)
    flat_patterns = 0
    indented_patterns = 0

    for line in lines:
        stripped = line.strip()
        # Skip headers and metadata
        if stripped.startswith('#') or stripped.startswith('**') or stripped.startswith('*Source'):
            continue
        # Check if it's a list item
        if stripped.startswith('-') or stripped.startswith('*'):
            # Check original line for leading whitespace (beyond the bullet)
            leading = len(line) - len(line.lstrip())
            if leading <= 2:  # No significant indentation
                flat_patterns += 1
            else:
                indented_patterns += 1

    # If mostly flat patterns and no indented ones, flatten the result
    if flat_patterns > 0 and indented_patterns == 0:
        # Flatten: set all sections to level 2, no parent, no children
        for section in index.sections:
            section.level = 2
            section.parent = None
            section.children = []

    return index


def _calculate_end_timestamps(index: NormalizedIndex) -> NormalizedIndex:
    """
    Calculate end_timestamp for each section based on the next section.

    Args:
        index: Normalized index without end timestamps

    Returns:
        Same index with end_timestamp populated
    """
    # Sort sections by order
    sorted_sections = sorted(index.sections, key=lambda s: s.order)

    for i, section in enumerate(sorted_sections):
        # Find the next section at same or higher (lower number) level
        end_ts = None
        for next_section in sorted_sections[i + 1:]:
            if next_section.level <= section.level:
                end_ts = next_section.timestamp
                break

        section.end_timestamp = end_ts

    return index


def normalize_index_sync(
    index_path: Path,
    model: str = "gpt-4.1-mini",
    llm_client: Optional[object] = None
) -> NormalizedIndex:
    """
    Synchronous wrapper for normalize_index.

    Args:
        index_path: Path to the raw index file
        model: LLM model to use for normalization
        llm_client: Optional pre-configured LLM client

    Returns:
        NormalizedIndex with consistent structure
    """
    import asyncio
    return asyncio.run(normalize_index(index_path, model, llm_client))


def validate_normalized_index(index: NormalizedIndex) -> list[str]:
    """
    Validate a normalized index for common issues.

    Args:
        index: The normalized index to validate

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    if not index.title:
        errors.append("Missing video title")

    if not index.sections:
        errors.append("No sections found")
        return errors

    # Check for duplicate orders
    orders = [s.order for s in index.sections]
    if len(orders) != len(set(orders)):
        errors.append("Duplicate order values found")

    # Check timestamp format
    import re
    timestamp_pattern = re.compile(r'^\d{2}:\d{2}:\d{2}$')
    for section in index.sections:
        if not timestamp_pattern.match(section.timestamp):
            errors.append(f"Invalid timestamp format for '{section.title}': {section.timestamp}")

    # Check parent references
    titles = {s.title for s in index.sections}
    for section in index.sections:
        if section.parent and section.parent not in titles:
            errors.append(f"Invalid parent reference for '{section.title}': {section.parent}")

    # Check level values
    for section in index.sections:
        if section.level < 2 or section.level > 6:
            errors.append(f"Invalid level for '{section.title}': {section.level}")

    return errors


def index_to_toc_string(index: NormalizedIndex) -> str:
    """
    Convert normalized index back to a readable TOC string.

    Useful for including in prompts for the extraction stage.
    Shows section time ranges (start – end) to help the LLM
    understand section boundaries.

    Args:
        index: The normalized index

    Returns:
        Formatted TOC string with time ranges
    """
    lines = [f"# {index.title}", ""]

    # Sort sections by order
    sorted_sections = sorted(index.sections, key=lambda s: s.order)

    for i, section in enumerate(sorted_sections):
        prefix = "#" * section.level

        # Determine if leaf (no children) or parent (has children)
        is_leaf = len(section.children) == 0
        marker = "🎤" if is_leaf else "☁️"

        # Calculate end time (start of next section at same or higher level)
        end_ts = None
        for next_section in sorted_sections[i + 1:]:
            if next_section.level <= section.level:
                end_ts = next_section.timestamp
                break

        # Format timestamp range
        if end_ts:
            ts_display = f"{section.timestamp} – {end_ts}"
        else:
            ts_display = f"{section.timestamp} – end"

        lines.append(f"{prefix} {marker} [{ts_display}] {section.title}")

    return "\n".join(lines)


if __name__ == "__main__":
    # Allow running this stage directly for debugging
    print("Normalize stage - run with debugger for testing")

    # Example: test with sample file
    sample_path = Path("data/samples/AI-900_FreeCodeCamp/Index - FreeCodeCamp.txt")
    if sample_path.exists():
        print(f"Sample file found: {sample_path}")
        content = sample_path.read_text(encoding="utf-8")
        print(f"Content preview:\n{content[:500]}...")
