"""
Pattern generation and output utilities for Pixel Art Pattern Generator

Generates various outputs from pixel patterns: visual previews, CSV files,
bead counts, and more.
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import csv
from io import StringIO, BytesIO
from typing import Dict, Tuple, Optional
from .models import PixelPattern, Color
from .config import (
    DEFAULT_GRID_LINE_COLOR,
    DEFAULT_GRID_LINE_WIDTH,
    DEFAULT_CELL_SIZE,
    CSV_DELIMITER
)


def create_pattern_preview(pattern: PixelPattern,
                          cell_size: int = DEFAULT_CELL_SIZE,
                          show_grid: bool = True,
                          grid_color: Tuple[int, int, int] = DEFAULT_GRID_LINE_COLOR,
                          grid_width: int = DEFAULT_GRID_LINE_WIDTH) -> Image.Image:
    """
    Create a visual preview of the bead pattern.

    Generates an image showing the pixelated pattern with optional grid lines
    overlaid. Each cell represents one bead position.

    Args:
        pattern: PixelPattern object to visualize
        cell_size: Size of each bead in pixels (default 20)
        show_grid: Whether to draw grid lines (default True)
        grid_color: RGB color for grid lines (default gray)
        grid_width: Width of grid lines in pixels (default 1)

    Returns:
        PIL Image showing the pattern preview

    Example:
        >>> pattern = PixelPattern(...)
        >>> preview = create_pattern_preview(pattern, cell_size=30, show_grid=True)
        >>> preview.save("pattern_preview.png")
    """
    # Calculate output image size
    img_width = pattern.width * cell_size
    img_height = pattern.height * cell_size

    # Create blank image
    image = Image.new('RGB', (img_width, img_height), color='white')
    draw = ImageDraw.Draw(image)

    # Draw each bead cell
    for y in range(pattern.height):
        for x in range(pattern.width):
            color = pattern.grid[y, x]

            # Calculate cell position
            x1 = x * cell_size
            y1 = y * cell_size
            x2 = x1 + cell_size
            y2 = y1 + cell_size

            # Draw filled rectangle with bead color
            draw.rectangle([x1, y1, x2, y2], fill=color.rgb)

    # Draw grid lines if requested
    if show_grid:
        # Vertical lines
        for x in range(pattern.width + 1):
            x_pos = x * cell_size
            draw.line([(x_pos, 0), (x_pos, img_height)],
                     fill=grid_color, width=grid_width)

        # Horizontal lines
        for y in range(pattern.height + 1):
            y_pos = y * cell_size
            draw.line([(0, y_pos), (img_width, y_pos)],
                     fill=grid_color, width=grid_width)

    return image


def create_pattern_preview_with_labels(pattern: PixelPattern,
                                       cell_size: int = 40) -> Image.Image:
    """
    Create a preview with color codes labeled in each cell.

    Useful for creating assembly instructions - each cell shows its color code.

    Args:
        pattern: PixelPattern to visualize
        cell_size: Size of each cell (should be large enough for text, 40+ recommended)

    Returns:
        PIL Image with labeled cells

    Note:
        Requires a reasonable cell size (40+) to fit text.
        Best for smaller patterns (20×20 or less).
    """
    # Create base preview
    image = create_pattern_preview(pattern, cell_size=cell_size, show_grid=True)
    draw = ImageDraw.Draw(image)

    # Try to load a font (fallback to default if unavailable)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                                  size=max(8, cell_size // 4))
    except:
        font = ImageFont.load_default()

    # Draw color codes
    for y in range(pattern.height):
        for x in range(pattern.width):
            color = pattern.grid[y, x]

            if color.code:
                # Calculate cell center
                cx = x * cell_size + cell_size // 2
                cy = y * cell_size + cell_size // 2

                # Determine text color (white or black) based on background brightness
                brightness = sum(color.rgb) / 3
                text_color = (0, 0, 0) if brightness > 128 else (255, 255, 255)

                # Draw text centered in cell
                bbox = draw.textbbox((cx, cy), color.code, font=font, anchor="mm")
                draw.text((cx, cy), color.code, fill=text_color,
                         font=font, anchor="mm")

    return image


def generate_bead_count_text(pattern: PixelPattern) -> str:
    """
    Generate a text shopping list of beads needed.

    Args:
        pattern: PixelPattern to analyze

    Returns:
        Formatted string with bead counts

    Example output:
        ```
        Bead Shopping List
        ==================
        Total beads needed: 841

        Red (P01): 245 beads (29.1%)
        Blue (P09): 187 beads (22.2%)
        White (P01): 156 beads (18.5%)
        ...
        ```
    """
    bead_count = pattern.get_bead_count()
    total = pattern.total_beads()

    # Build output text
    lines = []
    lines.append("Bead Shopping List")
    lines.append("=" * 50)
    lines.append(f"Total beads needed: {total}")
    lines.append(f"Unique colors: {len(bead_count)}")
    lines.append(f"Pattern size: {pattern.width}×{pattern.height}")
    lines.append("")

    # List each color with count and percentage
    for color, count in bead_count.items():
        percentage = (count / total) * 100
        color_str = str(color)  # Uses Color.__str__ which includes code
        lines.append(f"{color_str}: {count} beads ({percentage:.1f}%)")

    return "\n".join(lines)


def export_pattern_to_csv(pattern: PixelPattern,
                          use_codes: bool = True,
                          use_names: bool = False,
                          use_rgb: bool = False) -> str:
    """
    Export pattern to CSV format.

    Creates a grid where each cell contains the color representation.
    Can use color codes, names, or RGB values.

    Args:
        pattern: PixelPattern to export
        use_codes: Use color codes (e.g., "P01")
        use_names: Use color names (e.g., "Red")
        use_rgb: Use RGB values (e.g., "255,0,0")

    Returns:
        CSV string

    Note:
        If multiple options are True, they're combined (e.g., "Red (P01)").
        If none are True, defaults to using codes.

    Example CSV output:
        ```
        P01,P01,P09,P09
        P01,P09,P09,P12
        P12,P12,P01,P01
        ```
    """
    if not (use_codes or use_names or use_rgb):
        use_codes = True  # Default to codes

    # Build CSV data
    csv_data = []

    for y in range(pattern.height):
        row = []
        for x in range(pattern.width):
            color = pattern.grid[y, x]

            # Build cell value
            cell_parts = []

            if use_names:
                cell_parts.append(color.name)

            if use_codes and color.code:
                cell_parts.append(f"({color.code})")

            if use_rgb:
                rgb_str = f"{color.rgb[0]},{color.rgb[1]},{color.rgb[2]}"
                cell_parts.append(f"[{rgb_str}]")

            cell_value = " ".join(cell_parts) if cell_parts else str(color)
            row.append(cell_value)

        csv_data.append(row)

    # Convert to CSV string
    output = StringIO()
    writer = csv.writer(output, delimiter=CSV_DELIMITER)
    writer.writerows(csv_data)

    return output.getvalue()


def export_bead_count_to_csv(pattern: PixelPattern) -> str:
    """
    Export bead count as CSV (for importing into spreadsheets).

    Args:
        pattern: PixelPattern to analyze

    Returns:
        CSV string with columns: Color Name, Code, RGB, Count, Percentage

    Example CSV output:
        ```
        Color Name,Code,RGB,Count,Percentage
        Red,P01,"255,0,0",245,29.1
        Blue,P09,"0,0,255",187,22.2
        ```
    """
    bead_count = pattern.get_bead_count()
    total = pattern.total_beads()

    # Build CSV data
    output = StringIO()
    writer = csv.writer(output, delimiter=CSV_DELIMITER)

    # Header
    writer.writerow(["Color Name", "Code", "RGB", "Count", "Percentage"])

    # Data rows
    for color, count in bead_count.items():
        percentage = (count / total) * 100
        rgb_str = f"{color.rgb[0]},{color.rgb[1]},{color.rgb[2]}"

        writer.writerow([
            color.name,
            color.code or "",
            rgb_str,
            count,
            f"{percentage:.1f}"
        ])

    return output.getvalue()


def create_color_legend(pattern: PixelPattern,
                       swatch_size: int = 30) -> Image.Image:
    """
    Create a color legend showing all colors used in the pattern.

    Displays a swatch of each color with its name and code.

    Args:
        pattern: PixelPattern to create legend for
        swatch_size: Size of color swatch in pixels

    Returns:
        PIL Image showing the color legend

    Example:
        Generates an image like:
        [■ Red] Red (P01): 245 beads
        [■ Blue] Blue (P09): 187 beads
        ...
    """
    bead_count = pattern.get_bead_count()

    # Calculate image size
    padding = 10
    line_height = swatch_size + padding
    img_width = 500
    img_height = len(bead_count) * line_height + padding

    # Create image
    image = Image.new('RGB', (img_width, img_height), color='white')
    draw = ImageDraw.Draw(image)

    # Try to load font
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                                  size=14)
    except:
        font = ImageFont.load_default()

    # Draw each color
    y_pos = padding
    for color, count in bead_count.items():
        # Draw color swatch
        draw.rectangle([padding, y_pos, padding + swatch_size, y_pos + swatch_size],
                      fill=color.rgb, outline=(0, 0, 0))

        # Draw text
        text_x = padding * 2 + swatch_size
        text = f"{color.name}"
        if color.code:
            text += f" ({color.code})"
        text += f": {count} beads"

        draw.text((text_x, y_pos + swatch_size // 2), text,
                 fill=(0, 0, 0), font=font, anchor="lm")

        y_pos += line_height

    return image


def image_to_bytes(image: Image.Image, format: str = 'PNG') -> bytes:
    """
    Convert PIL Image to bytes for download.

    Args:
        image: PIL Image to convert
        format: Image format (PNG, JPEG, etc.)

    Returns:
        Bytes object containing image data

    Useful for Streamlit download buttons.
    """
    buffer = BytesIO()
    image.save(buffer, format=format)
    return buffer.getvalue()


def create_assembly_guide(pattern: PixelPattern) -> str:
    """
    Create a text-based assembly guide with row-by-row instructions.

    Args:
        pattern: PixelPattern to create guide for

    Returns:
        Formatted text guide

    Example output:
        ```
        Assembly Guide
        ==============
        Pattern: 29×29 (841 beads)

        Row 1: P01 P01 P09 P09 P12 ...
        Row 2: P01 P09 P09 P12 P12 ...
        ...
        ```
    """
    lines = []
    lines.append("Assembly Guide")
    lines.append("=" * 60)
    lines.append(f"Pattern: {pattern.width}×{pattern.height} ({pattern.total_beads()} beads)")
    lines.append("")

    for y in range(pattern.height):
        row_codes = []
        for x in range(pattern.width):
            color = pattern.grid[y, x]
            code = color.code if color.code else color.name[:3].upper()
            row_codes.append(code)

        row_str = " ".join(row_codes)
        lines.append(f"Row {y+1:2d}: {row_str}")

    return "\n".join(lines)
