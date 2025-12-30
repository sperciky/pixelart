"""
Color matching algorithms for Pixel Art Pattern Generator

Implements perceptually accurate color matching using CIEDE2000
distance metric in LAB color space.

The LAB color space is designed to be perceptually uniform, meaning
equal distances represent equal perceived color differences to the human eye.
This is much more accurate than simple RGB Euclidean distance.
"""

import numpy as np
from typing import Tuple, List
from skimage import color as skcolor
from .models import Color, Palette


def rgb_to_lab(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
    """
    Convert RGB color to LAB color space.

    LAB color space is perceptually uniform and device-independent.
    - L: Lightness (0-100, black to white)
    - A: Green to Red axis (-128 to 127)
    - B: Blue to Yellow axis (-128 to 127)

    Args:
        rgb: RGB tuple with values in range 0-255

    Returns:
        LAB tuple (L, A, B) as floats

    Example:
        >>> rgb_to_lab((255, 0, 0))  # Pure red
        (53.24, 80.09, 67.20)  # Approximate values
    """
    # Normalize RGB to 0-1 range
    rgb_normalized = np.array(rgb) / 255.0

    # skimage expects shape (1, 1, 3) for single color conversion
    rgb_image = rgb_normalized.reshape(1, 1, 3)

    # Convert to LAB
    lab_image = skcolor.rgb2lab(rgb_image)

    # Extract LAB values
    lab = lab_image[0, 0, :]

    return tuple(lab)


def compute_ciede2000(lab1: Tuple[float, float, float],
                      lab2: Tuple[float, float, float]) -> float:
    """
    Calculate CIEDE2000 color difference between two LAB colors.

    CIEDE2000 is the industry standard for measuring color difference.
    It's more accurate than earlier metrics (Delta E 1976, CMC, etc.)
    because it accounts for perceptual non-uniformities in LAB space.

    Lower values = more similar colors
    - ΔE < 1.0: Not perceptible by human eyes
    - ΔE 1-2: Perceptible through close observation
    - ΔE 2-10: Perceptible at a glance
    - ΔE 11-49: Colors are more similar than opposite
    - ΔE > 50: Different colors

    Args:
        lab1: First color in LAB space
        lab2: Second color in LAB space

    Returns:
        Color difference as float (lower = more similar)

    Note:
        We use scikit-image's deltaE_ciede2000 which implements
        the full CIEDE2000 formula with all correction terms.
    """
    # Convert to numpy arrays with shape (1, 1)
    lab1_array = np.array(lab1).reshape(1, 1, 3)
    lab2_array = np.array(lab2).reshape(1, 1, 3)

    # Calculate CIEDE2000 distance
    delta_e = skcolor.deltaE_ciede2000(lab1_array, lab2_array)

    return float(delta_e[0, 0])


def precompute_palette_lab(palette: Palette) -> None:
    """
    Precompute and cache LAB values for all colors in a palette.

    This optimization avoids repeated RGB→LAB conversions during
    image matching, significantly speeding up the process.

    Args:
        palette: Palette object to precompute LAB values for

    Side Effects:
        Modifies each Color object in palette.colors by setting
        the 'lab' attribute with precomputed LAB values
    """
    for color in palette.colors:
        if color.lab is None:  # Only compute if not already cached
            color.lab = rgb_to_lab(color.rgb)


def find_closest_color(target_rgb: Tuple[int, int, int],
                       palette: Palette) -> Color:
    """
    Find the closest color in a palette to a target RGB color.

    Uses CIEDE2000 distance in LAB color space for perceptually
    accurate matching.

    Args:
        target_rgb: Target color as RGB tuple (0-255)
        palette: Palette of available colors to choose from

    Returns:
        The Color from the palette that is perceptually closest
        to the target color

    Example:
        >>> palette = Palette(name="Test", colors=[red, blue, green])
        >>> target = (255, 100, 100)  # Pinkish red
        >>> closest = find_closest_color(target, palette)
        >>> print(closest.name)
        'Red'
    """
    # Ensure palette LAB values are precomputed
    precompute_palette_lab(palette)

    # Convert target to LAB
    target_lab = rgb_to_lab(target_rgb)

    # Find color with minimum CIEDE2000 distance
    min_distance = float('inf')
    closest_color = None

    for color in palette.colors:
        distance = compute_ciede2000(target_lab, color.lab)

        if distance < min_distance:
            min_distance = distance
            closest_color = color

    return closest_color


def match_image_to_palette(image_array: np.ndarray,
                           palette: Palette) -> np.ndarray:
    """
    Match all pixels in an image to the closest palette colors.

    This is the core function that converts a resized image into
    a bead pattern by mapping each pixel to the nearest available
    bead color.

    Args:
        image_array: 3D numpy array of shape (height, width, 3)
                     with RGB values in range 0-255
        palette: Palette of available bead colors

    Returns:
        2D numpy array of shape (height, width) containing
        Color objects representing the matched pattern

    Algorithm:
        1. Precompute LAB values for palette colors (one-time cost)
        2. For each pixel in the image:
           a. Extract RGB values
           b. Find closest palette color using CIEDE2000
           c. Store Color object in result grid
        3. Return completed pattern grid

    Note:
        For a 29×29 grid with 50 colors, this performs ~840 color
        matches, each comparing against 50 colors. Precomputing LAB
        values is crucial for performance.
    """
    height, width = image_array.shape[:2]

    # Precompute LAB values for all palette colors
    precompute_palette_lab(palette)

    # Initialize result grid to store Color objects
    result_grid = np.empty((height, width), dtype=object)

    # Match each pixel to closest palette color
    for y in range(height):
        for x in range(width):
            # Get RGB values for this pixel
            pixel_rgb = tuple(image_array[y, x, :3])  # Take only RGB, ignore alpha if present

            # Find closest color
            matched_color = find_closest_color(pixel_rgb, palette)

            # Store in result grid
            result_grid[y, x] = matched_color

    return result_grid


def compute_simple_rgb_distance(rgb1: Tuple[int, int, int],
                                rgb2: Tuple[int, int, int]) -> float:
    """
    Compute simple Euclidean distance in RGB space.

    Included for comparison/fallback, but NOT recommended for
    color matching as it's not perceptually uniform.

    For example, this metric treats a shift from dark green to
    light green the same as a shift from dark blue to light blue,
    even though human eyes are more sensitive to green differences.

    Args:
        rgb1: First RGB color (0-255)
        rgb2: Second RGB color (0-255)

    Returns:
        Euclidean distance as float

    Note:
        Use find_closest_color() with LAB/CIEDE2000 instead for
        accurate perceptual matching.
    """
    r1, g1, b1 = rgb1
    r2, g2, b2 = rgb2

    return np.sqrt((r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2)


def get_color_statistics(image_array: np.ndarray,
                         palette: Palette) -> dict:
    """
    Analyze color distribution in an image relative to a palette.

    Useful for giving users feedback about how well their image
    will convert with the selected palette.

    Args:
        image_array: Image as numpy array (height, width, 3)
        palette: Palette to analyze against

    Returns:
        Dictionary with statistics:
        - 'total_pixels': Total number of pixels
        - 'unique_colors': Number of unique RGB values in original
        - 'palette_utilization': Estimated % of palette colors used
        - 'average_distance': Average CIEDE2000 distance to palette

    Example:
        >>> stats = get_color_statistics(image, palette)
        >>> print(f"Will use ~{stats['palette_utilization']}% of available colors")
    """
    height, width = image_array.shape[:2]
    total_pixels = height * width

    # Count unique colors in original
    pixels_flat = image_array.reshape(-1, 3)
    unique_original = len(np.unique(pixels_flat, axis=0))

    # Sample pixels to estimate palette utilization and average distance
    # (sampling for performance on large images)
    sample_size = min(1000, total_pixels)
    sample_indices = np.random.choice(total_pixels, sample_size, replace=False)
    sample_pixels = pixels_flat[sample_indices]

    # Precompute palette LAB
    precompute_palette_lab(palette)

    # Track which palette colors get used and distances
    used_colors = set()
    total_distance = 0.0

    for pixel_rgb in sample_pixels:
        pixel_rgb_tuple = tuple(pixel_rgb)
        closest = find_closest_color(pixel_rgb_tuple, palette)
        used_colors.add(closest)

        # Calculate distance for averaging
        pixel_lab = rgb_to_lab(pixel_rgb_tuple)
        distance = compute_ciede2000(pixel_lab, closest.lab)
        total_distance += distance

    # Estimate full palette utilization from sample
    palette_utilization = (len(used_colors) / len(palette)) * 100
    average_distance = total_distance / sample_size

    return {
        'total_pixels': total_pixels,
        'unique_colors': unique_original,
        'palette_utilization': round(palette_utilization, 1),
        'average_distance': round(average_distance, 2),
        'estimated_colors_used': len(used_colors)
    }
