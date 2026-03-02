# -------------------------------------------------------------------------
# File: align.py
# Description: Align transcript segments to individual slides using LLM
# Context: PresentationNotes pipeline - slide-transcript alignment stage
# Author: Greg Tate
# -------------------------------------------------------------------------

"""
Alignment Stage

Uses an LLM to map transcript segments to individual slides by comparing
slide text content against the transcript. The LLM determines which portions
of the transcript correspond to each slide.

For large presentations, the transcript is windowed per batch of slides
so that the LLM prompt stays within token limits. Each batch receives
the proportional time window of transcript plus overlap margins.
"""

import asyncio
import json
import re
from typing import List, Optional

from presentation_notes.models import Slide, SlideTranscript
from presentation_notes.prompt_loader import get_slide_align_prompt
from presentation_notes.stages.parse_transcript import TranscriptSegment

# Import the shared LLM client from notes_generator
from notes_generator.llm_client import GitHubModelsClient, ChatMessage


def build_slide_summary(slides: List[Slide]) -> str:
    """
    Build a concise summary of all slides for the alignment prompt.

    Args:
        slides: List of Slide objects with extracted text

    Returns:
        Formatted slide summary string
    """

    lines = []

    for slide in slides:

        # Truncate very long slide text to keep the prompt manageable
        text = slide.text[:500] if slide.text else "(no text)"
        lines.append(f"--- Slide {slide.number} ---\n{text}\n")

    return "\n".join(lines)


def build_transcript_summary(segments: List[TranscriptSegment]) -> str:
    """
    Build a formatted transcript for the alignment prompt.

    Args:
        segments: List of consolidated TranscriptSegment objects

    Returns:
        Formatted transcript string with timestamps
    """

    lines = []

    for seg in segments:
        lines.append(f"[{seg.start_time} - {seg.end_time}] {seg.text}")

    return "\n".join(lines)


def _get_transcript_window(
    segments: List[TranscriptSegment],
    batch_start_slide: int,
    batch_end_slide: int,
    total_slides: int,
    overlap_pct: float = 0.15
) -> List[TranscriptSegment]:
    """
    Get the transcript window that corresponds to a batch of slides.

    Estimates the time range for a batch based on slide position
    within the total presentation, then selects segments in that
    range plus overlap margins on each side.

    Args:
        segments: All consolidated transcript segments
        batch_start_slide: First slide number in batch (1-indexed)
        batch_end_slide: Last slide number in batch (1-indexed)
        total_slides: Total number of slides
        overlap_pct: Fractional overlap margin (0.15 = 15%)

    Returns:
        List of TranscriptSegment objects in the window
    """

    if not segments:
        return []

    total_duration = segments[-1].end_seconds
    slide_duration = total_duration / total_slides

    # Estimate time range for this batch
    estimated_start = (batch_start_slide - 1) * slide_duration
    estimated_end = batch_end_slide * slide_duration

    # Add overlap margins
    margin = (estimated_end - estimated_start) * overlap_pct
    window_start = max(0, estimated_start - margin)
    window_end = min(total_duration, estimated_end + margin)

    # Select segments that overlap with this window
    windowed = [
        s for s in segments
        if s.end_seconds > window_start and s.start_seconds < window_end
    ]

    return windowed


async def align_slides_to_transcript(
    slides: List[Slide],
    segments: List[TranscriptSegment],
    model: str = "gpt-4.1-mini",
    batch_size: int = 10,
    llm_client: Optional[object] = None
) -> List[SlideTranscript]:
    """
    Align transcript segments to slides using an LLM.

    Processes slides in batches. For each batch, sends only the
    relevant transcript window (based on slide position) to keep
    the prompt within token limits.

    Args:
        slides: List of Slide objects with extracted text
        segments: Consolidated transcript segments
        model: LLM model identifier
        batch_size: Number of slides per LLM call
        llm_client: Optional pre-configured LLM client

    Returns:
        List of SlideTranscript objects mapping transcript to slides
    """

    # Initialize LLM client if not provided
    if llm_client is None:
        client = GitHubModelsClient(timeout=180.0)
    else:
        client = llm_client
    prompt_template = get_slide_align_prompt()
    all_alignments: List[SlideTranscript] = []
    total_slides = len(slides)

    # Process slides in batches
    total_batches = (total_slides + batch_size - 1) // batch_size

    for batch_idx in range(total_batches):
        start = batch_idx * batch_size
        end = min(start + batch_size, total_slides)
        batch_slides = slides[start:end]

        # Get the transcript window for this batch of slides
        window_segments = _get_transcript_window(
            segments,
            batch_start_slide=batch_slides[0].number,
            batch_end_slide=batch_slides[-1].number,
            total_slides=total_slides
        )

        # Build formatted text for this batch
        slide_summary = build_slide_summary(batch_slides)
        transcript_text = build_transcript_summary(window_segments)

        # Format the prompt
        slide_numbers = ", ".join(str(s.number) for s in batch_slides)
        prompt = prompt_template.replace("{slide_summary}", slide_summary)
        prompt = prompt.replace("{transcript}", transcript_text)
        prompt = prompt.replace("{slide_numbers}", slide_numbers)
        prompt = prompt.replace("{total_slides}", str(total_slides))

        # Call the LLM
        context_label = f"batch {batch_idx + 1}/{total_batches}"
        seg_count = len(window_segments)
        print(f"  Aligning slides {start + 1}-{end} ({context_label}, {seg_count} transcript segments)...")

        response = await client.generate(
            prompt=prompt,
            model=model,
            temperature=0.1,
            max_tokens=8000,
            system_prompt=(
                "You are a precise alignment tool. Analyze slide text and "
                "transcript content to determine which transcript segments "
                "correspond to each slide. Return valid JSON only."
            ),
            context=context_label
        )

        # Parse the alignment results
        batch_alignments = _parse_alignment_response(response, batch_slides)
        all_alignments.extend(batch_alignments)

    # Sort by slide number
    all_alignments.sort(key=lambda a: a.slide_number)

    # Count successful alignments
    good = sum(1 for a in all_alignments if a.confidence != "low")
    print(f"  Aligned {len(all_alignments)} slides ({good} with transcript content)")
    return all_alignments


def align_slides_to_transcript_sync(
    slides: List[Slide],
    segments: List[TranscriptSegment],
    model: str = "gpt-4.1-mini",
    batch_size: int = 10,
    llm_client: Optional[object] = None
) -> List[SlideTranscript]:
    """
    Synchronous wrapper for align_slides_to_transcript.

    Args:
        slides: List of Slide objects
        segments: Consolidated transcript segments
        model: LLM model identifier
        batch_size: Slides per LLM call
        llm_client: Optional pre-configured LLM client

    Returns:
        List of SlideTranscript objects
    """

    return asyncio.run(
        align_slides_to_transcript(slides, segments, model, batch_size, llm_client)
    )


def _parse_alignment_response(
    response: str,
    slides: List[Slide]
) -> List[SlideTranscript]:
    """
    Parse the LLM alignment response into SlideTranscript objects.

    Expects a JSON array of objects with slide_number, start_time,
    end_time, transcript_text, and confidence fields.

    Args:
        response: Raw LLM response text
        slides: The batch of slides that were aligned

    Returns:
        List of SlideTranscript objects
    """

    # Extract JSON from response (may be wrapped in markdown code blocks)
    json_str = response.strip()

    if json_str.startswith("```"):
        # Remove markdown code block wrapping
        lines = json_str.split("\n")
        json_lines = []
        in_block = False

        for line in lines:
            if line.strip().startswith("```") and not in_block:
                in_block = True
                continue
            elif line.strip().startswith("```") and in_block:
                break
            elif in_block:
                json_lines.append(line)

        json_str = "\n".join(json_lines)

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:

        # Try to find JSON array in the response
        import re
        match = re.search(r"\[.*\]", json_str, re.DOTALL)

        if match:
            try:
                data = json.loads(match.group())
            except json.JSONDecodeError:
                print(f"  Warning: Could not parse alignment response as JSON")
                return _create_fallback_alignments(slides)
        else:
            print(f"  Warning: No JSON array found in alignment response")
            return _create_fallback_alignments(slides)

    # Handle both array and object responses
    if isinstance(data, dict):
        data = data.get("alignments", data.get("slides", [data]))

    alignments = []

    for item in data:
        try:
            alignment = SlideTranscript(
                slide_number=item["slide_number"],
                transcript_text=item.get("transcript_text", ""),
                start_timestamp=item.get("start_time", item.get("start_timestamp", "00:00:00")),
                end_timestamp=item.get("end_time", item.get("end_timestamp", "00:00:00")),
                confidence=item.get("confidence", "medium")
            )
            alignments.append(alignment)
        except (KeyError, TypeError) as e:
            print(f"  Warning: Skipping malformed alignment entry: {e}")

    return alignments


def _create_fallback_alignments(slides: List[Slide]) -> List[SlideTranscript]:
    """
    Create fallback alignments when LLM parsing fails.

    Distributes transcript time evenly across slides.

    Args:
        slides: List of slides to create fallback alignments for

    Returns:
        List of SlideTranscript objects with empty transcript text
    """

    fallbacks = []

    for slide in slides:
        fallbacks.append(SlideTranscript(
            slide_number=slide.number,
            transcript_text="(alignment unavailable)",
            start_timestamp="00:00:00",
            end_timestamp="00:00:00",
            confidence="low"
        ))

    return fallbacks
