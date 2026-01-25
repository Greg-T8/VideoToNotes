from enum import Enum
from dataclasses import dataclass
from openai import AzureOpenAI

class MergeScenario(Enum):
    SINGLE_PARTIAL = "single"
    STANDARD_MERGE = "standard"
    LARGE_GAP = "gap"
    HIGH_OVERLAP = "overlap"
    CONFLICT_DETECTED = "conflict"

@dataclass
class PartialNotes:
    chunk_id: int
    timestamp_start: str
    timestamp_end: str
    content: str

@dataclass
class MergeAnalysis:
    scenario: MergeScenario
    overlap_percentage: float
    gap_minutes: float
    potential_conflicts: list[str]

def analyze_partials(partials: list[PartialNotes]) -> MergeAnalysis:
    """Pre-analyze partials to determine merge scenario and edge cases."""
    
    if len(partials) == 1:
        return MergeAnalysis(
            scenario=MergeScenario.SINGLE_PARTIAL,
            overlap_percentage=0,
            gap_minutes=0,
            potential_conflicts=[]
        )
    
    # Calculate timestamp gaps and overlaps
    gaps = []
    overlaps = []
    for i in range(len(partials) - 1):
        current_end = parse_timestamp(partials[i].timestamp_end)
        next_start = parse_timestamp(partials[i + 1].timestamp_start)
        diff = next_start - current_end
        if diff > 0:
            gaps.append(diff)
        else:
            overlaps.append(abs(diff))
    
    max_gap = max(gaps) if gaps else 0
    overlap_pct = calculate_content_overlap(partials)
    conflicts = detect_potential_conflicts(partials)
    
    # Determine scenario
    if conflicts:
        scenario = MergeScenario.CONFLICT_DETECTED
    elif max_gap > 300:  # > 5 minutes
        scenario = MergeScenario.LARGE_GAP
    elif overlap_pct > 40:
        scenario = MergeScenario.HIGH_OVERLAP
    else:
        scenario = MergeScenario.STANDARD_MERGE
    
    return MergeAnalysis(
        scenario=scenario,
        overlap_percentage=overlap_pct,
        gap_minutes=max_gap / 60,
        potential_conflicts=conflicts
    )

def detect_potential_conflicts(partials: list[PartialNotes]) -> list[str]:
    """Detect potential conflicts using keyword patterns."""
    conflict_patterns = [
        (r"default\s+is\s+(\w+)", "default value"),
        (r"always\s+(\w+)", "absolute statement"),
        (r"never\s+(\w+)", "absolute statement"),
        (r"must\s+be\s+(\w+)", "requirement"),
        (r"requires?\s+(\w+)", "requirement"),
        (r"(\d+)\s*(GB|MB|minutes|seconds|hours)", "numeric value"),
    ]
    
    conflicts = []
    all_matches = {pattern: [] for pattern, _ in conflict_patterns}
    
    for partial in partials:
        for pattern, category in conflict_patterns:
            matches = re.findall(pattern, partial.content, re.IGNORECASE)
            all_matches[(pattern, category)].extend(matches)
    
    for (pattern, category), matches in all_matches.items():
        unique_values = set(str(m).lower() for m in matches)
        if len(unique_values) > 1:
            conflicts.append(f"{category}: found varying values {unique_values}")
    
    return conflicts

def build_merge_prompt(
    section_title: str,
    partials: list[PartialNotes],
    analysis: MergeAnalysis
) -> str:
    """Build the appropriate merge prompt based on analysis."""
    
    # Load base prompt
    base_prompt = load_prompt_template("section_merge_prompt.txt")
    
    # Format partials
    partials_text = ""
    for i, partial in enumerate(partials, 1):
        partials_text += f"""
---
### Partial {i} of {len(partials)}
**Source Chunk**: {partial.chunk_id}
**Timestamps**: {partial.timestamp_start} – {partial.timestamp_end}

{partial.content}
"""
    
    # Add scenario-specific instructions
    scenario_additions = ""
    
    if analysis.scenario == MergeScenario.SINGLE_PARTIAL:
        return load_prompt_template("single_partial_prompt.txt").format(
            section_title=section_title,
            partial_notes=partials[0].content
        )
    
    elif analysis.scenario == MergeScenario.LARGE_GAP:
        scenario_additions = f"""
## ⚠️ Special Handling: Non-Contiguous Content
Detected timestamp gap of {analysis.gap_minutes:.1f} minutes between partials.
The instructor returned to this topic later. 
Add a note indicating the split and check for updates/corrections in later partials.
"""
    
    elif analysis.scenario == MergeScenario.HIGH_OVERLAP:
        scenario_additions = f"""
## ⚠️ Special Handling: High Overlap ({analysis.overlap_percentage:.0f}%)
Chunk boundaries caused significant content duplication.
Apply aggressive deduplication—keep only ONE version of repeated points.
"""
    
    elif analysis.scenario == MergeScenario.CONFLICT_DETECTED:
        conflict_list = "\n".join(f"- {c}" for c in analysis.potential_conflicts)
        scenario_additions = f"""
## ⚠️ Special Handling: Potential Conflicts Detected
Pre-analysis flagged these potential inconsistencies:
{conflict_list}

Apply conflict resolution rules carefully. Flag unresolved conflicts with ⚠️.
"""
    
    # Assemble final prompt
    return base_prompt.format(
        section_title=section_title,
        total_partials=len(partials),
        partial_notes_formatted=partials_text,
        scenario_additions=scenario_additions
    )

async def merge_section(
    section_title: str,
    partials: list[PartialNotes],
    client: AzureOpenAI
) -> str:
    """Execute the merge operation with appropriate prompt."""
    
    # Analyze partials
    analysis = analyze_partials(partials)
    
    # Build prompt
    prompt = build_merge_prompt(section_title, partials, analysis)
    
    # Call Azure OpenAI
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an expert exam study guide editor specializing in technical certification content."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        temperature=0.3,  # Lower temperature for consistent, accurate merges
        max_tokens=4000
    )
    
    merged_content = response.choices[0].message.content
    
    # Validate output structure
    if not validate_section_format(merged_content, section_title):
        # Retry with format correction prompt
        merged_content = await fix_format(merged_content, section_title, client)
    
    return merged_content

def validate_section_format(content: str, expected_title: str) -> bool:
    """Validate merged content has required structure."""
    required_elements = [
        f"### {expected_title}",
        "**Timestamp**:",
        "**Key Concepts**",
        "**Definitions**",
        "**Key Facts**",
        "**Examples**",
        "**Exam Tips 🎯**"
    ]
    return all(elem in content for elem in required_elements)