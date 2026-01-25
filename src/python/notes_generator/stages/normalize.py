# -------------------------------------------------------------------------
# File: normalize.py
# Description: Normalize stage - convert varied index formats to JSON
# Context: Stage 0 of the Exam Notes Generator pipeline
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

    # Call LLM
    if llm_client is None:
        # TODO: Initialize default LLM client
        raise NotImplementedError("LLM client initialization not yet implemented")

    response = await llm_client.generate(
        prompt=prompt,
        model=model,
        temperature=0.1,  # Low temperature for consistent parsing
        max_tokens=4000
    )

    # Parse JSON response
    try:
        data = json.loads(response)
    except json.JSONDecodeError as e:
        # Try to extract JSON from response if wrapped in markdown
        import re
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            data = json.loads(json_match.group())
        else:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")

    # Convert to NormalizedIndex
    return NormalizedIndex.from_dict(data)


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

    Args:
        index: The normalized index

    Returns:
        Formatted TOC string
    """
    lines = [f"# {index.title}", ""]

    for section in sorted(index.sections, key=lambda s: s.order):
        prefix = "#" * section.level
        lines.append(f"{prefix} [{section.timestamp}] {section.title}")

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
