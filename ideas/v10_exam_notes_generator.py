# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate exam notes from video transcript using GitHub Models API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python exam_notes_generator.py contents.md transcript.zip
  python exam_notes_generator.py contents.md transcript.zip -o notes.md
  python exam_notes_generator.py contents.md transcript.zip --prompts ./custom-prompts/
        """
    )
    parser.add_argument("contents", help="Path to contents/TOC markdown file")
    parser.add_argument("transcript_zip", help="Path to ZIP file with transcript chunks")
    parser.add_argument(
        "-o", "--output",
        default="exam_notes.md",
        help="Output file path (default: exam_notes.md)"
    )
    parser.add_argument(
        "-p", "--prompts",
        type=Path,
        default=DEFAULT_PROMPTS_DIR,
        help=f"Directory containing prompt files (default: {DEFAULT_PROMPTS_DIR})"
    )
    parser.add_argument(
        "--stage1-model",
        default="openai/gpt-4.1-mini",
        help="Model for Stage 1 chunk processing (default: openai/gpt-4.1-mini)"
    )
    parser.add_argument(
        "--stage2-model",
        default="deepseek/deepseek-r1-0528",
        help="Model for Stage 2 section merging (default: deepseek/deepseek-r1-0528)"
    )
    
    args = parser.parse_args()
    
    # Pass models to the generator
    asyncio.run(generate_notes(
        args.contents,
        args.transcript_zip,
        args.output,
        args.prompts,
        args.stage1_model,
        args.stage2_model
    ))

if __name__ == "__main__":
    main()