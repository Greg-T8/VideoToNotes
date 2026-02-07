# Slide-Transcript Alignment

You are given a set of slides (with their extracted text) and a timestamped transcript from a video presentation. Your task is to determine which portions of the transcript correspond to each slide.

## Slides

These are slides {slide_numbers} out of {total_slides} total slides.

{slide_summary}

## Transcript

{transcript}

## Instructions

For each slide listed above, determine::

1. Which portion of the transcript was spoken while that slide was displayed
2. The start and end timestamps of the relevant transcript section
3. Your confidence in the alignment (high, medium, or low)

### Alignment Strategy

- Match based on **topic similarity** between slide text and transcript content
- Slides are shown in order — transcript segments should progress chronologically
- A slide may correspond to a long section of transcript (if the presenter stayed on that slide)
- A slide may have very little transcript (e.g., a title slide or transition slide)
- Look for **key terms** from the slide text appearing in the transcript
- Consider the **flow of topics** — when the transcript moves to a new topic, it likely means a new slide

## Output Format

Return a JSON array with one object per slide. Each object must have:

```json
[
  {
    "slide_number": 1,
    "start_time": "00:00:00",
    "end_time": "00:02:30",
    "transcript_text": "The actual transcript text for this slide...",
    "confidence": "high"
  }
]
```

IMPORTANT:

- Return ONLY the JSON array, no other text
- Include ALL slides listed above ({slide_numbers})
- Timestamps must be in HH:MM:SS format
- transcript_text should contain the ACTUAL transcript text for the slide, not a summary
- If a slide has no corresponding transcript (e.g., title slide), use empty string for transcript_text and "low" confidence
