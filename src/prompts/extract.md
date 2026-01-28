# Chunk Processing

Generate exam-focused study notes from this transcript chunk.

## Table of Contents with Time Ranges

{toc}

## Transcript Chunk {chunk_id} of {total_chunks}

This chunk covers: {start_ts} – {end_ts}

```
{chunk_text}
```

## Instructions

Create note blocks for sections from the TOC whose time range overlaps with this chunk ({start_ts} – {end_ts}).

### Understanding the TOC Format

Each section shows: `[START_TIME – END_TIME] Section Name`

- **START_TIME**: When this section begins
- **END_TIME**: When this section ends (start of next section)
- **🎤 sections**: Content sections - create detailed notes for these
- **☁️ sections**: PARENT sections - create a brief overview block AND split detailed content into their 🎤 children

### CRITICAL: Match Content to the CORRECT Section by Time

Look at the timestamps IN THE TRANSCRIPT. Match them to the section whose time range contains that timestamp.

**Example**: If TOC shows:

```
## ☁️ [01:18:46 – 01:32:14] Access control options
### 🎤 [01:19:01 – 01:22:17] Account keys
### 🎤 [01:22:17 – 01:23:24] Blob anonymous access
### 🎤 [01:23:24 – 01:26:33] Entra ID integrated RBAC
### 🎤 [01:26:33 – 01:32:14] Shared Access Signatures
```

And transcript at 01:20:30 discusses "storage account keys have two keys for rotation":

- This goes in "🎤 [01:19:01 – 01:22:17] Account keys" (timestamp 01:20:30 is in range 01:19:01–01:22:17)
- Do NOT put detailed content in the parent "☁️ Access control options" - only the overview

### Important Rules

1. **For ☁️ parent sections**: Create a brief overview block with `[PARENT SECTION]` marker that summarizes what topics are covered
2. **For 🎤 content sections**: Create full detailed notes with all key concepts, definitions, facts, examples
3. **Use timestamp ranges to match content** - each piece of content belongs to ONE section
4. **Even short sections (1-3 minutes) need their own note block** - don't skip them
5. **Copy section titles EXACTLY** from the TOC including the marker, timestamps, and name

## Output Format

### For ☁️ PARENT sections (create a brief overview)

### [Copy EXACT section title from TOC: ☁️ [time range] Name]

**[PARENT SECTION]**

This section covers the following topics:

- [List of child topic names covered in this parent section]

**Overview**: [1-2 sentence high-level summary of what this section is about]

---

### For 🎤 CONTENT sections (create detailed notes)

### [Copy EXACT section title from TOC: 🎤 [time range] Name]

**Timestamp**: [actual first mention] – [actual last mention in chunk]

**Key Concepts**

- [main concepts as bullet points]

**Definitions**

- **[Term]**: [definition]

**Key Facts**

- [important facts, numbers, specifications]

**Examples**

- [concrete examples mentioned, or "None in this chunk" if none]

**Key Takeaways 🎯**

- [exam focus points]

---

## IMPORTANT: Output Only Section Blocks

- Output ONLY the note blocks for sections from the TOC
- Do NOT add any commentary, summaries, checklists, or "final notes" sections
- Do NOT output anything after the last section block
- Include BOTH ☁️ parent section blocks AND 🎤 content section blocks
