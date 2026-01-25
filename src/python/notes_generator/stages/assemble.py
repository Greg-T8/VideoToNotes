# -------------------------------------------------------------------------
# File: assemble.py
# Description: Assemble stage - build final document from merged sections
# Context: Stage 4 of the Exam Notes Generator pipeline
# Author: Greg Tate
# -------------------------------------------------------------------------

"""
Assemble Stage

Builds the final document from merged sections.
- Deterministic (no LLM)
- Reconstructs heading hierarchy from index
- Uses fuzzy matching to handle LLM section title variations
- Outputs formatted Markdown
"""

import re
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from notes_generator.models import NormalizedIndex, MergedSection, IndexSection


def normalize_title(title: str) -> str:
    """
    Normalize a title for fuzzy matching.

    Removes timestamps, brackets, emojis, extra whitespace, and lowercases.
    """
    # Remove emoji markers (☁️, 🎤)
    title = re.sub(r'[☁️🎤]+\s*', '', title)
    # Remove timestamp prefixes like [00:22:31] or (00:22:31)
    title = re.sub(r'[\[(]\d{1,2}:\d{2}(?::\d{2})?[\])]\s*', '', title)
    # Remove leading/trailing brackets
    title = re.sub(r'^\[|\]$', '', title)
    # Remove parenthetical notes like "(continued)"
    title = re.sub(r'\s*\([^)]+\)\s*$', '', title)
    # Normalize whitespace (collapse multiple spaces, remove around hyphens)
    title = re.sub(r'\s+', ' ', title)
    # Lowercase and strip
    return title.lower().strip()


def extract_timestamp(title: str) -> Optional[str]:
    """
    Extract timestamp from a title if present.

    Args:
        title: Section title that may contain a timestamp

    Returns:
        Timestamp string (HH:MM:SS) or None
    """
    match = re.search(r'[\[(]?(\d{1,2}:\d{2}(?::\d{2})?)[\])]?', title)
    return match.group(1) if match else None


def extract_timestamp_from_range(ts_range: str) -> Optional[str]:
    """
    Extract start timestamp from a timestamp range string.

    Args:
        ts_range: Timestamp range like "02:34:56 – 02:38:40"

    Returns:
        Start timestamp string or None
    """
    if not ts_range:
        return None
    # Match the first timestamp in the range
    match = re.search(r'(\d{1,2}:\d{2}(?::\d{2})?)', ts_range)
    return match.group(1) if match else None


def timestamp_to_seconds(ts: str) -> int:
    """
    Convert timestamp string to seconds.

    Args:
        ts: Timestamp in HH:MM:SS or HH:MM format

    Returns:
        Total seconds
    """
    parts = ts.split(':')
    if len(parts) == 2:
        return int(parts[0]) * 3600 + int(parts[1]) * 60
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    return 0


def timestamps_near(ts1: str, ts2: str, tolerance_seconds: int = 300) -> bool:
    """
    Check if two timestamps are within tolerance of each other.

    Args:
        ts1: First timestamp string
        ts2: Second timestamp string
        tolerance_seconds: Maximum difference in seconds (default 5 minutes)

    Returns:
        True if timestamps are within tolerance
    """
    sec1 = timestamp_to_seconds(ts1)
    sec2 = timestamp_to_seconds(ts2)
    return abs(sec1 - sec2) <= tolerance_seconds


def fuzzy_match_section(
    merged_title: str,
    index_sections: List[IndexSection],
    threshold: float = 0.80,
    fallback_timestamp: Optional[str] = None
) -> Optional[str]:
    """
    Find the best matching index section title for a merged section.

    Prioritizes timestamp matching for sections with similar names
    that appear at different times in the video.

    Args:
        merged_title: The title from the merged section
        index_sections: List of index sections to match against
        threshold: Minimum similarity ratio (0-1) for a match
        fallback_timestamp: Timestamp to use if not found in title

    Returns:
        The exact title from the index, or None if no match found
    """
    normalized_merged = normalize_title(merged_title)
    merged_ts = extract_timestamp(merged_title)
    # Use fallback timestamp if title doesn't contain one
    if not merged_ts and fallback_timestamp:
        merged_ts = fallback_timestamp

    best_match = None
    best_ratio = 0.0
    best_ts_near = False

    for section in index_sections:
        normalized_index = normalize_title(section.title)

        # Check if timestamps are near each other (within 5 minutes)
        ts_near = False
        if merged_ts and section.timestamp:
            ts_near = timestamps_near(merged_ts, section.timestamp)

        # Exact match after normalization
        if normalized_merged == normalized_index:
            if ts_near:
                return section.title  # Perfect match with nearby timestamp
            elif not merged_ts:
                return section.title  # No timestamp to compare

        # Check if one title contains the other (e.g., "OCR Computer Vision" contains "OCR")
        # If timestamps are near, this is a strong match even if ratio is low
        contains_match = (normalized_index in normalized_merged or
                          normalized_merged in normalized_index)

        # Fuzzy match
        ratio = SequenceMatcher(None, normalized_merged, normalized_index).ratio()

        # Accept match if ratio >= threshold OR if contains match with nearby timestamp
        if ratio >= threshold or (contains_match and ts_near):
            # Prefer matches where timestamps are nearby
            # This prevents "Text Analytics" (01:08) matching "Text Analysis" (03:02)
            if ts_near and not best_ts_near:
                # This is a better match because timestamps are close
                best_ratio = ratio
                best_match = section.title
                best_ts_near = True
            elif ts_near == best_ts_near and ratio > best_ratio:
                # Same timestamp status, higher ratio wins
                best_ratio = ratio
                best_match = section.title
                best_ts_near = ts_near

    return best_match


def build_content_map(
    merged_sections: List[MergedSection],
    index: NormalizedIndex
) -> Dict[str, MergedSection]:
    """
    Build a content map with fuzzy matching of section titles.

    Uses timestamps to disambiguate similar section titles like
    "Text Analytics" vs "Text Analysis".

    Args:
        merged_sections: List of merged section content
        index: The normalized index for title matching

    Returns:
        Dictionary mapping index section titles to merged content
    """
    content_map = {}

    # Build normalized index lookup with timestamp disambiguation
    # Key: (normalized_title, timestamp_prefix) -> index_title
    norm_ts_to_index = {}
    norm_only_to_index = {}  # Fallback without timestamp

    for section in index.sections:
        norm = normalize_title(section.title)
        # Use the timestamp field from the section, not from the title
        ts_prefix = section.timestamp[:5] if section.timestamp else None  # HH:MM prefix

        # Store with timestamp for disambiguation
        if ts_prefix:
            key = (norm, ts_prefix)
            norm_ts_to_index[key] = section.title

        # Also store without timestamp as fallback (first one wins)
        if norm not in norm_only_to_index:
            norm_only_to_index[norm] = section.title

    for merged in merged_sections:
        merged_norm = normalize_title(merged.section_title)
        merged_ts = extract_timestamp(merged.section_title)
        # If title doesn't have a timestamp, try to get it from timestamp_range
        if not merged_ts and merged.timestamp_range:
            merged_ts = extract_timestamp_from_range(merged.timestamp_range)
        merged_ts_prefix = merged_ts[:5] if merged_ts else None

        matched_title = None

        # Try exact match with timestamp first
        if merged_ts_prefix:
            key = (merged_norm, merged_ts_prefix)
            if key in norm_ts_to_index:
                matched_title = norm_ts_to_index[key]

        # If merged has timestamp but exact match failed, try fuzzy with timestamp awareness
        # (fuzzy considers timestamps, norm_only doesn't)
        if not matched_title and merged_ts_prefix:
            matched_title = fuzzy_match_section(
                merged.section_title, index.sections,
                fallback_timestamp=merged_ts
            )

        # Try exact normalized match only when there's no timestamp
        if not matched_title and merged_norm in norm_only_to_index:
            matched_title = norm_only_to_index[merged_norm]

        # Try fuzzy match as last resort for non-timestamped titles
        if not matched_title:
            matched_title = fuzzy_match_section(
                merged.section_title, index.sections,
                fallback_timestamp=merged_ts
            )

        # If matched to a parent section (has children), try to find better child match
        if matched_title:
            matched_section = next(
                (s for s in index.sections if s.title == matched_title), None
            )
            if matched_section and matched_section.children and merged_ts:
                # This content matched a parent but has a timestamp - try to find child
                child_match = fuzzy_match_section(
                    merged.section_title,
                    [s for s in index.sections if s.title in matched_section.children],
                    fallback_timestamp=merged_ts
                )
                if child_match:
                    matched_title = child_match

        # Skip content that's mostly empty placeholders (parent sections with no real content)
        if matched_title and matched_title not in content_map:
            # Check if content is meaningful (not just "None in this chunk" placeholders)
            content_lower = merged.content.lower()
            none_count = content_lower.count("none in this chunk")
            if none_count >= 4:  # 4+ "none" entries means it's an empty placeholder
                continue
            content_map[matched_title] = merged

    return content_map


def build_hierarchy_map(index: NormalizedIndex) -> Dict[str, List[str]]:
    """
    Build a map of parent sections to their children.

    Args:
        index: The normalized index

    Returns:
        Dictionary mapping parent title to list of child titles
    """
    hierarchy = {}

    for section in index.sections:
        if section.parent:
            if section.parent not in hierarchy:
                hierarchy[section.parent] = []
            hierarchy[section.parent].append(section.title)

    return hierarchy


def get_section_by_title(
    index: NormalizedIndex,
    title: str
) -> Optional[IndexSection]:
    """
    Get a section from the index by title.

    Args:
        index: The normalized index
        title: Section title to find

    Returns:
        IndexSection or None if not found
    """
    for section in index.sections:
        if section.title == title:
            return section
    return None


def build_document_structure(
    index: NormalizedIndex,
    merged_sections: List[MergedSection]
) -> str:
    """
    Build the complete document structure.

    Args:
        index: The normalized index
        merged_sections: List of merged section content

    Returns:
        Complete markdown document
    """
    # Create lookup for merged content with fuzzy matching
    content_map = build_content_map(merged_sections, index)

    # Get all top-level sections (level 2)
    top_level = [s for s in index.sections if s.level == 2]
    top_level.sort(key=lambda s: s.order)

    lines = []

    # Document title
    lines.append(f"# {index.title} - Exam Notes")
    lines.append("")
    lines.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Build table of contents
    lines.append("## Table of Contents")
    lines.append("")
    for section in index.sections:
        indent = "  " * (section.level - 2)
        lines.append(f"{indent}- [{section.title}](#{slugify(section.title)})")
    lines.append("")

    # Track rendered sections to prevent infinite recursion
    rendered_sections = set()
    sections_with_rules = set()  # Track which sections already have a rule before them

    # Render each section recursively
    def render_section(section: IndexSection, depth: int = 0, parent_has_content: bool = False,
                       is_first_child: bool = False):
        nonlocal sections_with_rules
        # Prevent infinite recursion from circular references
        if section.title in rendered_sections:
            return []
        rendered_sections.add(section.title)

        # Limit recursion depth as safety measure
        if depth > 10:
            return []

        section_lines = []
        has_content = section.title in content_map

        # Add horizontal rule before sections with content
        # Skip if: parent has content (would be consecutive), or this is the first content section
        should_add_rule = has_content and not parent_has_content and len(sections_with_rules) > 0
        if should_add_rule:
            section_lines.append("---")
            section_lines.append("")

        if has_content:
            sections_with_rules.add(section.title)

        # Add heading
        heading_prefix = "#" * section.level
        section_lines.append(f"{heading_prefix} {section.title}")
        section_lines.append("")

        # Add content if this is a content section (has merged content)
        if section.title in content_map:
            merged = content_map[section.title]

            # Extract content without the heading (it's already added)
            content = merged.content

            # Remove the ### heading from content if present
            content = content.lstrip()
            if content.startswith("###"):
                # Remove first line (the heading)
                content = "\n".join(content.split("\n")[1:]).lstrip()

            # Strip trailing horizontal rules (LLM sometimes adds them)
            content = content.rstrip()
            while content.endswith("---"):
                content = content[:-3].rstrip()

            section_lines.append(content)
            section_lines.append("")

        # Render children
        for child_title in section.children:
            child = get_section_by_title(index, child_title)
            if child:
                section_lines.extend(render_section(child, depth + 1, has_content))

        return section_lines

    # Render all top-level sections
    for top_section in top_level:
        lines.extend(render_section(top_section))

    return "\n".join(lines)


def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug for anchors.

    Args:
        text: Text to slugify

    Returns:
        Slug string
    """
    import re

    # Lowercase
    slug = text.lower()

    # Replace spaces and special chars
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)

    return slug


def assemble_document(
    index: NormalizedIndex,
    merged_sections: List[MergedSection],
    output_path: Path
) -> None:
    """
    Assemble the final document from merged sections.

    Args:
        index: The normalized index
        merged_sections: List of merged section content
        output_path: Path to write the final document
    """
    # Build the document
    document = build_document_structure(index, merged_sections)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the file
    output_path.write_text(document, encoding="utf-8")

    print(f"Document assembled: {output_path}")
    print(f"Total sections: {len(merged_sections)}")
    print(f"Document size: {len(document):,} characters")


def generate_summary(
    index: NormalizedIndex,
    merged_sections: List[MergedSection]
) -> str:
    """
    Generate a summary of the assembled document.

    Args:
        index: The normalized index
        merged_sections: List of merged sections

    Returns:
        Summary string
    """
    lines = [
        "Assembly Summary",
        "=" * 40,
        f"Title: {index.title}",
        f"Total sections in index: {len(index.sections)}",
        f"Sections with content: {len(merged_sections)}",
        "",
        "Sections by level:",
    ]

    # Count by level
    level_counts = {}
    for s in index.sections:
        level_counts[s.level] = level_counts.get(s.level, 0) + 1

    for level in sorted(level_counts.keys()):
        prefix = "#" * level
        lines.append(f"  {prefix}: {level_counts[level]} sections")

    # Check for missing content
    content_titles = {s.section_title for s in merged_sections}
    missing = [s.title for s in index.sections if s.title not in content_titles]

    if missing:
        lines.append("")
        lines.append(f"Sections without content ({len(missing)}):")
        for title in missing[:10]:  # Show first 10
            lines.append(f"  - {title}")
        if len(missing) > 10:
            lines.append(f"  ... and {len(missing) - 10} more")

    return "\n".join(lines)


if __name__ == "__main__":
    # Allow running this stage directly for debugging
    print("Assemble stage - run with debugger for testing")
