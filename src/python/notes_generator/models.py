# -------------------------------------------------------------------------
# File: models.py
# Description: Data classes for the VideoToNotes pipeline
# Context: Shared models used across all pipeline stages
# Author: Greg Tate
# -------------------------------------------------------------------------

"""
Data Models

Defines the core data structures used throughout the pipeline:
- IndexSection: A section from the normalized index
- TranscriptChunk: A chunk of transcript text
- SectionPartial: Notes for a section from a single chunk
- MergedSection: Fully merged notes for a section
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class IndexSection:
    """
    A section from the index/TOC file.

    Represents a single entry in the table of contents with its
    hierarchical position and timestamp.
    """

    title: str
    timestamp: str  # HH:MM:SS format (start time)
    level: int  # 2 = ##, 3 = ###, 4 = ####
    order: int  # Position in document (1-indexed)
    parent: Optional[str] = None  # Parent section title
    children: List[str] = field(default_factory=list)  # Child section titles
    end_timestamp: Optional[str] = None  # HH:MM:SS format (end time, usually start of next section)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "timestamp": self.timestamp,
            "level": self.level,
            "order": self.order,
            "parent": self.parent,
            "children": self.children,
            "end_timestamp": self.end_timestamp
        }

    @classmethod
    def from_dict(cls, data: dict) -> "IndexSection":
        """Create from dictionary."""
        return cls(
            title=data["title"],
            timestamp=data["timestamp"],
            level=data["level"],
            order=data["order"],
            parent=data.get("parent"),
            children=data.get("children", []),
            end_timestamp=data.get("end_timestamp")
        )


@dataclass
class NormalizedIndex:
    """
    The complete normalized index structure.

    Contains the video title and all sections in hierarchical order.
    """

    title: str
    sections: List[IndexSection]
    url: Optional[str] = None
    upload_date: Optional[str] = None
    duration: Optional[int] = None  # Duration in seconds

    def get_lowest_level_sections(self) -> List[IndexSection]:
        """Return only sections at the lowest (most detailed) level."""
        if not self.sections:
            return []

        # Find max level
        max_level = max(s.level for s in self.sections)

        return [s for s in self.sections if s.level == max_level]

    def get_sections_by_level(self, level: int) -> List[IndexSection]:
        """Return sections at a specific level."""
        return [s for s in self.sections if s.level == level]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "title": self.title,
            "sections": [s.to_dict() for s in self.sections]
        }
        if self.url:
            result["url"] = self.url
        if self.upload_date:
            result["upload_date"] = self.upload_date
        if self.duration:
            result["duration"] = self.duration
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "NormalizedIndex":
        """Create from dictionary."""
        return cls(
            title=data["title"],
            sections=[IndexSection.from_dict(s) for s in data["sections"]],
            url=data.get("url"),
            upload_date=data.get("upload_date"),
            duration=data.get("duration")
        )


@dataclass
class TranscriptChunk:
    """
    A chunk of transcript text.

    Represents a ~20KB portion of the transcript, bounded by timestamps.
    """

    chunk_id: int
    text: str
    start_timestamp: str  # HH:MM:SS format
    end_timestamp: str  # HH:MM:SS format
    file_path: Optional[str] = None  # Original chunk file path

    @property
    def timestamp_range(self) -> str:
        """Return formatted timestamp range."""
        return f"{self.start_timestamp} – {self.end_timestamp}"


@dataclass
class SectionPartial:
    """
    Notes for a section from a single chunk.

    When a section spans multiple chunks, each chunk produces a partial.
    These partials are later merged.
    """

    section_title: str
    chunk_id: int
    timestamp_range: str
    key_concepts: List[str] = field(default_factory=list)
    definitions: Dict[str, str] = field(default_factory=dict)
    key_facts: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    exam_tips: List[str] = field(default_factory=list)
    raw_markdown: str = ""  # Original markdown from LLM

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "section_title": self.section_title,
            "chunk_id": self.chunk_id,
            "timestamp_range": self.timestamp_range,
            "key_concepts": self.key_concepts,
            "definitions": self.definitions,
            "key_facts": self.key_facts,
            "examples": self.examples,
            "exam_tips": self.exam_tips,
            "raw_markdown": self.raw_markdown
        }


@dataclass
class MergedSection:
    """
    Fully merged notes for a section.

    The result of combining all partials for a single section.
    """

    section_title: str
    timestamp_range: str  # Earliest start – Latest end
    level: int  # Heading level from index
    order: int  # Position in final document
    content: str  # Full markdown content

    def to_markdown(self) -> str:
        """Generate markdown output for this section."""
        heading_prefix = "#" * self.level
        return f"{heading_prefix} {self.section_title}\n\n{self.content}"


@dataclass
class PipelineConfig:
    """
    Configuration for the pipeline run.
    """

    index_path: str
    transcript_path: str
    output_path: str
    extract_model: str = "gpt-4.1-mini"
    merge_model: str = "deepseek-r1"
    prompts_dir: Optional[str] = None
    chunk_size: int = 20000  # ~20KB chunks
    chunk_period: int = 20  # Consolidate into 20-second periods


@dataclass
class PipelineState:
    """
    Tracks state throughout the pipeline.

    Used for resumability and debugging.
    """

    config: PipelineConfig
    normalized_index: Optional[NormalizedIndex] = None
    chunks: List[TranscriptChunk] = field(default_factory=list)
    partials: List[SectionPartial] = field(default_factory=list)
    merged_sections: List[MergedSection] = field(default_factory=list)
    current_stage: str = "init"
    errors: List[str] = field(default_factory=list)

    def add_error(self, error: str) -> None:
        """Record an error."""
        self.errors.append(error)

    @property
    def has_errors(self) -> bool:
        """Check if any errors occurred."""
        return len(self.errors) > 0
