# -------------------------------------------------------------------------
# File: main.py
# Description: Main entry point for the Exam Notes Generator pipeline
# Context: Orchestrates extract, merge, and assemble stages
# Author: Greg Tate
# -------------------------------------------------------------------------

"""
Main entry point for the Exam Notes Generator.

Usage:
    python -m notes_generator.main --contents <path> --chunks <path>
"""

import argparse
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate structured notes from video transcripts"
    )

    parser.add_argument(
        "--contents",
        type=Path,
        required=True,
        help="Path to contents.md (TOC with headings and timestamps)"
    )

    parser.add_argument(
        "--chunks",
        type=Path,
        required=True,
        help="Path to transcript.zip (20KB text chunks)"
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/notes.md"),
        help="Output path for generated notes (default: output/notes.md)"
    )

    parser.add_argument(
        "--extract-model",
        type=str,
        default="gpt-4.1-mini",
        help="Model for extraction stage (default: gpt-4.1-mini)"
    )

    parser.add_argument(
        "--merge-model",
        type=str,
        default="deepseek-r1",
        help="Model for merge stage (default: deepseek-r1)"
    )

    return parser.parse_args()


def main() -> int:
    """Run the notes generation pipeline."""
    args = parse_args()

    # Validate inputs
    if not args.contents.exists():
        print(f"Error: Contents file not found: {args.contents}", file=sys.stderr)
        return 1

    if not args.chunks.exists():
        print(f"Error: Chunks file not found: {args.chunks}", file=sys.stderr)
        return 1

    # Ensure output directory exists
    args.output.parent.mkdir(parents=True, exist_ok=True)

    print(f"Contents: {args.contents}")
    print(f"Chunks: {args.chunks}")
    print(f"Output: {args.output}")
    print(f"Extract model: {args.extract_model}")
    print(f"Merge model: {args.merge_model}")

    # TODO: Implement pipeline stages
    # 1. Extract: Process chunks in parallel
    # 2. Merge: Combine and deduplicate by section
    # 3. Assemble: Build final document

    print("\nPipeline not yet implemented.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
