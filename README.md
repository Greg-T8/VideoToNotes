# Exam Notes Generator

Generate structured, exam-focused study notes from video transcripts using AI.

## Overview

This tool transforms video transcripts into comprehensive markdown notes by:

1. **Normalize** - Convert varied index formats to consistent JSON (LLM)
2. **Chunk** - Split transcript into ~20KB pieces (PowerShell)
3. **Extract** - Generate section notes from chunks in parallel (LLM)
4. **Merge** - Combine and deduplicate partials by section (LLM)
5. **Assemble** - Build final markdown document (deterministic)

## Quick Start

```powershell
# Generate notes from a video transcript
.\New-ExamNotes.ps1 -Index "data\samples\AI-900_FreeCodeCamp\Index - FreeCodeCamp.txt" `
                    -Transcript "data\samples\AI-900_FreeCodeCamp\Transcript - FreeCodeCamp.txt"
```

## Project Structure

```
Exam-Notes-Generator/
├── New-ExamNotes.ps1            # Main entry point (PowerShell wrapper)
├── requirements.txt             # Python dependencies
├── data/
│   └── samples/                 # Sample input files
│       ├── AI-900_FreeCodeCamp/
│       │   ├── Index - FreeCodeCamp.txt
│       │   └── Transcript - FreeCodeCamp.txt
│       └── Deep_Dive_Into_Foundry_IQ/
│           ├── Index - Deep Dive into Foundry IQ.txt
│           └── Transcript - Deep Dive into Foundry IQ.txt
├── output/                      # Generated notes
├── prompts/                     # LLM prompt templates
│   ├── normalize.md             # Index → JSON conversion
│   ├── extract.md               # Chunk → section notes
│   └── merge.md                 # Partials → merged section
├── src/
│   ├── powershell/
│   │   └── transcript_chunker.ps1   # Transcript splitting utility
│   └── python/
│       └── notes_generator/
│           ├── __init__.py
│           ├── main.py              # Python CLI (called by wrapper)
│           ├── models.py            # Data classes
│           └── stages/
│               ├── __init__.py
│               ├── normalize.py     # Stage 0: Index normalization
│               ├── chunk.py         # Stage 1: Transcript chunking
│               ├── extract.py       # Stage 2: Notes extraction
│               ├── merge.py         # Stage 3: Section merging
│               └── assemble.py      # Stage 4: Document assembly
└── ideas/                       # Reference materials from design
```

## Prerequisites

- Python 3.10+
- PowerShell 7+ (pwsh)
- VS Code with recommended extensions

## Installation

The PowerShell wrapper handles environment setup automatically on first run.

Manual setup:

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

Or use VS Code tasks: `Ctrl+Shift+P` → "Tasks: Run Task" → "Setup: Install Dependencies"

## Usage

### Basic Usage

```powershell
.\New-ExamNotes.ps1 -Index "path\to\index.txt" -Transcript "path\to\transcript.txt"
```

### With Custom Output

```powershell
.\New-ExamNotes.ps1 -Index "path\to\index.txt" `
                    -Transcript "path\to\transcript.txt" `
                    -Output "output\MyNotes.md"
```

### With Custom Models

```powershell
.\New-ExamNotes.ps1 -Index "path\to\index.txt" `
                    -Transcript "path\to\transcript.txt" `
                    -ExtractModel "gpt-4o" `
                    -MergeModel "gpt-4o"
```

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `-Index` | Yes | - | Path to index/TOC file with timestamps |
| `-Transcript` | Yes | - | Path to transcript file |
| `-Output` | No | Auto-generated | Output path for notes |
| `-ExtractModel` | No | gpt-4.1-mini | Model for extraction stage |
| `-MergeModel` | No | deepseek-r1 | Model for merge stage |

## Input File Formats

### Index File

The index file contains the table of contents with timestamps. Various formats are supported:

**Format 1 (FreeCodeCamp style):**

```
☁️ Introduction
🎤 (00:00:00) Introduction to AI-900
🎤 (00:08:18) Exam Guide Breakdown

☁️ ML Introduction
🎤 (00:12:51) Layers of Machine Learning
```

**Format 2 (Simple style):**

```
00:00 - Introduction
00:15 - AI models and their knowledge
01:31 - RAG to the rescue
```

The normalize stage uses an LLM to convert any format to a consistent structure.

### Transcript File

Timestamped transcript content:

```
00:00:00
hey this is Andrew Brown and I'm bringing you another certification course...

00:00:28
additional uh paid materials where you can get access...
```

## Pipeline Stages

### Stage 0: Normalize

- **Input**: Raw index file (varied formats)
- **Output**: Structured JSON with hierarchy
- **Model**: gpt-4.1-mini

### Stage 1: Chunk

- **Input**: Transcript file
- **Output**: ZIP file with ~20KB text chunks
- **Technology**: PowerShell (transcript_chunker.ps1)

### Stage 2: Extract

- **Input**: Chunks + Normalized index
- **Output**: Section partials (notes per chunk)
- **Model**: gpt-4.1-mini (parallel processing)

### Stage 3: Merge

- **Input**: Section partials
- **Output**: Merged sections (deduplicated)
- **Model**: deepseek-r1 (reasoning)

### Stage 4: Assemble

- **Input**: Merged sections + Index
- **Output**: Final markdown document
- **Technology**: Python (deterministic)

## Output Format

Each section in the generated notes follows this structure:

```markdown
### Section Title
**Timestamp**: 00:12:51 – 00:13:58

**Key Concepts**
- Concept 1
- Concept 2

**Definitions**
- **Term 1**: Definition text

**Key Facts**
- Fact 1
- Fact 2

**Examples**
- Example 1

**Exam Tips 🎯**
- Tip 1
```

## Debugging

The project includes VS Code debug configurations:

| Configuration | Description |
|--------------|-------------|
| PowerShell: Transcript Chunker | Debug the chunker with a sample file |
| PowerShell: Interactive Session | REPL for testing |
| Python: Current File | Debug any open Python file |
| Python: Notes Generator (Full Pipeline) | Debug the complete pipeline |
| Python: Extract/Merge/Assemble Stage Only | Debug individual stages |

Press `F5` to start debugging with the selected configuration.

## AI Models

| Stage | Default Model | Purpose |
|-------|---------------|---------|
| Normalize | gpt-4.1-mini | Fast, structured output |
| Extract | gpt-4.1-mini | Parallel chunk processing |
| Merge | deepseek-r1 | Reasoning for deduplication |

## Author

Greg Tate
