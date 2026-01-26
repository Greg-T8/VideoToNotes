#!/usr/bin/env python
"""Debug script to check section levels."""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src" / "python"))

from notes_generator.models import NormalizedIndex, MergedSection
from notes_generator.stages.assemble import build_content_map, build_document_structure

# Load normalized index
index_path = Path('data/Azure_AI_Fundamentals_Certification_2024_(AI-900)_-_Full_Course_to_PASS_the_Exam/debug/01_normalized_index.json')
data = json.loads(index_path.read_text())
index = NormalizedIndex.from_dict(data)

# Load merged sections
merged_path = Path('data/Azure_AI_Fundamentals_Certification_2024_(AI-900)_-_Full_Course_to_PASS_the_Exam/debug/02_extracted_sections.json')
merged_data = json.loads(merged_path.read_text())
merged_sections = [
    MergedSection(
        section_title=s['section_title'],
        timestamp_range=s.get('timestamp_range', ''),
        level=s.get('level', 3),
        order=s.get('order', 0),
        content=s.get('content', '')
    )
    for s in merged_data
]

# Find sections with title 'Responsible AI'
print("=== Responsible AI sections in index ===")
for s in index.sections:
    if 'Responsible AI' in s.title:
        print(f'Order {s.order}: level={s.level}, title="{s.title}", parent={s.parent}')

# Check what's in merged sections
print("\n=== Responsible AI in merged sections ===")
for m in merged_sections:
    if 'Responsible AI' in m.section_title:
        print(f'Order {m.order}: level={m.level}, title="{m.section_title}"')

# Build content map
print("\n=== Content map for Responsible AI ===")
content_map = build_content_map(merged_sections, index)
for order in [26, 27]:
    if order in content_map:
        m = content_map[order]
        print(f'Order {order}: FOUND - "{m.section_title}", content length={len(m.content)}')
    else:
        print(f'Order {order}: NOT FOUND in content_map')

# Generate document and write to output
print("\n=== Regenerating output file ===")
document = build_document_structure(index, merged_sections)
output_path = Path('output/Azure_AI_Fundamentals_Certification_2024_(AI-900)_-_Full_Course_to_PASS_the_Exam_Exam_Notes.md')
output_path.write_text(document, encoding='utf-8')
print(f"Written to: {output_path}")
print(f"Document size: {len(document):,} characters")

# Verify
lines = document.split('\n')
print("\n=== Verification: lines around Responsible AI ===")
for i, line in enumerate(lines):
    if line.strip().startswith('#') and 'Responsible AI' in line:
        print(f'Line {i+1}: {line}')
