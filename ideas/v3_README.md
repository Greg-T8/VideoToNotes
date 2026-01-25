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

## Licensea

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