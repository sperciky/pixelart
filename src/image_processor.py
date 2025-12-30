"""
Image processing utilities for Pixel Art Pattern Generator

Handles image loading, validation, resizing, and conversion to pixel grids.
"""

import numpy as np
from PIL import Image
from typing import Tuple, Optional, Union
from io import BytesIO


def load_image(image_source: Union[str, bytes, BytesIO]) -> Image.Image:
    """
    Load an image from various sources.

    Args:
        image_source: Can be:
            - File path (str)
            - Bytes object
            - BytesIO stream (from file upload)

    Returns:
        PIL Image object in RGB mode

    Raises:
        ValueError: If image cannot be loaded or is invalid
        IOError: If file cannot be read

    Example:
        >>> img = load_image("photo.jpg")
        >>> img = load_image(uploaded_file.read())
    """
    try:
        if isinstance(image_source, str):
            # Load from file path
            img = Image.open(image_source)
        elif isinstance(image_source, bytes):
            # Load from bytes
            img = Image.open(BytesIO(image_source))
        elif isinstance(image_source, BytesIO):
            # Load from BytesIO stream
            img = Image.open(image_source)
        else:
            raise ValueError(f"Unsupported image source type: {type(image_source)}")

        # Convert to RGB mode (handles RGBA, grayscale, etc.)
        # This ensures consistent 3-channel output
        if img.mode != 'RGB':
            img = img.convert('RGB')

        return img

    except Exception as e:
        raise ValueError(f"Failed to load image: {str(e)}")


def calculate_aspect_ratio_dimensions(original_width: int,
                                      original_height: int,
                                      target_width: Optional[int] = None,
                                      target_height: Optional[int] = None) -> Tuple[int, int]:
    """
    Calculate dimensions that maintain aspect ratio.

    If both target dimensions are provided, returns them as-is.
    If only one is provided, calculates the other to maintain aspect ratio.

    Args:
        original_width: Original image width
        original_height: Original image height
        target_width: Desired width (optional)
        target_height: Desired height (optional)

    Returns:
        Tuple of (width, height) that maintains aspect ratio

    Raises:
        ValueError: If neither target dimension is provided

    Example:
        >>> calculate_aspect_ratio_dimensions(1920, 1080, target_width=29)
        (29, 16)  # Maintains 16:9 aspect ratio
    """
    if target_width is None and target_height is None:
        raise ValueError("At least one target dimension must be provided")

    aspect_ratio = original_width / original_height

    if target_width is not None and target_height is not None:
        # Both provided, use as-is
        return (target_width, target_height)
    elif target_width is not None:
        # Calculate height from width
        calculated_height = int(round(target_width / aspect_ratio))
        return (target_width, calculated_height)
    else:
        # Calculate width from height
        calculated_width = int(round(target_height * aspect_ratio))
        return (calculated_width, target_height)


def resize_image(image: Image.Image,
                width: int,
                height: int,
                maintain_aspect: bool = False,
                resample: int = Image.Resampling.LANCZOS) -> Image.Image:
    """
    Resize image to target dimensions.

    For pixel art, we resize the image to match the exact grid dimensions
    (e.g., 29×29 pixels for a 29×29 bead grid). Each pixel in the resized
    image will correspond to one bead.

    Args:
        image: PIL Image to resize
        width: Target width in pixels (= number of beads horizontally)
        height: Target height in pixels (= number of beads vertically)
        maintain_aspect: If True, adjust dimensions to keep aspect ratio
        resample: Resampling filter (LANCZOS for best quality)

    Returns:
        Resized PIL Image

    Resampling Filters Explained:
        - LANCZOS: Highest quality, best for downscaling (recommended)
        - BILINEAR: Fast, good quality
        - NEAREST: Fastest, preserves hard edges (good for pixel art input)

    Note:
        For bead art, LANCZOS is recommended as it produces smooth color
        transitions when downscaling photos. If input is already pixel art,
        NEAREST might be better to preserve exact colors.
    """
    if width <= 0 or height <= 0:
        raise ValueError(f"Invalid dimensions: {width}×{height}")

    if maintain_aspect:
        width, height = calculate_aspect_ratio_dimensions(
            image.width,
            image.height,
            target_width=width,
            target_height=height
        )

    # Resize image
    resized = image.resize((width, height), resample=resample)

    return resized


def image_to_array(image: Image.Image) -> np.ndarray:
    """
    Convert PIL Image to numpy array.

    Args:
        image: PIL Image object (must be in RGB mode)

    Returns:
        Numpy array of shape (height, width, 3) with dtype uint8
        Values are in range 0-255

    Example:
        >>> img = Image.open("photo.jpg")
        >>> arr = image_to_array(img)
        >>> arr.shape
        (1080, 1920, 3)
        >>> arr[0, 0]  # First pixel RGB
        array([125, 200, 75], dtype=uint8)
    """
    # Convert to numpy array
    array = np.array(image, dtype=np.uint8)

    # Ensure it's 3D (height, width, channels)
    if array.ndim != 3:
        raise ValueError(f"Expected 3D array, got shape {array.shape}")

    # Ensure RGB (3 channels)
    if array.shape[2] != 3:
        raise ValueError(f"Expected 3 channels (RGB), got {array.shape[2]}")

    return array


def load_and_resize_image(image_source: Union[str, bytes, BytesIO],
                          width: int,
                          height: int,
                          maintain_aspect: bool = False) -> Tuple[Image.Image, np.ndarray]:
    """
    Convenience function: load and resize image in one step.

    This is the main function used by the UI to prepare images
    for pattern conversion.

    Args:
        image_source: Image file path, bytes, or BytesIO stream
        width: Target grid width (number of beads)
        height: Target grid height (number of beads)
        maintain_aspect: Whether to maintain original aspect ratio

    Returns:
        Tuple of:
        - Resized PIL Image (for preview/display)
        - Numpy array of image (for color matching)

    Example:
        >>> image, array = load_and_resize_image("photo.jpg", 29, 29)
        >>> print(array.shape)
        (29, 29, 3)
    """
    # Load image
    image = load_image(image_source)

    # Resize to grid dimensions
    resized_image = resize_image(image, width, height, maintain_aspect)

    # Convert to array
    image_array = image_to_array(resized_image)

    return resized_image, image_array


def get_image_info(image: Image.Image) -> dict:
    """
    Extract useful information about an image.

    Args:
        image: PIL Image object

    Returns:
        Dictionary with image metadata:
        - 'width': Image width in pixels
        - 'height': Image height in pixels
        - 'mode': Color mode (RGB, RGBA, etc.)
        - 'format': Original file format (JPEG, PNG, etc.)
        - 'size_bytes': Approximate size in bytes

    Useful for displaying info to users and validation.
    """
    info = {
        'width': image.width,
        'height': image.height,
        'mode': image.mode,
        'format': image.format,
        'aspect_ratio': round(image.width / image.height, 2)
    }

    return info


def validate_image_dimensions(width: int, height: int,
                              min_size: int = 5,
                              max_size: int = 200) -> None:
    """
    Validate that image dimensions are within acceptable range.

    Args:
        width: Image width
        height: Image height
        min_size: Minimum allowed dimension
        max_size: Maximum allowed dimension

    Raises:
        ValueError: If dimensions are invalid

    Note:
        For bead art:
        - Minimum (5×5): Technically possible but very small
        - Maximum (200×200): Practical limit - very large projects
        - Common range: 15×15 to 58×58
    """
    if width < min_size or height < min_size:
        raise ValueError(
            f"Dimensions too small: {width}×{height}. "
            f"Minimum is {min_size}×{min_size}"
        )

    if width > max_size or height > max_size:
        raise ValueError(
            f"Dimensions too large: {width}×{height}. "
            f"Maximum is {max_size}×{max_size}"
        )


def create_thumbnail(image: Image.Image, max_size: int = 400) -> Image.Image:
    """
    Create a thumbnail of an image for preview purposes.

    Args:
        image: PIL Image to thumbnail
        max_size: Maximum dimension for thumbnail

    Returns:
        Thumbnail image (maintains aspect ratio)

    Example:
        >>> large_img = Image.open("huge_photo.jpg")  # 4000×3000
        >>> thumb = create_thumbnail(large_img, max_size=400)
        >>> thumb.size
        (400, 300)
    """
    # Calculate thumbnail size maintaining aspect ratio
    image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    return image
