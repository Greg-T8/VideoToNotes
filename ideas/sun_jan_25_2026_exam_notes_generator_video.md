# Copilot Chat Conversation Export: Exam Notes Generator (Video)

**User:** @Greg-T8
**Thread URL:** https://github.com/copilot/c/d4587849-2afd-4cec-9e20-0150b135bb5c

## @Greg-T8

Help me design a solution for producing an exam notes markdown file from a video transcript. Inputs are a contents file that has time-stamped headings and subheadings. Other input is a zip file that includes 20kb transcript chunks.

The solution needs to use Azure AI technologies.

## Copilot

Based on your requirements and the instructions in your `instructions.txt` file, here's a comprehensive **Azure AI-based solution architecture** for producing exam notes from video transcripts:

---

## Solution Architecture: Hierarchical Exam Notes Generator

### Overview

This pipeline processes timestamped video transcripts and a contents/index file to produce structured, exam-focused markdown notes using Azure AI services.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           INPUT LAYER                                       │
├─────────────────┬───────────────────────────────────────────────────────────┤
│ Contents File   │  Transcript Chunks ZIP (20KB each)                        │
│ (TOC + Timestamps)                                                          │
└────────┬────────┴───────────────────────────┬───────────────────────────────┘
         │                                    │
         ▼                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      AZURE BLOB STORAGE                                     │
│   • Contents container    • Chunks container    • Output container          │
└─────────────────────────────────────────────────────────────────────────────┘
         │                                    │
         ▼                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                                      │
│              Azure Functions / Azure Durable Functions                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. Parse Contents → Build Hierarchy                                        │
│  2. Unzip & Queue Transcript Chunks                                         │
│  3. Fan-out: Process Each Chunk in Parallel                                 │
│  4. Fan-in: Stitch Final Notes                                              │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     AI PROCESSING LAYER                                     │
├──────────────────────────┬──────────────────────────────────────────────────┤
│  Azure OpenAI Service    │  Azure AI Language Service                       │
│  (GPT-4 / GPT-4o)        │  (Extractive Summarization)                      │
├──────────────────────────┴──────────────────────────────────────────────────┤
│  Tasks:                                                                     │
│  • Map transcript segments to TOC sections (semantic matching)              │
│  • Extract Key Concepts, Definitions, Facts, Examples                       │
│  • Generate Exam Tips                                                       │
│  • Abstractive summarization for condensed notes                            │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       OUTPUT LAYER                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  • Per-chunk markdown files (ZIPped)                                        │
│  • Final stitched [VideoTitle]_Complete_Exam_Notes.md                       │
│  • Downloadable via Azure Blob SAS URLs                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Azure Services & Their Roles

| Component | Azure Service | Purpose |
|-----------|---------------|---------|
| **Storage** | Azure Blob Storage | Store inputs (contents, chunks ZIP), intermediate files, and final outputs |
| **Orchestration** | Azure Durable Functions | Stateful workflow: fan-out/fan-in pattern for parallel chunk processing |
| **Text Understanding** | Azure OpenAI (GPT-4/4o) | Semantic mapping of transcript→TOC, structured note generation, exam tips |
| **Summarization** | Azure AI Language (Extractive) | Extract key sentences for definitions and facts |
| **Queue Management** | Azure Queue Storage | Decouple chunk processing for resilience |
| **API Gateway** | Azure API Management (optional) | Expose endpoints for upload/download, rate limiting |

---

## Detailed Workflow

### Phase 1: Initialization (Contents Parsing)

```python
# Pseudocode for contents parsing
def parse_contents(contents_file: str) -> dict:
    """
    Parse TOC into hierarchical structure.
    Returns nested dict with heading levels starting at ##.
    """
    hierarchy = {}
    # Detect ## → top-level, ### → nested, #### → lowest-level sections
    # Return structure with timestamps and parent-child relationships
    return {
        "video_title": "...",
        "total_level2_sections": N,
        "total_lowest_level_sections": M,
        "hierarchy": [...]
    }
```

### Phase 2: Chunk Processing (Parallelized)

Each chunk is processed independently via Azure Durable Functions fan-out:

```python
# Azure Function: Process Single Chunk
async def process_chunk(chunk_id: int, chunk_text: str, hierarchy: dict):
    
    # 1. Call Azure OpenAI for semantic section mapping
    mapping_prompt = f"""
    Given this transcript chunk and the table of contents hierarchy,
    map each portion of the transcript to its corresponding lowest-level section.
    Transcript: {chunk_text}
    TOC: {hierarchy}
    Return JSON with section assignments.
    """
    section_mapping = await call_azure_openai(mapping_prompt)
    
    # 2. For each mapped section, generate structured notes
    for section in section_mapping:
        notes_prompt = f"""
        Create exam-focused notes for this section.
        Section: {section['title']}
        Content: {section['transcript_portion']}
        
        Format:
        ### {section['title']}
        **Timestamp**: [start] – [end]
        **Key Concepts** ...
        **Definitions** ...
        **Key Facts** ...
        **Examples** ...
        **Exam Tips 🎯** ...
        """
        markdown = await call_azure_openai(notes_prompt)
        save_to_blob(f"{section['order']}_{section['title']}__Part_{chunk_id}.md", markdown)
    
    # 3. Create ZIP and return SAS URL
    zip_url = create_chunk_zip(chunk_id)
    return zip_url
```

### Phase 3: Final Stitching

```python
# Stitch all section files into final document
def stitch_final_notes(uploaded_files: list, hierarchy: dict) -> str:
    """
    1. Group files by section
    2. Order by TOC hierarchy
    3. Rebuild heading structure (##, ###, ####)
    4. Merge content under correct parents
    """
    final_markdown = f"# {hierarchy['video_title']} - Complete Exam Notes\n\n"
    
    for level2_section in hierarchy['sections']:
        final_markdown += f"## {level2_section['title']}\n\n"
        for level3_section in level2_section['children']:
            final_markdown += f"### {level3_section['title']}\n\n"
            # ... continue for all levels
            final_markdown += merged_content
    
    return final_markdown
```

---

## Infrastructure as Code (Bicep Template)

```bicep name=exam-notes-infra.bicep
@description('Azure region for resources')
param location string = resourceGroup().location

@description('OpenAI deployment model')
param openAIModel string = 'gpt-4o'

// Storage Account
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'examnotes${uniqueString(resourceGroup().id)}'
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
  }
}

// Blob Containers
resource contentsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  name: '${storageAccount.name}/default/contents'
}

resource chunksContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  name: '${storageAccount.name}/default/chunks'
}

resource outputContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  name: '${storageAccount.name}/default/output'
}

// Azure OpenAI
resource openAI 'Microsoft.CognitiveServices/accounts@2023-10-01-preview' = {
  name: 'examnotes-openai'
  location: location
  kind: 'OpenAI'
  sku: { name: 'S0' }
  properties: {
    customSubDomainName: 'examnotes-openai-${uniqueString(resourceGroup().id)}'
  }
}

// Azure Language Service
resource languageService 'Microsoft.CognitiveServices/accounts@2023-10-01-preview' = {
  name: 'examnotes-language'
  location: location
  kind: 'TextAnalytics'
  sku: { name: 'S' }
}

// Function App (Durable Functions)
resource functionApp 'Microsoft.Web/sites@2023-01-01' = {
  name: 'examnotes-func-${uniqueString(resourceGroup().id)}'
  location: location
  kind: 'functionapp'
  properties: {
    siteConfig: {
      appSettings: [
        { name: 'AZURE_OPENAI_ENDPOINT', value: openAI.properties.endpoint }
        { name: 'AZURE_LANGUAGE_ENDPOINT', value: languageService.properties.endpoint }
        { name: 'STORAGE_CONNECTION', value: storageAccount.properties.primaryEndpoints.blob }
      ]
    }
  }
}
```

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Durable Functions fan-out/fan-in** | Enables parallel processing of 20KB chunks while maintaining state for final stitching |
| **Azure OpenAI for mapping** | Superior semantic understanding for aligning transcript text to TOC sections |
| **Per-chunk ZIP persistence** | Matches your stateless requirement—user downloads each ZIP as system of record |
| **Blob Storage with SAS URLs** | Secure, time-limited download links for each processing round |
| **Hierarchical heading preservation** | Parsing TOC into nested structure ensures `##`, `###`, `####` levels are correctly rebuilt |

---

## Cost Optimization Tips

1. **Use GPT-4o-mini** for initial mapping (cheaper), GPT-4o for final note generation
2. **Batch API calls** to Azure OpenAI where possible
3. **Use consumption plan** for Azure Functions (pay-per-execution)
4. **Archive processed chunks** to cool/archive tier after 7 days

---

Would you like me to:
1. **Generate the complete Azure Function code** (Python or C#) for this pipeline?
2. **Create a GitHub repository structure** with the implementation?
3. **Design the API contract** for upload/download endpoints?
4. **Build a detailed prompt engineering guide** for the exam notes generation?

## @Greg-T8

My concern here is when the orchestration layer stitches the transcript together, the total token size becomes so big that the model is unable to reason through it effectively. 

Instead, I want the model to process each 20kb chunk and produce notes, then have the model take all notes and stitch them together semantically according to the contents hierarchy.

## Copilot

You're absolutely right—that's a critical architectural insight. Feeding a massive stitched transcript to the model causes **context window saturation** and degrades reasoning quality. Your proposed approach is the correct pattern:

---

## Revised Architecture: Two-Stage AI Processing

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STAGE 1: CHUNK → NOTES                              │
│                    (Parallel, Independent Processing)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Chunk 1 (20KB)  ──→  Azure OpenAI  ──→  Notes_Part_01.md                 │
│   Chunk 2 (20KB)  ──→  Azure OpenAI  ──→  Notes_Part_02.md                 │
│   Chunk 3 (20KB)  ──→  Azure OpenAI  ──→  Notes_Part_03.md                 │
│        ...                                      ...                         │
│   Chunk N (20KB)  ──→  Azure OpenAI  ──→  Notes_Part_N.md                  │
│                                                                             │
│   Each chunk processed with FULL TOC context for section mapping            │
│   Output: Structured markdown with section assignments                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      STAGE 2: NOTES → FINAL DOCUMENT                        │
│                    (Semantic Stitching & Deduplication)                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   All Notes_Part_*.md  ──→  Group by Section  ──→  Azure OpenAI            │
│                                                                             │
│   For each lowest-level section:                                            │
│   ┌─────────────────────────────────────────────────────────────┐          │
│   │  Section "Configure VNets"                                   │          │
│   │  ├── Notes_Part_02.md (partial)                             │          │
│   │  ├── Notes_Part_03.md (partial)    ──→ MERGE & DEDUPE ──→   │          │
│   │  └── Notes_Part_04.md (partial)                             │          │
│   └─────────────────────────────────────────────────────────────┘          │
│                                                                             │
│   Output: One coherent section with no duplicates                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      STAGE 3: HIERARCHICAL ASSEMBLY                         │
│                         (Deterministic, No AI)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Rebuild TOC hierarchy:                                                    │
│   ## Section 1                                                              │
│   ### Subsection 1.1                                                        │
│   #### Topic 1.1.1  ← merged notes inserted here                           │
│   #### Topic 1.1.2  ← merged notes inserted here                           │
│                                                                             │
│   Output: [VideoTitle]_Complete_Exam_Notes.md                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Why This Works

| Problem with Monolithic Stitching | Solution in Two-Stage Approach |
|-----------------------------------|--------------------------------|
| Token limit exceeded | Each chunk stays within ~8K tokens |
| Model loses focus on later content | Fresh context per chunk |
| Redundant/overlapping content | Stage 2 deduplicates per-section |
| Poor section alignment | TOC provided to every chunk for consistent mapping |
| Hallucination under pressure | Smaller, focused prompts = higher accuracy |

---

## Detailed Stage Breakdown

### Stage 1: Chunk Processing (Parallel)

**Input per call:**
- 1 transcript chunk (~20KB ≈ 5-6K tokens)
- Full TOC hierarchy (typically <2K tokens)
- Processing instructions

**Prompt Template:**
```text
You are generating exam-focused study notes from a video transcript chunk.

## Table of Contents (Full Hierarchy)
{toc_hierarchy}

## Transcript Chunk {chunk_id} of {total_chunks}
Timestamps: {chunk_start} – {chunk_end}

{chunk_text}

## Instructions
1. Map each portion of this transcript to the appropriate lowest-level TOC section
2. For each section touched, generate notes in this format:

### [Section Title from TOC]
**Timestamp**: [first] – [last timestamp in this chunk for this section]
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

Rules:
- Only use ### for section titles
- Every word of transcript must be assigned to a section
- If content spans multiple sections, create separate note blocks
- Preserve technical accuracy
```

**Output:** `Notes_Part_{chunk_id}.md` containing 1+ section note blocks

---

### Stage 2: Section-Level Semantic Merge

**Process:** Group all partial notes by section, then merge intelligently.

```python
# Pseudocode
def merge_section_notes(section_title: str, partial_notes: list[str]) -> str:
    """
    Takes all note fragments for a single section across chunks.
    Returns one coherent, deduplicated section.
    """
    merge_prompt = f"""
You are merging multiple partial notes for the same exam topic into one coherent section.

## Section: {section_title}

## Partial Notes (from different transcript chunks):
{chr(10).join(partial_notes)}

## Instructions:
1. Combine all Key Concepts - remove exact duplicates, keep complementary details
2. Merge Definitions - deduplicate, keep the most complete version
3. Consolidate Key Facts - no redundancy, logical flow
4. Combine Examples - keep all unique examples
5. Merge Exam Tips - deduplicate, prioritize actionable tips
6. Update Timestamp to span full range: [earliest] – [latest]

Output the merged section in the standard format:
### {section_title}
**Timestamp**: ...
**Key Concepts** ...
(etc.)

Do NOT add new information. Only merge and deduplicate what's provided.
"""
    return call_azure_openai(merge_prompt)
```

**Token budget per merge call:**
- Section partials: ~2-8K tokens (depends on how many chunks touched this section)
- Instructions: ~500 tokens
- Well within GPT-4o's effective reasoning window

---

### Stage 3: Hierarchical Assembly (Deterministic)

**No AI needed here**—pure programmatic assembly:

```python
def assemble_final_document(toc_hierarchy: dict, merged_sections: dict) -> str:
    """
    Reconstructs the full document with proper heading levels.
    """
    output = f"# {toc_hierarchy['video_title']} - Complete Exam Notes\n\n"
    
    for section in toc_hierarchy['sections']:
        output += build_section_recursive(section, merged_sections, level=2)
    
    return output

def build_section_recursive(section: dict, merged_sections: dict, level: int) -> str:
    heading_prefix = "#" * level
    output = ""
    
    if section.get('children'):
        # Parent section - just add heading, recurse into children
        output += f"{heading_prefix} {section['title']}\n\n"
        for child in section['children']:
            output += build_section_recursive(child, merged_sections, level + 1)
    else:
        # Lowest-level section - insert merged notes (already has ### heading)
        if section['title'] in merged_sections:
            # Replace ### with correct level
            notes = merged_sections[section['title']]
            notes = notes.replace(f"### {section['title']}", 
                                  f"{heading_prefix} {section['title']}")
            output += notes + "\n\n"
    
    return output
```

---

## Updated Data Flow

```
                    ┌──────────────────┐
                    │  Contents File   │
                    │  (TOC + Times)   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Parse Hierarchy │ ──→ {sections: [{title, children, ...}]}
                    └────────┬─────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
   ┌───────────┐       ┌───────────┐       ┌───────────┐
   │  Chunk 1  │       │  Chunk 2  │       │  Chunk N  │
   └─────┬─────┘       └─────┬─────┘       └─────┬─────┘
         │                   │                   │
         ▼                   ▼                   ▼
   ┌───────────┐       ┌───────────┐       ┌───────────┐
   │ GPT-4o    │       │ GPT-4o    │       │ GPT-4o    │
   │ +TOC      │       │ +TOC      │       │ +TOC      │
   └─────┬─────┘       └─────┬─────┘       └─────┬─────┘
         │                   │                   │
         ▼                   ▼                   ▼
   Notes_Part_1.md    Notes_Part_2.md    Notes_Part_N.md
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Group by Section │
                    └────────┬─────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
   Section A parts    Section B parts    Section M parts
         │                   │                   │
         ▼                   ▼                   ▼
   ┌───────────┐       ┌───────────┐       ┌───────────┐
   │ GPT-4o    │       │ GPT-4o    │       │ GPT-4o    │
   │ MERGE     │       │ MERGE     │       │ MERGE     │
   └─────┬─────┘       └─────┬─────┘       └─────┬─────┘
         │                   │                   │
         ▼                   ▼                   ▼
   Section_A.md       Section_B.md       Section_M.md
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Assemble Final   │  (Deterministic)
                    │ with Hierarchy   │
                    └────────┬─────────┘
                             │
                             ▼
              Complete_Exam_Notes.md
```

---

## Azure Implementation

```python name=durable_orchestrator.py
import azure.functions as func
import azure.durable_functions as df

# Orchestrator: Two-stage processing
@df.orchestrator_trigger(context_name="context")
def orchestrate_exam_notes(context: df.DurableOrchestrationContext):
    input_data = context.get_input()
    toc_hierarchy = input_data["toc_hierarchy"]
    chunk_blob_urls = input_data["chunk_blob_urls"]
    
    # ═══════════════════════════════════════════════════════════
    # STAGE 1: Process chunks in parallel (fan-out)
    # ═══════════════════════════════════════════════════════════
    chunk_tasks = []
    for i, chunk_url in enumerate(chunk_blob_urls):
        task = context.call_activity("process_chunk", {
            "chunk_id": i + 1,
            "total_chunks": len(chunk_blob_urls),
            "chunk_url": chunk_url,
            "toc_hierarchy": toc_hierarchy
        })
        chunk_tasks.append(task)
    
    # Wait for all chunks to complete
    chunk_notes = yield context.task_all(chunk_tasks)
    # chunk_notes = [{"sections": {"Section A": "...", "Section B": "..."}}, ...]
    
    # ═══════════════════════════════════════════════════════════
    # STAGE 2: Group by section, merge in parallel (fan-out)
    # ═══════════════════════════════════════════════════════════
    section_partials = group_notes_by_section(chunk_notes)
    # section_partials = {"Section A": [part1, part2], "Section B": [part1], ...}
    
    merge_tasks = []
    for section_title, partials in section_partials.items():
        if len(partials) == 1:
            # No merge needed, single source
            merge_tasks.append(context.call_activity("passthrough", {
                "section_title": section_title,
                "content": partials[0]
            }))
        else:
            # Multiple partials, need AI merge
            merge_tasks.append(context.call_activity("merge_section", {
                "section_title": section_title,
                "partials": partials
            }))
    
    merged_sections = yield context.task_all(merge_tasks)
    # merged_sections = [{"title": "Section A", "content": "..."}, ...]
    
    # ═══════════════════════════════════════════════════════════
    # STAGE 3: Assemble final document (deterministic, no AI)
    # ═══════════════════════════════════════════════════════════
    final_doc = yield context.call_activity("assemble_document", {
        "toc_hierarchy": toc_hierarchy,
        "merged_sections": {s["title"]: s["content"] for s in merged_sections}
    })
    
    return final_doc  # URL to final markdown file


def group_notes_by_section(chunk_notes: list) -> dict:
    """Group all partial notes by section title."""
    section_partials = {}
    for chunk_result in chunk_notes:
        for section_title, content in chunk_result["sections"].items():
            if section_title not in section_partials:
                section_partials[section_title] = []
            section_partials[section_title].append(content)
    return section_partials
```

---

## Token Budget Analysis

| Stage | Input Tokens | Output Tokens | Calls |
|-------|--------------|---------------|-------|
| **Stage 1** (per chunk) | ~6K (chunk) + ~2K (TOC) = **8K** | ~2-4K notes | N chunks |
| **Stage 2** (per section) | ~2-8K partials + ~500 instructions | ~1-3K merged | M sections |
| **Stage 3** | N/A (deterministic) | N/A | 1 |

**Example:** 20 chunks × 50 sections
- Stage 1: 20 API calls @ 8K input each
- Stage 2: 50 API calls @ ~3K input each (many sections only touched by 1-2 chunks)
- Total: 70 API calls, all within optimal reasoning window ✓

---

Would you like me to:
1. **Build the complete Azure Functions project** with all activities?
2. **Design the section-merge prompt** with edge case handling (overlapping timestamps, contradictions)?
3. **Create a cost estimation calculator** based on chunk count and section count?

## @Greg-T8

Design the section-merge prompt with edge case handling.

## Copilot

## Section-Merge Prompt Design

This prompt handles the critical Stage 2 operation: merging multiple partial notes for the same section into one coherent, deduplicated result.

---

### Core Merge Prompt

```text name=section_merge_prompt.txt
You are an expert exam study guide editor. Your task is to merge multiple partial notes for the same exam topic into ONE coherent, comprehensive section.

## Section Title
{section_title}

## Source Partial Notes
The following notes were extracted from different portions of a video transcript. They cover the same topic but may have:
- Overlapping content (duplicates)
- Complementary details (unique to each partial)
- Slightly different phrasing of the same concept
- Timestamp gaps or overlaps

---
### Partial 1 of {total_partials}
**Source Chunk**: {chunk_id_1}
{partial_notes_1}

---
### Partial 2 of {total_partials}
**Source Chunk**: {chunk_id_2}
{partial_notes_2}

---
{additional_partials_if_any}

## Merge Instructions

### 1. Timestamp Handling
- Extract all timestamps from partials
- Final timestamp range: [earliest start] – [latest end]
- If timestamps overlap, this is normal (chunk boundaries don't align with topic boundaries)
- If there's a gap > 5 minutes between partials, note it as "(continued at [timestamp])" in the content

### 2. Key Concepts
- Combine all bullet points across partials
- REMOVE exact duplicates (identical phrasing)
- KEEP near-duplicates if they add nuance (merge into one refined bullet)
- Preserve technical accuracy—do not simplify or generalize
- Order logically: foundational concepts first, advanced concepts later

### 3. Definitions
- If the same term is defined multiple times:
  - Keep the MOST COMPLETE definition
  - If definitions conflict, include both with clarification: "(also described as: ...)"
- If a definition in one partial is incomplete, supplement with details from another

### 4. Key Facts
- Remove redundant facts (same information, different words)
- Keep all UNIQUE facts
- If facts appear to contradict:
  - Check if they apply to different contexts (e.g., "default is X" vs "when configured, default is Y")
  - If true contradiction, flag with: "⚠️ Note: Source mentions both X and Y—verify current behavior"
- Order chronologically or by dependency (prerequisite facts first)

### 5. Examples
- Keep ALL unique examples (examples are high-value for exams)
- Remove only exact duplicate examples
- If the same scenario is explained differently, keep the clearer version
- Preserve code snippets, CLI commands, and configuration samples exactly

### 6. Exam Tips 🎯
- Combine all tips, remove duplicates
- Prioritize actionable tips ("Remember to..." > "This is important")
- If tips conflict, keep both with context
- Consolidate similar tips into stronger combined tips

### 7. Content NOT in Partials
- Do NOT add information not present in the source partials
- Do NOT infer or expand beyond what's provided
- Do NOT add generic study advice not specific to this section

## Output Format

Produce exactly this structure:

### {section_title}
**Timestamp**: [earliest] – [latest]

**Key Concepts**
- [merged bullets]

**Definitions**
- **[Term]**: [merged definition]

**Key Facts**
- [merged facts]

**Examples**
- [all unique examples]

**Exam Tips 🎯**
- [merged tips]

## Edge Case Handling

| Situation | Action |
|-----------|--------|
| Only 1 partial provided | Return it unchanged (no merge needed) |
| Empty section in a partial | Omit that section, use content from other partials |
| All partials empty for a subsection | Omit that subsection entirely |
| Conflicting technical details | Include both with ⚠️ flag |
| Same example, different detail level | Keep the more detailed version |
| Timestamps out of order | Sort chronologically, note if non-linear |

Now merge the partials above into a single cohesive section.
```

---

### Edge Case Prompt Variations

#### Edge Case 1: Single Partial (No Merge Needed)

```text name=single_partial_prompt.txt
You are validating a single set of notes for an exam topic. No merge is required.

## Section Title
{section_title}

## Notes
{partial_notes}

## Instructions
1. Verify the format matches the required structure
2. Fix any formatting inconsistencies (heading levels, bold markers)
3. Return the notes unchanged in content, corrected in format only

Output the validated section.
```

---

#### Edge Case 2: Large Gap Between Partials

When partials have timestamp gaps > 5 minutes, the topic was likely revisited later in the video:

```text name=gap_handling_prompt.txt
## Special Handling: Non-Contiguous Content

The partials below have a significant timestamp gap, indicating the instructor returned to this topic later in the video.

### Partial 1
**Timestamps**: 05:30 – 08:45
{partial_1}

### Partial 2
**Timestamps**: 45:20 – 48:10
{partial_2}

## Additional Instructions
- Merge as normal, but add a note at the start:
  "📝 This topic is covered in two parts: [05:30–08:45] and [45:20–48:10]"
- If Partial 2 adds corrections or updates to Partial 1, clearly indicate:
  "**Update**: Later in the video, the instructor clarified that..."
- Do not artificially blend content that was intentionally separated
```

---

#### Edge Case 3: Conflicting Information

```text name=conflict_handling_prompt.txt
## Special Handling: Potential Conflicts Detected

Pre-analysis has flagged potential conflicts in these partials. Apply extra scrutiny.

### Partial 1 (Chunk 3)
{partial_1}

### Partial 2 (Chunk 7)
{partial_2}

## Conflict Resolution Rules

1. **Version/Date Conflicts**
   - If one partial mentions a version and another doesn't, keep the versioned info
   - Example: "In Azure CLI 2.50+" vs general statement → keep version-specific

2. **Default Value Conflicts**
   - Often context-dependent: "default is X" (portal) vs "default is Y" (CLI)
   - Merge as: "Default: X (portal), Y (CLI)" or flag for verification

3. **Behavioral Conflicts**
   - If instructor corrects themselves later: "**Correction**: Initially stated X, but later clarified Y"
   - If genuinely conflicting with no resolution: flag with ⚠️

4. **Terminology Conflicts**
   - Same concept, different names: include both as aliases
   - Example: "Storage Account (also called: storage resource, blob account)"

Apply these rules and merge, flagging any unresolved conflicts.
```

---

#### Edge Case 4: Heavily Overlapping Partials

When chunk boundaries fall mid-sentence, creating significant overlap:

```text name=overlap_handling_prompt.txt
## Special Handling: High Overlap Detected

These partials have ~{overlap_percentage}% content overlap due to chunk boundary placement.

### Partial 1 (Chunk 4)
**Timestamps**: 12:00 – 15:30
{partial_1}

### Partial 2 (Chunk 5)
**Timestamps**: 14:45 – 18:20
{partial_2}

## Overlap Resolution Rules

1. For overlapping timestamp ranges (14:45–15:30 in this case):
   - Content in this range may appear in both partials
   - Deduplicate aggressively—keep ONE version of each point

2. If the same bullet appears twice with minor wording differences:
   - Choose the more precise/complete version
   - Do NOT create two similar bullets

3. Timestamp output should be: 12:00 – 18:20 (full span, no gap notation)

Merge with aggressive deduplication.
```

---

### Python Implementation

```python name=merge_section.py
from enum import Enum
from dataclasses import dataclass
from openai import AzureOpenAI

class MergeScenario(Enum):
    SINGLE_PARTIAL = "single"
    STANDARD_MERGE = "standard"
    LARGE_GAP = "gap"
    HIGH_OVERLAP = "overlap"
    CONFLICT_DETECTED = "conflict"

@dataclass
class PartialNotes:
    chunk_id: int
    timestamp_start: str
    timestamp_end: str
    content: str

@dataclass
class MergeAnalysis:
    scenario: MergeScenario
    overlap_percentage: float
    gap_minutes: float
    potential_conflicts: list[str]

def analyze_partials(partials: list[PartialNotes]) -> MergeAnalysis:
    """Pre-analyze partials to determine merge scenario and edge cases."""
    
    if len(partials) == 1:
        return MergeAnalysis(
            scenario=MergeScenario.SINGLE_PARTIAL,
            overlap_percentage=0,
            gap_minutes=0,
            potential_conflicts=[]
        )
    
    # Calculate timestamp gaps and overlaps
    gaps = []
    overlaps = []
    for i in range(len(partials) - 1):
        current_end = parse_timestamp(partials[i].timestamp_end)
        next_start = parse_timestamp(partials[i + 1].timestamp_start)
        diff = next_start - current_end
        if diff > 0:
            gaps.append(diff)
        else:
            overlaps.append(abs(diff))
    
    max_gap = max(gaps) if gaps else 0
    overlap_pct = calculate_content_overlap(partials)
    conflicts = detect_potential_conflicts(partials)
    
    # Determine scenario
    if conflicts:
        scenario = MergeScenario.CONFLICT_DETECTED
    elif max_gap > 300:  # > 5 minutes
        scenario = MergeScenario.LARGE_GAP
    elif overlap_pct > 40:
        scenario = MergeScenario.HIGH_OVERLAP
    else:
        scenario = MergeScenario.STANDARD_MERGE
    
    return MergeAnalysis(
        scenario=scenario,
        overlap_percentage=overlap_pct,
        gap_minutes=max_gap / 60,
        potential_conflicts=conflicts
    )

def detect_potential_conflicts(partials: list[PartialNotes]) -> list[str]:
    """Detect potential conflicts using keyword patterns."""
    conflict_patterns = [
        (r"default\s+is\s+(\w+)", "default value"),
        (r"always\s+(\w+)", "absolute statement"),
        (r"never\s+(\w+)", "absolute statement"),
        (r"must\s+be\s+(\w+)", "requirement"),
        (r"requires?\s+(\w+)", "requirement"),
        (r"(\d+)\s*(GB|MB|minutes|seconds|hours)", "numeric value"),
    ]
    
    conflicts = []
    all_matches = {pattern: [] for pattern, _ in conflict_patterns}
    
    for partial in partials:
        for pattern, category in conflict_patterns:
            matches = re.findall(pattern, partial.content, re.IGNORECASE)
            all_matches[(pattern, category)].extend(matches)
    
    for (pattern, category), matches in all_matches.items():
        unique_values = set(str(m).lower() for m in matches)
        if len(unique_values) > 1:
            conflicts.append(f"{category}: found varying values {unique_values}")
    
    return conflicts

def build_merge_prompt(
    section_title: str,
    partials: list[PartialNotes],
    analysis: MergeAnalysis
) -> str:
    """Build the appropriate merge prompt based on analysis."""
    
    # Load base prompt
    base_prompt = load_prompt_template("section_merge_prompt.txt")
    
    # Format partials
    partials_text = ""
    for i, partial in enumerate(partials, 1):
        partials_text += f"""
---
### Partial {i} of {len(partials)}
**Source Chunk**: {partial.chunk_id}
**Timestamps**: {partial.timestamp_start} – {partial.timestamp_end}

{partial.content}
"""
    
    # Add scenario-specific instructions
    scenario_additions = ""
    
    if analysis.scenario == MergeScenario.SINGLE_PARTIAL:
        return load_prompt_template("single_partial_prompt.txt").format(
            section_title=section_title,
            partial_notes=partials[0].content
        )
    
    elif analysis.scenario == MergeScenario.LARGE_GAP:
        scenario_additions = f"""
## ⚠️ Special Handling: Non-Contiguous Content
Detected timestamp gap of {analysis.gap_minutes:.1f} minutes between partials.
The instructor returned to this topic later. 
Add a note indicating the split and check for updates/corrections in later partials.
"""
    
    elif analysis.scenario == MergeScenario.HIGH_OVERLAP:
        scenario_additions = f"""
## ⚠️ Special Handling: High Overlap ({analysis.overlap_percentage:.0f}%)
Chunk boundaries caused significant content duplication.
Apply aggressive deduplication—keep only ONE version of repeated points.
"""
    
    elif analysis.scenario == MergeScenario.CONFLICT_DETECTED:
        conflict_list = "\n".join(f"- {c}" for c in analysis.potential_conflicts)
        scenario_additions = f"""
## ⚠️ Special Handling: Potential Conflicts Detected
Pre-analysis flagged these potential inconsistencies:
{conflict_list}

Apply conflict resolution rules carefully. Flag unresolved conflicts with ⚠️.
"""
    
    # Assemble final prompt
    return base_prompt.format(
        section_title=section_title,
        total_partials=len(partials),
        partial_notes_formatted=partials_text,
        scenario_additions=scenario_additions
    )

async def merge_section(
    section_title: str,
    partials: list[PartialNotes],
    client: AzureOpenAI
) -> str:
    """Execute the merge operation with appropriate prompt."""
    
    # Analyze partials
    analysis = analyze_partials(partials)
    
    # Build prompt
    prompt = build_merge_prompt(section_title, partials, analysis)
    
    # Call Azure OpenAI
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an expert exam study guide editor specializing in technical certification content."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        temperature=0.3,  # Lower temperature for consistent, accurate merges
        max_tokens=4000
    )
    
    merged_content = response.choices[0].message.content
    
    # Validate output structure
    if not validate_section_format(merged_content, section_title):
        # Retry with format correction prompt
        merged_content = await fix_format(merged_content, section_title, client)
    
    return merged_content

def validate_section_format(content: str, expected_title: str) -> bool:
    """Validate merged content has required structure."""
    required_elements = [
        f"### {expected_title}",
        "**Timestamp**:",
        "**Key Concepts**",
        "**Definitions**",
        "**Key Facts**",
        "**Examples**",
        "**Exam Tips 🎯**"
    ]
    return all(elem in content for elem in required_elements)
```

---

### Validation & Quality Checks

```python name=merge_validation.py
@dataclass
class MergeQualityReport:
    section_title: str
    input_bullet_count: int
    output_bullet_count: int
    dedup_ratio: float
    has_conflicts_flagged: bool
    timestamp_valid: bool
    all_sections_present: bool
    warnings: list[str]

def validate_merge_quality(
    partials: list[PartialNotes],
    merged_output: str
) -> MergeQualityReport:
    """Post-merge validation to ensure quality."""
    
    warnings = []
    
    # Count bullets in vs out
    input_bullets = sum(
        len(re.findall(r"^- ", p.content, re.MULTILINE)) 
        for p in partials
    )
    output_bullets = len(re.findall(r"^- ", merged_output, re.MULTILINE))
    
    dedup_ratio = 1 - (output_bullets / input_bullets) if input_bullets > 0 else 0
    
    # Check for over-deduplication (lost content)
    if dedup_ratio > 0.7:
        warnings.append(f"High dedup ratio ({dedup_ratio:.0%})—verify no content lost")
    
    # Check for under-deduplication (too much redundancy)
    if dedup_ratio < 0.1 and len(partials) > 1:
        warnings.append("Low dedup ratio—possible redundant content remaining")
    
    # Verify timestamps
    timestamps = re.search(r"\*\*Timestamp\*\*:\s*(.+?)(?:\n|$)", merged_output)
    timestamp_valid = bool(timestamps and "–" in timestamps.group(1))
    
    # Check all sections present
    required_sections = [
        "Key Concepts", "Definitions", "Key Facts", "Examples", "Exam Tips"
    ]
    all_present = all(s in merged_output for s in required_sections)
    
    # Check for conflict flags
    has_conflicts = "⚠️" in merged_output
    
    return MergeQualityReport(
        section_title=extract_section_title(merged_output),
        input_bullet_count=input_bullets,
        output_bullet_count=output_bullets,
        dedup_ratio=dedup_ratio,
        has_conflicts_flagged=has_conflicts,
        timestamp_valid=timestamp_valid,
        all_sections_present=all_present,
        warnings=warnings
    )
```

---

### Example: Merge in Action

**Input Partials:**

```markdown
# Partial 1 (Chunk 3)
### Configure Virtual Networks
**Timestamp**: 12:30 – 15:45

**Key Concepts**
- VNets provide network isolation in Azure
- Subnets divide VNets into smaller segments
- VNets are region-specific

**Definitions**
- **VNet**: A logically isolated network in Azure

**Key Facts**
- Default address space: 10.0.0.0/16
- Maximum 50 VNets per subscription

**Examples**
- Create VNet via portal: Networking > Virtual Networks > Create

**Exam Tips 🎯**
- Remember VNets cannot span regions
```

```markdown
# Partial 2 (Chunk 4)
### Configure Virtual Networks
**Timestamp**: 15:30 – 18:20

**Key Concepts**
- VNets are region-specific and cannot span regions
- Peering connects VNets across regions
- Network Security Groups filter traffic

**Definitions**
- **VNet**: An isolated network environment in Azure cloud
- **Peering**: Connection between two VNets

**Key Facts**
- Maximum 500 VNets per subscription (increased limit)
- Peering is non-transitive

**Examples**
- Create VNet via CLI: `az network vnet create --name MyVNet`

**Exam Tips 🎯**
- VNets cannot span regions—use peering instead
- Know the difference between local and global peering
```

**Merged Output:**

```markdown
### Configure Virtual Networks
**Timestamp**: 12:30 – 18:20

**Key Concepts**
- VNets provide network isolation in Azure
- Subnets divide VNets into smaller segments
- VNets are region-specific and cannot span regions
- Peering connects VNets across regions (local or global)
- Network Security Groups (NSGs) filter traffic at subnet/NIC level

**Definitions**
- **VNet**: A logically isolated network environment in Azure cloud
- **Peering**: Non-transitive connection between two VNets

**Key Facts**
- Default address space: 10.0.0.0/16
- ⚠️ Note: Maximum VNets per subscription mentioned as both 50 and 500—verify current limits (likely 500 with quota increase)
- Peering is non-transitive (A↔B and B↔C does not mean A↔C)

**Examples**
- Create VNet via portal: Networking > Virtual Networks > Create
- Create VNet via CLI: `az network vnet create --name MyVNet --resource-group MyRG --address-prefix 10.0.0.0/16`

**Exam Tips 🎯**
- Remember VNets cannot span regions—use peering for cross-region connectivity
- Know the difference between local peering (same region) and global peering (cross-region)
- Peering is non-transitive—this is a common exam question
```

---

Would you like me to:
1. **Build the complete Azure Function activity** that wraps this merge logic?
2. **Design the Stage 1 chunk-processing prompt** with similar rigor?
3. **Create a test suite** with sample partials covering all edge cases?

## @Greg-T8

Create a high-level implementation plan for this.

## Copilot

## High-Level Implementation Plan: Hierarchical Exam Notes Generator

---

### Executive Summary

Build an Azure-native pipeline that transforms video transcripts into structured exam study notes. The system processes content in two AI stages (chunk→notes, notes→merged sections) followed by deterministic assembly, ensuring high-quality output without context window limitations.

**Timeline**: 6-8 weeks | **Team**: 2-3 engineers | **Azure Monthly Cost**: ~$150-400 (variable with usage)

---

## Phase 1: Foundation (Week 1-2)

### 1.1 Azure Infrastructure Setup

| Resource | Purpose | Configuration |
|----------|---------|---------------|
| Resource Group | Container for all resources | `rg-exam-notes-{env}` |
| Storage Account | Blob storage for files | Standard LRS, Hot tier |
| Azure OpenAI | GPT-4o for note generation | East US 2 (or available region) |
| Function App | Durable Functions orchestration | Consumption plan, Python 3.11 |
| Application Insights | Monitoring & logging | Connected to Function App |
| Key Vault | Secrets management | API keys, connection strings |

**Blob Containers:**
```
├── inputs/
│   ├── contents/          # TOC files
│   └── transcripts/       # Uploaded ZIPs
├── processing/
│   ├── chunks/            # Extracted 20KB chunks
│   ├── chunk-notes/       # Stage 1 output
│   └── section-partials/  # Grouped by section
├── outputs/
│   ├── merged-sections/   # Stage 2 output
│   └── final/             # Complete notes
└── archive/               # Processed jobs (cool tier)
```

### 1.2 Development Environment

- [ ] Create GitHub repository with branch protection
- [ ] Set up Azure Developer CLI (azd) for infrastructure deployment
- [ ] Configure GitHub Actions for CI/CD
- [ ] Establish local development environment with Azurite emulator
- [ ] Create shared library for prompt templates

### 1.3 Deliverables

- [ ] Bicep/Terraform templates for all infrastructure
- [ ] Local development guide
- [ ] Architecture decision records (ADRs)

---

## Phase 2: Core Processing Engine (Week 2-4)

### 2.1 Contents Parser Module

**Input**: Markdown or text file with timestamped headings
**Output**: Hierarchical JSON structure

```python
# Target output structure
{
  "video_title": "AZ-104 Module 5",
  "total_duration": "02:45:30",
  "hierarchy": [
    {
      "level": 2,
      "title": "Configure Virtual Networks",
      "timestamp_start": "00:00:00",
      "children": [
        {
          "level": 3,
          "title": "VNet Fundamentals",
          "timestamp_start": "00:00:00",
          "children": [
            {
              "level": 4,
              "title": "Address Spaces",
              "timestamp_start": "00:02:30",
              "timestamp_end": "00:08:45",
              "is_leaf": true
            }
          ]
        }
      ]
    }
  ]
}
```

**Tasks:**
- [ ] Build regex-based heading parser (##, ###, ####)
- [ ] Implement timestamp extraction (multiple formats)
- [ ] Create hierarchy builder with parent-child linking
- [ ] Add validation for missing timestamps, orphan sections

### 2.2 Chunk Processor (Stage 1)

**Durable Function Activity**: `process_chunk`

```
Input:  chunk_id, chunk_text, toc_hierarchy
Output: {section_title: notes_markdown, ...}
```

**Tasks:**
- [ ] Design chunk processing prompt (with TOC context)
- [ ] Implement Azure OpenAI client with retry logic
- [ ] Build section extractor from model response
- [ ] Create output validation (required sections present)
- [ ] Add per-chunk ZIP generation for user downloads

### 2.3 Section Merger (Stage 2)

**Durable Function Activity**: `merge_section`

```
Input:  section_title, list[partial_notes]
Output: merged_notes_markdown
```

**Tasks:**
- [ ] Implement partial analyzer (detect scenario: gap, overlap, conflict)
- [ ] Build prompt selector based on scenario
- [ ] Create merge executor with quality validation
- [ ] Add conflict flagging and resolution logic
- [ ] Implement deduplication ratio checks

### 2.4 Document Assembler (Stage 3)

**Pure Python function** (no AI):

```
Input:  toc_hierarchy, dict[section_title: merged_notes]
Output: complete_markdown_document
```

**Tasks:**
- [ ] Build recursive heading writer
- [ ] Implement heading level adjustment (### → proper level)
- [ ] Add table of contents generation
- [ ] Create final document validation

---

## Phase 3: Orchestration Layer (Week 4-5)

### 3.1 Durable Functions Orchestrator

```
┌─────────────────────────────────────────────────────────────────┐
│                    Main Orchestrator                            │
├─────────────────────────────────────────────────────────────────┤
│  1. Receive job request (contents + transcript ZIP)            │
│  2. Call: parse_contents → hierarchy                            │
│  3. Call: extract_chunks → chunk_urls[]                         │
│  4. Fan-out: process_chunk[] → chunk_notes[]                    │
│  5. Call: group_by_section → section_partials{}                 │
│  6. Fan-out: merge_section[] → merged_sections[]                │
│  7. Call: assemble_document → final_url                         │
│  8. Return: job_result with download URLs                       │
└─────────────────────────────────────────────────────────────────┘
```

**Tasks:**
- [ ] Implement orchestrator with error handling
- [ ] Add checkpoint/resume for long-running jobs
- [ ] Create sub-orchestrator for Stage 1 (chunk processing)
- [ ] Create sub-orchestrator for Stage 2 (section merging)
- [ ] Implement progress tracking and status updates

### 3.2 Job Management

**Tasks:**
- [ ] Design job status model (queued, processing, stage1, stage2, complete, failed)
- [ ] Implement job status API endpoint
- [ ] Add job cancellation support
- [ ] Create job cleanup (archive after 7 days)

---

## Phase 4: API & Integration Layer (Week 5-6)

### 4.1 HTTP Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/jobs` | POST | Create new processing job |
| `/jobs/{id}` | GET | Get job status and results |
| `/jobs/{id}/cancel` | POST | Cancel in-progress job |
| `/upload/contents` | POST | Upload TOC file |
| `/upload/transcript` | POST | Upload transcript ZIP |
| `/download/{blob_path}` | GET | Get SAS URL for download |

### 4.2 Request/Response Models

```python
# Job creation request
class CreateJobRequest:
    contents_blob_url: str
    transcript_zip_blob_url: str
    options: ProcessingOptions

class ProcessingOptions:
    generate_chunk_zips: bool = True  # Per-chunk downloads
    include_timestamps: bool = True
    exam_focus_level: str = "high"    # high, medium, low

# Job status response
class JobStatusResponse:
    job_id: str
    status: str
    progress: ProgressInfo
    stage1_results: list[ChunkResult] | None
    stage2_results: list[SectionResult] | None
    final_document_url: str | None
    errors: list[str]

class ProgressInfo:
    current_stage: int  # 1, 2, or 3
    chunks_processed: int
    chunks_total: int
    sections_merged: int
    sections_total: int
```

### 4.3 Tasks

- [ ] Implement FastAPI/Flask HTTP triggers
- [ ] Add request validation with Pydantic
- [ ] Create SAS URL generator for secure downloads
- [ ] Implement CORS for web client access
- [ ] Add API key authentication

---

## Phase 5: Prompt Engineering & Tuning (Week 6-7)

### 5.1 Prompt Library

| Prompt | Purpose | Variables |
|--------|---------|-----------|
| `chunk_process.txt` | Stage 1: Extract notes from chunk | chunk_text, toc, chunk_id |
| `section_merge_standard.txt` | Stage 2: Standard merge | section_title, partials[] |
| `section_merge_gap.txt` | Stage 2: Handle timestamp gaps | section_title, partials[], gap_info |
| `section_merge_conflict.txt` | Stage 2: Resolve conflicts | section_title, partials[], conflicts[] |
| `format_fix.txt` | Correct malformed output | content, expected_format |

### 5.2 Prompt Versioning

```
prompts/
├── v1/
│   ├── chunk_process.txt
│   ├── section_merge_standard.txt
│   └── ...
├── v2/
│   └── ...
└── active/ → symlink to current version
```

### 5.3 Tasks

- [ ] Finalize all prompt templates
- [ ] Create prompt testing harness with sample inputs
- [ ] Tune temperature and token limits per prompt
- [ ] Build A/B testing framework for prompt comparison
- [ ] Document prompt design decisions

---

## Phase 6: Testing & Quality Assurance (Week 7-8)

### 6.1 Test Categories

| Category | Scope | Tools |
|----------|-------|-------|
| Unit Tests | Parsers, validators, utilities | pytest |
| Integration Tests | Azure service interactions | pytest + Azurite |
| E2E Tests | Full pipeline execution | pytest + real Azure |
| Prompt Tests | Output quality validation | Custom harness |
| Load Tests | Concurrent job handling | Locust |

### 6.2 Test Data

- [ ] Create 5 sample contents files (varying complexity)
- [ ] Prepare 3 transcript ZIPs (small: 5 chunks, medium: 20 chunks, large: 50 chunks)
- [ ] Build expected output baselines for comparison
- [ ] Generate edge case samples (gaps, overlaps, conflicts)

### 6.3 Quality Gates

| Metric | Target | Measurement |
|--------|--------|-------------|
| Section coverage | 100% | All TOC sections present in output |
| Content preservation | >95% | Key terms from transcript in notes |
| Deduplication | 20-50% | Bullet reduction ratio |
| Format compliance | 100% | All required sections present |
| Processing time | <5 min | For 20-chunk transcript |

### 6.4 Tasks

- [ ] Write unit tests for all modules (>80% coverage)
- [ ] Create integration test suite
- [ ] Build automated quality scoring for outputs
- [ ] Set up CI pipeline with test gates
- [ ] Document manual QA checklist

---

## Phase 7: Deployment & Operations (Week 8+)

### 7.1 Environments

| Environment | Purpose | Azure Subscription |
|-------------|---------|-------------------|
| dev | Development & testing | Dev subscription |
| staging | Pre-production validation | Prod subscription |
| prod | Production workloads | Prod subscription |

### 7.2 CI/CD Pipeline

```yaml
# Simplified GitHub Actions workflow
stages:
  - lint-and-test:
      - ruff check
      - pytest unit tests
      - pytest integration tests (Azurite)
  
  - build:
      - package function app
      - upload artifacts
  
  - deploy-dev:
      - azd deploy --environment dev
      - run smoke tests
  
  - deploy-staging:
      - requires: approval
      - azd deploy --environment staging
      - run E2E tests
  
  - deploy-prod:
      - requires: approval + staging success
      - azd deploy --environment prod
      - run smoke tests
```

### 7.3 Monitoring & Alerting

| Metric | Alert Threshold | Action |
|--------|-----------------|--------|
| Job failure rate | >5% in 1 hour | Page on-call |
| Processing time | >10 min avg | Investigate bottleneck |
| OpenAI errors | >10 in 5 min | Check quota/rate limits |
| Storage errors | Any | Check connectivity |

### 7.4 Tasks

- [ ] Create deployment scripts (azd or GitHub Actions)
- [ ] Set up Application Insights dashboards
- [ ] Configure alerts in Azure Monitor
- [ ] Write runbook for common issues
- [ ] Create cost monitoring dashboard

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| OpenAI rate limits | Job delays/failures | Implement exponential backoff, queue management |
| Large transcript (100+ chunks) | Timeout, cost overrun | Add job size limits, chunked billing estimates |
| Prompt injection in transcript | Malformed output | Input sanitization, output validation |
| Azure region outage | Complete service disruption | Multi-region deployment (Phase 2) |
| Cost overrun | Budget exceeded | Daily cost alerts, job quotas per user |

---

## Cost Estimate (Monthly)

| Resource | Configuration | Estimated Cost |
|----------|---------------|----------------|
| Azure OpenAI (GPT-4o) | ~2M tokens/month | $60-120 |
| Storage Account | 50GB + transactions | $5-10 |
| Function App | Consumption plan | $20-50 |
| Application Insights | Basic logging | $10-20 |
| Key Vault | Standard | $1 |
| **Total** | | **$96-201** |

*Scales with usage. Heavy usage (1000+ jobs/month) may reach $400+.*

---

## Success Criteria

| Milestone | Criteria | Target Date |
|-----------|----------|-------------|
| MVP | Process single transcript end-to-end | Week 4 |
| Beta | API endpoints, 90% test coverage | Week 6 |
| Production | Deployed, monitored, documented | Week 8 |

---

## Next Steps

1. **Immediate**: Provision Azure resources, set up repository
2. **This week**: Build contents parser and chunk processor
3. **Review point**: End of Week 2—demo Stage 1 processing

Would you like me to:
1. **Generate the Bicep templates** for Phase 1 infrastructure?
2. **Build the contents parser module** with test cases?
3. **Create the GitHub repository structure** with CI/CD workflows?

## @Greg-T8

I'm just using this for personal use, not for business. The cost is way too high for my need, as I may only be doing these notes generations a few times a month.  Is there a way I can significantly reduce cost, e.g. less than $5/month with this architecture?


## Copilot

Absolutely! For personal use with only a few runs per month, we can dramatically reduce costs by rethinking the architecture. Here's a redesigned approach:

---

## Cost-Optimized Architecture: Personal Use

### Cost Comparison

| Component | Original Design | Optimized Design |
|-----------|-----------------|------------------|
| Compute | Azure Functions (always-on app plan) | Local Python script or GitHub Codespaces |
| AI Model | GPT-4o ($5-15/1M tokens) | GPT-4o-mini ($0.15-0.60/1M tokens) |
| Storage | Azure Blob Storage | Local filesystem or GitHub repo |
| Orchestration | Durable Functions | Simple Python script |
| **Monthly Cost** | **$100-200+** | **$0.50-3.00** |

---

## Option 1: Fully Local + Azure OpenAI (Pay-Per-Use Only)

**Cost: ~$0.50-2.00 per transcript processed**

```
┌─────────────────────────────────────────────────────────────────┐
│                     YOUR LOCAL MACHINE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│   │ Contents    │    │ Transcript  │    │ Output      │        │
│   │ File        │    │ Chunks ZIP  │    │ Folder      │        │
│   └──────┬──────┘    └──────┬──────┘    └──────▲──────┘        │
│          │                  │                   │               │
│          ▼                  ▼                   │               │
│   ┌────────────────────────────────────────────┴──────┐        │
│   │              Python CLI Script                     │        │
│   │  • Parse contents                                  │        │
│   │  • Process chunks (parallel async)                 │        │
│   │  • Merge sections                                  │        │
│   │  • Assemble final document                         │        │
│   └────────────────────────┬──────────────────────────┘        │
│                            │                                    │
└────────────────────────────┼────────────────────────────────────┘
                             │ API calls only
                             ▼
                   ┌─────────────────────┐
                   │  Azure OpenAI       │
                   │  (GPT-4o-mini)      │
                   │  Pay-per-token only │
                   └─────────────────────┘
```

**Monthly costs:**
- Azure OpenAI: ~$0 base + ~$0.50-2.00 per transcript
- Storage: $0 (local)
- Compute: $0 (your machine)

---

## Option 2: GitHub Codespaces + OpenAI API

**Cost: $0-2.00/month (within free tier)**

```
┌─────────────────────────────────────────────────────────────────┐
│                   GitHub Codespaces (Free Tier)                 │
│                   60 hours/month included                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐                                               │
│   │ Your Repo   │                                               │
│   │ ├── inputs/ │  ← Upload contents + transcript               │
│   │ ├── output/ │  ← Generated notes                            │
│   │ └── src/    │  ← Processing scripts                         │
│   └──────┬──────┘                                               │
│          │                                                      │
│          ▼                                                      │
│   ┌─────────────────────────────────────────────────┐          │
│   │  python generate_notes.py input.zip contents.md │          │
│   └─────────────────────────┬───────────────────────┘          │
│                             │                                   │
└─────────────────────────────┼───────────────────────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │  OpenAI API       │
                    │  (GPT-4o-mini)    │
                    │  $0.15/1M input   │
                    │  $0.60/1M output  │
                    └───────────────────┘
```

**Monthly costs:**
- Codespaces: $0 (within 60 hr free tier)
- OpenAI API: ~$0.30-1.50 per transcript
- GitHub: $0 (free repo)

---

## Option 3: 100% Free with Ollama (Local LLM)

**Cost: $0.00**

```
┌─────────────────────────────────────────────────────────────────┐
│                     YOUR LOCAL MACHINE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────┐          │
│   │                    Ollama                        │          │
│   │            (Local LLM Runtime)                   │          │
│   │                                                  │          │
│   │   Models:                                        │          │
│   │   • llama3.1:8b (good balance)                  │          │
│   │   • mistral:7b (fast)                           │          │
│   │   • deepseek-r1:8b (reasoning)                  │          │
│   └─────────────────────────┬───────────────────────┘          │
│                             │                                   │
│                             ▼                                   │
│   ┌─────────────────────────────────────────────────┐          │
│   │         Python Script (same logic)              │          │
│   │         Points to localhost:11434               │          │
│   └─────────────────────────────────────────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Cost: $0 (requires 8-16GB RAM, GPU optional but faster)
```

---

## Recommended: Hybrid Approach

Use **OpenAI API directly** (not Azure OpenAI) with **GPT-4o-mini** for best cost/quality balance:

### Token Cost Calculation

| Transcript Size | Chunks | Input Tokens | Output Tokens | Cost |
|-----------------|--------|--------------|---------------|------|
| Small (30 min video) | 5 | ~30K | ~15K | ~$0.02 |
| Medium (2 hr video) | 20 | ~120K | ~60K | ~$0.06 |
| Large (5 hr video) | 50 | ~300K | ~150K | ~$0.15 |

**GPT-4o-mini pricing:**
- Input: $0.15 per 1M tokens
- Output: $0.60 per 1M tokens

**Monthly estimate (4 transcripts):** $0.10-0.60

---

## Simplified Implementation

```python name=exam_notes_generator.py
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
```

---

## Cost Breakdown: Your Use Case

| Item | Cost |
|------|------|
| OpenAI API (4 transcripts/month × $0.10) | ~$0.40 |
| Local compute | $0 |
| Storage | $0 |
| **Total** | **~$0.40/month** |

---

## Quick Start

```bash
# 1. Install dependencies
pip install openai

# 2. Set API key
export OPENAI_API_KEY="sk-..."

# 3. Run
python exam_notes_generator.py contents.md transcript_chunks.zip
```

---

## If You Still Want Azure (Minimal)

If you prefer Azure for learning purposes, here's the minimal viable setup:

| Resource | Configuration | Monthly Cost |
|----------|---------------|--------------|
| Azure OpenAI | Pay-as-you-go only, no reserved capacity | ~$0.50 per use |
| **No other Azure resources needed** | Run script locally | $0 |

Just deploy Azure OpenAI, get the endpoint/key, and use the same local script with the Azure client:

```python
from openai import AsyncAzureOpenAI

client = AsyncAzureOpenAI(
    azure_endpoint="https://your-resource.openai.azure.com/",
    api_key="your-key",
    api_version="2024-02-15-preview"
)
```

---

Would you like me to:
1. **Expand the Python script** with full error handling and progress output?
2. **Add Ollama support** for completely free local processing?
3. **Create a simple CLI interface** with argument parsing and configuration?

## @Greg-T8

I have a GitHub Copilot Pro+ subscription. Is there a way I can take advantage of this? For example, to use Claude Opus 4.5?

## Copilot

Yes! With your **GitHub Copilot Pro+ subscription**, you can leverage the **GitHub Models API** to access premium models like Claude, GPT-4o, and others—essentially getting **$0 marginal cost** for your exam notes generator (within your 1,500 premium requests/month).

---

## GitHub Models API + Copilot Pro+

### What You Get

| Feature | Copilot Pro+ Benefit |
|---------|---------------------|
| **Premium Requests** | 1,500/month included |
| **Available Models** | Claude Sonnet 3.7, Claude Sonnet 4, GPT-4o, GPT-4.1, Gemini, Llama, etc. |
| **API Access** | Full REST API via `models.github.ai` |
| **Cost** | $0 additional (within your subscription) |

### Cost for Your Use Case

| Transcript Size | Chunks | API Calls (Stage 1 + 2) | Premium Requests Used |
|-----------------|--------|-------------------------|----------------------|
| Medium (2 hr) | 20 | ~20 + ~30 sections = ~50 | **50 requests** |
| Large (5 hr) | 50 | ~50 + ~50 sections = ~100 | **100 requests** |

**Monthly usage (4 transcripts):** ~200-400 requests → **Well within 1,500 limit** ✓

---

## Revised Architecture: Zero Marginal Cost

```
┌─────────────────────────────────────────────────────────────────┐
│                     YOUR LOCAL MACHINE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│   │ Contents    │    │ Transcript  │    │ Output      │        │
│   │ File        │    │ Chunks ZIP  │    │ Folder      │        │
│   └──────┬──────┘    └──────┬──────┘    └──────▲──────┘        │
│          │                  │                   │               │
│          ▼                  ▼                   │               │
│   ┌────────────────────────────────────────────┴──────┐        │
│   │         Python CLI (exam_notes_generator.py)       │        │
│   │                                                    │        │
│   │  Uses OpenAI SDK with GitHub Models endpoint       │        │
│   └────────────────────────┬──────────────────────────┘        │
│                            │                                    │
└────────────────────────────┼────────────────────────────────────┘
                             │ HTTPS
                             ▼
              ┌───────────────────────────────┐
              │   GitHub Models API           │
              │   https://models.github.ai    │
              ├───────────────────────────────┤
              │                               │
              │   Models Available:           │
              │   • openai/gpt-4o             │
              │   • anthropic/claude-sonnet-4 │
              │   • meta/llama-3.3-70b        │
              │   • google/gemini-2.5-pro     │
              │                               │
              │   Auth: GitHub PAT            │
              │   Cost: $0 (Pro+ included)    │
              │                               │
              └───────────────────────────────┘
```

---

## Implementation

### Step 1: Create GitHub Personal Access Token

1. Go to [GitHub Settings → Developer Settings → Personal Access Tokens](https://github.com/settings/tokens)
2. Create a **Fine-grained token** with:
   - **Resource owner**: Your account
   - **Permissions**: `models:read` and `models:write`
3. Save the token securely

### Step 2: Install Dependencies

```bash
pip install openai
```

### Step 3: The Script

```python name=exam_notes_generator.py
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
```

---

## Usage

```bash
# 1. Set your GitHub token
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"

# 2. Run with Claude (default - best quality)
python exam_notes_generator.py contents.md transcript_chunks.zip

# 3. Or specify a different model
python exam_notes_generator.py contents.md transcript_chunks.zip --model gpt4o

# 4. Custom output path
python exam_notes_generator.py contents.md transcript_chunks.zip -o "AZ-104_Notes.md"
```

---

## Cost Summary

| Item | Cost |
|------|------|
| GitHub Copilot Pro+ subscription | $39/month (you already have this) |
| Additional API costs | **$0** (within 1,500 requests) |
| Storage | **$0** (local files) |
| Compute | **$0** (your machine) |
| **Marginal cost per transcript** | **$0** |

---

## Model Recommendations

| Model | Best For | Speed | Quality |
|-------|----------|-------|---------|
| `claude` (Claude Sonnet 4) | Complex reasoning, exam tips | Medium | ⭐⭐⭐⭐⭐ |
| `gpt4o` | Fast processing, good quality | Fast | ⭐⭐⭐⭐ |
| `gpt4.1` | Latest capabilities | Medium | ⭐⭐⭐⭐⭐ |
| `llama` | Open source, privacy | Fast | ⭐⭐⭐ |

For exam notes, I recommend **Claude Sonnet 4** (`--model claude`) for best reasoning and structured output.

---

Would you like me to:
1. **Add progress saving/resume** for interrupted runs?
2. **Create a VS Code task** to run this from your editor?
3. **Add a web UI** using Gradio for easier file uploads?

## @Greg-T8

The Anthropic models are not available. Here's the list of models from GitHub models. Recommend one for the best appraoch:

╭─( ~\OneDrive\Apps\Profiles\PowerShell [main ≡]
╰╴> gh models list

Showing 41 available chat models

ID                                           DISPLAY NAME
ai21-labs/ai21-jamba-1.5-large               AI21 Jamba 1.5 Large
cohere/cohere-command-a                      Cohere Command A
cohere/cohere-command-r-08-2024              Cohere Command R 08-2024
cohere/cohere-command-r-plus-08-2024         Cohere Command R+ 08-2024
deepseek/deepseek-r1                         DeepSeek-R1
deepseek/deepseek-r1-0528                    DeepSeek-R1-0528
deepseek/deepseek-v3-0324                    DeepSeek-V3-0324
meta/llama-3.2-11b-vision-instruct           Llama-3.2-11B-Vision-Instruct
meta/llama-3.2-90b-vision-instruct           Llama-3.2-90B-Vision-Instruct
meta/llama-3.3-70b-instruct                  Llama-3.3-70B-Instruct
meta/llama-4-maverick-17b-128e-instruct-fp8  Llama 4 Maverick 17B 128E Instruct FP8
meta/llama-4-scout-17b-16e-instruct          Llama 4 Scout 17B 16E Instruct
meta/meta-llama-3.1-405b-instruct            Meta-Llama-3.1-405B-Instruct
meta/meta-llama-3.1-8b-instruct              Meta-Llama-3.1-8B-Instruct
microsoft/mai-ds-r1                          MAI-DS-R1
microsoft/phi-4                              Phi-4
microsoft/phi-4-mini-instruct                Phi-4-mini-instruct
microsoft/phi-4-mini-reasoning               Phi-4-mini-reasoning
microsoft/phi-4-multimodal-instruct          Phi-4-multimodal-instruct
microsoft/phi-4-reasoning                    Phi-4-reasoning
mistral-ai/codestral-2501                    Codestral 25.01
mistral-ai/ministral-3b                      Ministral 3B
mistral-ai/mistral-medium-2505               Mistral Medium 3 (25.05)
mistral-ai/mistral-small-2503                Mistral Small 3.1
openai/gpt-4.1                               OpenAI GPT-4.1
openai/gpt-4.1-mini                          OpenAI GPT-4.1-mini
openai/gpt-4.1-nano                          OpenAI GPT-4.1-nano
openai/gpt-4o                                OpenAI GPT-4o
openai/gpt-4o-mini                           OpenAI GPT-4o mini
openai/gpt-5                                 OpenAI gpt-5
openai/gpt-5-chat                            OpenAI gpt-5-chat (preview)
openai/gpt-5-mini                            OpenAI gpt-5-mini
openai/gpt-5-nano                            OpenAI gpt-5-nano
openai/o1                                    OpenAI o1
openai/o1-mini                               OpenAI o1-mini
openai/o1-preview                            OpenAI o1-preview
openai/o3                                    OpenAI o3
openai/o3-mini                               OpenAI o3-mini
openai/o4-mini                               OpenAI o4-mini
xai/grok-3                                   Grok 3
xai/grok-3-mini                              Grok 3 Mini

## Copilot

Excellent list! Here's my analysis and recommendation:

---

## Model Recommendations for Exam Notes Generation

### Tier 1: Best Overall (Recommended)

| Model | Why | Best For |
|-------|-----|----------|
| **`deepseek/deepseek-r1-0528`** | Exceptional reasoning, structured output, handles long context well | ⭐ **Primary recommendation** |
| **`openai/gpt-4.1`** | Reliable, great at following complex instructions | Backup option |

### Tier 2: Strong Alternatives

| Model | Why | Trade-offs |
|-------|-----|------------|
| `openai/gpt-5-mini` | Latest OpenAI, balanced speed/quality | May use more premium requests |
| `meta/meta-llama-3.1-405b-instruct` | Massive model, excellent reasoning | Slower |
| `openai/o3-mini` | Strong reasoning (chain-of-thought) | Designed for reasoning tasks |

### Tier 3: Fast/Lightweight

| Model | Why | Trade-offs |
|-------|-----|------------|
| `openai/gpt-4.1-mini` | Fast, cheap on requests | Less nuanced output |
| `microsoft/phi-4-reasoning` | Good reasoning, efficient | Smaller context window |
| `deepseek/deepseek-v3-0324` | Fast, capable | Less reasoning focus than R1 |

---

## My Recommendation: DeepSeek-R1-0528

**Why DeepSeek-R1 is ideal for this task:**

1. **Reasoning-focused**: The "R1" models are specifically designed for complex reasoning—perfect for mapping transcripts to sections and generating structured notes

2. **Long context handling**: Handles the TOC + chunk context well without losing coherence

3. **Structured output**: Excellent at following markdown formatting instructions consistently

4. **Cost-efficient**: Typically uses fewer tokens to achieve the same quality (fewer premium requests consumed)

5. **Latest version**: The `0528` variant is the most recent with improvements

---

## Updated Script Configuration

```python name=exam_notes_generator.py
# ============================================================================
# CONFIGURATION - Updated for GitHub Models
# ============================================================================

# GitHub Models API endpoint
GITHUB_MODELS_BASE_URL = "https://models.github.ai/inference"

# Available models from GitHub Models (ranked by recommendation)
MODELS = {
    # Tier 1: Best for exam notes
    "deepseek": "deepseek/deepseek-r1-0528",      # ⭐ RECOMMENDED
    "gpt4.1": "openai/gpt-4.1",                    # Reliable backup
    
    # Tier 2: Strong alternatives  
    "gpt5-mini": "openai/gpt-5-mini",              # Latest OpenAI balanced
    "llama-405b": "meta/meta-llama-3.1-405b-instruct",  # Massive, thorough
    "o3-mini": "openai/o3-mini",                   # Reasoning-optimized
    
    # Tier 3: Fast options (for quick iterations)
    "gpt4.1-mini": "openai/gpt-4.1-mini",          # Fast, good enough
    "phi4-reason": "microsoft/phi-4-reasoning",   # Efficient reasoning
    "deepseek-v3": "deepseek/deepseek-v3-0324",   # Fast DeepSeek
    
    # Experimental
    "gpt5": "openai/gpt-5",                        # If you want bleeding edge
    "grok3": "xai/grok-3",                         # Alternative perspective
}

DEFAULT_MODEL = "deepseek"  # DeepSeek-R1-0528

# Model-specific settings (some models need adjustments)
MODEL_SETTINGS = {
    "deepseek/deepseek-r1-0528": {
        "temperature": 0.2,      # Lower for consistency
        "max_tokens": 4000,
    },
    "openai/gpt-4.1": {
        "temperature": 0.3,
        "max_tokens": 4000,
    },
    "openai/o3-mini": {
        "temperature": 0.2,      # Reasoning models work better with low temp
        "max_tokens": 4000,
    },
    "meta/meta-llama-3.1-405b-instruct": {
        "temperature": 0.3,
        "max_tokens": 4000,
    },
    # Default for unlisted models
    "default": {
        "temperature": 0.3,
        "max_tokens": 4000,
    }
}

def get_model_settings(model_id: str) -> dict:
    """Get optimal settings for a specific model."""
    return MODEL_SETTINGS.get(model_id, MODEL_SETTINGS["default"])
```

---

## Hybrid Strategy (Best Results)

For maximum quality, use **different models for different stages**:

```python
# Stage 1 (Chunk Processing): Use fast model - many calls
STAGE1_MODEL = "openai/gpt-4.1-mini"  # Fast, handles extraction well

# Stage 2 (Section Merging): Use reasoning model - fewer calls, need quality
STAGE2_MODEL = "deepseek/deepseek-r1-0528"  # Best reasoning for dedup/merge
```

**Why this works:**
- Stage 1 is mostly extraction (simpler task) → fast model saves requests
- Stage 2 requires reasoning (dedup, conflict resolution) → quality model shines

---

## Updated Full Script with Hybrid Approach

```python name=exam_notes_generator.py
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
```

---

## Quick Start

```bash
# Set token
export GITHUB_TOKEN="ghp_xxxx"

# Run
python exam_notes_generator.py contents.md chunks.zip -o "AZ-104_Notes.md"
```

---

## Request Budget Estimate

| Transcript | Chunks | Stage 1 (gpt-4.1-mini) | Stage 2 (deepseek-r1) | Total |
|------------|--------|------------------------|----------------------|-------|
| 2 hr video | 20 | 20 requests | ~25 requests | ~45 |
| 5 hr video | 50 | 50 requests | ~40 requests | ~90 |

**Monthly (4 transcripts):** ~180-360 requests → **Well under 1,500 limit** ✓

---

Would you like me to:
1. **Add a `--single-model` flag** to use one model for everything?
2. **Add progress saving** so you can resume interrupted runs?
3. **Create sample contents/transcript files** to test with?

## @Greg-T8

I have concerns on specifying the GitHub token in plain-text form in the file, as I intend to commit this file to my GitHub repository.

## Copilot

Great security awareness! Here are several secure approaches, ranked from simplest to most robust:

---

## Option 1: Environment Variable Only (Simplest)

The script already uses `os.environ.get("GITHUB_TOKEN")` — just never hardcode it:

```bash
# Set in your shell session (not committed)
export GITHUB_TOKEN="ghp_xxxx"

# Or use a .env file (add to .gitignore)
```

**Add `.env` support:**

```python name=exam_notes_generator.py (partial)
import os
from pathlib import Path

def load_token() -> str:
    """Load token from environment or .env file."""
    
    # 1. Check environment variable first
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    
    # 2. Try .env file in current directory
    env_file = Path(".env")
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("GITHUB_TOKEN="):
                return line.split("=", 1)[1].strip().strip('"\'')
    
    # 3. Try ~/.config/gh-models/.env
    config_file = Path.home() / ".config" / "gh-models" / ".env"
    if config_file.exists():
        for line in config_file.read_text().splitlines():
            if line.startswith("GITHUB_TOKEN="):
                return line.split("=", 1)[1].strip().strip('"\'')
    
    raise ValueError(
        "GITHUB_TOKEN not found.\n"
        "Options:\n"
        "  1. export GITHUB_TOKEN='ghp_xxx'\n"
        "  2. Create .env file with: GITHUB_TOKEN=ghp_xxx\n"
        "  3. Create ~/.config/gh-models/.env"
    )
```

**Create `.gitignore`:**

```gitignore name=.gitignore
# Secrets
.env
.env.*
*.env

# Don't commit output
exam_notes.md
output/
```

---

## Option 2: Use GitHub CLI Token (Recommended)

Since you have GitHub CLI (`gh`) installed, **reuse its authentication** — no separate token needed:

```python name=exam_notes_generator.py (partial)
import subprocess
import os

def get_github_token() -> str:
    """Get token from GitHub CLI (most secure for local use)."""
    
    # 1. Check environment variable first (for CI/automation)
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    
    # 2. Use GitHub CLI's stored token
    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            check=True
        )
        token = result.stdout.strip()
        if token:
            return token
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    raise ValueError(
        "GitHub token not found.\n"
        "Options:\n"
        "  1. Run: gh auth login\n"
        "  2. Set: export GITHUB_TOKEN='ghp_xxx'\n"
        "  3. Create .env file with: GITHUB_TOKEN=ghp_xxx"
    )
```

**Benefits:**
- Uses your existing `gh auth login` session
- No token stored in any file
- Token auto-refreshes
- Works immediately since you already use `gh models list`

---

## Option 3: Windows Credential Manager / macOS Keychain

For maximum security on your local machine:

```python name=exam_notes_generator.py (partial)
import subprocess
import platform
import os

def get_github_token() -> str:
    """Get token from secure OS credential store."""
    
    # 1. Environment variable (for CI/override)
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    
    # 2. GitHub CLI
    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            check=True
        )
        if result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # 3. OS-specific credential store
    system = platform.system()
    
    if system == "Windows":
        # Windows Credential Manager
        try:
            import subprocess
            result = subprocess.run(
                ["powershell", "-Command",
                 "(Get-StoredCredential -Target 'github-models-token').Password"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception:
            pass
    
    elif system == "Darwin":  # macOS
        # Keychain
        try:
            result = subprocess.run(
                ["security", "find-generic-password",
                 "-s", "github-models-token", "-w"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
    
    raise ValueError(
        "GitHub token not found.\n\n"
        "Setup options:\n"
        "  1. Run: gh auth login (recommended)\n"
        "  2. Set: export GITHUB_TOKEN='ghp_xxx'\n"
        "  3. Store in credential manager (see docs)"
    )
```

**Store token in Windows Credential Manager:**

```powershell
# PowerShell (one-time setup)
Install-Module -Name CredentialManager -Scope CurrentUser
New-StoredCredential -Target "github-models-token" -UserName "github" -Password "ghp_xxxx" -Persist LocalMachine
```

---

## Recommended: Option 2 (GitHub CLI)

Since you already use `gh`, this is the cleanest approach. Here's the complete updated client section:

```python name=exam_notes_generator.py (updated client section)
# ============================================================================
# SECURE TOKEN HANDLING
# ============================================================================

import subprocess
import os
from pathlib import Path

def get_github_token() -> str:
    """
    Get GitHub token securely. Priority:
    1. GITHUB_TOKEN environment variable
    2. GitHub CLI (gh auth token)
    3. .env file in current directory
    4. ~/.config/gh-models/.env
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
    
    # 3. .env file in current directory
    env_file = Path(".env")
    if env_file.exists():
        token = _parse_env_file(env_file)
        if token:
            print("   🔑 Using token from .env file")
            return token
    
    # 4. User config directory
    config_file = Path.home() / ".config" / "gh-models" / ".env"
    if config_file.exists():
        token = _parse_env_file(config_file)
        if token:
            print("   🔑 Using token from ~/.config/gh-models/.env")
            return token
    
    # No token found
    raise ValueError(
        "\n❌ GitHub token not found!\n\n"
        "Setup (choose one):\n\n"
        "  Option A - GitHub CLI (recommended):\n"
        "    gh auth login\n\n"
        "  Option B - Environment variable:\n"
        "    export GITHUB_TOKEN='ghp_xxxx'\n\n"
        "  Option C - .env file (add to .gitignore!):\n"
        "    echo 'GITHUB_TOKEN=ghp_xxxx' > .env\n"
    )

def _parse_env_file(path: Path) -> str | None:
    """Parse GITHUB_TOKEN from .env file."""
    for line in path.read_text().splitlines():
        line = line.strip()
        if line.startswith("#") or not line:
            continue
        if line.startswith("GITHUB_TOKEN="):
            value = line.split("=", 1)[1].strip()
            # Remove quotes if present
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            return value
    return None

def create_client() -> AsyncOpenAI:
    """Create OpenAI-compatible client for GitHub Models."""
    token = get_github_token()
    return AsyncOpenAI(api_key=token, base_url=GITHUB_MODELS_BASE_URL)
```

---

## Files to Add to Your Repo

```gitignore name=.gitignore
# ============================================================================
# Secrets - NEVER commit these
# ============================================================================
.env
.env.*
*.env
secrets/
.secrets

# ============================================================================
# Output files
# ============================================================================
exam_notes.md
*_Complete_Exam_Notes.md
output/

# ============================================================================
# Python
# ============================================================================
__pycache__/
*.pyc
.venv/
venv/
```

```markdown name=README.md (partial)
## Setup

### Authentication (choose one)

**Option A: GitHub CLI (recommended)**
```bash
gh auth login
```

**Option B: Environment variable**
```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

**Option C: .env file**
```bash
echo 'GITHUB_TOKEN=ghp_your_token_here' > .env
# ⚠️ Make sure .env is in .gitignore!
```

### Run
```bash
python exam_notes_generator.py contents.md transcript.zip
```
```

---

## Summary

| Approach | Security | Convenience | Recommended For |
|----------|----------|-------------|-----------------|
| `gh auth token` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **Your use case** |
| `.env` + `.gitignore` | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Backup option |
| OS Credential Store | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Extra paranoid |
| Environment variable | ⭐⭐⭐ | ⭐⭐⭐ | CI/CD pipelines |

**My recommendation:** Use GitHub CLI (`gh auth token`). You already have it set up, it's the most secure for local use, and requires zero additional configuration.

Would you like me to provide the complete updated script with this secure token handling integrated?

## @Greg-T8

I like option B, using the gh command.

Next, I want to specify the instructions.md file separately than have it encoded in the script.

## Copilot

Great choices! Here's the updated architecture with external prompt files:

---

## File Structure

```
exam-notes-generator/
├── exam_notes_generator.py    # Main script
├── prompts/
│   ├── chunk_process.md       # Stage 1 prompt
│   ├── section_merge.md       # Stage 2 prompt
│   └── system.md              # System prompts
├── .gitignore
└── README.md
```

---

## Prompt Files

````markdown name=prompts/system.md
# System Prompts for Exam Notes Generator

## Stage 1: Chunk Processing
You are an expert at creating study notes for technical certification exams. Be thorough and precise. Extract all relevant information from the transcript.

## Stage 2: Section Merging
You are an expert editor specializing in technical certification study materials. Your task is to merge partial notes while preserving all unique information and eliminating redundancy.
````

````markdown name=prompts/chunk_process.md
# Chunk Processing Prompt

Generate exam-focused study notes from this transcript chunk.

## Table of Contents
{toc}

## Transcript Chunk {chunk_id} of {total_chunks}
{chunk_text}

## Instructions

Map each portion of this transcript to the appropriate TOC section. For EACH section that has content in this chunk, generate notes in this EXACT format:

### [Section Title from TOC]
**Timestamp**: [first timestamp] – [last timestamp in this chunk for this section]

**Key Concepts**
- [main concepts as bullet points]

**Definitions**
- **[Term]**: [definition]

**Key Facts**
- [important facts, numbers, specifications]

**Examples**
- [concrete examples, commands, configurations mentioned]

**Exam Tips 🎯**
- [what to remember for the exam, common pitfalls]

## Rules

1. Use `###` for section titles ONLY
2. Use bold (`**text**`) for subsection headers
3. Include ALL content from the transcript — no information loss
4. If content spans multiple sections, create separate note blocks for each
5. Be technically precise — preserve exact values, commands, configurations
6. If a subsection has no content (e.g., no examples), write "- None in this chunk"
7. Timestamps should reflect the actual time range covered in this chunk for each section
````

````markdown name=prompts/section_merge.md
# Section Merge Prompt

Merge these partial notes into ONE coherent, comprehensive section.

## Section: {section_title}

## Partial Notes from Different Transcript Chunks:
{partials}

## Merge Instructions

### 1. Timestamp Handling
- Final timestamp: [earliest start] – [latest end]
- If there's a gap > 5 minutes between partials, note it as "(continued at [timestamp])"

### 2. Key Concepts
- Combine all bullet points across partials
- REMOVE exact duplicates (identical phrasing)
- KEEP near-duplicates if they add nuance (merge into one refined bullet)
- Order logically: foundational concepts first, advanced concepts later

### 3. Definitions
- If the same term is defined multiple times, keep the MOST COMPLETE definition
- If definitions conflict, include both with clarification: "(also described as: ...)"

### 4. Key Facts
- Remove redundant facts (same information, different words)
- Keep all UNIQUE facts
- If facts appear to contradict, flag with: "⚠️ Verify: mentioned as both X and Y"
- Order by dependency (prerequisite facts first)

### 5. Examples
- Keep ALL unique examples (examples are high-value for exams)
- Remove only exact duplicate examples
- Preserve code snippets, CLI commands, and configuration samples exactly

### 6. Exam Tips 🎯
- Combine all tips, remove duplicates
- Prioritize actionable tips ("Remember to..." > "This is important")
- Consolidate similar tips into stronger combined tips

## Rules

- Do NOT add information not present in the source partials
- Do NOT infer or expand beyond what's provided
- Do NOT summarize or lose detail
- Output in the standard format with ### heading

## Output

Produce the merged section now:
````

---

## Updated Script

```python name=exam_notes_generator.py
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
```

---

## Usage

```bash
# Default prompts (from ./prompts/ directory)
python exam_notes_generator.py contents.md transcript.zip

# Custom prompts directory
python exam_notes_generator.py contents.md transcript.zip --prompts ./my-prompts/

# Full options
python exam_notes_generator.py contents.md transcript.zip -o "AZ-104_Notes.md" -p ./prompts/
```

---

## Customizing Prompts

You can now edit the prompt files without touching the Python code:

| File | Purpose | Variables Available |
|------|---------|---------------------|
| `prompts/system.md` | System prompts for both stages | None |
| `prompts/chunk_process.md` | Stage 1 user prompt | `{toc}`, `{chunk_id}`, `{total_chunks}`, `{chunk_text}` |
| `prompts/section_merge.md` | Stage 2 user prompt | `{section_title}`, `{partials}` |

**Example customization** — add exam-specific focus:

````markdown name=prompts/chunk_process.md (modified section)
## Exam-Specific Focus

This is for the **AZ-104 Azure Administrator** exam. Pay special attention to:
- Azure CLI and PowerShell commands
- Portal navigation paths
- Default values and limits
- SKU differences
- Region availability
````

---

## Complete File Tree

```
exam-notes-generator/
├── exam_notes_generator.py
├── prompts/
│   ├── system.md
│   ├── chunk_process.md
│   └── section_merge.md
├── .gitignore
└── README.md
```

---

Would you like me to:
1. **Add prompt validation** to check for required variables before running?
2. **Add a `--dry-run` flag** to preview what will be processed without API calls?
3. **Create a sample contents.md and transcript ZIP** for testing?

## @Greg-T8

I  want to create a GitHub Space for this work. Write a simple set of instructions that helps me design this app.

## Copilot

# Creating a GitHub Copilot Space for Exam Notes Generator

Here's a step-by-step guide to set up a Copilot Space for your exam notes generator project:

---

## What is a Copilot Space?

A **Copilot Space** is a persistent context container that gives GitHub Copilot deep knowledge about your specific project. When you chat with Copilot in a Space, it uses your attached files, instructions, and repositories to provide highly relevant responses[[1]](https://github.blog/changelog/2025-05-29-introducing-copilot-spaces-a-new-way-to-work-with-code-and-context/)[[2]](https://github.blog/ai-and-ml/github-copilot/github-copilot-spaces-bring-the-right-context-to-every-suggestion/).

---

## Step 1: Create the Space

1. Go to **https://github.com/copilot/spaces**
2. Click **"Create space"**
3. Configure:
   - **Name**: `Exam Notes Generator`
   - **Owner**: Your personal account
   - **Description**: `Generates structured exam study notes from video transcripts using GitHub Models API`

---

## Step 2: Add Instructions

In the **Instructions** section, paste the following:

```text
You are helping develop an Exam Notes Generator application.

## Project Overview
This is a Python CLI tool that:
1. Takes a video transcript (chunked into 20KB files) and a table of contents
2. Uses GitHub Models API to process each chunk into structured exam notes
3. Merges notes by section using a reasoning model
4. Assembles a final hierarchical markdown document

## Tech Stack
- Python 3.11+ with asyncio
- OpenAI Python SDK (pointing to GitHub Models API)
- GitHub CLI for authentication (gh auth token)
- Models: gpt-4.1-mini (Stage 1), deepseek-r1-0528 (Stage 2)

## Key Design Decisions
- Two-stage AI processing to avoid context window limitations
- External prompt files in /prompts directory for easy customization
- Secure token handling via GitHub CLI (no hardcoded secrets)
- Hybrid model strategy: fast model for extraction, reasoning model for merging

## File Structure
```
exam-notes-generator/
├── exam_notes_generator.py    # Main script
├── prompts/
│   ├── system.md              # System prompts
│   ├── chunk_process.md       # Stage 1 prompt
│   └── section_merge.md       # Stage 2 prompt
├── .gitignore
└── README.md
```

## When Helping
- Follow existing code patterns and style
- Keep prompts in external markdown files, not hardcoded
- Use async/await for API calls
- Ensure no secrets are committed to the repository
- Optimize for minimal premium request usage
```

---

## Step 3: Add Source Files

Click **"Add sources"** and attach the following:

### Option A: From Your Repository (if already created)
1. Click **"Add repository"**
2. Select your `exam-notes-generator` repository
3. Copilot will index the entire repo

### Option B: Upload Individual Files (if not yet in a repo)
Upload these files:

| File | Purpose |
|------|---------|
| `exam_notes_generator.py` | Main script |
| `prompts/chunk_process.md` | Stage 1 prompt template |
| `prompts/section_merge.md` | Stage 2 prompt template |
| `prompts/system.md` | System prompts |

### Option C: Paste Key Context as Text
Click **"Add text"** and paste:

```text
## GitHub Models API Available Models

The following models are available via GitHub Models API:
- deepseek/deepseek-r1-0528 (recommended for reasoning)
- openai/gpt-4.1-mini (recommended for fast extraction)
- openai/gpt-4.1
- openai/gpt-5-mini
- meta/meta-llama-3.1-405b-instruct

## API Endpoint
Base URL: https://models.github.ai/inference
Authentication: GitHub Personal Access Token or `gh auth token`

## Usage Pattern
Uses OpenAI Python SDK with custom base_url pointing to GitHub Models.
```

---

## Step 4: Add Reference Documentation (Optional)

Add links to relevant documentation:

1. Click **"Add link"**
2. Add these URLs:
   - `https://docs.github.com/en/github-models/quickstart`
   - `https://docs.github.com/en/rest/models/inference`

---

## Step 5: Using Your Space

### In the Browser
1. Go to your Space at `https://github.com/copilot/spaces`
2. Click on **"Exam Notes Generator"**
3. Start chatting—Copilot now has full context about your project

**Example prompts to try:**
- "Add error handling for when a chunk produces no sections"
- "Create a --dry-run flag that shows what would be processed"
- "Add progress saving so interrupted runs can resume"
- "Optimize the merge prompt for better deduplication"

### In VS Code
1. Install the **GitHub Copilot** extension
2. Open Copilot Chat (`Ctrl+Shift+I` or `Cmd+Shift+I`)
3. Type `@spaces` to see available spaces
4. Select your **Exam Notes Generator** space
5. Your chat is now grounded in your project context

---

## Complete Space Configuration Summary

| Setting | Value |
|---------|-------|
| **Name** | Exam Notes Generator |
| **Description** | Generates structured exam study notes from video transcripts using GitHub Models API |
| **Instructions** | Project overview, tech stack, design decisions (see Step 2) |
| **Sources** | Repository or uploaded files |
| **Links** | GitHub Models documentation |

---

## Tips for Effective Spaces

1. **Keep instructions focused** — Tell Copilot what the project does and your preferences
2. **Add your actual code** — Attach the repository for the best context
3. **Update as you iterate** — Add new files or update instructions as the project evolves
4. **Use for specific tasks** — "Add feature X following existing patterns" works better than vague requests

---

## References

- [Creating GitHub Copilot Spaces](https://docs.github.com/en/copilot/how-tos/provide-context/use-copilot-spaces/create-copilot-spaces)
- [Using GitHub Copilot Spaces](https://docs.github.com/en/copilot/how-tos/provide-context/use-copilot-spaces/use-copilot-spaces)
- [GitHub Copilot Spaces Blog Post](https://github.blog/ai-and-ml/github-copilot/github-copilot-spaces-bring-the-right-context-to-every-suggestion/)
- [Video Tutorial: Create Your First Space](https://www.youtube.com/watch?v=6pbdTiT-Pcg)

---

Would you like me to:
1. **Generate a README.md** for your repository?
2. **Create additional prompt variations** for different exam types (Azure, AWS, etc.)?
3. **Add a sample contents.md and test transcript** so you can test the Space immediately?

## @Greg-T8

I ultimately want to call the script using PowerShell but keep the Python core.

## Copilot

Great approach! Here's a PowerShell wrapper that provides a clean CLI experience while keeping the Python core:

---

## File Structure

```
exam-notes-generator/
├── exam_notes_generator.py        # Python core
├── Generate-ExamNotes.ps1         # PowerShell wrapper
├── prompts/
│   ├── system.md
│   ├── chunk_process.md
│   └── section_merge.md
├── .gitignore
└── README.md
```

---

## PowerShell Wrapper

```powershell name=Generate-ExamNotes.ps1
<#
.SYNOPSIS
    Generates exam-focused study notes from video transcripts using GitHub Models API.

.DESCRIPTION
    This script wraps the Python exam notes generator, providing a PowerShell-native
    interface with parameter validation, prerequisite checking, and enhanced output.

.PARAMETER ContentsFile
    Path to the markdown file containing the table of contents with timestamps.

.PARAMETER TranscriptZip
    Path to the ZIP file containing transcript chunks (20KB each).

.PARAMETER OutputFile
    Path for the generated exam notes. Defaults to "exam_notes.md" in current directory.

.PARAMETER PromptsDir
    Directory containing prompt templates. Defaults to "./prompts" relative to script.

.PARAMETER Stage1Model
    Model for chunk processing (fast extraction). Default: openai/gpt-4.1-mini

.PARAMETER Stage2Model
    Model for section merging (quality reasoning). Default: deepseek/deepseek-r1-0528

.PARAMETER DryRun
    Show what would be processed without making API calls.

.PARAMETER Force
    Overwrite output file if it exists.

.EXAMPLE
    .\Generate-ExamNotes.ps1 -ContentsFile .\contents.md -TranscriptZip .\transcript.zip

.EXAMPLE
    .\Generate-ExamNotes.ps1 .\contents.md .\transcript.zip -OutputFile "AZ-104_Notes.md"

.EXAMPLE
    .\Generate-ExamNotes.ps1 .\contents.md .\transcript.zip -Stage1Model "openai/gpt-4.1" -Force

.NOTES
    Requires:
    - Python 3.11+
    - GitHub CLI (gh) authenticated
    - OpenAI Python package: pip install openai
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory, Position = 0)]
    [ValidateScript({ Test-Path $_ -PathType Leaf })]
    [string]$ContentsFile,

    [Parameter(Mandatory, Position = 1)]
    [ValidateScript({ Test-Path $_ -PathType Leaf })]
    [string]$TranscriptZip,

    [Parameter(Position = 2)]
    [string]$OutputFile = "exam_notes.md",

    [Parameter()]
    [string]$PromptsDir,

    [Parameter()]
    [ValidateSet(
        "openai/gpt-4.1-mini",
        "openai/gpt-4.1",
        "openai/gpt-5-mini",
        "deepseek/deepseek-r1-0528",
        "deepseek/deepseek-v3-0324"
    )]
    [string]$Stage1Model = "openai/gpt-4.1-mini",

    [Parameter()]
    [ValidateSet(
        "deepseek/deepseek-r1-0528",
        "deepseek/deepseek-v3-0324",
        "openai/gpt-4.1",
        "openai/gpt-5-mini",
        "openai/o3-mini"
    )]
    [string]$Stage2Model = "deepseek/deepseek-r1-0528",

    [Parameter()]
    [switch]$DryRun,

    [Parameter()]
    [switch]$Force
)

# ============================================================================
# CONFIGURATION
# ============================================================================

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Default prompts directory relative to script location
if (-not $PromptsDir) {
    $PromptsDir = Join-Path $ScriptDir "prompts"
}

# Python script location
$PythonScript = Join-Path $ScriptDir "exam_notes_generator.py"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

function Write-Status {
    param([string]$Message, [string]$Type = "Info")
    
    $symbol = switch ($Type) {
        "Info"    { "ℹ️ " }
        "Success" { "✅" }
        "Warning" { "⚠️ " }
        "Error"   { "❌" }
        "Step"    { "▶️ " }
    }
    
    $color = switch ($Type) {
        "Info"    { "Cyan" }
        "Success" { "Green" }
        "Warning" { "Yellow" }
        "Error"   { "Red" }
        "Step"    { "White" }
    }
    
    Write-Host "$symbol $Message" -ForegroundColor $color
}

function Test-Prerequisites {
    <#
    .SYNOPSIS
        Validates all prerequisites are met before running.
    #>
    
    $issues = @()
    
    # Check Python
    Write-Status "Checking Python..." -Type Step
    try {
        $pythonVersion = & python --version 2>&1
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 11)) {
                $issues += "Python 3.11+ required. Found: $pythonVersion"
            } else {
                Write-Status "Python: $pythonVersion" -Type Success
            }
        }
    } catch {
        $issues += "Python not found. Install from https://python.org"
    }
    
    # Check GitHub CLI
    Write-Status "Checking GitHub CLI..." -Type Step
    try {
        $null = & gh --version 2>&1
        
        # Check authentication
        $token = & gh auth token 2>&1
        if ($LASTEXITCODE -ne 0) {
            $issues += "GitHub CLI not authenticated. Run: gh auth login"
        } else {
            Write-Status "GitHub CLI: Authenticated" -Type Success
        }
    } catch {
        $issues += "GitHub CLI not found. Install from https://cli.github.com"
    }
    
    # Check OpenAI package
    Write-Status "Checking OpenAI package..." -Type Step
    $pipCheck = & python -c "import openai; print(openai.__version__)" 2>&1
    if ($LASTEXITCODE -ne 0) {
        $issues += "OpenAI package not installed. Run: pip install openai"
    } else {
        Write-Status "OpenAI package: v$pipCheck" -Type Success
    }
    
    # Check Python script exists
    if (-not (Test-Path $PythonScript)) {
        $issues += "Python script not found: $PythonScript"
    }
    
    # Check prompts directory
    if (-not (Test-Path $PromptsDir)) {
        $issues += "Prompts directory not found: $PromptsDir"
    } else {
        $requiredPrompts = @("chunk_process.md", "section_merge.md")
        foreach ($prompt in $requiredPrompts) {
            $promptPath = Join-Path $PromptsDir $prompt
            if (-not (Test-Path $promptPath)) {
                $issues += "Required prompt file not found: $promptPath"
            }
        }
    }
    
    # Check output file
    if ((Test-Path $OutputFile) -and -not $Force) {
        $issues += "Output file exists: $OutputFile (use -Force to overwrite)"
    }
    
    return $issues
}

function Get-TranscriptInfo {
    <#
    .SYNOPSIS
        Extracts information about the transcript ZIP without processing.
    #>
    param([string]$ZipPath)
    
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    
    $zip = [System.IO.Compression.ZipFile]::OpenRead($ZipPath)
    try {
        $chunks = $zip.Entries | Where-Object { 
            $_.Name -match '\.(txt|md)$' -and $_.Length -gt 0 
        }
        
        $totalSize = ($chunks | Measure-Object -Property Length -Sum).Sum
        
        return @{
            ChunkCount = $chunks.Count
            TotalSizeKB = [math]::Round($totalSize / 1KB, 1)
            Files = $chunks.Name
        }
    } finally {
        $zip.Dispose()
    }
}

function Get-ContentsInfo {
    <#
    .SYNOPSIS
        Parses the contents file to extract section count.
    #>
    param([string]$ContentsPath)
    
    $content = Get-Content $ContentsPath -Raw
    $lines = $content -split "`n"
    
    # Extract title
    $title = ($lines | Where-Object { $_ -match "^# " } | Select-Object -First 1) -replace "^# ", ""
    
    # Count sections by heading level
    $level2 = ($lines | Where-Object { $_ -match "^## " }).Count
    $level3 = ($lines | Where-Object { $_ -match "^### " }).Count
    $level4 = ($lines | Where-Object { $_ -match "^#### " }).Count
    
    return @{
        Title = $title.Trim()
        Level2Sections = $level2
        Level3Sections = $level3
        Level4Sections = $level4
        TotalSections = $level2 + $level3 + $level4
    }
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

# Banner
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║           📚 Exam Notes Generator                            ║" -ForegroundColor Cyan
Write-Host "║           Using GitHub Models API                            ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow
Write-Host ""
$issues = Test-Prerequisites

if ($issues.Count -gt 0) {
    Write-Host ""
    Write-Status "Prerequisites check failed:" -Type Error
    foreach ($issue in $issues) {
        Write-Host "   • $issue" -ForegroundColor Red
    }
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Status "All prerequisites met!" -Type Success
Write-Host ""

# Analyze inputs
Write-Host "Analyzing inputs..." -ForegroundColor Yellow
Write-Host ""

$contentsInfo = Get-ContentsInfo -ContentsPath $ContentsFile
Write-Status "Contents: $($contentsInfo.Title)" -Type Info
Write-Host "   Sections: $($contentsInfo.TotalSections) total ($($contentsInfo.Level2Sections) L2, $($contentsInfo.Level3Sections) L3, $($contentsInfo.Level4Sections) L4)"

$transcriptInfo = Get-TranscriptInfo -ZipPath $TranscriptZip
Write-Status "Transcript: $($transcriptInfo.ChunkCount) chunks ($($transcriptInfo.TotalSizeKB) KB)" -Type Info

# Estimate API usage
$estimatedStage1 = $transcriptInfo.ChunkCount
$estimatedStage2 = [math]::Min($contentsInfo.TotalSections, $transcriptInfo.ChunkCount * 2)
$estimatedTotal = $estimatedStage1 + $estimatedStage2

Write-Host ""
Write-Host "Estimated API usage:" -ForegroundColor Yellow
Write-Host "   Stage 1 ($Stage1Model): ~$estimatedStage1 requests"
Write-Host "   Stage 2 ($Stage2Model): ~$estimatedStage2 requests"
Write-Host "   Total: ~$estimatedTotal premium requests"
Write-Host ""

# Dry run - stop here
if ($DryRun) {
    Write-Status "Dry run complete. No API calls made." -Type Warning
    Write-Host ""
    Write-Host "To process, run without -DryRun flag." -ForegroundColor Gray
    exit 0
}

# Confirm before proceeding
$confirm = Read-Host "Proceed with generation? (Y/n)"
if ($confirm -and $confirm -notmatch "^[Yy]") {
    Write-Status "Cancelled by user." -Type Warning
    exit 0
}

Write-Host ""

# Build Python arguments
$pythonArgs = @(
    $PythonScript
    (Resolve-Path $ContentsFile).Path
    (Resolve-Path $TranscriptZip).Path
    "--output", $OutputFile
    "--prompts", $PromptsDir
    "--stage1-model", $Stage1Model
    "--stage2-model", $Stage2Model
)

# Execute Python script
Write-Status "Starting generation..." -Type Step
Write-Host ""

$startTime = Get-Date

try {
    & python @pythonArgs
    
    if ($LASTEXITCODE -ne 0) {
        throw "Python script exited with code $LASTEXITCODE"
    }
    
    $duration = (Get-Date) - $startTime
    
    Write-Host ""
    Write-Status "Generation complete!" -Type Success
    Write-Host ""
    Write-Host "   Output: $((Resolve-Path $OutputFile).Path)" -ForegroundColor Green
    Write-Host "   Duration: $($duration.ToString('mm\:ss'))" -ForegroundColor Gray
    Write-Host "   Size: $([math]::Round((Get-Item $OutputFile).Length / 1KB, 1)) KB" -ForegroundColor Gray
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Status "Generation failed: $_" -Type Error
    exit 1
}
```

---

## Updated Python Script (with model parameters)

Add these CLI arguments to the Python script:

```python name=exam_notes_generator.py (updated CLI section)
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
    parser.add_argument(
        "--stage1-model",
        default="openai/gpt-4.1-mini",
        help="Model for Stage 1 chunk processing (default: openai/gpt-4.1-mini)"
    )
    parser.add_argument(
        "--stage2-model",
        default="deepseek/deepseek-r1-0528",
        help="Model for Stage 2 section merging (default: deepseek/deepseek-r1-0528)"
    )
    
    args = parser.parse_args()
    
    # Pass models to the generator
    asyncio.run(generate_notes(
        args.contents,
        args.transcript_zip,
        args.output,
        args.prompts,
        args.stage1_model,
        args.stage2_model
    ))

if __name__ == "__main__":
    main()
```

Update the `generate_notes` function signature:

```python name=exam_notes_generator.py (updated generate_notes)
async def generate_notes(
    contents_path: str,
    zip_path: str,
    output_path: str,
    prompts_dir: Path,
    stage1_model: str = "openai/gpt-4.1-mini",
    stage2_model: str = "deepseek/deepseek-r1-0528"
):
    """Main pipeline."""
    
    print(f"🤖 Models: Stage1={stage1_model}, Stage2={stage2_model}")
    print(f"📝 Prompts: {prompts_dir}")
    
    # ... rest of function uses stage1_model and stage2_model instead of constants
```

---

## Usage Examples

```powershell
# Basic usage
.\Generate-ExamNotes.ps1 -ContentsFile .\contents.md -TranscriptZip .\transcript.zip

# Positional parameters (shorter)
.\Generate-ExamNotes.ps1 .\contents.md .\transcript.zip

# Custom output file
.\Generate-ExamNotes.ps1 .\contents.md .\transcript.zip -OutputFile "AZ-104_Notes.md"

# Use different models
.\Generate-ExamNotes.ps1 .\contents.md .\transcript.zip -Stage1Model "openai/gpt-4.1" -Stage2Model "openai/o3-mini"

# Dry run (see what would happen without API calls)
.\Generate-ExamNotes.ps1 .\contents.md .\transcript.zip -DryRun

# Overwrite existing output
.\Generate-ExamNotes.ps1 .\contents.md .\transcript.zip -Force

# Full example with all options
.\Generate-ExamNotes.ps1 `
    -ContentsFile ".\AZ-104\contents.md" `
    -TranscriptZip ".\AZ-104\transcript_chunks.zip" `
    -OutputFile ".\output\AZ-104_Complete_Notes.md" `
    -PromptsDir ".\prompts" `
    -Stage1Model "openai/gpt-4.1-mini" `
    -Stage2Model "deepseek/deepseek-r1-0528" `
    -Force
```

---

## Sample Output

```
╔══════════════════════════════════════════════════════════════╗
║           📚 Exam Notes Generator                            ║
║           Using GitHub Models API                            ║
╚══════════════════════════════════════════════════════════════╝

Checking prerequisites...

▶️  Checking Python...
✅ Python: Python 3.12.1
▶️  Checking GitHub CLI...
✅ GitHub CLI: Authenticated
▶️  Checking OpenAI package...
✅ OpenAI package: v1.52.0

✅ All prerequisites met!

Analyzing inputs...

ℹ️  Contents: AZ-104 Azure Administrator
   Sections: 47 total (8 L2, 24 L3, 15 L4)
ℹ️  Transcript: 23 chunks (412.5 KB)

Estimated API usage:
   Stage 1 (openai/gpt-4.1-mini): ~23 requests
   Stage 2 (deepseek/deepseek-r1-0528): ~35 requests
   Total: ~58 premium requests

Proceed with generation? (Y/n): Y

▶️  Starting generation...

🤖 Models: Stage1=openai/gpt-4.1-mini, Stage2=deepseek/deepseek-r1-0528
📝 Prompts: C:\code\exam-notes-generator\prompts
   ✓ Prompts loaded
   🔑 Using token from GitHub CLI
📋 Parsing contents...
   AZ-104 Azure Administrator (47 sections)
📦 Extracting chunks...
   23 chunks

⚙️  Stage 1: Processing chunks (openai/gpt-4.1-mini)...
   ✓ Chunk 1/23
   ✓ Chunk 2/23
   ...

🔀 Stage 2: Merging sections (deepseek/deepseek-r1-0528)...
   ✓ 1/35
   ...

📄 Stage 3: Assembling...

✅ Done! exam_notes.md
   Premium requests: ~58

✅ Generation complete!

   Output: C:\code\exam-notes-generator\exam_notes.md
   Duration: 04:23
   Size: 127.4 KB
```

---

## PowerShell Profile Alias (Optional)

Add to your PowerShell profile (`$PROFILE`) for quick access:

```powershell
# Add to $PROFILE
function New-ExamNotes {
    param(
        [Parameter(Mandatory, Position = 0)]
        [string]$Contents,
        
        [Parameter(Mandatory, Position = 1)]
        [string]$Transcript,
        
        [string]$Output = "exam_notes.md"
    )
    
    & "C:\path\to\exam-notes-generator\Generate-ExamNotes.ps1" `
        -ContentsFile $Contents `
        -TranscriptZip $Transcript `
        -OutputFile $Output
}

Set-Alias -Name examgen -Value New-ExamNotes
```

Then use:
```powershell
examgen .\contents.md .\transcript.zip
```

---

Would you like me to:
1. **Add a `-Verbose` flag** for detailed logging?
2. **Create a config file** (`exam-notes.config.json`) for default settings?
3. **Add progress bars** using PowerShell's `Write-Progress`?

## @Greg-T8

Create a detailed description of this tool, including what it does, its inputs, and how it works.

## Copilot

````markdown name=README.md
# 📚 Exam Notes Generator

A command-line tool that transforms video transcripts into structured, exam-focused study notes using AI. Built for certification exam preparation, it processes chunked transcripts and produces hierarchical markdown notes optimized for studying.

## Overview

```
┌─────────────────┐     ┌─────────────────┐
│  Contents File  │     │  Transcript ZIP │
│  (TOC + Times)  │     │  (20KB chunks)  │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
         ┌───────────────────────┐
         │   Exam Notes Generator │
         │   ─────────────────── │
         │   Stage 1: Extract    │──→ GitHub Models API
         │   Stage 2: Merge      │──→ GitHub Models API
         │   Stage 3: Assemble   │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Complete Exam Notes  │
         │  (Markdown)           │
         └───────────────────────┘
```

## What It Does

The Exam Notes Generator solves a common problem: turning lengthy video courses into concise, exam-ready study materials. It:

1. **Processes video transcripts** split into manageable chunks
2. **Maps content to your table of contents** preserving the course structure
3. **Extracts exam-relevant information** including concepts, definitions, facts, examples, and tips
4. **Merges overlapping content** from different chunks intelligently
5. **Produces a single markdown document** with proper heading hierarchy

### Key Features

| Feature | Description |
|---------|-------------|
| **Two-Stage AI Processing** | Avoids context window limitations by processing chunks individually, then merging by section |
| **Hybrid Model Strategy** | Uses fast models for extraction, reasoning models for quality merging |
| **Hierarchical Output** | Preserves your TOC structure with proper `##`, `###`, `####` heading levels |
| **Exam-Focused Format** | Each section includes Key Concepts, Definitions, Facts, Examples, and Exam Tips |
| **Customizable Prompts** | External prompt files let you tune output without modifying code |
| **Secure Authentication** | Uses GitHub CLI—no hardcoded tokens |
| **Cost Optimized** | Designed for GitHub Copilot Pro+ subscribers—$0 marginal cost within your subscription |

---

## Inputs

### 1. Contents File (`contents.md`)

A markdown file containing your video's table of contents with optional timestamps. This defines the structure of your output notes.

**Format:**
```markdown
# AZ-104 Azure Administrator

## Manage Azure Identities and Governance [00:00:00]
### Manage Azure AD Objects [00:02:30]
#### Create Users and Groups [00:02:30]
#### Manage Licenses [00:15:45]
### Manage Role-Based Access Control [00:28:00]
#### Built-in Roles [00:28:00]
#### Custom Roles [00:42:15]

## Implement and Manage Storage [01:15:00]
### Configure Storage Accounts [01:15:00]
#### Replication Options [01:15:00]
#### Access Tiers [01:32:30]
```

**Rules:**
- `#` = Video title (one only)
- `##` = Top-level sections
- `###`, `####`, etc. = Subsections (nested as needed)
- `[HH:MM:SS]` = Optional timestamps (helps with mapping but not required)
- Lowest-level headings become the atomic units for note generation

### 2. Transcript ZIP (`transcript_chunks.zip`)

A ZIP archive containing transcript text files, each approximately 20KB. Chunks should be sequential and named for proper ordering.

**Structure:**
```
transcript_chunks.zip
├── chunk_001.txt
├── chunk_002.txt
├── chunk_003.txt
├── ...
└── chunk_023.txt
```

**Chunk Requirements:**
- **Size**: ~20KB each (roughly 5,000-6,000 tokens)
- **Format**: Plain text (`.txt`) or markdown (`.md`)
- **Naming**: Sequential numbering for correct ordering
- **Content**: Raw transcript text, timestamps optional

**Creating Chunks:**

If you have a full transcript, split it:

```powershell
# PowerShell: Split transcript into 20KB chunks
$content = Get-Content -Path "full_transcript.txt" -Raw
$chunkSize = 20000  # 20KB
$chunks = [regex]::Matches($content, ".{1,$chunkSize}(?:\s|$)", "Singleline")

$i = 1
foreach ($chunk in $chunks) {
    $chunk.Value | Out-File -FilePath ("chunk_{0:D3}.txt" -f $i++) -Encoding UTF8
}

Compress-Archive -Path "chunk_*.txt" -DestinationPath "transcript_chunks.zip"
```

### 3. Prompt Templates (`prompts/` directory)

External markdown files containing the AI prompts. Customize these to tune output quality.

| File | Purpose | Variables |
|------|---------|-----------|
| `system.md` | System role prompts for each stage | None |
| `chunk_process.md` | Stage 1: Extract notes from transcript | `{toc}`, `{chunk_id}`, `{total_chunks}`, `{chunk_text}` |
| `section_merge.md` | Stage 2: Merge partial notes | `{section_title}`, `{partials}` |

---

## Output

### Generated File (`exam_notes.md`)

A single markdown document with hierarchical structure matching your contents file.

**Example Output:**

```markdown
# AZ-104 Azure Administrator - Complete Exam Notes

*Generated using GitHub Models API*
*Stage 1: openai/gpt-4.1-mini | Stage 2: deepseek/deepseek-r1-0528*

---

## Manage Azure Identities and Governance

### Manage Azure AD Objects

#### Create Users and Groups
**Timestamp**: 00:02:30 – 00:15:40

**Key Concepts**
- Azure AD is the cloud-based identity and access management service
- Users can be cloud-only or synced from on-premises AD
- Groups can be Security or Microsoft 365 type
- Dynamic groups use rules to automatically manage membership

**Definitions**
- **Azure AD**: Microsoft's cloud-based identity provider (IdP)
- **Guest User**: External user invited via B2B collaboration
- **Dynamic Group**: Group with membership managed by query rules

**Key Facts**
- Maximum 50,000 objects in Azure AD Free tier
- Bulk operations support up to 50,000 users via CSV
- Guest users count against directory quota
- Dynamic group rules are evaluated on user attribute changes

**Examples**
- Create user via CLI: `az ad user create --display-name "John Doe" --user-principal-name john@contoso.com --password "P@ssw0rd"`
- Dynamic group rule: `user.department -eq "Engineering"`

**Exam Tips 🎯**
- Know the difference between Security and M365 groups
- Dynamic groups require Azure AD Premium P1
- Bulk user creation uses CSV with specific column headers
- Guest users can be restricted from certain directory operations
```

---

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PROCESSING PIPELINE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ STAGE 1: Chunk Processing (Parallel)                                │   │
│  │                                                                      │   │
│  │   Chunk 1 ──┐                                                       │   │
│  │   Chunk 2 ──┼──→ [GPT-4.1-mini] ──→ Notes with section assignments │   │
│  │   Chunk N ──┘        ▲                                              │   │
│  │                      │                                              │   │
│  │              TOC provided to                                        │   │
│  │              each call for                                          │   │
│  │              section mapping                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ GROUPING: Organize by Section                                       │   │
│  │                                                                      │   │
│  │   Section A: [chunk1_partial, chunk2_partial]                       │   │
│  │   Section B: [chunk2_partial, chunk3_partial, chunk4_partial]       │   │
│  │   Section C: [chunk4_partial]                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ STAGE 2: Section Merging (Parallel)                                 │   │
│  │                                                                      │   │
│  │   Section A partials ──┐                                            │   │
│  │   Section B partials ──┼──→ [DeepSeek-R1] ──→ Merged sections      │   │
│  │   Section C partials ──┘                                            │   │
│  │                                                                      │   │
│  │   • Deduplicates overlapping content                                │   │
│  │   • Resolves conflicts                                              │   │
│  │   • Combines timestamps                                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ STAGE 3: Document Assembly (Deterministic)                          │   │
│  │                                                                      │   │
│  │   • Rebuilds heading hierarchy from TOC                             │   │
│  │   • Inserts merged sections at correct positions                    │   │
│  │   • Adjusts heading levels (### → ##, ####, etc.)                  │   │
│  │   • No AI involved—pure programmatic assembly                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│                    [Complete Exam Notes]                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Stage Details

#### Stage 1: Chunk Processing

**Purpose**: Extract structured notes from each transcript chunk.

**Process**:
1. Each chunk is processed independently (parallel async calls)
2. Full TOC is provided to every call for context
3. AI maps transcript content to appropriate sections
4. Outputs structured notes for each section touched by that chunk

**Model**: `openai/gpt-4.1-mini` (fast, cost-effective)

**Why this approach**:
- Keeps each API call within optimal token limits (~8K input)
- Enables parallel processing for speed
- Fresh context per chunk prevents model fatigue

#### Stage 2: Section Merging

**Purpose**: Combine partial notes from multiple chunks into coherent sections.

**Process**:
1. Group all partial notes by section title
2. For sections with multiple partials, invoke AI to merge
3. Deduplicates content, resolves conflicts, combines timestamps
4. Single-partial sections pass through unchanged

**Model**: `deepseek/deepseek-r1-0528` (strong reasoning for deduplication)

**Merge Logic**:
| Element | Merge Strategy |
|---------|----------------|
| Timestamps | Use [earliest] – [latest] range |
| Key Concepts | Combine, remove exact duplicates, order logically |
| Definitions | Keep most complete version, note conflicts |
| Key Facts | Deduplicate, flag contradictions with ⚠️ |
| Examples | Keep ALL unique examples (high exam value) |
| Exam Tips | Combine, prioritize actionable tips |

#### Stage 3: Document Assembly

**Purpose**: Reconstruct the final document with proper hierarchy.

**Process**:
1. Parse TOC into nested structure
2. Walk hierarchy, inserting merged content at leaf nodes
3. Adjust heading levels to match position in hierarchy
4. Output single markdown file

**Implementation**: Pure Python (no AI)—deterministic assembly.

---

## Technical Requirements

### Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.11+ | Core runtime |
| GitHub CLI | Latest | Authentication (`gh auth token`) |
| OpenAI package | Latest | API client (`pip install openai`) |
| GitHub Copilot Pro+ | Active subscription | Access to GitHub Models API |

### Authentication

The tool uses GitHub CLI for secure token retrieval:

```
┌─────────────────────────────────────────┐
│         Authentication Flow             │
├─────────────────────────────────────────┤
│                                         │
│  1. Check GITHUB_TOKEN env var          │
│           │                             │
│           ▼ (not set)                   │
│  2. Run: gh auth token                  │
│           │                             │
│           ▼                             │
│  3. Use returned token for API calls    │
│                                         │
└─────────────────────────────────────────┘
```

**Setup**: Simply run `gh auth login` once—no tokens in code or config files.

### API Usage

| Transcript Size | Chunks | Stage 1 Calls | Stage 2 Calls | Total Requests |
|-----------------|--------|---------------|---------------|----------------|
| 30 min video | 5 | 5 | ~8 | ~13 |
| 2 hr video | 20 | 20 | ~30 | ~50 |
| 5 hr video | 50 | 50 | ~50 | ~100 |

**Cost with Copilot Pro+**: $0 within 1,500 monthly premium requests.

---

## Installation

### 1. Clone or Download

```bash
git clone https://github.com/yourusername/exam-notes-generator.git
cd exam-notes-generator
```

### 2. Install Dependencies

```bash
pip install openai
```

### 3. Authenticate GitHub CLI

```bash
gh auth login
```

### 4. Verify Setup

```powershell
.\Generate-ExamNotes.ps1 -ContentsFile .\sample\contents.md -TranscriptZip .\sample\transcript.zip -DryRun
```

---

## Usage

### PowerShell (Recommended)

```powershell
# Basic usage
.\Generate-ExamNotes.ps1 -ContentsFile .\contents.md -TranscriptZip .\transcript.zip

# With custom output
.\Generate-ExamNotes.ps1 .\contents.md .\transcript.zip -OutputFile "AZ-104_Notes.md"

# Dry run (preview without API calls)
.\Generate-ExamNotes.ps1 .\contents.md .\transcript.zip -DryRun

# Custom models
.\Generate-ExamNotes.ps1 .\contents.md .\transcript.zip `
    -Stage1Model "openai/gpt-4.1" `
    -Stage2Model "openai/o3-mini"
```

### Python (Direct)

```bash
python exam_notes_generator.py contents.md transcript.zip -o exam_notes.md
```

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `-ContentsFile` | Yes | - | Path to TOC markdown file |
| `-TranscriptZip` | Yes | - | Path to transcript chunks ZIP |
| `-OutputFile` | No | `exam_notes.md` | Output file path |
| `-PromptsDir` | No | `./prompts` | Custom prompts directory |
| `-Stage1Model` | No | `openai/gpt-4.1-mini` | Model for chunk processing |
| `-Stage2Model` | No | `deepseek/deepseek-r1-0528` | Model for section merging |
| `-DryRun` | No | - | Preview without API calls |
| `-Force` | No | - | Overwrite existing output |

---

## Customization

### Prompt Tuning

Edit files in `prompts/` to customize output:

**Add exam-specific focus** (`prompts/chunk_process.md`):
```markdown
## Exam-Specific Focus

This is for the **AZ-104 Azure Administrator** exam. Pay special attention to:
- Azure CLI and PowerShell commands
- Portal navigation paths  
- Default values and limits
- SKU differences
```

**Adjust output format** (`prompts/section_merge.md`):
```markdown
## Additional Output Requirements

- Include Azure documentation links where relevant
- Flag deprecated features with ⚠️ DEPRECATED
- Note GA vs Preview features
```

### Model Selection

| Use Case | Stage 1 | Stage 2 |
|----------|---------|---------|
| **Balanced (default)** | `gpt-4.1-mini` | `deepseek-r1-0528` |
| **Maximum quality** | `gpt-4.1` | `deepseek-r1-0528` |
| **Fastest** | `gpt-4.1-mini` | `deepseek-v3-0324` |
| **All OpenAI** | `gpt-4.1-mini` | `o3-mini` |

---

## File Structure

```
exam-notes-generator/
├── exam_notes_generator.py    # Python core processing engine
├── Generate-ExamNotes.ps1     # PowerShell wrapper with validation
├── prompts/
│   ├── system.md              # System role prompts
│   ├── chunk_process.md       # Stage 1 extraction prompt
│   └── section_merge.md       # Stage 2 merge prompt
├── sample/                    # Sample inputs for testing
│   ├── contents.md
│   └── transcript.zip
├── .gitignore
└── README.md
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "GitHub token not found" | Run `gh auth login` to authenticate |
| "OpenAI package not installed" | Run `pip install openai` |
| "Prompts directory not found" | Ensure `prompts/` exists with required files |
| "Output file exists" | Use `-Force` to overwrite or choose different output path |
| Rate limit errors | Wait and retry; reduce parallel processing if persistent |
| Poor section mapping | Improve TOC specificity; add timestamps |
| Missing content in output | Check that chunks cover full transcript; verify no encoding issues |

---

## License

MIT License - See LICENSE file for details.

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## Acknowledgments

- Built for use with [GitHub Models API](https://docs.github.com/en/github-models)
- Powered by [GitHub Copilot Pro+](https://github.com/features/copilot)
- Inspired by the need for better exam prep tools
````

---

This README provides:

1. **Clear overview** with visual diagram
2. **Detailed input specifications** with examples
3. **Output format** with sample
4. **Architecture explanation** with stage-by-stage breakdown
5. **Installation and usage instructions**
6. **Customization guide**
7. **Troubleshooting section**

Would you like me to:
1. **Create the sample contents.md and transcript.zip** for the `sample/` directory?
2. **Add a "Workflow Examples" section** showing end-to-end usage for different exam types?
3. **Create a CONTRIBUTING.md** with development guidelines?

## @Greg-T8

Reduce this description to less than 3000 characters.

## Copilot

Here's a condensed description under 3,000 characters:

---

````markdown name=README.md
# 📚 Exam Notes Generator

Transforms video transcripts into structured, exam-focused study notes using AI. Built for certification exam prep with GitHub Copilot Pro+.

## How It Works

```
Contents File + Transcript ZIP
            │
            ▼
   ┌─────────────────────┐
   │  Stage 1: Extract   │──→ Process chunks in parallel
   │  Stage 2: Merge     │──→ Deduplicate by section  
   │  Stage 3: Assemble  │──→ Build final document
   └─────────────────────┘
            │
            ▼
   Complete Exam Notes (Markdown)
```

**Three-Stage Pipeline:**
1. **Extract**: Each 20KB transcript chunk → structured notes (parallel, fast model)
2. **Merge**: Combine partials by section, deduplicate, resolve conflicts (reasoning model)
3. **Assemble**: Rebuild hierarchy from TOC (deterministic, no AI)

## Inputs

| Input | Description |
|-------|-------------|
| `contents.md` | Table of contents with `##`/`###`/`####` headings and optional `[HH:MM:SS]` timestamps |
| `transcript.zip` | ZIP of ~20KB text chunks named sequentially (`chunk_001.txt`, etc.) |
| `prompts/` | Customizable prompt templates for tuning output |

## Output

Hierarchical markdown with per-section:
- **Key Concepts** / **Definitions** / **Key Facts**
- **Examples** (commands, configs)
- **Exam Tips 🎯**

## Quick Start

```bash
# Prerequisites
pip install openai
gh auth login

# Run
.\Generate-ExamNotes.ps1 -ContentsFile .\contents.md -TranscriptZip .\transcript.zip
```

## Key Features

- **Hybrid models**: Fast extraction (`gpt-4.1-mini`) + quality merging (`deepseek-r1-0528`)
- **Secure auth**: Uses `gh auth token`—no hardcoded secrets
- **$0 cost**: Within Copilot Pro+ 1,500 monthly requests
- **Customizable**: External prompt files for exam-specific tuning

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `-ContentsFile` | Required | TOC markdown file |
| `-TranscriptZip` | Required | Chunked transcript ZIP |
| `-OutputFile` | `exam_notes.md` | Output path |
| `-Stage1Model` | `openai/gpt-4.1-mini` | Extraction model |
| `-Stage2Model` | `deepseek/deepseek-r1-0528` | Merge model |
| `-DryRun` | - | Preview without API calls |

## Requirements

- Python 3.11+
- GitHub CLI (authenticated)
- GitHub Copilot Pro+ subscription
- `pip install openai`

## File Structure

```
├── exam_notes_generator.py   # Python core
├── Generate-ExamNotes.ps1    # PowerShell wrapper
├── prompts/                  # Customizable AI prompts
│   ├── chunk_process.md
│   └── section_merge.md
└── README.md
```

---

Built for [GitHub Models API](https://docs.github.com/en/github-models) • Powered by [Copilot Pro+](https://github.com/features/copilot)
````

---

**Character count: ~2,450** ✓

This condensed version retains:
- Architecture overview with diagram
- Input/output descriptions
- Quick start commands
- Key features and parameters
- Requirements and file structure

Would you like any sections expanded or adjusted?

## @Greg-T8

I am creating a repository for this code. Give me a short description for the repository, suitable for use in GitHub.

## Copilot

Here are three concise repository description options (pick one):

1. "Transform video transcripts into hierarchical, exam-focused study notes using GitHub Models API."

2. "AI pipeline to convert chunked video transcripts + TOC into structured, exam-ready Markdown notes."

3. "Generate organized exam study notes from transcripts using a two-stage AI (extract → merge) workflow."
