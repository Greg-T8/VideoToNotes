# Normalize Prompt

Convert this index/table of contents into a structured JSON format.

## Raw Index Content

```
{raw_index}
```

## Instructions

1. **Identify the hierarchy**: Detect parent-child relationships between sections.
   - Look for visual groupings (icons, indentation, heading markers)
   - Parent sections typically have no timestamp or a broader scope
   - Child sections have specific timestamps and detailed topics

2. **Extract timestamps**: Find all timestamps and normalize to HH:MM:SS format.
   - MM:SS → 00:MM:SS
   - HH:MM:SS stays as-is
   - If no timestamp, use "00:00:00"

3. **Determine heading levels**:
   - Level 2 (##): Top-level sections/categories
   - Level 3 (###): Subsections under a category
   - Level 4 (####): Detailed topics (if present)

4. **Preserve order**: Keep the original document order (1-indexed).

5. **Infer video title**: Extract or infer the video/course title from context.

## Output Format

Return ONLY valid JSON (no markdown code fences, no explanation):

```json
{
  "title": "Video or Course Title",
  "sections": [
    {
      "title": "Section Name",
      "timestamp": "00:00:00",
      "level": 2,
      "order": 1,
      "parent": null,
      "children": ["Child Section 1", "Child Section 2"]
    },
    {
      "title": "Child Section 1",
      "timestamp": "00:12:51",
      "level": 3,
      "order": 2,
      "parent": "Section Name",
      "children": []
    }
  ]
}
```

## Rules

- Every section must have: title, timestamp, level, order, parent, children
- Parent is null for top-level sections, otherwise the parent's title
- Children is an array of child section titles (empty array if none)
- Timestamps must be exactly HH:MM:SS format
- Order starts at 1 and increments for each section
- Output ONLY the JSON object, nothing else
