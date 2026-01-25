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