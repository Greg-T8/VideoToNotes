# Targeted Section Extraction

Extract notes for ONE SPECIFIC SECTION from this transcript chunk.

## Target Section

**Section**: {section_title}
**Time Range**: {section_start} – {section_end}

## Transcript Chunk

This chunk covers: {chunk_start} – {chunk_end}

```
{chunk_text}
```

## Instructions

Find content in the transcript that falls within the time range {section_start} – {section_end} and create notes for the section "{section_title}".

Look for transcript entries with timestamps between {section_start} and {section_end}. The content may discuss topics like:

- {topic_hints}

## Output Format

### 🎤 [{section_start} – {section_end}] {section_name}

**Timestamp**: [first mention] – [last mention]

**Key Concepts**

- [main concepts as bullet points]

**Definitions**

- **[Term]**: [definition]

**Key Facts**

- [important facts, numbers, specifications]

**Examples**

- [concrete examples or "None in this chunk"]

**Key Takeaways 🎯**

- [focus points]

---

If no relevant content is found for this section in the given time range, output:

### 🎤 [{section_start} – {section_end}] {section_name}

**Timestamp**: {section_start}

**Key Concepts**

- [Brief summary based on section title]

---
