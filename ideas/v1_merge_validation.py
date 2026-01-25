@dataclass
class MergeQualityReport:
    section_title: str
    input_bullet_count: int
    output_bullet_count: int
    dedup_ratio: float
    has_conflicts_flagged: bool
    timestamp_valid: bool
    all_sections_present: bool
    warnings: list[str]

def validate_merge_quality(
    partials: list[PartialNotes],
    merged_output: str
) -> MergeQualityReport:
    """Post-merge validation to ensure quality."""
    
    warnings = []
    
    # Count bullets in vs out
    input_bullets = sum(
        len(re.findall(r"^- ", p.content, re.MULTILINE)) 
        for p in partials
    )
    output_bullets = len(re.findall(r"^- ", merged_output, re.MULTILINE))
    
    dedup_ratio = 1 - (output_bullets / input_bullets) if input_bullets > 0 else 0
    
    # Check for over-deduplication (lost content)
    if dedup_ratio > 0.7:
        warnings.append(f"High dedup ratio ({dedup_ratio:.0%})—verify no content lost")
    
    # Check for under-deduplication (too much redundancy)
    if dedup_ratio < 0.1 and len(partials) > 1:
        warnings.append("Low dedup ratio—possible redundant content remaining")
    
    # Verify timestamps
    timestamps = re.search(r"\*\*Timestamp\*\*:\s*(.+?)(?:\n|$)", merged_output)
    timestamp_valid = bool(timestamps and "–" in timestamps.group(1))
    
    # Check all sections present
    required_sections = [
        "Key Concepts", "Definitions", "Key Facts", "Examples", "Exam Tips"
    ]
    all_present = all(s in merged_output for s in required_sections)
    
    # Check for conflict flags
    has_conflicts = "⚠️" in merged_output
    
    return MergeQualityReport(
        section_title=extract_section_title(merged_output),
        input_bullet_count=input_bullets,
        output_bullet_count=output_bullets,
        dedup_ratio=dedup_ratio,
        has_conflicts_flagged=has_conflicts,
        timestamp_valid=timestamp_valid,
        all_sections_present=all_present,
        warnings=warnings
    )