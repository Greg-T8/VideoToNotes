# Chunk Processing Prompt

Generate exam-focused study notes from this transcript chunk.

## Table of Contents

{toc}

## Transcript Chunk {chunk_id} of {total_chunks}

Timestamps: {start_ts} – {end_ts}

```
{chunk_text}
```

## Instructions

Map each portion of this transcript to the appropriate TOC section based on timestamps.
For EACH section that has content in this chunk, generate notes in this EXACT format:

### [Section Title from TOC]

**Timestamp**: [first timestamp] – [last timestamp in this chunk for this section]

**Key Concepts**

- [main concepts as bullet points]

**Definitions**

- **[Term]**: [definition]

**Key Facts**

- [important facts, numbers, specifications]

**Examples**

- [concrete examples, commands, configurations mentioned]

**Key Takeaways 🎯**

- [what to remember for the exam, common pitfalls]

## Rules

1. Use `###` for section titles ONLY
2. Use bold (`**text**`) for subsection headers
3. Include ALL content from the transcript — no information loss
4. If content spans multiple sections, create separate note blocks for each
5. Be technically precise — preserve exact values, commands, configurations
6. If a subsection has no content (e.g., no examples), write "- None in this chunk"
7. Timestamps should reflect the actual time range covered in this chunk for each section
8. Only generate notes for sections that have content in THIS chunk
