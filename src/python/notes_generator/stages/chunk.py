# -------------------------------------------------------------------------
# File: chunk.py
# Description: Chunk stage - split transcript into processable chunks
# Context: Stage 1 of the Exam Notes Generator pipeline
# Author: Greg Tate
# -------------------------------------------------------------------------

"""
Chunk Stage

Wraps the PowerShell transcript_chunker.ps1 script to split transcripts
into ~20KB chunks suitable for LLM processing.

The PowerShell script handles:
- Timestamp detection (MM:SS and HH:MM:SS formats)
- Period consolidation (20-second blocks)
- Character limit enforcement
- ZIP archive creation
"""

import subprocess
import tempfile
import zipfile
import re
from pathlib import Path
from typing import List, Optional

from notes_generator.models import TranscriptChunk


def chunk_transcript(
    transcript_path: Path,
    output_dir: Optional[Path] = None,
    max_chars: int = 20000,
    period_seconds: int = 20,
    chunker_script: Optional[Path] = None
) -> Path:
    """
    Split a transcript file into chunks using the PowerShell chunker.

    Args:
        transcript_path: Path to the transcript file
        output_dir: Directory for output (default: temp directory)
        max_chars: Maximum characters per chunk (default: 20000)
        period_seconds: Consolidation period in seconds (default: 20)
        chunker_script: Path to transcript_chunker.ps1 (auto-detected if None)

    Returns:
        Path to the ZIP file containing chunks
    """
    # Resolve chunker script path
    if chunker_script is None:
        # Look relative to this file
        this_dir = Path(__file__).parent.parent.parent.parent  # src/python/notes_generator/stages -> src
        chunker_script = this_dir / "powershell" / "transcript_chunker.ps1"

    if not chunker_script.exists():
        raise FileNotFoundError(f"Chunker script not found: {chunker_script}")

    # Create output directory if needed
    if output_dir is None:
        output_dir = Path(tempfile.mkdtemp(prefix="transcript_chunks_"))
    else:
        output_dir.mkdir(parents=True, exist_ok=True)

    # Build PowerShell command
    cmd = [
        "pwsh",
        "-File", str(chunker_script),
        "-InputFile", str(transcript_path),
        "-MaxChars", str(max_chars),
        "-PeriodSeconds", str(period_seconds),
        "-OutDir", str(output_dir)
    ]

    # Run the chunker
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Chunker failed with exit code {result.returncode}:\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )

    # Find the ZIP file in parent of output directory (where chunker creates it)
    parent_dir = output_dir.parent
    zip_files = list(parent_dir.glob("*.zip"))
    if not zip_files:
        raise FileNotFoundError(f"No ZIP file created in {parent_dir}")

    # Return the most recently created ZIP
    return max(zip_files, key=lambda p: p.stat().st_mtime)


def load_chunks_from_zip(zip_path: Path) -> List[TranscriptChunk]:
    """
    Load transcript chunks from a ZIP archive.

    Args:
        zip_path: Path to the ZIP file containing chunks

    Returns:
        List of TranscriptChunk objects, ordered by chunk_id
    """
    chunks = []

    with zipfile.ZipFile(zip_path, 'r') as zf:
        # Get list of chunk files
        chunk_files = sorted([
            name for name in zf.namelist()
            if name.endswith('.txt') and not name.startswith('__')
        ])

        for idx, filename in enumerate(chunk_files, start=1):
            content = zf.read(filename).decode('utf-8')

            # Extract timestamps from content
            start_ts, end_ts = extract_timestamp_range(content)

            chunks.append(TranscriptChunk(
                chunk_id=idx,
                text=content,
                start_timestamp=start_ts,
                end_timestamp=end_ts,
                file_path=filename
            ))

    return chunks


def extract_timestamp_range(text: str) -> tuple[str, str]:
    """
    Extract the first and last timestamps from chunk text.

    Args:
        text: The chunk text content

    Returns:
        Tuple of (start_timestamp, end_timestamp) in HH:MM:SS format
    """
    # Pattern matches MM:SS or HH:MM:SS at start of line
    pattern = r'^(\d{1,2}:\d{2}(?::\d{2})?)'
    matches = re.findall(pattern, text, re.MULTILINE)

    if not matches:
        return "00:00:00", "00:00:00"

    start_ts = normalize_timestamp(matches[0])
    end_ts = normalize_timestamp(matches[-1])

    return start_ts, end_ts


def normalize_timestamp(ts: str) -> str:
    """
    Normalize a timestamp to HH:MM:SS format.

    Args:
        ts: Timestamp in MM:SS or HH:MM:SS format

    Returns:
        Timestamp in HH:MM:SS format
    """
    parts = ts.split(':')

    if len(parts) == 2:
        # MM:SS -> 00:MM:SS
        return f"00:{int(parts[0]):02d}:{int(parts[1]):02d}"
    elif len(parts) == 3:
        # HH:MM:SS -> HH:MM:SS (normalized)
        return f"{int(parts[0]):02d}:{int(parts[1]):02d}:{int(parts[2]):02d}"
    else:
        return "00:00:00"


def chunks_to_toc_context(chunks: List[TranscriptChunk]) -> str:
    """
    Generate a summary of chunks for context.

    Args:
        chunks: List of transcript chunks

    Returns:
        Summary string
    """
    lines = [f"Total chunks: {len(chunks)}", ""]

    for chunk in chunks:
        lines.append(
            f"Chunk {chunk.chunk_id}: {chunk.start_timestamp} – {chunk.end_timestamp} "
            f"({len(chunk.text):,} chars)"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    # Allow running this stage directly for debugging
    print("Chunk stage - run with debugger for testing")

    # Example: test with sample file
    sample_path = Path("data/samples/AI-900_FreeCodeCamp/Transcript - FreeCodeCamp.txt")
    if sample_path.exists():
        print(f"Sample file found: {sample_path}")
        print(f"File size: {sample_path.stat().st_size:,} bytes")
