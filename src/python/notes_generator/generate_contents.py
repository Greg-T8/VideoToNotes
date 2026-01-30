# -------------------------------------------------------------------------
# Program: generate_contents.py
# Description: Generate table of contents from transcript using LLM
# Context: VideoToNotes pipeline - fallback when YouTube has no chapters
# Author: Greg Tate
# -------------------------------------------------------------------------
"""
Generate Table of Contents from Transcript

This script analyzes a transcript file and generates a structured table of
contents with timestamps using an LLM. It is used as a fallback when the
YouTube video description does not contain chapter information.

Usage:
    python -m notes_generator.generate_contents \
        --transcript <path.srt> \
        --title "Video Title" \
        --channel "Channel Name" \
        --duration 3600 \
        --output <output.json>
"""

import argparse
import asyncio
import json
import re
import sys
from pathlib import Path

# Add parent directory to path for imports when run as script
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

from notes_generator.llm_client import GitHubModelsClient, ChatMessage
from notes_generator.prompt_loader import load_prompt


def parse_srt(srt_content: str) -> str:
    """
    Parse SRT content and return simplified text with timestamps.

    Args:
        srt_content: Raw SRT file content

    Returns:
        Simplified transcript with timestamps
    """
    lines = []
    current_time = None

    for line in srt_content.split('\n'):
        line = line.strip()

        # Skip empty lines and sequence numbers
        if not line or line.isdigit():
            continue

        # Parse timestamp line
        if '-->' in line:
            # Extract start time: "00:00:00,000 --> 00:00:02,500"
            match = re.match(r'(\d{2}):(\d{2}):(\d{2})', line)
            if match:
                h, m, s = match.groups()
                current_time = f"{h}:{m}:{s}"
            continue

        # This is a text line
        if current_time and line:
            lines.append(f"[{current_time}] {line}")
            current_time = None

    return '\n'.join(lines)


def format_duration(seconds: int) -> str:
    """Format duration in seconds to HH:MM:SS."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


async def generate_contents(
    transcript_path: Path,
    title: str,
    channel: str,
    duration: int,
    model: str = "gpt-4.1-mini"
) -> dict:
    """
    Generate table of contents from transcript.

    Args:
        transcript_path: Path to SRT transcript file
        title: Video title
        channel: Channel name
        duration: Video duration in seconds
        model: LLM model to use

    Returns:
        Dictionary with generated sections
    """
    # Read and parse transcript
    srt_content = transcript_path.read_text(encoding="utf-8")
    transcript_text = parse_srt(srt_content)

    # For long transcripts, sample to avoid token limits
    # Take beginning, middle, and end portions
    lines = transcript_text.split('\n')
    if len(lines) > 500:
        # Sample: first 150, middle 200, last 150 lines
        sampled = lines[:150] + ['...'] + lines[len(lines)//2 - 100:len(lines)//2 + 100] + ['...'] + lines[-150:]
        transcript_text = '\n'.join(sampled)

    # Load prompt template
    prompt_template = load_prompt("generate_contents")

    # Fill in template
    prompt = prompt_template.format(
        video_title=title,
        channel=channel,
        duration=format_duration(duration),
        transcript=transcript_text
    )

    # Call LLM
    client = GitHubModelsClient()

    response = await client.chat(
        messages=[ChatMessage(role="user", content=prompt)],
        model=model,
        temperature=0.3
    )

    # Parse JSON response
    response_text = response.strip()

    # Remove markdown code fences if present
    if response_text.startswith("```"):
        response_text = re.sub(r'^```\w*\n?', '', response_text)
        response_text = re.sub(r'\n?```$', '', response_text)

    try:
        result = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"Error parsing LLM response: {e}", file=sys.stderr)
        print(f"Response was: {response_text[:500]}...", file=sys.stderr)
        raise

    return result


def convert_to_contents_format(
    generated: dict,
    title: str,
    channel: str,
    duration: int,
    url: str
) -> dict:
    """
    Convert LLM output to the standard contents.json format.

    Args:
        generated: Dictionary with "sections" from LLM
        title: Video title
        channel: Channel name
        duration: Video duration in seconds
        url: YouTube URL

    Returns:
        Dictionary in contents.json format
    """
    chapters = []

    for section in generated.get("sections", []):
        # Parse timestamp to seconds
        ts = section.get("timestamp", "00:00:00")
        parts = ts.split(":")

        if len(parts) == 3:
            seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:
            seconds = int(parts[0]) * 60 + int(parts[1])
        else:
            seconds = 0

        chapters.append({
            "title": section.get("title", "Untitled"),
            "startTime": seconds,
            "timestamp": ts,
            "level": section.get("level", 2)
        })

    return {
        "title": title,
        "channel": channel,
        "duration": duration,
        "url": url,
        "chaptersSource": "generated",
        "chapters": chapters
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate table of contents from transcript"
    )

    parser.add_argument(
        "--transcript",
        type=Path,
        required=True,
        help="Path to SRT transcript file"
    )

    parser.add_argument(
        "--title",
        type=str,
        required=True,
        help="Video title"
    )

    parser.add_argument(
        "--channel",
        type=str,
        required=True,
        help="Channel name"
    )

    parser.add_argument(
        "--duration",
        type=int,
        required=True,
        help="Video duration in seconds"
    )

    parser.add_argument(
        "--url",
        type=str,
        default="",
        help="YouTube URL"
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output path for generated contents.json"
    )

    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4.1-mini",
        help="LLM model to use (default: gpt-4.1-mini)"
    )

    args = parser.parse_args()

    # Validate input
    if not args.transcript.exists():
        print(f"Error: Transcript file not found: {args.transcript}", file=sys.stderr)
        sys.exit(1)

    # Generate contents
    print(f"Generating table of contents from transcript...")
    print(f"  Title: {args.title}")
    print(f"  Duration: {format_duration(args.duration)}")

    generated = asyncio.run(generate_contents(
        transcript_path=args.transcript,
        title=args.title,
        channel=args.channel,
        duration=args.duration,
        model=args.model
    ))

    # Convert to contents format
    contents = convert_to_contents_format(
        generated=generated,
        title=args.title,
        channel=args.channel,
        duration=args.duration,
        url=args.url
    )

    # Save JSON output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(contents, indent=2), encoding="utf-8")

    print(f"[OK] Generated {len(contents['chapters'])} sections")
    print(f"  Output: {args.output}")


if __name__ == "__main__":
    main()
