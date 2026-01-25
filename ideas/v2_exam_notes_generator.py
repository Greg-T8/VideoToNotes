#!/usr/bin/env python3
"""
Exam Notes Generator - Uses GitHub Models API (included with Copilot Pro+)
Zero marginal cost within your subscription limits.

Usage:
    export GITHUB_TOKEN="ghp_your_token_here"
    python exam_notes_generator.py contents.md transcript_chunks.zip
"""

import asyncio
import json
import re
import zipfile
from pathlib import Path
from dataclasses import dataclass
from openai import AsyncOpenAI
import argparse
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

# GitHub Models API endpoint (OpenAI-compatible)
GITHUB_MODELS_BASE_URL = "https://models.github.ai/inference"

# Choose your model (all included with Pro+)
MODELS = {
    "claude": "anthropic/claude-sonnet-4",      # Best reasoning
    "gpt4o": "openai/gpt-4o",                    # Fast & capable  
    "gpt4.1": "openai/gpt-4.1",                  # Latest OpenAI
    "llama": "meta/llama-3.3-70b-instruct",     # Open source option
}

DEFAULT_MODEL = "claude"  # Use Claude Sonnet 4 by default

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Section:
    title: str
    level: int
    timestamp_start: str
    timestamp_end: str
    children: list
    is_leaf: bool

@dataclass
class ChunkResult:
    chunk_id: int
    sections: dict  # {section_title: notes_content}

# ============================================================================
# GITHUB MODELS CLIENT
# ============================================================================

def create_client() -> AsyncOpenAI:
    """Create OpenAI client pointing to GitHub Models API."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError(
            "GITHUB_TOKEN environment variable not set.\n"
            "Create a token at: https://github.com/settings/tokens\n"
            "Required permission: models:read"
        )
    
    return AsyncOpenAI(
        api_key=token,
        base_url=GITHUB_MODELS_BASE_URL
    )

# ============================================================================
# CONTENTS PARSER
# ============================================================================

def parse_contents(contents_text: str) -> dict:
    """Parse markdown TOC into hierarchical structure."""
    lines = contents_text.strip().split('\n')
    
    # Extract video title (first # heading)
    video_title = "Exam Notes"
    for line in lines:
        if line.startswith('# '):
            video_title = line[2:].strip()
            break
    
    # Parse sections with timestamps
    # Expected format: ## Section Title [00:00:00]
    timestamp_pattern = r'\[(\d{1,2}:\d{2}(?::\d{2})?)\]'
    heading_pattern = r'^(#{2,6})\s+(.+?)(?:\s*\[(\d{1,2}:\d{2}(?::\d{2})?)\])?$'
    
    sections = []
    
    for line in lines:
        match = re.match(heading_pattern, line)
        if match:
            hashes, title, timestamp = match.groups()
            level = len(hashes)
            sections.append({
                "level": level,
                "title": title.strip(),
                "timestamp": timestamp or "",
                "children": []
            })
    
    # Build hierarchy
    hierarchy = build_hierarchy(sections)
    
    # Count sections
    total_level2 = sum(1 for s in hierarchy if s["level"] == 2)
    total_leaves = count_leaves(hierarchy)
    
    return {
        "video_title": video_title,
        "total_level2_sections": total_level2,
        "total_lowest_level_sections": total_leaves,
        "hierarchy": hierarchy,
        "flat_sections": sections
    }

def build_hierarchy(sections: list) -> list:
    """Convert flat section list to nested hierarchy."""
    if not sections:
        return []
    
    root = []
    stack = [({"children": root, "level": 1}, 1)]
    
    for section in sections:
        level = section["level"]
        
        while stack and stack[-1][1] >= level:
            stack.pop()
        
        parent = stack[-1][0] if stack else {"children": root}
        parent["children"].append(section)
        stack.append((section, level))
    
    return root

def count_leaves(sections: list) -> int:
    """Count leaf (lowest-level) sections."""
    count = 0
    for section in sections:
        if section.get("children"):
            count += count_leaves(section["children"])
        else:
            count += 1
    return count

def get_toc_text(parsed_contents: dict) -> str:
    """Generate clean TOC text for prompts."""
    lines = []
    for section in parsed_contents["flat_sections"]:
        prefix = "#" * section["level"]
        timestamp = f" [{section['timestamp']}]" if section["timestamp"] else ""
        lines.append(f"{prefix} {section['title']}{timestamp}")
    return "\n".join(lines)

# ============================================================================
# STAGE 1: CHUNK PROCESSING
# ============================================================================

CHUNK_PROMPT = """You are generating exam-focused study notes from a video transcript chunk.

## Table of Contents (Full Hierarchy)
{toc}

## Transcript Chunk {chunk_id} of {total_chunks}
{chunk_text}

## Instructions
1. Map each portion of this transcript to the appropriate TOC section
2. For EACH section that has content in this chunk, generate notes in this EXACT format:

### [Section Title from TOC]
**Timestamp**: [first timestamp] – [last timestamp in this chunk for this section]

**Key Concepts**
- [bullet points of main concepts]

**Definitions**
- **[Term]**: [definition]

**Key Facts**
- [important facts, numbers, specifications]

**Examples**
- [concrete examples, commands, configurations mentioned]

**Exam Tips 🎯**
- [what to remember for the exam, common pitfalls]

## Rules
- Use ### for section titles ONLY
- Use bold (**text**) for subsection headers
- Include ALL content from the transcript - no information loss
- If content spans multiple sections, create separate note blocks for each
- Be technically precise - preserve exact values, commands, configurations
- If a subsection has no content (e.g., no examples), include the header with "- None in this section"
"""

async def process_chunk(
    client: AsyncOpenAI,
    model: str,
    chunk_id: int,
    total_chunks: int,
    chunk_text: str,
    toc: str
) -> ChunkResult:
    """Process a single transcript chunk into structured notes."""
    
    prompt = CHUNK_PROMPT.format(
        toc=toc,
        chunk_id=chunk_id,
        total_chunks=total_chunks,
        chunk_text=chunk_text
    )
    
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are an expert at creating study notes for technical certification exams. Be thorough and precise."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=4000
    )
    
    notes_text = response.choices[0].message.content
    
    # Parse notes into sections
    sections = parse_notes_into_sections(notes_text)
    
    return ChunkResult(chunk_id=chunk_id, sections=sections)

def parse_notes_into_sections(notes_text: str) -> dict:
    """Parse generated notes into section dict."""
    sections = {}
    current_section = None
    current_content = []
    
    for line in notes_text.split('\n'):
        if line.startswith('### '):
            # Save previous section
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            # Start new section
            current_section = line[4:].strip()
            current_content = [line]
        elif current_section:
            current_content.append(line)
    
    # Save last section
    if current_section:
        sections[current_section] = '\n'.join(current_content)
    
    return sections

# ============================================================================
# STAGE 2: SECTION MERGING
# ============================================================================

MERGE_PROMPT = """You are merging multiple partial notes for the same exam topic into ONE coherent section.

## Section: {section_title}

## Partial Notes from Different Transcript Chunks:
{partials}

## Merge Instructions

1. **Timestamps**: Use [earliest start] – [latest end]

2. **Key Concepts**: 
   - Combine all bullets, remove exact duplicates
   - Keep near-duplicates if they add nuance
   - Order: foundational → advanced

3. **Definitions**:
   - Keep the most complete version of each term
   - If definitions conflict, note: "(also described as: ...)"

4. **Key Facts**:
   - Remove redundant facts
   - If facts conflict, flag with: "⚠️ Verify: mentioned as both X and Y"

5. **Examples**:
   - Keep ALL unique examples
   - Preserve code/commands exactly

6. **Exam Tips**:
   - Combine and deduplicate
   - Prioritize actionable tips

## Rules
- Do NOT add information not in the source partials
- Do NOT summarize or lose detail
- Output in the standard format with ### heading

Output the merged section now:
"""

async def merge_section(
    client: AsyncOpenAI,
    model: str,
    section_title: str,
    partials: list[str]
) -> str:
    """Merge multiple partial notes for one section."""
    
    if len(partials) == 1:
        return partials[0]
    
    # Format partials
    partials_text = "\n\n---\n\n".join(
        f"**Partial {i+1}:**\n{p}" for i, p in enumerate(partials)
    )
    
    prompt = MERGE_PROMPT.format(
        section_title=section_title,
        partials=partials_text
    )
    
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are an expert editor specializing in technical certification study materials."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=3000
    )
    
    return response.choices[0].message.content

# ============================================================================
# STAGE 3: FINAL ASSEMBLY
# ============================================================================

def assemble_final_document(
    video_title: str,
    hierarchy: list,
    merged_sections: dict
) -> str:
    """Assemble final markdown document with proper heading hierarchy."""
    
    lines = [f"# {video_title} - Complete Exam Notes\n"]
    lines.append(f"*Generated with GitHub Models API*\n")
    lines.append("---\n")
    
    def process_section(section: dict, level: int):
        prefix = "#" * level
        title = section["title"]
        
        if section.get("children"):
            # Parent section - add heading and recurse
            lines.append(f"\n{prefix} {title}\n")
            for child in section["children"]:
                process_section(child, level + 1)
        else:
            # Leaf section - insert merged content
            if title in merged_sections:
                content = merged_sections[title]
                # Adjust heading level in content
                adjusted = re.sub(
                    r'^### ',
                    f'{prefix} ',
                    content,
                    flags=re.MULTILINE
                )
                lines.append(f"\n{adjusted}\n")
            else:
                # Section not covered in transcript
                lines.append(f"\n{prefix} {title}\n")
                lines.append("*No content in transcript for this section.*\n")
    
    for section in hierarchy:
        process_section(section, 2)
    
    return "\n".join(lines)

# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================

async def generate_exam_notes(
    contents_path: str,
    zip_path: str,
    output_path: str,
    model_key: str = DEFAULT_MODEL
):
    """Main entry point - orchestrates the full pipeline."""
    
    model = MODELS.get(model_key, MODELS[DEFAULT_MODEL])
    print(f"🤖 Using model: {model}")
    
    # Initialize client
    client = create_client()
    
    # Parse contents
    print("📋 Parsing table of contents...")
    contents_text = Path(contents_path).read_text()
    parsed_contents = parse_contents(contents_text)
    toc = get_toc_text(parsed_contents)
    
    print(f"   Video: {parsed_contents['video_title']}")
    print(f"   Sections: {parsed_contents['total_lowest_level_sections']}")
    
    # Extract chunks
    print("📦 Extracting transcript chunks...")
    chunks = []
    with zipfile.ZipFile(zip_path, 'r') as z:
        for name in sorted(z.namelist()):
            if name.endswith('.txt') or name.endswith('.md'):
                chunks.append(z.read(name).decode('utf-8'))
    
    print(f"   Found {len(chunks)} chunks")
    
    # Stage 1: Process chunks in parallel
    print("\n⚙️  Stage 1: Processing chunks...")
    tasks = [
        process_chunk(client, model, i+1, len(chunks), chunk, toc)
        for i, chunk in enumerate(chunks)
    ]
    
    chunk_results = []
    for i, coro in enumerate(asyncio.as_completed(tasks)):
        result = await coro
        chunk_results.append(result)
        print(f"   ✓ Chunk {result.chunk_id}/{len(chunks)} complete")
    
    # Group by section
    print("\n📑 Grouping notes by section...")
    section_partials = {}
    for result in chunk_results:
        for section_title, content in result.sections.items():
            if section_title not in section_partials:
                section_partials[section_title] = []
            section_partials[section_title].append(content)
    
    print(f"   {len(section_partials)} sections found across chunks")
    
    # Stage 2: Merge sections
    print("\n🔀 Stage 2: Merging sections...")
    merge_tasks = [
        merge_section(client, model, title, partials)
        for title, partials in section_partials.items()
    ]
    
    merged_list = []
    section_titles = list(section_partials.keys())
    for i, coro in enumerate(asyncio.as_completed(merge_tasks)):
        merged = await coro
        merged_list.append((section_titles[i], merged))
        print(f"   ✓ Merged {i+1}/{len(section_titles)}: {section_titles[i][:40]}...")
    
    merged_sections = dict(merged_list)
    
    # Stage 3: Assemble
    print("\n📄 Stage 3: Assembling final document...")
    final_doc = assemble_final_document(
        parsed_contents["video_title"],
        parsed_contents["hierarchy"],
        merged_sections
    )
    
    # Write output
    output_file = Path(output_path)
    output_file.write_text(final_doc)
    
    print(f"\n✅ Done! Output saved to: {output_file.absolute()}")
    print(f"   Size: {len(final_doc):,} characters")
    
    # Estimate requests used
    total_requests = len(chunks) + len(section_partials)
    print(f"   Premium requests used: ~{total_requests}")

# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate exam notes from video transcript using GitHub Models API"
    )
    parser.add_argument("contents", help="Path to contents/TOC markdown file")
    parser.add_argument("transcript_zip", help="Path to ZIP file with transcript chunks")
    parser.add_argument(
        "-o", "--output",
        default="exam_notes.md",
        help="Output file path (default: exam_notes.md)"
    )
    parser.add_argument(
        "-m", "--model",
        choices=list(MODELS.keys()),
        default=DEFAULT_MODEL,
        help=f"Model to use (default: {DEFAULT_MODEL})"
    )
    
    args = parser.parse_args()
    
    asyncio.run(generate_exam_notes(
        args.contents,
        args.transcript_zip,
        args.output,
        args.model
    ))

if __name__ == "__main__":
    main()