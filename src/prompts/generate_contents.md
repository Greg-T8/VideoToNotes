# Generate Table of Contents from Transcript

Analyze this video transcript and create a structured table of contents with timestamps.

## Video Information

**Title:** {video_title}
**Channel:** {channel}
**Duration:** {duration}

## Transcript

```
{transcript}
```

## Instructions

1. **Identify major topic transitions**: Look for:
   - Speaker announcing new topics ("Now let's talk about...", "Moving on to...")
   - Clear subject matter changes
   - Logical section boundaries
   - Opening/introduction and closing/summary sections

2. **Extract timestamps**: Use the SRT timestamps to determine when each section begins.
   - Format timestamps as HH:MM:SS or MM:SS
   - Round to the nearest logical starting point

3. **Create descriptive titles**:
   - Keep titles concise but descriptive (3-8 words)
   - Use title case
   - Reflect the actual content discussed

4. **Aim for reasonable granularity**:
   - For short videos (<15 min): 3-6 sections
   - For medium videos (15-45 min): 5-10 sections
   - For longer videos (>45 min): 8-15 sections

5. **Hierarchy**: If there are clear parent-child relationships (main topics with subtopics), reflect that structure.

## Output Format

Return ONLY valid JSON (no markdown code fences, no explanation):

{{
  "sections": [
    {{
      "title": "Section Title",
      "timestamp": "00:00:00",
      "level": 2
    }},
    {{
      "title": "Subsection Title",
      "timestamp": "00:05:30",
      "level": 3
    }}
  ]
}}

Where:

- `level` 2 = main section (##)
- `level` 3 = subsection (###)
- Timestamps are in HH:MM:SS format
