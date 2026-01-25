# Exam Notes Generator

A three-stage pipeline for generating structured study notes from video transcripts.

## Overview

This tool processes video transcripts and generates organized, exam-focused notes by:

1. **Extract** - Process 20KB transcript chunks into structured notes (parallel, fast model)
2. **Merge** - Combine partials by section, deduplicate (reasoning model)
3. **Assemble** - Build final document from TOC (deterministic)

## Project Structure

```
Exam-Notes-Generator/
├── .vscode/                 # VS Code configuration
│   ├── launch.json          # Debug configurations
│   ├── tasks.json           # Build/test tasks
│   ├── settings.json        # Workspace settings
│   └── extensions.json      # Recommended extensions
├── data/
│   └── samples/             # Sample transcript files
├── output/                  # Generated notes
├── src/
│   ├── powershell/
│   │   └── transcript_chunker.ps1   # Splits transcripts into chunks
│   └── python/
│       └── notes_generator/
│           ├── main.py              # Pipeline entry point
│           └── stages/
│               ├── extract.py       # Stage 1: Chunk → Notes
│               ├── merge.py         # Stage 2: Deduplicate
│               └── assemble.py      # Stage 3: Build document
├── tests/                   # Unit tests
├── requirements.txt         # Python dependencies
└── README.md
```

## Prerequisites

- Python 3.10+
- PowerShell 7+ (pwsh)
- VS Code with recommended extensions

## Setup

1. **Create virtual environment:**

   ```powershell
   python -m venv .venv
   ```

2. **Activate virtual environment:**

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**

   ```powershell
   pip install -r requirements.txt
   ```

Or use VS Code tasks: `Ctrl+Shift+P` → "Tasks: Run Task" → "Setup: Install Dependencies"

## Usage

### Step 1: Chunk the Transcript (PowerShell)

```powershell
pwsh -File src/powershell/transcript_chunker.ps1 -InputFile "data/samples/Transcript - FreeCodeCamp.txt"
```

This produces a ZIP file containing 20KB text chunks.

### Step 2: Generate Notes (Python)

```powershell
python -m notes_generator.main --contents data/samples/contents.md --chunks data/samples/transcript.zip
```

## Debugging

The project includes VS Code debug configurations for both PowerShell and Python:

| Configuration | Description |
|--------------|-------------|
| PowerShell: Transcript Chunker | Debug the chunker with a sample file |
| PowerShell: Interactive Session | REPL for testing |
| Python: Current File | Debug any open Python file |
| Python: Notes Generator (Full Pipeline) | Debug the complete pipeline |
| Python: Extract/Merge/Assemble Stage Only | Debug individual stages |
| Python: Run Tests | Debug pytest execution |

Press `F5` to start debugging with the selected configuration.

## Running Tests

```powershell
pytest tests/ -v
```

Or use VS Code task: "Python: Run Tests"

## Architecture

### Input Files

- **contents.md** - Table of contents with headings and timestamps
- **transcript.zip** - 20KB text chunks from the transcript chunker

### AI Models

- **Extract Stage**: gpt-4.1-mini (fast, parallel processing)
- **Merge Stage**: deepseek-r1 (reasoning for deduplication)
- **Assemble Stage**: No LLM (deterministic)

### Authentication

Uses GitHub CLI for authentication (no hardcoded secrets).

## Author

Greg Tate
