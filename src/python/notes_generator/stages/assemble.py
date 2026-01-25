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
- Outputs formatted Markdown
"""

from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from notes_generator.models import NormalizedIndex, MergedSection, IndexSection


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
    # Create lookup for merged content
    content_map = {s.section_title: s for s in merged_sections}

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

    # Render each section recursively
    def render_section(section: IndexSection, depth: int = 0):
        section_lines = []

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
