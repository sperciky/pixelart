"""
Data models for Pixel Art Pattern Generator

Defines the core data structures used throughout the application.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import numpy as np


@dataclass
class Color:
    """
    Represents a single bead color.

    Attributes:
        name: Human-readable color name (e.g., "Cherry Red")
        rgb: RGB tuple (0-255 range) - e.g., (220, 20, 60)
        code: Optional product code (e.g., "P01" for Perler bead #1)
        hex: Optional hex color string (e.g., "#DC143C")
        lab: Optional LAB color space values (computed on demand)
    """
    name: str
    rgb: Tuple[int, int, int]
    code: Optional[str] = None
    hex: Optional[str] = None
    lab: Optional[Tuple[float, float, float]] = None

    def __post_init__(self):
        """Validate RGB values and auto-generate hex if not provided."""
        # Validate RGB values are in valid range
        if not all(0 <= val <= 255 for val in self.rgb):
            raise ValueError(f"RGB values must be in range 0-255, got {self.rgb}")

        # Auto-generate hex if not provided
        if self.hex is None:
            self.hex = "#{:02X}{:02X}{:02X}".format(*self.rgb)

    def to_dict(self) -> dict:
        """Convert Color to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "rgb": list(self.rgb),
            "code": self.code,
            "hex": self.hex
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Color':
        """Create Color from dictionary (e.g., from JSON)."""
        return cls(
            name=data["name"],
            rgb=tuple(data["rgb"]),
            code=data.get("code"),
            hex=data.get("hex")
        )

    def __str__(self) -> str:
        """String representation for display."""
        if self.code:
            return f"{self.name} ({self.code})"
        return self.name

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"Color(name='{self.name}', rgb={self.rgb}, code='{self.code}')"

    def __hash__(self) -> int:
        """
        Make Color hashable so it can be used in sets and as dict keys.

        Hash is based on name and RGB values, which uniquely identify a color.
        The lab field is excluded since it's computed later and doesn't affect identity.
        """
        return hash((self.name, self.rgb))


@dataclass
class Palette:
    """
    Collection of available bead colors.

    Attributes:
        name: Palette name (e.g., "Perler Beads Standard")
        colors: List of Color objects
        description: Optional palette description
        source: Optional source/brand information
    """
    name: str
    colors: List[Color]
    description: Optional[str] = None
    source: Optional[str] = None

    def __post_init__(self):
        """Validate palette has at least one color."""
        if not self.colors:
            raise ValueError("Palette must contain at least one color")

    def __len__(self) -> int:
        """Return number of colors in palette."""
        return len(self.colors)

    def get_color_by_name(self, name: str) -> Optional[Color]:
        """Find color by name (case-insensitive)."""
        name_lower = name.lower()
        for color in self.colors:
            if color.name.lower() == name_lower:
                return color
        return None

    def get_color_by_code(self, code: str) -> Optional[Color]:
        """Find color by product code."""
        for color in self.colors:
            if color.code == code:
                return color
        return None

    def to_dict(self) -> dict:
        """Convert Palette to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "source": self.source,
            "colors": [color.to_dict() for color in self.colors]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Palette':
        """Create Palette from dictionary (e.g., from JSON)."""
        colors = [Color.from_dict(c) for c in data["colors"]]
        return cls(
            name=data["name"],
            colors=colors,
            description=data.get("description"),
            source=data.get("source")
        )

    def __str__(self) -> str:
        """String representation for display."""
        return f"{self.name} ({len(self.colors)} colors)"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"Palette(name='{self.name}', colors={len(self.colors)})"


@dataclass
class PixelPattern:
    """
    Represents a completed pixel art pattern.

    This is the result of converting an image to a bead pattern.
    Contains the matched colors for each grid position plus metadata.

    Attributes:
        width: Grid width (number of beads horizontally)
        height: Grid height (number of beads vertically)
        grid: 2D array of Color objects [height, width]
        palette: The Palette used for color matching
        original_image: Optional reference to original PIL Image
        metadata: Optional additional information
    """
    width: int
    height: int
    grid: np.ndarray  # 2D array of Color objects
    palette: Palette
    original_image: Optional[object] = None  # PIL.Image.Image
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        """Validate dimensions match grid shape."""
        if self.grid.shape != (self.height, self.width):
            raise ValueError(
                f"Grid shape {self.grid.shape} doesn't match "
                f"dimensions ({self.height}, {self.width})"
            )

    def get_bead_count(self) -> dict:
        """
        Calculate how many beads of each color are needed.

        Returns:
            Dictionary mapping Color objects to counts
            Example: {Color("Red"): 45, Color("Blue"): 32}
        """
        color_counts = {}

        for row in self.grid:
            for color in row:
                if color in color_counts:
                    color_counts[color] += 1
                else:
                    color_counts[color] = 1

        # Sort by count (descending) for easier reading
        return dict(sorted(color_counts.items(),
                          key=lambda x: x[1],
                          reverse=True))

    def get_color_at(self, x: int, y: int) -> Color:
        """
        Get color at specific grid position.

        Args:
            x: Column index (0 to width-1)
            y: Row index (0 to height-1)

        Returns:
            Color object at that position
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError(f"Position ({x}, {y}) out of bounds")
        return self.grid[y, x]

    def total_beads(self) -> int:
        """Return total number of beads needed."""
        return self.width * self.height

    def unique_colors_count(self) -> int:
        """Return number of unique colors used."""
        return len(self.get_bead_count())

    def __str__(self) -> str:
        """String representation for display."""
        return (f"PixelPattern({self.width}×{self.height}, "
                f"{self.unique_colors_count()} colors, "
                f"{self.total_beads()} beads)")

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (f"PixelPattern(width={self.width}, height={self.height}, "
                f"palette='{self.palette.name}')")
