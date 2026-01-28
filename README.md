# VideoToNotes

Generate structured study notes from video transcripts using AI.

## Overview

This tool transforms video transcripts into comprehensive markdown notes by:

1. **Transcribe** - Download YouTube video and transcribe audio (optional)
2. **Normalize** - Convert varied index formats to consistent JSON (LLM)
3. **Chunk** - Split transcript into ~20KB pieces (Python)
4. **Extract** - Generate notes per section from relevant chunks (LLM)
5. **Assemble** - Build final markdown document (deterministic)

## Quick Start

### From YouTube URL (Recommended)

```powershell
# Generate notes directly from a YouTube video
.\New-VideoNotes.ps1 -YouTubeUrl "https://www.youtube.com/watch?v=VIDEO_ID"
```

### From Existing Files

```powershell
# Generate notes from pre-existing index and transcript files
.\New-VideoNotes.ps1 -Index "data\video_title\contents.md" `
                     -Transcript "data\video_title\transcript.srt"
```

## Project Structure

```
VideoToNotes/
├── New-VideoNotes.ps1           # Main entry point (PowerShell wrapper)
├── requirements.txt             # Python dependencies
├── data/
│   └── <video_title>/           # Video-specific data folders
│       ├── contents.json        # Extracted video chapters (JSON)
│       ├── contents.md          # Extracted video chapters (Markdown)
│       ├── transcript.srt       # Transcribed audio (SRT format)
│       └── debug/               # Debug output (intermediate files)
├── input/                       # Manual input files
├── output/                      # Generated notes
│   └── debug/                   # Debug output for file-based runs
├── src/
│   ├── prompts/                 # LLM prompt templates
│   │   ├── normalize.md         # Index → JSON conversion
│   │   ├── extract.md           # Section → notes extraction
│   │   ├── merge.md             # Partials → merged section
│   │   ├── section_extract.md   # Per-section extraction
│   │   └── targeted_extract.md  # Targeted re-extraction
│   ├── powershell/
│   │   ├── Split-Transcript.ps1         # Transcript splitting utility
│   │   ├── Get-YouTubeContents.ps1      # Extract video chapters/TOC
│   │   └── Invoke-YouTubeTranscription.ps1  # Download & transcribe audio
│   └── python/
│       └── notes_generator/
│           ├── __init__.py
│           ├── main.py              # Python CLI (called by wrapper)
│           ├── llm_client.py        # LLM API client (GitHub Models)
│           ├── models.py            # Data classes
│           ├── prompt_loader.py     # Load prompts from .md files
│           └── stages/
│               ├── __init__.py
│               ├── normalize.py         # Stage 0: Index normalization
│               ├── chunk.py             # Stage 1: Transcript chunking
│               ├── extract_by_section.py  # Stage 2: Per-section extraction
│               ├── extract.py           # Legacy chunk-based extraction
│               ├── merge.py             # Legacy merge stage
│               ├── validate.py          # Input validation
│               └── assemble.py          # Stage 3: Document assembly
└── tests/                       # Test suite
```

## Prerequisites

- Python 3.10+
- PowerShell 7+ (pwsh)
- VS Code with recommended extensions

### For YouTube Transcription (Optional)

| Tool | Purpose | Installation |
|------|---------|--------------|
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | YouTube audio download | `winget install yt-dlp` |
| [ffmpeg](https://ffmpeg.org/) | Audio conversion | `winget install ffmpeg` |
| [Azure Speech CLI](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/spx-overview) | Transcription | `dotnet tool install -g Microsoft.CognitiveServices.Speech.CLI` |

You'll also need an Azure Speech Services resource configured with the `spx` CLI.

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
.\New-VideoNotes.ps1 -Index "path\to\index.txt" -Transcript "path\to\transcript.txt"
```

### With Custom Output

```powershell
.\New-VideoNotes.ps1 -Index "path\to\index.txt" `
                     -Transcript "path\to\transcript.txt" `
                     -Output "output\MyNotes.md"
```

### With Custom Models

```powershell
.\New-VideoNotes.ps1 -Index "path\to\index.txt" `
                     -Transcript "path\to\transcript.txt" `
                     -ExtractModel "gpt-4o" `
                     -MergeModel "gpt-4o"
```

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `-YouTubeUrl` | Yes* | - | YouTube video URL to process |
| `-Index` | Yes* | - | Path to index/TOC file with timestamps |
| `-Transcript` | Yes* | - | Path to transcript file |
| `-Output` | No | Auto-generated | Output path for notes |
| `-ExtractModel` | No | gpt-4.1-mini | Model for extraction stage |
| `-MergeModel` | No | gpt-4.1-mini | Model for merge stage |
| `-Language` | No | en-US | Language code for transcription |
| `-KeepIntermediateFiles` | No | false | Keep audio files after transcription |

*Either `-YouTubeUrl` OR both `-Index` and `-Transcript` are required.

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

- **Input**: Transcript file (SRT format)
- **Output**: ZIP file with ~20KB text chunks
- **Technology**: Python (chunk.py)

### Stage 2: Extract (Per-Section)

- **Input**: Normalized index + All chunks
- **Output**: Notes for each section
- **Model**: gpt-4.1-mini
- **Description**: For each leaf section, identifies relevant chunks by timestamp range and extracts focused notes

### Stage 3: Assemble

- **Input**: Extracted sections + Normalized index
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

**Key Takeaways 🎯**
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
| Extract | gpt-4.1-mini | Per-section notes extraction |

Models are accessed via [GitHub Models](https://github.com/marketplace/models) using the GitHub CLI for authentication.

## Author

Greg Tate
