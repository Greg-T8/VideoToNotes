# Section Merge Prompt

Merge these partial notes into ONE coherent, comprehensive section.

## Section: {section_title}

## Partial Notes from Different Transcript Chunks

{partials}

## Merge Instructions

### 1. Timestamp Handling

- Final timestamp: [earliest start] – [latest end]
- If there's a gap > 5 minutes between partials, note it as "(continued at [timestamp])"

### 2. Key Concepts

- Combine all bullet points across partials
- REMOVE exact duplicates (identical phrasing)
- KEEP near-duplicates if they add nuance (merge into one refined bullet)
- Order logically: foundational concepts first, advanced concepts later

### 3. Definitions

- If the same term is defined multiple times, keep the MOST COMPLETE definition
- If definitions conflict, include both with clarification: "(also described as: ...)"

### 4. Key Facts

- Remove redundant facts (same information, different words)
- Keep all UNIQUE facts
- If facts appear to contradict, flag with: "⚠️ Verify: mentioned as both X and Y"
- Order by dependency (prerequisite facts first)

### 5. Examples

- Keep ALL unique examples (examples are high-value for exams)
- Remove only exact duplicate examples
- Preserve code snippets, CLI commands, and configuration samples exactly

### 6. Exam Tips 🎯

- Combine all tips, remove duplicates
- Prioritize actionable tips ("Remember to..." > "This is important")
- Consolidate similar tips into stronger combined tips

## Rules

- Do NOT add information not present in the source partials
- Do NOT infer or expand beyond what's provided
- Do NOT summarize or lose detail
- Output in the standard format with ### heading

## Output Format

### {section_title}

**Timestamp**: [merged timestamp range]

**Key Concepts**

- [merged concepts]

**Definitions**

- **[Term]**: [merged definition]

**Key Facts**

- [merged facts]

**Examples**

- [merged examples]

**Exam Tips 🎯**

- [merged tips]
