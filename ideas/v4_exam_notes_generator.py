#!/usr/bin/env python3
"""
Exam Notes Generator - Uses GitHub Models API (Copilot Pro+)
Hybrid model approach: fast model for extraction, reasoning model for merging.

Usage:
    export GITHUB_TOKEN="ghp_your_token_here"
    python exam_notes_generator.py contents.md transcript_chunks.zip
"""

import asyncio
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

GITHUB_MODELS_BASE_URL = "https://models.github.ai/inference"

# Model presets
MODELS = {
    # Primary recommendations
    "deepseek": "deepseek/deepseek-r1-0528",
    "gpt4.1": "openai/gpt-4.1",
    "gpt5-mini": "openai/gpt-5-mini",
    
    # Fast options
    "gpt4.1-mini": "openai/gpt-4.1-mini",
    "deepseek-v3": "deepseek/deepseek-v3-0324",
    
    # Reasoning-focused
    "o3-mini": "openai/o3-mini",
    "phi4-reason": "microsoft/phi-4-reasoning",
    
    # Large models
    "llama-405b": "meta/meta-llama-3.1-405b-instruct",
    "gpt5": "openai/gpt-5",
}

# Hybrid strategy: different models per stage
STAGE1_MODEL = "openai/gpt-4.1-mini"      # Fast extraction
STAGE2_MODEL = "deepseek/deepseek-r1-0528" # Quality merging

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class ChunkResult:
    chunk_id: int
    sections: dict  # {section_title: notes_content}

# ============================================================================
# CLIENT
# ============================================================================

def create_client() -> AsyncOpenAI:
    """Create OpenAI-compatible client for GitHub Models."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError(
            "GITHUB_TOKEN not set.\n"
            "Create at: https://github.com/settings/tokens\n"
            "Permission needed: models:read"
        )
    return AsyncOpenAI(api_key=token, base_url=GITHUB_MODELS_BASE_URL)

# ============================================================================
# CONTENTS PARSER
# ============================================================================

def parse_contents(contents_text: str) -> dict:
    """Parse markdown TOC into hierarchical structure."""
    lines = contents_text.strip().split('\n')
    
    video_title = "Exam Notes"
    for line in lines:
        if line.startswith('# '):
            video_title = line[2:].strip()
            break
    
    heading_pattern = r'^(#{2,6})\s+(.+?)(?:\s*\[(\d{1,2}:\d{2}(?::\d{2})?)\])?$'
    sections = []
    
    for line in lines:
        match = re.match(heading_pattern, line)
        if match:
            hashes, title, timestamp = match.groups()
            sections.append({
                "level": len(hashes),
                "title": title.strip(),
                "timestamp": timestamp or "",
                "children": []
            })
    
    hierarchy = build_hierarchy(sections)
    
    return {
        "video_title": video_title,
        "total_sections": len(sections),
        "hierarchy": hierarchy,
        "flat_sections": sections
    }

def build_hierarchy(sections: list) -> list:
    """Build nested hierarchy from flat sections."""
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

def get_toc_text(parsed: dict) -> str:
    """Generate TOC text for prompts."""
    lines = []
    for s in parsed["flat_sections"]:
        prefix = "#" * s["level"]
        ts = f" [{s['timestamp']}]" if s["timestamp"] else ""
        lines.append(f"{prefix} {s['title']}{ts}")
    return "\n".join(lines)

# ============================================================================
# STAGE 1: CHUNK PROCESSING
# ============================================================================

CHUNK_PROMPT = """Generate exam-focused study notes from this transcript chunk.

## Table of Contents
{toc}

## Transcript Chunk {chunk_id} of {total_chunks}
{chunk_text}

## Instructions
Map content to TOC sections. For EACH section with content, output:

### [Section Title]
**Timestamp**: [start] – [end]

**Key Concepts**
- [main concepts as bullets]

**Definitions**
- **[Term]**: [definition]

**Key Facts**
- [important facts, numbers, specs]

**Examples**
- [examples, commands, configs]

**Exam Tips 🎯**
- [exam focus points]

Rules:
- Use ### ONLY for section titles
- Include ALL transcript content
- Be technically precise
- If no content for a subsection, write "- None in this chunk"
"""

async def process_chunk(
    client: AsyncOpenAI,
    chunk_id: int,
    total_chunks: int,
    chunk_text: str,
    toc: str
) -> ChunkResult:
    """Process single chunk with fast model."""
    
    response = await client.chat.completions.create(
        model=STAGE1_MODEL,
        messages=[
            {"role": "system", "content": "You create precise technical study notes."},
            {"role": "user", "content": CHUNK_PROMPT.format(
                toc=toc,
                chunk_id=chunk_id,
                total_chunks=total_chunks,
                chunk_text=chunk_text
            )}
        ],
        temperature=0.3,
        max_tokens=4000
    )
    
    sections = {}
    current_section = None
    current_content = []
    
    for line in response.choices[0].message.content.split('\n'):
        if line.startswith('### '):
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            current_section = line[4:].strip()
            current_content = [line]
        elif current_section:
            current_content.append(line)
    
    if current_section:
        sections[current_section] = '\n'.join(current_content)
    
    return ChunkResult(chunk_id=chunk_id, sections=sections)

# ============================================================================
# STAGE 2: SECTION MERGING
# ============================================================================

MERGE_PROMPT = """Merge these partial notes into ONE coherent section.

## Section: {section_title}

## Partials:
{partials}

## Instructions
1. **Timestamp**: [earliest] – [latest]
2. **Key Concepts**: Combine, remove duplicates, order logically
3. **Definitions**: Keep most complete; note conflicts as "(also: ...)"
4. **Key Facts**: Deduplicate; flag conflicts with ⚠️
5. **Examples**: Keep ALL unique examples
6. **Exam Tips**: Combine, prioritize actionable tips

Rules:
- Do NOT add new information
- Do NOT summarize or lose detail
- Output standard format with ### heading
"""

async def merge_section(
    client: AsyncOpenAI,
    section_title: str,
    partials: list[str]
) -> tuple[str, str]:
    """Merge partials with reasoning model."""
    
    if len(partials) == 1:
        return (section_title, partials[0])
    
    partials_text = "\n\n---\n\n".join(
        f"**Partial {i+1}:**\n{p}" for i, p in enumerate(partials)
    )
    
    response = await client.chat.completions.create(
        model=STAGE2_MODEL,
        messages=[
            {"role": "system", "content": "You are an expert editor for technical certification materials."},
            {"role": "user", "content": MERGE_PROMPT.format(
                section_title=section_title,
                partials=partials_text
            )}
        ],
        temperature=0.2,
        max_tokens=3000
    )
    
    return (section_title, response.choices[0].message.content)

# ============================================================================
# STAGE 3: ASSEMBLY
# ============================================================================

def assemble_document(video_title: str, hierarchy: list, merged: dict) -> str:
    """Assemble final markdown with proper heading levels."""
    
    lines = [
        f"# {video_title} - Complete Exam Notes\n",
        f"*Generated using GitHub Models API*\n",
        f"*Stage 1: {STAGE1_MODEL} | Stage 2: {STAGE2_MODEL}*\n",
        "---\n"
    ]
    
    def process(section: dict, level: int):
        prefix = "#" * level
        title = section["title"]
        
        if section.get("children"):
            lines.append(f"\n{prefix} {title}\n")
            for child in section["children"]:
                process(child, level + 1)
        else:
            if title in merged:
                content = re.sub(r'^### ', f'{prefix} ', merged[title], flags=re.MULTILINE)
                lines.append(f"\n{content}\n")
            else:
                lines.append(f"\n{prefix} {title}\n")
                lines.append("*No transcript content for this section.*\n")
    
    for section in hierarchy:
        process(section, 2)
    
    return "\n".join(lines)

# ============================================================================
# ORCHESTRATOR
# ============================================================================

async def generate_notes(contents_path: str, zip_path: str, output_path: str):
    """Main pipeline."""
    
    print(f"🤖 Models: Stage1={STAGE1_MODEL}, Stage2={STAGE2_MODEL}")
    
    client = create_client()
    
    # Parse TOC
    print("📋 Parsing contents...")
    parsed = parse_contents(Path(contents_path).read_text())
    toc = get_toc_text(parsed)
    print(f"   {parsed['video_title']} ({parsed['total_sections']} sections)")
    
    # Extract chunks
    print("📦 Extracting chunks...")
    chunks = []
    with zipfile.ZipFile(zip_path, 'r') as z:
        for name in sorted(z.namelist()):
            if name.endswith(('.txt', '.md')):
                chunks.append(z.read(name).decode('utf-8'))
    print(f"   {len(chunks)} chunks")
    
    # Stage 1
    print(f"\n⚙️  Stage 1: Processing chunks ({STAGE1_MODEL})...")
    tasks = [process_chunk(client, i+1, len(chunks), c, toc) for i, c in enumerate(chunks)]
    results = []
    for coro in asyncio.as_completed(tasks):
        r = await coro
        results.append(r)
        print(f"   ✓ Chunk {r.chunk_id}/{len(chunks)}")
    
    # Group by section
    print("\n📑 Grouping by section...")
    section_partials = {}
    for r in results:
        for title, content in r.sections.items():
            section_partials.setdefault(title, []).append(content)
    print(f"   {len(section_partials)} sections")
    
    # Stage 2
    print(f"\n🔀 Stage 2: Merging sections ({STAGE2_MODEL})...")
    merge_tasks = [merge_section(client, t, p) for t, p in section_partials.items()]
    merged = {}
    for i, coro in enumerate(asyncio.as_completed(merge_tasks)):
        title, content = await coro
        merged[title] = content
        print(f"   ✓ {i+1}/{len(section_partials)}")
    
    # Stage 3
    print("\n📄 Stage 3: Assembling...")
    doc = assemble_document(parsed["video_title"], parsed["hierarchy"], merged)
    
    Path(output_path).write_text(doc)
    
    total_requests = len(chunks) + len([p for p in section_partials.values() if len(p) > 1])
    print(f"\n✅ Done! {output_path}")
    print(f"   Premium requests: ~{total_requests}")

# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Generate exam notes from transcript")
    parser.add_argument("contents", help="TOC markdown file")
    parser.add_argument("transcript_zip", help="ZIP with transcript chunks")
    parser.add_argument("-o", "--output", default="exam_notes.md", help="Output file")
    
    args = parser.parse_args()
    asyncio.run(generate_notes(args.contents, args.transcript_zip, args.output))

if __name__ == "__main__":
    main()