"""
Pixel Art Pattern Generator - Core Modules

This package contains the core business logic for converting images
to pixel art patterns suitable for bead art projects.

Modules:
- models: Data classes and type definitions
- color_matcher: Color distance algorithms (CIEDE2000 in LAB space)
- image_processor: Image loading, resizing, and pixel extraction
- palette_manager: Palette loading, validation, and management
- pattern_generator: Output generation (previews, CSV, bead counts)
- config: Application constants and configuration
"""

__version__ = "1.0.0"
__author__ = "Pixel Art Generator Team"

# Import main classes for convenient access
from .models import Color, Palette, PixelPattern

__all__ = [
    "Color",
    "Palette",
    "PixelPattern",
]
