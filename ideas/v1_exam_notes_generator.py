#!/usr/bin/env python3
"""
Minimal exam notes generator - runs locally, costs pennies.
Usage: python exam_notes_generator.py contents.md transcript_chunks.zip
"""

import asyncio
import json
import zipfile
from pathlib import Path
from openai import AsyncOpenAI

# Initialize client - uses OPENAI_API_KEY env var
client = AsyncOpenAI()
MODEL = "gpt-4o-mini"  # $0.15/1M in, $0.60/1M out

async def process_chunk(chunk_id: int, chunk_text: str, toc: str) -> dict:
    """Stage 1: Process single chunk into notes."""
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": f"""Generate exam notes from this transcript chunk.

## Table of Contents
{toc}

## Transcript Chunk {chunk_id}
{chunk_text}

Map content to TOC sections. For each section, output:
### [Section Title]
**Timestamp**: [start] – [end]
**Key Concepts**
- ...
**Definitions**
- ...
**Key Facts**
- ...
**Examples**
- ...
**Exam Tips 🎯**
- ...
"""
        }],
        temperature=0.3
    )
    return {"chunk_id": chunk_id, "notes": response.choices[0].message.content}

async def merge_sections(section_title: str, partials: list[str]) -> str:
    """Stage 2: Merge partials for one section."""
    if len(partials) == 1:
        return partials[0]
    
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": f"""Merge these partial notes for "{section_title}" into one coherent section.
Remove duplicates, resolve conflicts, keep all unique content.

{chr(10).join(f'--- Partial {i+1} ---{chr(10)}{p}' for i, p in enumerate(partials))}

Output single merged section in the standard format.
"""
        }],
        temperature=0.3
    )
    return response.choices[0].message.content

async def main(contents_path: str, zip_path: str, output_path: str = "exam_notes.md"):
    # Load TOC
    toc = Path(contents_path).read_text()
    
    # Extract and process chunks in parallel
    chunks = []
    with zipfile.ZipFile(zip_path, 'r') as z:
        for name in sorted(z.namelist()):
            if name.endswith('.txt'):
                chunks.append(z.read(name).decode('utf-8'))
    
    print(f"Processing {len(chunks)} chunks...")
    
    # Stage 1: Process all chunks in parallel
    tasks = [process_chunk(i+1, chunk, toc) for i, chunk in enumerate(chunks)]
    chunk_results = await asyncio.gather(*tasks)
    
    print("Stage 1 complete. Merging sections...")
    
    # Group notes by section (simplified - assumes ### headers)
    section_partials = {}
    for result in chunk_results:
        # Parse sections from notes (simplified parsing)
        current_section = None
        current_content = []
        for line in result["notes"].split('\n'):
            if line.startswith('### '):
                if current_section:
                    section_partials.setdefault(current_section, []).append('\n'.join(current_content))
                current_section = line[4:].strip()
                current_content = [line]
            elif current_section:
                current_content.append(line)
        if current_section:
            section_partials.setdefault(current_section, []).append('\n'.join(current_content))
    
    # Stage 2: Merge sections in parallel
    merge_tasks = [
        merge_sections(title, partials) 
        for title, partials in section_partials.items()
    ]
    merged_sections = await asyncio.gather(*merge_tasks)
    
    # Stage 3: Assemble (deterministic)
    final_doc = "# Exam Notes\n\n" + "\n\n".join(merged_sections)
    
    Path(output_path).write_text(final_doc)
    print(f"Done! Output: {output_path}")

if __name__ == "__main__":
    import sys
    asyncio.run(main(sys.argv[1], sys.argv[2]))