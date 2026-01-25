#!/usr/bin/env python3
"""
Exam Notes Generator - Uses GitHub Models API (Copilot Pro+)

Usage:
    python exam_notes_generator.py contents.md transcript_chunks.zip
    python exam_notes_generator.py contents.md transcript_chunks.zip -o output.md
    python exam_notes_generator.py contents.md transcript_chunks.zip --prompts ./my-prompts/
"""

import asyncio
import re
import subprocess
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

# Default prompt directory (relative to script location)
DEFAULT_PROMPTS_DIR = Path(__file__).parent / "prompts"

# Models for each stage
STAGE1_MODEL = "openai/gpt-4.1-mini"       # Fast extraction
STAGE2_MODEL = "deepseek/deepseek-r1-0528"  # Quality merging

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class ChunkResult:
    chunk_id: int
    sections: dict  # {section_title: notes_content}

@dataclass
class Prompts:
    system_stage1: str
    system_stage2: str
    chunk_process: str
    section_merge: str

# ============================================================================
# SECURE TOKEN HANDLING
# ============================================================================

def get_github_token() -> str:
    """
    Get GitHub token securely. Priority:
    1. GITHUB_TOKEN environment variable
    2. GitHub CLI (gh auth token)
    """
    
    # 1. Environment variable (CI/CD or explicit override)
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        print("   🔑 Using token from GITHUB_TOKEN environment variable")
        return token
    
    # 2. GitHub CLI (recommended for local use)
    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        token = result.stdout.strip()
        if token:
            print("   🔑 Using token from GitHub CLI")
            return token
    except subprocess.CalledProcessError:
        pass  # gh not authenticated
    except FileNotFoundError:
        pass  # gh not installed
    except subprocess.TimeoutExpired:
        pass  # gh hanging
    
    # No token found
    raise ValueError(
        "\n❌ GitHub token not found!\n\n"
        "Setup (choose one):\n\n"
        "  Option A - GitHub CLI (recommended):\n"
        "    gh auth login\n\n"
        "  Option B - Environment variable:\n"
        "    export GITHUB_TOKEN='ghp_xxxx'\n"
    )

def create_client() -> AsyncOpenAI:
    """Create OpenAI-compatible client for GitHub Models."""
    token = get_github_token()
    return AsyncOpenAI(api_key=token, base_url=GITHUB_MODELS_BASE_URL)

# ============================================================================
# PROMPT LOADING
# ============================================================================

def load_prompts(prompts_dir: Path) -> Prompts:
    """Load prompt templates from external files."""
    
    if not prompts_dir.exists():
        raise FileNotFoundError(
            f"Prompts directory not found: {prompts_dir}\n"
            f"Expected files:\n"
            f"  - {prompts_dir}/system.md\n"
            f"  - {prompts_dir}/chunk_process.md\n"
            f"  - {prompts_dir}/section_merge.md"
        )
    
    # Load system prompts
    system_file = prompts_dir / "system.md"
    if system_file.exists():
        system_content = system_file.read_text()
        # Parse sections from system.md
        system_stage1 = _extract_section(system_content, "Stage 1")
        system_stage2 = _extract_section(system_content, "Stage 2")
    else:
        # Defaults if file doesn't exist
        system_stage1 = "You are an expert at creating study notes for technical certification exams."
        system_stage2 = "You are an expert editor for technical certification study materials."
    
    # Load chunk processing prompt
    chunk_file = prompts_dir / "chunk_process.md"
    if not chunk_file.exists():
        raise FileNotFoundError(f"Required prompt file not found: {chunk_file}")
    chunk_process = chunk_file.read_text()
    
    # Load section merge prompt
    merge_file = prompts_dir / "section_merge.md"
    if not merge_file.exists():
        raise FileNotFoundError(f"Required prompt file not found: {merge_file}")
    section_merge = merge_file.read_text()
    
    return Prompts(
        system_stage1=system_stage1,
        system_stage2=system_stage2,
        chunk_process=chunk_process,
        section_merge=section_merge
    )

def _extract_section(content: str, section_name: str) -> str:
    """Extract content under a ## heading containing section_name."""
    lines = content.split('\n')
    capturing = False
    result = []
    
    for line in lines:
        if line.startswith('## ') and section_name in line:
            capturing = True
            continue
        elif line.startswith('## ') and capturing:
            break
        elif capturing:
            result.append(line)
    
    return '\n'.join(result).strip()

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
    
    hierarchy = _build_hierarchy(sections)
    
    return {
        "video_title": video_title,
        "total_sections": len(sections),
        "hierarchy": hierarchy,
        "flat_sections": sections
    }

def _build_hierarchy(sections: list) -> list:
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

async def process_chunk(
    client: AsyncOpenAI,
    prompts: Prompts,
    chunk_id: int,
    total_chunks: int,
    chunk_text: str,
    toc: str
) -> ChunkResult:
    """Process single chunk with fast model."""
    
    # Format the prompt template
    user_prompt = prompts.chunk_process.format(
        toc=toc,
        chunk_id=chunk_id,
        total_chunks=total_chunks,
        chunk_text=chunk_text
    )
    
    response = await client.chat.completions.create(
        model=STAGE1_MODEL,
        messages=[
            {"role": "system", "content": prompts.system_stage1},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=4000
    )
    
    sections = _parse_notes_into_sections(response.choices[0].message.content)
    
    return ChunkResult(chunk_id=chunk_id, sections=sections)

def _parse_notes_into_sections(notes_text: str) -> dict:
    """Parse generated notes into section dict."""
    sections = {}
    current_section = None
    current_content = []
    
    for line in notes_text.split('\n'):
        if line.startswith('### '):
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            current_section = line[4:].strip()
            current_content = [line]
        elif current_section:
            current_content.append(line)
    
    if current_section:
        sections[current_section] = '\n'.join(current_content)
    
    return sections

# ============================================================================
# STAGE 2: SECTION MERGING
# ============================================================================

async def merge_section(
    client: AsyncOpenAI,
    prompts: Prompts,
    section_title: str,
    partials: list[str]
) -> tuple[str, str]:
    """Merge partials with reasoning model."""
    
    if len(partials) == 1:
        return (section_title, partials[0])
    
    # Format partials
    partials_text = "\n\n---\n\n".join(
        f"**Partial {i+1}:**\n{p}" for i, p in enumerate(partials)
    )
    
    # Format the prompt template
    user_prompt = prompts.section_merge.format(
        section_title=section_title,
        partials=partials_text
    )
    
    response = await client.chat.completions.create(
        model=STAGE2_MODEL,
        messages=[
            {"role": "system", "content": prompts.system_stage2},
            {"role": "user", "content": user_prompt}
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

async def generate_notes(
    contents_path: str,
    zip_path: str,
    output_path: str,
    prompts_dir: Path
):
    """Main pipeline."""
    
    print(f"🤖 Models: Stage1={STAGE1_MODEL}, Stage2={STAGE2_MODEL}")
    print(f"📝 Prompts: {prompts_dir}")
    
    # Load prompts
    prompts = load_prompts(prompts_dir)
    print("   ✓ Prompts loaded")
    
    # Create client
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
    tasks = [
        process_chunk(client, prompts, i+1, len(chunks), c, toc)
        for i, c in enumerate(chunks)
    ]
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
    merge_tasks = [
        merge_section(client, prompts, t, p)
        for t, p in section_partials.items()
    ]
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
    parser = argparse.ArgumentParser(
        description="Generate exam notes from video transcript using GitHub Models API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python exam_notes_generator.py contents.md transcript.zip
  python exam_notes_generator.py contents.md transcript.zip -o notes.md
  python exam_notes_generator.py contents.md transcript.zip --prompts ./custom-prompts/
        """
    )
    parser.add_argument("contents", help="Path to contents/TOC markdown file")
    parser.add_argument("transcript_zip", help="Path to ZIP file with transcript chunks")
    parser.add_argument(
        "-o", "--output",
        default="exam_notes.md",
        help="Output file path (default: exam_notes.md)"
    )
    parser.add_argument(
        "-p", "--prompts",
        type=Path,
        default=DEFAULT_PROMPTS_DIR,
        help=f"Directory containing prompt files (default: {DEFAULT_PROMPTS_DIR})"
    )
    
    args = parser.parse_args()
    
    asyncio.run(generate_notes(
        args.contents,
        args.transcript_zip,
        args.output,
        args.prompts
    ))

if __name__ == "__main__":
    main()