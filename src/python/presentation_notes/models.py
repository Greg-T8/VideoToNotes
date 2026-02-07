# -------------------------------------------------------------------------
# File: models.py
# Description: Data classes for the presentation notes pipeline
# Context: Shared models used across all presentation pipeline stages
# Author: Greg Tate
# -------------------------------------------------------------------------

"""
Presentation Pipeline Data Models

Defines the core data structures:
- Slide: A single slide with image path and extracted text
- SlideTranscript: Transcript segment aligned to a slide
- SlideNotes: Generated notes for a single slide
- PresentationConfig: Pipeline configuration
- PresentationState: Pipeline state tracking
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Slide:
    """
    A single slide extracted from a PDF.

    Contains the rendered image path and any text extracted from the page.
    """

    number: int  # 1-indexed slide number
    image_path: str  # Path to the rendered PNG image
    text: str  # Extracted text content from the slide
    width: int = 0  # Image width in pixels
    height: int = 0  # Image height in pixels

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "number": self.number,
            "image_path": self.image_path,
            "text": self.text,
            "width": self.width,
            "height": self.height
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Slide":
        """Create from dictionary."""
        return cls(
            number=data["number"],
            image_path=data["image_path"],
            text=data["text"],
            width=data.get("width", 0),
            height=data.get("height", 0)
        )


@dataclass
class SlideTranscript:
    """
    Transcript content aligned to a specific slide.

    Maps a portion of the full transcript to the slide it corresponds to,
    based on LLM-assisted alignment of slide text and transcript content.
    """

    slide_number: int
    transcript_text: str  # The transcript segment for this slide
    start_timestamp: str  # HH:MM:SS format
    end_timestamp: str  # HH:MM:SS format
    confidence: str = "high"  # Alignment confidence: high, medium, low

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "slide_number": self.slide_number,
            "transcript_text": self.transcript_text,
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "confidence": self.confidence
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SlideTranscript":
        """Create from dictionary."""
        return cls(
            slide_number=data["slide_number"],
            transcript_text=data["transcript_text"],
            start_timestamp=data["start_timestamp"],
            end_timestamp=data["end_timestamp"],
            confidence=data.get("confidence", "high")
        )


@dataclass
class SlideNotes:
    """
    Generated notes for a single slide.

    Combines slide image, extracted text, and AI-generated notes
    from the aligned transcript segment.
    """

    slide_number: int
    slide_title: str  # Title extracted or inferred from the slide
    image_path: str  # Path to the slide image
    timestamp_range: str  # Start – End timestamps
    notes_markdown: str  # Full markdown notes content

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "slide_number": self.slide_number,
            "slide_title": self.slide_title,
            "image_path": self.image_path,
            "timestamp_range": self.timestamp_range,
            "notes_markdown": self.notes_markdown
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SlideNotes":
        """Create from dictionary."""
        return cls(
            slide_number=data["slide_number"],
            slide_title=data["slide_title"],
            image_path=data["image_path"],
            timestamp_range=data["timestamp_range"],
            notes_markdown=data["notes_markdown"]
        )


@dataclass
class PresentationConfig:
    """
    Configuration for the presentation notes pipeline.
    """

    pdf_path: str  # Path to the PDF slide deck
    transcript_path: str  # Path to the SRT transcript file
    output_path: str  # Path for the output markdown file
    slides_dir: str  # Directory to store rendered slide images
    title: str = ""  # Presentation title (derived from PDF if empty)
    model: str = "gpt-4.1-mini"  # LLM model for alignment and annotation
    dpi: int = 200  # DPI for PDF rendering
    image_format: str = "png"  # Output image format


@dataclass
class PresentationState:
    """
    Tracks state throughout the presentation pipeline.
    """

    config: PresentationConfig
    slides: List[Slide] = field(default_factory=list)
    alignments: List[SlideTranscript] = field(default_factory=list)
    slide_notes: List[SlideNotes] = field(default_factory=list)
    current_stage: str = "init"
    errors: List[str] = field(default_factory=list)

    def add_error(self, error: str) -> None:
        """Record an error."""
        self.errors.append(error)

    @property
    def has_errors(self) -> bool:
        """Check if any errors occurred."""
        return len(self.errors) > 0
