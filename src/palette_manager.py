"""
Palette management for Pixel Art Pattern Generator

Handles loading, saving, and managing color palettes from JSON files.
"""

import json
import os
from typing import List, Optional, Dict, Tuple
from pathlib import Path
from .models import Color, Palette
from .config import PALETTES_DIR


def load_palette_from_json(file_path: str) -> Palette:
    """
    Load a color palette from a JSON file.

    Expected JSON format:
    {
        "name": "Palette Name",
        "description": "Optional description",
        "source": "Optional source/brand",
        "colors": [
            {
                "name": "Color Name",
                "rgb": [255, 0, 0],
                "code": "P01",
                "hex": "#FF0000"
            },
            ...
        ]
    }

    Args:
        file_path: Path to JSON file

    Returns:
        Palette object

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If JSON is malformed or invalid
        json.JSONDecodeError: If file is not valid JSON
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Palette file not found: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Validate required fields
        if 'name' not in data:
            raise ValueError("Palette JSON must include 'name' field")
        if 'colors' not in data or not data['colors']:
            raise ValueError("Palette JSON must include non-empty 'colors' array")

        # Use Palette.from_dict to create palette
        palette = Palette.from_dict(data)

        return palette

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in palette file: {str(e)}")
    except KeyError as e:
        raise ValueError(f"Missing required field in palette: {str(e)}")


def save_palette_to_json(palette: Palette, file_path: str,
                         indent: int = 2) -> None:
    """
    Save a palette to a JSON file.

    Args:
        palette: Palette object to save
        file_path: Destination file path
        indent: JSON indentation (default 2 for readability)

    Raises:
        IOError: If file cannot be written
    """
    try:
        # Convert palette to dictionary
        data = palette.to_dict()

        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Write JSON file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)

    except Exception as e:
        raise IOError(f"Failed to save palette: {str(e)}")


def list_available_palettes(palettes_dir: str = PALETTES_DIR) -> List[Dict[str, str]]:
    """
    List all available palette files in the palettes directory.

    Args:
        palettes_dir: Directory containing palette JSON files

    Returns:
        List of dictionaries with palette info:
        [
            {
                'name': 'Perler Beads Standard',
                'file': 'perler.json',
                'path': 'palettes/perler.json',
                'description': 'Standard Perler bead colors'
            },
            ...
        ]

    Returns empty list if directory doesn't exist or contains no palettes.
    """
    if not os.path.exists(palettes_dir):
        return []

    palette_files = []

    # Find all JSON files
    for filename in os.listdir(palettes_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(palettes_dir, filename)

            try:
                # Try to load palette to get name and description
                palette = load_palette_from_json(file_path)

                palette_files.append({
                    'name': palette.name,
                    'file': filename,
                    'path': file_path,
                    'description': palette.description or '',
                    'color_count': len(palette.colors)
                })
            except Exception:
                # Skip invalid palette files
                continue

    # Sort by name
    palette_files.sort(key=lambda x: x['name'])

    return palette_files


def get_palette_by_name(palette_name: str,
                       palettes_dir: str = PALETTES_DIR) -> Optional[Palette]:
    """
    Load a palette by its display name (not filename).

    Args:
        palette_name: Name of the palette (e.g., "Perler Beads Standard")
        palettes_dir: Directory containing palettes

    Returns:
        Palette object if found, None otherwise

    Example:
        >>> palette = get_palette_by_name("Perler Beads Standard")
        >>> print(len(palette.colors))
        50
    """
    available = list_available_palettes(palettes_dir)

    for palette_info in available:
        if palette_info['name'] == palette_name:
            return load_palette_from_json(palette_info['path'])

    return None


def validate_palette_json(file_path: str) -> Tuple[bool, str]:
    """
    Validate a palette JSON file without fully loading it.

    Useful for user feedback when uploading custom palettes.

    Args:
        file_path: Path to JSON file to validate

    Returns:
        Tuple of (is_valid, error_message)
        - If valid: (True, "")
        - If invalid: (False, "Error description")

    Example:
        >>> valid, error = validate_palette_json("custom.json")
        >>> if not valid:
        >>>     print(f"Invalid palette: {error}")
    """
    try:
        palette = load_palette_from_json(file_path)

        # Additional validation checks
        if len(palette.colors) == 0:
            return False, "Palette contains no colors"

        if len(palette.colors) > 500:
            return False, f"Too many colors ({len(palette.colors)}). Maximum is 500."

        # Check for duplicate color names
        color_names = [c.name for c in palette.colors]
        if len(color_names) != len(set(color_names)):
            return False, "Palette contains duplicate color names"

        return True, ""

    except FileNotFoundError:
        return False, "File not found"
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {str(e)}"
    except ValueError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unknown error: {str(e)}"


def create_palette_from_colors(name: str,
                               color_list: List[Tuple[str, tuple]],
                               description: str = "") -> Palette:
    """
    Create a palette from a simple list of colors.

    Convenience function for programmatically creating palettes.

    Args:
        name: Palette name
        color_list: List of (name, rgb_tuple) pairs
        description: Optional description

    Returns:
        Palette object

    Example:
        >>> colors = [
        ...     ("Red", (255, 0, 0)),
        ...     ("Blue", (0, 0, 255)),
        ...     ("Green", (0, 255, 0))
        ... ]
        >>> palette = create_palette_from_colors("Primary Colors", colors)
        >>> len(palette.colors)
        3
    """
    colors = []

    for i, (color_name, rgb) in enumerate(color_list):
        color = Color(
            name=color_name,
            rgb=rgb,
            code=f"C{i:03d}"  # Auto-generate code
        )
        colors.append(color)

    return Palette(
        name=name,
        colors=colors,
        description=description
    )


def merge_palettes(palette1: Palette, palette2: Palette,
                  new_name: str = None) -> Palette:
    """
    Merge two palettes into one.

    Useful for combining different bead sets.

    Args:
        palette1: First palette
        palette2: Second palette
        new_name: Name for merged palette (default: "Merged Palette")

    Returns:
        New palette containing all colors from both palettes

    Note:
        Duplicate colors (same name) are kept from palette1.
    """
    if new_name is None:
        new_name = f"{palette1.name} + {palette2.name}"

    # Collect all colors, avoiding duplicates by name
    color_names_seen = set()
    merged_colors = []

    for color in palette1.colors + palette2.colors:
        if color.name not in color_names_seen:
            merged_colors.append(color)
            color_names_seen.add(color.name)

    return Palette(
        name=new_name,
        colors=merged_colors,
        description=f"Merged from {palette1.name} and {palette2.name}"
    )


def get_default_palette(palettes_dir: str = PALETTES_DIR) -> Optional[Palette]:
    """
    Get the default palette (usually the first available).

    Args:
        palettes_dir: Directory containing palettes

    Returns:
        Default Palette object, or None if no palettes available
    """
    available = list_available_palettes(palettes_dir)

    if not available:
        return None

    # Return first palette (they're sorted by name)
    return load_palette_from_json(available[0]['path'])
