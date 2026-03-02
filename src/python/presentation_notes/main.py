# -------------------------------------------------------------------------
# File: main.py
# Description: Main entry point for the presentation notes pipeline
# Context: Orchestrates PDF extraction, alignment, annotation, and assembly
# Author: Greg Tate
# -------------------------------------------------------------------------

"""
Main entry point for PresentationNotes.

Usage:
    python -m presentation_notes.main \
        --pdf <path.pdf> \
        --transcript <path.srt> \
        --output <output.md>

The pipeline runs these stages:
    0. Extract   - Render PDF pages as images, extract text per slide
    1. Parse     - Parse SRT transcript into timestamped segments
    2. Align     - Map transcript segments to slides (LLM)
    3. Annotate  - Generate detailed notes per slide (LLM)
    4. Assemble  - Build final markdown with embedded slide images
"""

import argparse
import json
import sys
from pathlib import Path

from presentation_notes.models import PresentationConfig, PresentationState


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Generate presentation notes from PDF slides and transcript"
    )

    parser.add_argument(
        "--pdf",
        type=Path,
        required=True,
        help="Path to the PDF slide presentation"
    )

    parser.add_argument(
        "--transcript",
        type=Path,
        required=True,
        help="Path to the SRT transcript file"
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path for generated notes (default: output/<title>_Notes.md)"
    )

    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4.1-mini",
        help="LLM model for alignment and annotation (default: gpt-4.1-mini)"
    )

    parser.add_argument(
        "--title",
        type=str,
        default=None,
        help="Presentation title (default: extracted from PDF metadata)"
    )

    parser.add_argument(
        "--dpi",
        type=int,
        default=200,
        help="DPI for PDF rendering (default: 200)"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Save intermediate outputs for debugging"
    )

    parser.add_argument(
        "--debug-dir",
        type=Path,
        default=None,
        help="Directory for debug output (default: output/debug)"
    )

    parser.add_argument(
        "--provider",
        type=str,
        choices=["github", "azure"],
        default="github",
        help="LLM provider: github (default) or azure"
    )

    parser.add_argument(
        "--azure-endpoint",
        type=str,
        default=None,
        help="Azure OpenAI endpoint URL (required when provider is azure)"
    )

    parser.add_argument(
        "--azure-deployment",
        type=str,
        default=None,
        help="Azure OpenAI deployment name (required when provider is azure)"
    )

    return parser.parse_args()


def print_stage(stage: str, message: str) -> None:
    """Print a stage progress message."""
    print(f"[{stage}] {message}")


def print_success(message: str) -> None:
    """Print a success message."""
    print(f"[OK] {message}")


def print_error(message: str) -> None:
    """Print an error message."""
    print(f"[FAIL] {message}", file=sys.stderr)


def run_pipeline(
    config: PresentationConfig,
    verbose: bool = False,
    debug: bool = False,
    debug_dir: Path | None = None
) -> int:
    """
    Run the presentation notes pipeline.

    Args:
        config: Pipeline configuration
        verbose: Enable verbose output
        debug: Save intermediate outputs for debugging
        debug_dir: Custom directory for debug output

    Returns:
        Exit code (0 for success)
    """

    # Initialize pipeline state
    state = PresentationState(config=config)

    # Create the LLM client based on the selected provider
    from notes_generator.llm_client import create_llm_client
    llm_client = create_llm_client(
        provider=config.provider,
        azure_endpoint=config.azure_endpoint,
        azure_deployment=config.azure_deployment
    )

    # Debug output directory
    if debug_dir:
        actual_debug_dir = debug_dir
    else:
        actual_debug_dir = Path(config.output_path).parent / "debug"

    if debug:
        actual_debug_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Stage 0: Extract slides from PDF
        print_stage("Extract", "Rendering PDF pages as images...")
        state.current_stage = "extract"

        from presentation_notes.pdf_processor import extract_slides, get_pdf_title

        # Create slides directory
        slides_dir = Path(config.slides_dir)
        slides_dir.mkdir(parents=True, exist_ok=True)

        state.slides = extract_slides(
            pdf_path=Path(config.pdf_path),
            output_dir=slides_dir,
            dpi=config.dpi,
            image_format=config.image_format
        )
        print_success(f"Extracted {len(state.slides)} slides")

        # Get title from PDF if not provided
        if not config.title:
            config.title = get_pdf_title(Path(config.pdf_path))

        if debug:
            slides_data = [s.to_dict() for s in state.slides]
            (actual_debug_dir / "00_slides.json").write_text(
                json.dumps(slides_data, indent=2), encoding="utf-8"
            )

        # Stage 1: Parse transcript
        print_stage("Parse", "Parsing SRT transcript...")
        state.current_stage = "parse"

        from presentation_notes.stages.parse_transcript import (
            parse_srt,
            consolidate_segments
        )

        raw_segments = parse_srt(Path(config.transcript_path))
        segments = consolidate_segments(raw_segments, period_seconds=30)
        print_success(f"Parsed {len(raw_segments)} segments, consolidated to {len(segments)}")

        if debug:
            seg_data = [s.to_dict() for s in segments]
            (actual_debug_dir / "01_segments.json").write_text(
                json.dumps(seg_data, indent=2), encoding="utf-8"
            )

        # Stage 2: Align transcript to slides
        print_stage("Align", "Mapping transcript to slides using LLM...")
        state.current_stage = "align"

        from presentation_notes.stages.align import align_slides_to_transcript_sync

        state.alignments = align_slides_to_transcript_sync(
            slides=state.slides,
            segments=segments,
            model=config.model,
            llm_client=llm_client
        )
        print_success(f"Aligned {len(state.alignments)} slide-transcript pairs")

        if debug:
            align_data = [a.to_dict() for a in state.alignments]
            (actual_debug_dir / "02_alignments.json").write_text(
                json.dumps(align_data, indent=2), encoding="utf-8"
            )

        # Stage 3: Annotate slides with detailed notes
        print_stage("Annotate", "Generating notes per slide using LLM...")
        state.current_stage = "annotate"

        from presentation_notes.stages.annotate import annotate_all_slides_sync

        state.slide_notes = annotate_all_slides_sync(
            slides=state.slides,
            alignments=state.alignments,
            model=config.model,
            llm_client=llm_client
        )
        print_success(f"Generated notes for {len(state.slide_notes)} slides")

        if debug:
            notes_data = [n.to_dict() for n in state.slide_notes]
            (actual_debug_dir / "03_slide_notes.json").write_text(
                json.dumps(notes_data, indent=2), encoding="utf-8"
            )

        # Stage 4: Assemble final document
        print_stage("Assemble", "Building final document...")
        state.current_stage = "assemble"

        from presentation_notes.stages.assemble import assemble_presentation_notes

        assemble_presentation_notes(
            slide_notes=state.slide_notes,
            output_path=Path(config.output_path),
            title=config.title,
            slides_dir=slides_dir
        )
        print_success(f"Document created: {config.output_path}")

        if debug:
            print_success(f"Debug output saved to: {actual_debug_dir}")

        return 0

    except Exception as e:
        print_error(f"Pipeline failed at stage '{state.current_stage}': {e}")

        if verbose:
            import traceback
            traceback.print_exc()

        return 1


def main() -> int:
    """Run the presentation notes pipeline."""

    args = parse_args()

    # Validate inputs
    if not args.pdf.exists():
        print_error(f"PDF file not found: {args.pdf}")
        return 1

    if not args.transcript.exists():
        print_error(f"Transcript file not found: {args.transcript}")
        return 1

    # Get title from PDF metadata if not specified
    from presentation_notes.pdf_processor import get_pdf_title
    title = args.title or get_pdf_title(args.pdf)

    # Determine output path if not specified
    output_path = args.output
    if output_path is None:
        safe_title = title.replace(" ", "_").replace("/", "_")
        output_path = Path("output") / f"{safe_title}_Notes.md"

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Set up slides directory in staging
    safe_title = title.replace(" ", "_").replace("/", "_")
    slides_dir = Path("staging") / safe_title / "slides"

    # Build configuration
    config = PresentationConfig(
        pdf_path=str(args.pdf),
        transcript_path=str(args.transcript),
        output_path=str(output_path),
        slides_dir=str(slides_dir),
        title=title,
        model=args.model,
        dpi=args.dpi,
        provider=args.provider,
        azure_endpoint=args.azure_endpoint,
        azure_deployment=args.azure_deployment
    )

    # Display configuration
    print()
    print("PresentationNotes")
    print("=" * 60)
    print(f"PDF:           {config.pdf_path}")
    print(f"Transcript:    {config.transcript_path}")
    print(f"Output:        {config.output_path}")
    print(f"Title:         {config.title}")
    print(f"Model:         {config.model}")
    print(f"DPI:           {config.dpi}")
    print(f"Provider:      {config.provider}")
    if config.provider == "azure":
        print(f"Azure Endpoint:    {config.azure_endpoint}")
        print(f"Azure Deployment:  {config.azure_deployment}")
    print("=" * 60)
    print()

    # Run the pipeline
    return run_pipeline(
        config,
        verbose=args.verbose,
        debug=args.debug,
        debug_dir=args.debug_dir
    )


if __name__ == "__main__":
    sys.exit(main())
