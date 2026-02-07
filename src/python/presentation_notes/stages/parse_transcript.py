# -------------------------------------------------------------------------
# File: parse_transcript.py
# Description: Parse SRT transcript files into timestamped segments
# Context: PresentationNotes pipeline - transcript parsing stage
# Author: Greg Tate
# -------------------------------------------------------------------------

"""
Parse Transcript Stage

Reads an SRT subtitle file and converts it into a list of timestamped
text segments. These segments are later aligned to individual slides.
"""

import re
from pathlib import Path
from typing import List
from dataclasses import dataclass


@dataclass
class TranscriptSegment:
    """A single timestamped segment from an SRT file."""

    index: int
    start_time: str  # HH:MM:SS format
    end_time: str  # HH:MM:SS format
    start_seconds: float
    end_seconds: float
    text: str

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "index": self.index,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "start_seconds": self.start_seconds,
            "end_seconds": self.end_seconds,
            "text": self.text
        }


def parse_srt(srt_path: Path) -> List[TranscriptSegment]:
    """
    Parse an SRT subtitle file into transcript segments.

    Args:
        srt_path: Path to the .srt file

    Returns:
        List of TranscriptSegment objects in chronological order
    """

    content = srt_path.read_text(encoding="utf-8-sig")

    # Normalize line endings
    content = content.replace("\r\n", "\n").replace("\r", "\n")

    # Split into SRT blocks (separated by blank lines)
    blocks = re.split(r"\n\n+", content.strip())

    segments: List[TranscriptSegment] = []

    for block in blocks:
        segment = _parse_srt_block(block.strip())

        # Skip empty or invalid blocks
        if segment is not None:
            segments.append(segment)

    # Sort by start time
    segments.sort(key=lambda s: s.start_seconds)

    print(f"  Parsed {len(segments)} transcript segments from SRT")
    return segments


def consolidate_segments(
    segments: List[TranscriptSegment],
    period_seconds: int = 30
) -> List[TranscriptSegment]:
    """
    Consolidate small segments into larger time-based groups.

    SRT files often have very short segments (a few words each).
    This groups them into larger periods for more meaningful alignment.

    Args:
        segments: List of parsed TranscriptSegment objects
        period_seconds: Target period length in seconds (default 30)

    Returns:
        List of consolidated TranscriptSegment objects
    """

    if not segments:
        return []

    consolidated: List[TranscriptSegment] = []
    current_texts: List[str] = []
    current_start = segments[0]
    period_start_seconds = segments[0].start_seconds

    for seg in segments:

        # Check if this segment starts a new period
        if seg.start_seconds - period_start_seconds >= period_seconds and current_texts:

            # Flush current period
            consolidated.append(TranscriptSegment(
                index=len(consolidated) + 1,
                start_time=current_start.start_time,
                end_time=seg.start_time,
                start_seconds=current_start.start_seconds,
                end_seconds=seg.start_seconds,
                text=" ".join(current_texts)
            ))

            # Start new period
            current_texts = [seg.text]
            current_start = seg
            period_start_seconds = seg.start_seconds
        else:
            current_texts.append(seg.text)

    # Flush final period
    if current_texts:
        last = segments[-1]
        consolidated.append(TranscriptSegment(
            index=len(consolidated) + 1,
            start_time=current_start.start_time,
            end_time=last.end_time,
            start_seconds=current_start.start_seconds,
            end_seconds=last.end_seconds,
            text=" ".join(current_texts)
        ))

    print(f"  Consolidated into {len(consolidated)} segments ({period_seconds}s periods)")
    return consolidated


def segments_to_text(segments: List[TranscriptSegment]) -> str:
    """
    Convert transcript segments to a single timestamped text block.

    Args:
        segments: List of TranscriptSegment objects

    Returns:
        Formatted text with timestamps
    """

    lines = []

    for seg in segments:
        lines.append(f"[{seg.start_time} - {seg.end_time}] {seg.text}")

    return "\n".join(lines)


def get_segments_in_range(
    segments: List[TranscriptSegment],
    start_seconds: float,
    end_seconds: float
) -> List[TranscriptSegment]:
    """
    Get all segments that overlap with a given time range.

    Args:
        segments: List of TranscriptSegment objects
        start_seconds: Range start in seconds
        end_seconds: Range end in seconds

    Returns:
        List of segments that overlap with the range
    """

    return [
        s for s in segments
        if s.end_seconds > start_seconds and s.start_seconds < end_seconds
    ]


def _parse_srt_block(block: str) -> TranscriptSegment | None:
    """
    Parse a single SRT block into a TranscriptSegment.

    Expected format:
        1
        00:00:01,234 --> 00:00:05,678
        Text content here

    Args:
        block: A single SRT subtitle block

    Returns:
        TranscriptSegment or None if the block is invalid
    """

    lines = block.split("\n")

    if len(lines) < 3:
        return None

    # First line: sequence number
    try:
        index = int(lines[0].strip())
    except ValueError:
        return None

    # Second line: timestamp range
    timestamp_match = re.match(
        r"(\d{2}:\d{2}:\d{2}),\d{3}\s*-->\s*(\d{2}:\d{2}:\d{2}),\d{3}",
        lines[1].strip()
    )

    if not timestamp_match:
        return None

    start_time = timestamp_match.group(1)
    end_time = timestamp_match.group(2)

    # Remaining lines: text content
    text = " ".join(line.strip() for line in lines[2:] if line.strip())

    if not text:
        return None

    return TranscriptSegment(
        index=index,
        start_time=start_time,
        end_time=end_time,
        start_seconds=_timestamp_to_seconds(start_time),
        end_seconds=_timestamp_to_seconds(end_time),
        text=text
    )


def _timestamp_to_seconds(ts: str) -> float:
    """
    Convert HH:MM:SS timestamp to total seconds.

    Args:
        ts: Timestamp string in HH:MM:SS format

    Returns:
        Total seconds as float
    """

    parts = ts.split(":")

    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    elif len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])

    return 0.0
