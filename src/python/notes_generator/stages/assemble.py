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


def fuzzy_match_section(
    merged_title: str,
    index_sections: List[IndexSection],
    threshold: float = 0.85
) -> Optional[str]:
    """
    Find the best matching index section title for a merged section.

    Uses a higher threshold (0.85) to avoid matching similar but distinct
    section names like "Text Analytics" vs "Text Analysis".

    Args:
        merged_title: The title from the merged section
        index_sections: List of index sections to match against
        threshold: Minimum similarity ratio (0-1) for a match

    Returns:
        The exact title from the index, or None if no match found
    """
    normalized_merged = normalize_title(merged_title)
    merged_ts = extract_timestamp(merged_title)

    best_match = None
    best_ratio = 0.0

    for section in index_sections:
        normalized_index = normalize_title(section.title)

        # Exact match after normalization
        if normalized_merged == normalized_index:
            return section.title

        # Fuzzy match
        ratio = SequenceMatcher(None, normalized_merged, normalized_index).ratio()

        # For very similar titles (>0.9), also check timestamps if available
        if ratio > 0.9 and merged_ts:
            section_ts = extract_timestamp(section.title)
            if section_ts and merged_ts[:5] == section_ts[:5]:
                # Timestamps match (at least HH:MM) - strong match
                return section.title

        if ratio > best_ratio and ratio >= threshold:
            best_ratio = ratio
            best_match = section.title

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
    norm_to_index = {}
    norm_only_to_index = {}  # Fallback without timestamp

    for section in index.sections:
        norm = normalize_title(section.title)
        ts = extract_timestamp(section.title)
        ts_prefix = ts[:5] if ts else None  # HH:MM prefix

        # Store with timestamp for disambiguation
        if ts_prefix:
            key = (norm, ts_prefix)
            norm_to_index[key] = section.title

        # Also store without timestamp as fallback (first one wins)
        if norm not in norm_only_to_index:
            norm_only_to_index[norm] = section.title

    for merged in merged_sections:
        merged_norm = normalize_title(merged.section_title)
        merged_ts = extract_timestamp(merged.section_title)
        merged_ts_prefix = merged_ts[:5] if merged_ts else None

        matched_title = None

        # Try exact match with timestamp first
        if merged_ts_prefix:
            key = (merged_norm, merged_ts_prefix)
            if key in norm_to_index:
                matched_title = norm_to_index[key]

        # Try exact normalized match (without timestamp)
        if not matched_title and merged_norm in norm_only_to_index:
            matched_title = norm_only_to_index[merged_norm]

        # Try fuzzy match as last resort
        if not matched_title:
            matched_title = fuzzy_match_section(merged.section_title, index.sections)

        if matched_title and matched_title not in content_map:
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
    lines.append("---")
    lines.append("")

    # Track rendered sections to prevent infinite recursion
    rendered_sections = set()

    # Render each section recursively
    def render_section(section: IndexSection, depth: int = 0):
        # Prevent infinite recursion from circular references
        if section.title in rendered_sections:
            return []
        rendered_sections.add(section.title)

        # Limit recursion depth as safety measure
        if depth > 10:
            return []

        section_lines = []

        # Add horizontal rule before leaf sections (sections with content)
        if section.title in content_map:
            section_lines.append("---")
            section_lines.append("")

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

            section_lines.append(content)
            section_lines.append("")

        # Render children
        for child_title in section.children:
            child = get_section_by_title(index, child_title)
            if child:
                section_lines.extend(render_section(child, depth + 1))

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
