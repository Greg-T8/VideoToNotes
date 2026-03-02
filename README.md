# VideoToNotes

Generate structured study notes from video transcripts and slide presentations using AI.

## Overview

Two pipelines are available depending on your source material:

### Video Notes (`New-VideoNotes.ps1`)

Transforms YouTube videos or local transcripts into comprehensive markdown notes:

1. **Transcribe** - Download YouTube video and transcribe audio via Azure Speech (optional)
2. **Normalize** - Convert varied index formats to consistent JSON (LLM)
3. **Chunk** - Split transcript into ~20KB pieces (Python)
4. **Extract** - Generate notes per section from relevant chunks (LLM)
5. **Assemble** - Build final markdown document (deterministic)

### Presentation Notes (`New-PresentationNotes.ps1`)

Transforms a PDF slide deck and video recording into annotated notes:

1. **Extract** - Render PDF pages as images and extract text per slide (Python)
2. **Transcribe** - Extract audio from the video and transcribe via Azure Speech
3. **Align** - Map transcript segments to slides using LLM
4. **Annotate** - Generate detailed notes per slide using LLM
5. **Assemble** - Build final markdown with embedded slide images

## Quick Start

### Video Notes from YouTube

```powershell
# Using GitHub Models (default)
.\New-VideoNotes.ps1 -YouTubeUrl "https://www.youtube.com/watch?v=VIDEO_ID"

# Using Azure OpenAI
.\New-VideoNotes.ps1 -YouTubeUrl "https://www.youtube.com/watch?v=VIDEO_ID" `
                     -Provider Azure `
                     -AzureEndpoint "https://<name>.cognitiveservices.azure.com/" `
                     -AzureDeployment "gpt-4.1-mini"
```

### Video Notes from Existing Files

```powershell
.\New-VideoNotes.ps1 -Index "staging\video_title\contents.md" `
                     -Transcript "staging\video_title\transcript.srt"
```

### Presentation Notes

```powershell
# From a local video file
.\New-PresentationNotes.ps1 -PdfFile "slides.pdf" -VideoFile "recording.mp4"

# From a stream URL
.\New-PresentationNotes.ps1 -PdfFile "slides.pdf" `
                             -StreamUrl "https://example.com/manifest.mpd"

# From a pre-existing transcript
.\New-PresentationNotes.ps1 -PdfFile "slides.pdf" -Transcript "transcript.srt"

# Using Azure OpenAI
.\New-PresentationNotes.ps1 -PdfFile "slides.pdf" -VideoFile "recording.mp4" `
                             -Provider Azure `
                             -AzureEndpoint "https://<name>.cognitiveservices.azure.com/" `
                             -AzureDeployment "gpt-4.1-mini"
```

## Project Structure

```
VideoToNotes/
├── New-VideoNotes.ps1              # Entry point for video notes pipeline
├── New-PresentationNotes.ps1       # Entry point for presentation notes pipeline
├── requirements.txt                # Python dependencies
├── terraform/                      # Azure infrastructure (Terraform)
│   ├── main.tf                     # Resource definitions
│   ├── variables.tf                # Input variables
│   ├── outputs.tf                  # Output values (endpoints, CLI commands)
│   ├── providers.tf                # Provider configuration (azurerm, random)
│   └── terraform.tfvars            # Variable values (non-sensitive)
├── staging/
│   └── <video_title>/              # Video-specific working folders
│       ├── contents.json           # Extracted chapters (JSON)
│       ├── contents.md             # Extracted chapters (Markdown)
│       ├── transcript.srt          # Transcribed audio (SRT format)
│       └── debug/                  # Intermediate files
├── input/                          # Manual input files
├── output/                         # Generated notes
└── src/
    ├── prompts/                    # LLM prompt templates
    │   ├── normalize.md
    │   ├── extract.md
    │   ├── merge.md
    │   ├── section_extract.md
    │   ├── targeted_extract.md
    │   ├── slide_align.md
    │   └── slide_annotate.md
    ├── powershell/
    │   ├── Split-Transcript.ps1
    │   ├── Get-YouTubeContents.ps1
    │   ├── Invoke-VideoTranscription.ps1
    │   └── Invoke-YouTubeTranscription.ps1
    └── python/
        ├── notes_generator/            # Video notes pipeline
        │   ├── main.py
        │   ├── llm_client.py           # GitHub Models + Azure OpenAI clients
        │   ├── generate_contents.py    # Fallback TOC generator
        │   ├── models.py
        │   ├── prompt_loader.py
        │   └── stages/
        │       ├── normalize.py
        │       ├── chunk.py
        │       ├── extract_by_section.py
        │       ├── merge.py
        │       ├── validate.py
        │       └── assemble.py
        └── presentation_notes/         # Presentation notes pipeline
            ├── main.py
            ├── pdf_processor.py
            ├── models.py
            ├── prompt_loader.py
            └── stages/
                ├── align.py
                ├── annotate.py
                └── assemble.py
└── tests/
```

## Prerequisites

- Python 3.10+
- PowerShell 7+ (`pwsh`)
- VS Code with recommended extensions

### For YouTube Transcription

| Tool | Purpose | Installation |
|------|---------|--------------|
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | YouTube audio download | `winget install yt-dlp` |
| [ffmpeg](https://ffmpeg.org/) | Audio conversion | `winget install ffmpeg` |
| [Azure Speech CLI](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/spx-overview) | Transcription | `dotnet tool install -g Microsoft.CognitiveServices.Speech.CLI` |

### For Azure OpenAI Provider

- Azure CLI (`az`) installed and logged in (`az login`)
- An Azure AI Services resource (see [Terraform Deployment](#terraform-deployment) below)

## Installation

The PowerShell wrapper handles environment setup automatically on first run.

Manual setup:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Or use VS Code tasks: `Ctrl+Shift+P` → "Tasks: Run Task" → "Setup: Install Dependencies"

## Terraform Deployment

The `terraform/` directory provisions all required Azure resources:

| Resource | Purpose |
|----------|---------|
| Resource Group | `project-videonotes-tf` |
| Azure AI Services | Speech transcription + OpenAI chat completions |
| GPT-4.1-mini deployment | LLM for notes extraction pipeline |
| Storage Account | Audio uploads for batch transcription |

### Deploy

```powershell
cd terraform
terraform init
terraform plan
terraform apply
```

### Configure `spx` After Deployment

After `terraform apply`, run the commands shown in the `spx_config_commands` output:

```powershell
terraform output spx_config_commands
# Run the two spx config commands it prints
```

### Get Azure Provider Arguments

```powershell
$endpoint   = terraform output -raw azure_openai_endpoint
$deployment = terraform output -raw model_deployment_name
```

Then pass them to either script with `-Provider Azure -AzureEndpoint $endpoint -AzureDeployment $deployment`.

## Usage

### `New-VideoNotes.ps1` Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `-YouTubeUrl` | Yes* | — | YouTube video URL |
| `-Index` | Yes* | — | Path to index/TOC file with timestamps |
| `-Transcript` | Yes* | — | Path to SRT transcript file |
| `-Output` | No | Auto-generated | Output path for notes |
| `-ExtractModel` | No | `gpt-4.1-mini` | Model for extraction stage |
| `-MergeModel` | No | `gpt-4.1-mini` | Model for merge stage |
| `-Language` | No | `en-US` | Language code for transcription |
| `-KeepIntermediateFiles` | No | `false` | Keep audio files after transcription |
| `-Provider` | No | `GitHub` | LLM provider: `GitHub` or `Azure` |
| `-AzureEndpoint` | No† | — | Azure OpenAI endpoint URL |
| `-AzureDeployment` | No† | — | Azure OpenAI deployment name |

\*Either `-YouTubeUrl` OR both `-Index` and `-Transcript` are required.
†Required when `-Provider Azure` is specified.

### `New-PresentationNotes.ps1` Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `-PdfFile` | Yes | — | Path to PDF slide deck |
| `-VideoFile` | Yes* | — | Path to local video file |
| `-StreamUrl` | Yes* | — | URL to a stream manifest (.mpd, .m3u8) |
| `-Transcript` | Yes* | — | Path to pre-existing SRT transcript |
| `-Output` | No | Auto-generated | Output path for notes |
| `-Model` | No | `gpt-4.1-mini` | Model for alignment and annotation |
| `-Language` | No | `en-US` | Language code for transcription |
| `-Dpi` | No | `200` | DPI for PDF rendering |
| `-KeepIntermediateFiles` | No | `false` | Keep audio files after transcription |
| `-Provider` | No | `GitHub` | LLM provider: `GitHub` or `Azure` |
| `-AzureEndpoint` | No† | — | Azure OpenAI endpoint URL |
| `-AzureDeployment` | No† | — | Azure OpenAI deployment name |

\*One of `-VideoFile`, `-StreamUrl`, or `-Transcript` is required.
†Required when `-Provider Azure` is specified.

## Input File Formats

### Index File (Video Notes)

Various formats are supported — the normalize stage uses an LLM to convert any format to structured JSON.

**FreeCodeCamp style:**

```
☁️ Introduction
🎤 (00:00:00) Introduction to AI-900
🎤 (00:08:18) Exam Guide Breakdown
```

**Simple style:**

```
00:00 - Introduction
00:15 - AI models and their knowledge
01:31 - RAG to the rescue
```

### Transcript File

SRT format (produced by Azure Speech CLI or provided externally):

```srt
1
00:00:00,000 --> 00:00:04,500
Hey, this is the introduction to the course.

2
00:00:04,500 --> 00:00:09,000
We'll cover the fundamentals today.
```

## AI Models and Providers

Both scripts support two LLM providers:

| Provider | Auth | When to Use |
|----------|------|------------|
| `GitHub` (default) | `gh` CLI token | Local development, no Azure subscription needed |
| `Azure` | `az` CLI token (managed identity-compatible) | Production, cost control, private deployments |

| Stage | Default Model | Purpose |
|-------|---------------|---------|
| Normalize | gpt-4.1-mini | Index → structured JSON |
| Extract | gpt-4.1-mini | Per-section notes generation |
| Align | gpt-4.1-mini | Slide-to-transcript mapping |
| Annotate | gpt-4.1-mini | Per-slide notes generation |

## Pipeline Stages

### Video Notes

| Stage | Input | Output | Technology |
|-------|-------|--------|-----------|
| Normalize | Raw index file | Structured JSON | LLM |
| Chunk | SRT transcript | ZIP of ~20KB chunks | Python |
| Extract | Index + chunks | Notes per section | LLM |
| Assemble | Extracted sections | Final markdown | Python |

### Presentation Notes

| Stage | Input | Output | Technology |
|-------|-------|--------|-----------|
| Extract | PDF file | Slide images + text | Python (pdf2image) |
| Transcribe | Video/stream | SRT transcript | Azure Speech CLI |
| Align | Slides + transcript | Slide-transcript mapping | LLM |
| Annotate | Slide mapping | Notes per slide | LLM |
| Assemble | Annotated slides | Final markdown | Python |

## Output Format

```markdown
### Section Title
**Timestamp**: 00:12:51 – 00:13:58

**Key Concepts**
- Concept 1

**Definitions**
- **Term 1**: Definition text

**Key Facts**
- Fact 1

**Examples**
- Example 1

**Key Takeaways 🎯**
- Tip 1
```

## Debugging

VS Code debug configurations are provided:

| Configuration | Description |
|--------------|-------------|
| PowerShell: Transcript Chunker | Debug the chunker with a sample file |
| PowerShell: Interactive Session | REPL for testing |
| Python: Current File | Debug any open Python file |
| Python: Notes Generator (Full Pipeline) | Debug the complete video notes pipeline |
| Python: Extract/Merge/Assemble Stage Only | Debug individual stages |

Press `F5` to launch the selected configuration.

## Author

Greg Tate
