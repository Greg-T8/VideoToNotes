# -------------------------------------------------------------------------
# File: annotate.py
# Description: Generate detailed notes per slide using LLM
# Context: PresentationNotes pipeline - slide annotation stage
# Author: Greg Tate
# -------------------------------------------------------------------------

"""
Annotate Stage

For each slide, combines the slide's extracted text and aligned transcript
content, then uses an LLM to generate comprehensive notes. This produces
the final per-slide notes that appear in the output document.
"""

import asyncio
from typing import List, Optional

from presentation_notes.models import Slide, SlideTranscript, SlideNotes
from presentation_notes.prompt_loader import get_slide_annotate_prompt

# Import the shared LLM client from notes_generator
from notes_generator.llm_client import GitHubModelsClient, ChatMessage


async def annotate_slide(
    slide: Slide,
    alignment: SlideTranscript,
    model: str = "gpt-4.1-mini",
    client: Optional[GitHubModelsClient] = None,
    context: Optional[str] = None
) -> SlideNotes:
    """
    Generate detailed notes for a single slide.

    Combines slide text and transcript content, then sends to the LLM
    to produce structured notes.

    Args:
        slide: The Slide object with extracted text
        alignment: The SlideTranscript with aligned transcript content
        model: LLM model identifier
        client: Optional pre-initialized LLM client
        context: Optional context string for logging

    Returns:
        SlideNotes object with generated notes
    """

    if client is None:
        client = GitHubModelsClient(timeout=180.0)

    # Load prompt template
    prompt_template = get_slide_annotate_prompt()

    # Format the prompt
    prompt = prompt_template.replace("{slide_number}", str(slide.number))
    prompt = prompt.replace("{slide_text}", slide.text or "(no text on slide)")
    prompt = prompt.replace("{transcript_text}", alignment.transcript_text or "(no transcript)")
    prompt = prompt.replace("{start_time}", alignment.start_timestamp)
    prompt = prompt.replace("{end_time}", alignment.end_timestamp)

    # Call the LLM
    response = await client.generate(
        prompt=prompt,
        model=model,
        temperature=0.2,
        max_tokens=3000,
        system_prompt=(
            "You are an expert at creating detailed study notes from "
            "presentation slides and speaker narration. Create comprehensive, "
            "well-structured notes that capture everything important."
        ),
        context=context
    )

    # Extract a title from the response or slide text
    slide_title = _extract_slide_title(slide, response)

    # Build timestamp range string
    timestamp_range = f"{alignment.start_timestamp} – {alignment.end_timestamp}"

    return SlideNotes(
        slide_number=slide.number,
        slide_title=slide_title,
        image_path=slide.image_path,
        timestamp_range=timestamp_range,
        notes_markdown=response.strip()
    )


async def annotate_all_slides(
    slides: List[Slide],
    alignments: List[SlideTranscript],
    model: str = "gpt-4.1-mini",
    concurrency: int = 1,
    llm_client: Optional[object] = None
) -> List[SlideNotes]:
    """
    Generate notes for all slides sequentially.

    Processes slides one-at-a-time to avoid rate limiting issues
    with the GitHub Models API. Each failure is caught and replaced
    with a fallback entry so the pipeline always completes.

    Args:
        slides: List of Slide objects
        alignments: List of SlideTranscript objects (one per slide)
        model: LLM model identifier
        concurrency: Reserved for future use (currently serial)
        llm_client: Optional pre-configured LLM client

    Returns:
        List of SlideNotes objects, sorted by slide number
    """

    # Initialize LLM client if not provided
    if llm_client is None:
        client = GitHubModelsClient(timeout=180.0)
    else:
        client = llm_client

    # Build a map of alignments by slide number
    alignment_map = {a.slide_number: a for a in alignments}
    total = len(slides)
    slide_notes: List[SlideNotes] = []

    for slide in slides:
        context_label = f"slide {slide.number}/{total}"
        print(f"  Annotating {context_label}...")

        # Get alignment for this slide (or create empty one)
        alignment = alignment_map.get(
            slide.number,
            SlideTranscript(
                slide_number=slide.number,
                transcript_text="(no transcript alignment)",
                start_timestamp="00:00:00",
                end_timestamp="00:00:00",
                confidence="low"
            )
        )

        try:
            notes = await annotate_slide(
                slide=slide,
                alignment=alignment,
                model=model,
                client=client,
                context=context_label
            )
            slide_notes.append(notes)
        except Exception as exc:
            print(f"  Warning: Failed to annotate slide {slide.number}: {exc}")

            # Create a minimal fallback entry
            slide_notes.append(SlideNotes(
                slide_number=slide.number,
                slide_title=f"Slide {slide.number}",
                image_path=slide.image_path,
                timestamp_range="00:00:00 – 00:00:00",
                notes_markdown="*(Notes generation failed for this slide)*"
            ))

    # Sort by slide number
    slide_notes.sort(key=lambda n: n.slide_number)

    print(f"  Annotated {len(slide_notes)} slides "
          f"({sum(1 for n in slide_notes if 'failed' not in n.notes_markdown)} succeeded)")
    return slide_notes


def annotate_all_slides_sync(
    slides: List[Slide],
    alignments: List[SlideTranscript],
    model: str = "gpt-4.1-mini",
    concurrency: int = 1,
    llm_client: Optional[object] = None
) -> List[SlideNotes]:
    """
    Synchronous wrapper for annotate_all_slides.

    Args:
        slides: List of Slide objects
        alignments: List of SlideTranscript objects
        model: LLM model identifier
        concurrency: Reserved for future use
        llm_client: Optional pre-configured LLM client

    Returns:
        List of SlideNotes objects
    """

    return asyncio.run(
        annotate_all_slides(slides, alignments, model, concurrency, llm_client)
    )


def _extract_slide_title(slide: Slide, notes_response: str) -> str:
    """
    Extract a title for the slide from its text or the LLM response.

    Tries to find the first heading in the slide text, then falls
    back to the first significant line, then to a generic name.

    Args:
        slide: The Slide object
        notes_response: The LLM-generated notes markdown

    Returns:
        A title string for the slide
    """

    # Try to get title from slide text (first non-empty line is often the title)
    if slide.text:
        lines = slide.text.strip().split("\n")

        for line in lines:
            cleaned = line.strip()

            if cleaned and len(cleaned) > 2:
                # Truncate very long titles
                if len(cleaned) > 80:
                    cleaned = cleaned[:77] + "..."

                return cleaned

    # Fall back to generic title
    return f"Slide {slide.number}"
