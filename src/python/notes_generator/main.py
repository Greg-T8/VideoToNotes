# -------------------------------------------------------------------------
# File: main.py
# Description: Main entry point for the Exam Notes Generator pipeline
# Context: Orchestrates normalize, chunk, extract, merge, and assemble stages
# Author: Greg Tate
# -------------------------------------------------------------------------

"""
Main entry point for the Exam Notes Generator.

Usage:
    python -m notes_generator.main --index <path> --transcript <path>

The pipeline runs these stages:
    0. Normalize - Convert varied index formats to JSON
    1. Chunk     - Split transcript into ~20KB pieces
    2. Extract   - Generate section notes from chunks (parallel, LLM)
    3. Merge     - Combine and deduplicate partials (LLM)
    4. Assemble  - Build final markdown document
"""

import argparse
import sys
from pathlib import Path

from notes_generator.models import PipelineConfig, PipelineState


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate structured exam notes from video transcripts"
    )

    parser.add_argument(
        "--index",
        type=Path,
        required=True,
        help="Path to index file (TOC with headings and timestamps)"
    )

    parser.add_argument(
        "--transcript",
        type=Path,
        required=True,
        help="Path to transcript file with timestamped content"
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path for generated notes (default: output/<title>_Exam_Notes.md)"
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

    parser.add_argument(
        "--prompts-dir",
        type=Path,
        default=None,
        help="Directory containing prompt templates (optional)"
    )

    parser.add_argument(
        "--skip-chunk",
        action="store_true",
        help="Skip chunking (use pre-chunked ZIP file as transcript input)"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output"
    )

    return parser.parse_args()


def print_stage(stage: str, message: str) -> None:
    """Print a stage progress message."""
    print(f"[{stage}] {message}")


def print_success(message: str) -> None:
    """Print a success message."""
    print(f"✓ {message}")


def print_error(message: str) -> None:
    """Print an error message."""
    print(f"✗ {message}", file=sys.stderr)


def run_pipeline(config: PipelineConfig, verbose: bool = False) -> int:
    """
    Run the notes generation pipeline.

    Args:
        config: Pipeline configuration
        verbose: Enable verbose output

    Returns:
        Exit code (0 for success)
    """
    # Initialize pipeline state
    state = PipelineState(config=config)

    try:
        # Stage 0: Normalize
        print_stage("Normalize", "Converting index to structured format...")
        state.current_stage = "normalize"

        from notes_generator.stages.normalize import normalize_index_sync

        # TODO: Initialize LLM client
        # For now, show what would happen
        print_stage("Normalize", f"Would process: {config.index_path}")
        print_stage("Normalize", "LLM client not yet implemented - skipping")

        # state.normalized_index = normalize_index_sync(
        #     Path(config.index_path),
        #     model=config.extract_model
        # )
        # print_success(f"Index normalized: {len(state.normalized_index.sections)} sections")

        # Stage 1: Chunk
        print_stage("Chunk", "Splitting transcript into chunks...")
        state.current_stage = "chunk"

        from notes_generator.stages.chunk import chunk_transcript, load_chunks_from_zip

        # TODO: Actually run chunking
        print_stage("Chunk", f"Would process: {config.transcript_path}")
        print_stage("Chunk", "Chunking not yet integrated - skipping")

        # zip_path = chunk_transcript(
        #     Path(config.transcript_path),
        #     max_chars=config.chunk_size,
        #     period_seconds=config.chunk_period
        # )
        # state.chunks = load_chunks_from_zip(zip_path)
        # print_success(f"Transcript chunked: {len(state.chunks)} chunks")

        # Stage 2: Extract
        print_stage("Extract", "Extracting notes from chunks...")
        state.current_stage = "extract"

        from notes_generator.stages.extract import extract_all_chunks_sync

        # TODO: Run extraction
        print_stage("Extract", f"Would use model: {config.extract_model}")
        print_stage("Extract", "LLM client not yet implemented - skipping")

        # state.partials = extract_all_chunks_sync(
        #     state.chunks,
        #     state.normalized_index,
        #     model=config.extract_model
        # )
        # print_success(f"Extracted: {len(state.partials)} section partials")

        # Stage 3: Merge
        print_stage("Merge", "Merging section partials...")
        state.current_stage = "merge"

        from notes_generator.stages.merge import merge_all_sections_sync

        # TODO: Run merge
        print_stage("Merge", f"Would use model: {config.merge_model}")
        print_stage("Merge", "LLM client not yet implemented - skipping")

        # state.merged_sections = merge_all_sections_sync(
        #     state.partials,
        #     state.normalized_index,
        #     model=config.merge_model
        # )
        # print_success(f"Merged: {len(state.merged_sections)} sections")

        # Stage 4: Assemble
        print_stage("Assemble", "Building final document...")
        state.current_stage = "assemble"

        from notes_generator.stages.assemble import assemble_document

        # TODO: Run assembly
        print_stage("Assemble", f"Would output to: {config.output_path}")
        print_stage("Assemble", "No merged sections to assemble - skipping")

        # assemble_document(
        #     state.normalized_index,
        #     state.merged_sections,
        #     Path(config.output_path)
        # )
        # print_success(f"Document created: {config.output_path}")

        print()
        print("=" * 60)
        print("Pipeline structure validated. LLM integration pending.")
        print("=" * 60)

        return 0

    except Exception as e:
        print_error(f"Pipeline failed at stage '{state.current_stage}': {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return 1


def main() -> int:
    """Run the notes generation pipeline."""
    args = parse_args()

    # Validate inputs
    if not args.index.exists():
        print_error(f"Index file not found: {args.index}")
        return 1

    if not args.transcript.exists():
        print_error(f"Transcript file not found: {args.transcript}")
        return 1

    # Determine output path if not specified
    output_path = args.output
    if output_path is None:
        # Generate from index filename
        title = args.index.stem.replace("Index - ", "").replace(" ", "_")
        output_path = Path("output") / f"{title}_Exam_Notes.md"

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Build configuration
    config = PipelineConfig(
        index_path=str(args.index),
        transcript_path=str(args.transcript),
        output_path=str(output_path),
        extract_model=args.extract_model,
        merge_model=args.merge_model,
        prompts_dir=str(args.prompts_dir) if args.prompts_dir else None
    )

    # Display configuration
    print()
    print("Exam Notes Generator")
    print("=" * 60)
    print(f"Index:         {config.index_path}")
    print(f"Transcript:    {config.transcript_path}")
    print(f"Output:        {config.output_path}")
    print(f"Extract Model: {config.extract_model}")
    print(f"Merge Model:   {config.merge_model}")
    print("=" * 60)
    print()

    # Run the pipeline
    return run_pipeline(config, verbose=args.verbose)


if __name__ == "__main__":
    sys.exit(main())
