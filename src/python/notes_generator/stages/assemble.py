# -------------------------------------------------------------------------
# File: assemble.py
# Description: Assemble stage - build final document from merged sections
# Context: Stage 4 of the VideoToNotes pipeline
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


def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to a human-readable string (H:MM:SS or M:SS).
    """
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


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
) -> Dict[int, MergedSection]:
    """
    Build a content map with fuzzy matching of section titles.

    Uses timestamps to disambiguate similar section titles like
    "Face Service" under "Congitive Services" vs "Face Service" under "Follow Alongs".

    Args:
        merged_sections: List of merged section content
        index: The normalized index for title matching

    Returns:
        Dictionary mapping section ORDER (unique ID) to merged content
    """
    content_map = {}

    # Build normalized index lookup with timestamp disambiguation
    # Key: (normalized_title, timestamp_prefix) -> IndexSection
    norm_ts_to_section = {}

    for section in index.sections:
        norm = normalize_title(section.title)
        ts_prefix = section.timestamp[:5] if section.timestamp else None  # HH:MM prefix

        # Store with timestamp for disambiguation (timestamp is the best disambiguator)
        if ts_prefix:
            key = (norm, ts_prefix)
            norm_ts_to_section[key] = section

    for merged in merged_sections:
        merged_norm = normalize_title(merged.section_title)
        merged_ts = extract_timestamp(merged.section_title)
        # If title doesn't have a timestamp, try to get it from timestamp_range
        if not merged_ts and merged.timestamp_range:
            merged_ts = extract_timestamp_from_range(merged.timestamp_range)
        merged_ts_prefix = merged_ts[:5] if merged_ts else None

        # Check if this is a parent section by looking for [PARENT SECTION] marker
        is_parent_content = "[PARENT SECTION]" in merged.content

        matched_section = None

        # Try exact match with timestamp first - this is the best method
        if merged_ts_prefix:
            key = (merged_norm, merged_ts_prefix)
            if key in norm_ts_to_section:
                matched_section = norm_ts_to_section[key]

        # If merged has timestamp but exact match failed, try fuzzy with timestamp awareness
        if not matched_section and merged_ts_prefix:
            matched_title = fuzzy_match_section(
                merged.section_title, index.sections,
                fallback_timestamp=merged_ts
            )
            if matched_title:
                # Find section with closest timestamp to disambiguate duplicates
                candidates = [s for s in index.sections if s.title == matched_title]
                if len(candidates) == 1:
                    matched_section = candidates[0]
                elif len(candidates) > 1:
                    # Multiple matches - use timestamp to find the right one
                    merged_seconds = timestamp_to_seconds(merged_ts) if merged_ts else 0
                    best_match = None
                    best_diff = float('inf')
                    for c in candidates:
                        c_seconds = timestamp_to_seconds(c.timestamp)
                        diff = abs(c_seconds - merged_seconds)
                        if diff < best_diff:
                            best_diff = diff
                            best_match = c
                    matched_section = best_match

        # Fallback: try to find by normalized title only (for cases without timestamps)
        if not matched_section:
            # For parent content, prefer level 2 sections
            target_level = 2 if is_parent_content else 3
            candidates = [s for s in index.sections if normalize_title(s.title) == merged_norm]
            if candidates:
                # Prefer the section with matching level
                level_matches = [c for c in candidates if c.level == target_level]
                if level_matches:
                    matched_section = level_matches[0]
                else:
                    matched_section = candidates[0]

        # Try fuzzy match as last resort
        if not matched_section:
            matched_title = fuzzy_match_section(
                merged.section_title, index.sections,
                fallback_timestamp=merged_ts
            )
            if matched_title:
                matched_section = next(
                    (s for s in index.sections if s.title == matched_title), None
                )

        # Use order as key (unique identifier for each section)
        if matched_section:
            map_key = matched_section.order
            # Skip content that's mostly empty placeholders
            content_lower = merged.content.lower()
            none_count = content_lower.count("none in this chunk")
            if none_count >= 4:  # 4+ "none" entries means it's an empty placeholder
                continue
            if map_key not in content_map:
                content_map[map_key] = merged

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
    title: str,
    parent_title: Optional[str] = None
) -> Optional[IndexSection]:
    """
    Get a section from the index by title, optionally filtered by parent.

    Args:
        index: The normalized index
        title: Section title to find
        parent_title: Optional parent title to filter by (for duplicate names)

    Returns:
        IndexSection or None if not found
    """
    # If parent is specified, find the section with that specific parent
    if parent_title is not None:
        for section in index.sections:
            if section.title == title and section.parent == parent_title:
                return section
        # Fall through to return first match if parent match not found

    # Return first match
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

    # Video link and publish date (two trailing spaces for markdown line breaks)
    if index.url:
        lines.append(f"**Video:** [{index.url}]({index.url})  ")
    if index.upload_date:
        lines.append(f"**Published:** {index.upload_date}  ")
    if index.duration:
        lines.append(f"**Duration:** {format_duration(index.duration)}  ")

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

    # Track rendered sections to prevent infinite recursion (using order as unique key)
    rendered_sections = set()  # Set of order integers
    sections_with_rules = set()  # Track which sections already have a rule before them
    last_content_section = [None]  # Track last section that had content (mutable for closure)

    def get_content_for_section(section: IndexSection) -> Optional[MergedSection]:
        """Get content for a section using order as key (unique ID)."""
        return content_map.get(section.order)

    # Render each section recursively
    def render_section(section: IndexSection, depth: int = 0, parent_has_content: bool = False,
                       is_first_child: bool = False):
        nonlocal sections_with_rules
        # Prevent infinite recursion from circular references
        # Use order as unique key since titles can be duplicated
        if section.order in rendered_sections:
            return []
        rendered_sections.add(section.order)

        # Limit recursion depth as safety measure
        if depth > 10:
            return []

        section_lines = []
        merged_content = get_content_for_section(section)
        has_content = merged_content is not None

        # Add horizontal rule before sections with content
        # Skip only if this is the very first content section in the document
        should_add_rule = has_content and len(sections_with_rules) > 0
        if should_add_rule:
            section_lines.append("---")
            section_lines.append("")

        if has_content:
            sections_with_rules.add(section.order)
            last_content_section[0] = section.title

        # Add heading
        heading_prefix = "#" * section.level
        section_lines.append(f"{heading_prefix} {section.title}")
        section_lines.append("")

        # Add content if this section has merged content
        if merged_content:
            # Extract content without the heading (it's already added)
            content = merged_content.content

            # Remove the ### heading from content if present
            content = content.lstrip()
            if content.startswith("###") or content.startswith("##"):
                # Remove first line (the heading)
                content = "\n".join(content.split("\n")[1:]).lstrip()

            # Strip trailing horizontal rules (LLM sometimes adds them)
            content = content.rstrip()
            while content.endswith("---"):
                content = content[:-3].rstrip()

            section_lines.append(content)
            section_lines.append("")

        # Render children - pass current section title as parent to find correct child
        # (handles duplicate child names like "Face Service" under both "Congitive Services" and "Follow Alongs")
        for child_title in section.children:
            child = get_section_by_title(index, child_title, parent_title=section.title)
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


def assemble_from_sections(
    index: NormalizedIndex,
    sections: List[MergedSection],
    output_path: Path
) -> None:
    """
    Assemble document directly from ordered sections.

    This is a simpler assembly approach that:
    1. Sorts sections by their order field
    2. Adds parent section headers when level changes
    3. Writes content in order without complex matching

    Args:
        index: The normalized index (for parent section headers and TOC)
        sections: List of MergedSection objects (already have order, level, content)
        output_path: Path to write the final document
    """
    # Sort sections by order
    sorted_sections = sorted(sections, key=lambda s: s.order)

    # Build parent lookup from index: section_title -> parent_title
    parent_map = {}
    for s in index.sections:
        if s.parent:
            parent_map[s.title] = s.parent

    # Build section lookup from index for level info
    section_lookup = {s.title: s for s in index.sections}

    lines = []

    # Document title
    lines.append(f"# {index.title} - Exam Notes")
    lines.append("")

    # Video link and publish date (two trailing spaces for markdown line breaks)
    if index.url:
        lines.append(f"**Video:** [{index.url}]({index.url})  ")
    if index.upload_date:
        lines.append(f"**Published:** {index.upload_date}  ")
    if index.duration:
        lines.append(f"**Duration:** {format_duration(index.duration)}  ")

    lines.append("")
    lines.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    lines.append("")

    lines.append("---")
    lines.append("")

    # Build table of contents from index
    lines.append("## Table of Contents")
    lines.append("")
    for section in sorted(index.sections, key=lambda s: s.order):
        if section.level >= 2:
            indent = "  " * (section.level - 2)
            lines.append(f"{indent}- [{section.title}](#{slugify(section.title)})")
    lines.append("")

    # Track which parent sections we've output headers for
    output_parents = set()
    last_level = 2

    for section in sorted_sections:
        # Find all ancestor sections that need headers
        ancestors = []
        current_title = section.section_title
        visited = set()  # Prevent infinite loops from circular parent references
        while current_title in parent_map and current_title not in visited:
            visited.add(current_title)
            parent_title = parent_map[current_title]
            if parent_title not in output_parents and parent_title in section_lookup:
                parent_section = section_lookup[parent_title]
                ancestors.append(parent_section)
            current_title = parent_title

        # Output ancestor headers in order (root first)
        for ancestor in reversed(ancestors):
            if ancestor.level >= 2:
                lines.append(f"{'#' * ancestor.level} {ancestor.title}")
                lines.append("")
                if ancestor.level == 2:
                    lines.append("---")
                    lines.append("")
                output_parents.add(ancestor.title)

        # Now output the section content
        content = section.content.strip()

        # Remove duplicate heading if content starts with the section header
        content_lines = content.split('\n')
        if content_lines and content_lines[0].startswith('#'):
            # Check if it matches our section title
            first_line = content_lines[0].lstrip('#').strip()
            clean_title = re.sub(r'[☁️🎤\[\]]+', '', section.section_title).strip()
            if clean_title.lower() in first_line.lower() or first_line.lower() in clean_title.lower():
                # Skip duplicate heading
                content = '\n'.join(content_lines[1:]).strip()

        # Add section heading
        level = section.level if section.level >= 2 else 3
        lines.append(f"{'#' * level} {section.section_title}")
        lines.append("")

        # Add content
        if content:
            lines.append(content)
            lines.append("")
            lines.append("---")
            lines.append("")

    # Build final document
    document = "\n".join(lines)

    # Clean up excessive blank lines and trailing rules
    document = re.sub(r'\n{4,}', '\n\n\n', document)
    document = re.sub(r'---\s*---', '---', document)
    document = document.rstrip('\n-') + '\n'

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the file
    output_path.write_text(document, encoding="utf-8")

    print(f"Document assembled: {output_path}")
    print(f"Total sections: {len(sections)}")
    print(f"Document size: {len(document):,} characters")


if __name__ == "__main__":
    # Allow running this stage directly for debugging
    print("Assemble stage - run with debugger for testing")
