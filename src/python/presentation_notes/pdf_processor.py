# -------------------------------------------------------------------------
# File: pdf_processor.py
# Description: Extract slide images and text from PDF presentations
# Context: PresentationNotes pipeline - PDF to slides conversion
# Author: Greg Tate
# -------------------------------------------------------------------------

"""
PDF Processor

Renders each page of a PDF as a PNG image and extracts the text content.
Uses PyMuPDF (fitz) which is self-contained with no external dependencies.
"""

import re
from pathlib import Path
from typing import List

import fitz  # PyMuPDF

from presentation_notes.models import Slide


def extract_slides(
    pdf_path: Path,
    output_dir: Path,
    dpi: int = 200,
    image_format: str = "png"
) -> List[Slide]:
    """
    Extract slides from a PDF as images with associated text.

    Renders each page as a high-resolution image and extracts the
    text content for downstream LLM processing.

    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save slide images
        dpi: Resolution for rendering (default 200)
        image_format: Image format (default 'png')

    Returns:
        List of Slide objects with image paths and extracted text
    """

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Open the PDF
    doc = fitz.open(str(pdf_path))
    slides: List[Slide] = []

    # Calculate zoom factor from DPI (72 is the PDF default DPI)
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    print(f"  Extracting {len(doc)} slides from PDF...")

    for page_num in range(len(doc)):
        page = doc[page_num]
        slide_number = page_num + 1

        # Render page to image
        image_filename = f"slide_{slide_number:03d}.{image_format}"
        image_path = output_dir / image_filename

        pix = page.get_pixmap(matrix=matrix)
        pix.save(str(image_path))

        # Extract text from page
        text = page.get_text("text").strip()

        # Clean up extracted text
        text = _clean_slide_text(text)

        # Create Slide object
        slide = Slide(
            number=slide_number,
            image_path=str(image_path),
            text=text,
            width=pix.width,
            height=pix.height
        )
        slides.append(slide)

    doc.close()

    print(f"  Rendered {len(slides)} slide images to {output_dir}")
    return slides


def get_pdf_title(pdf_path: Path) -> str:
    """
    Extract the title from a PDF's metadata.

    Falls back to the filename if no metadata title is available.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        The PDF title string
    """

    doc = fitz.open(str(pdf_path))
    metadata = doc.metadata

    # Try metadata title first
    title = metadata.get("title", "").strip() if metadata else ""

    doc.close()

    # Fall back to filename without extension
    if not title:
        title = pdf_path.stem

    # Clean up underscores and hyphens for readability
    title = title.replace("_", " ").replace("-", " ")

    # Collapse multiple spaces
    title = re.sub(r"\s+", " ", title).strip()

    return title


def get_slide_count(pdf_path: Path) -> int:
    """
    Get the number of pages/slides in a PDF.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Number of pages
    """

    doc = fitz.open(str(pdf_path))
    count = len(doc)
    doc.close()
    return count


def _clean_slide_text(text: str) -> str:
    """
    Clean up text extracted from a slide.

    Removes excessive whitespace, page numbers, and common artifacts.

    Args:
        text: Raw extracted text

    Returns:
        Cleaned text
    """

    if not text:
        return ""

    # Remove standalone page numbers (e.g., just "3" on a line)
    text = re.sub(r"^\d{1,3}\s*$", "", text, flags=re.MULTILINE)

    # Collapse multiple blank lines to single
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text
