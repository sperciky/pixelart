"""
Configuration and constants for Pixel Art Pattern Generator

Centralized location for application-wide settings and constants.
"""

# Image processing defaults
DEFAULT_GRID_WIDTH = 29  # Standard pegboard size
DEFAULT_GRID_HEIGHT = 29
MIN_GRID_SIZE = 5
MAX_GRID_SIZE = 200  # Practical limit for bead art

# Supported image formats
SUPPORTED_IMAGE_FORMATS = {
    'PNG': 'image/png',
    'JPEG': 'image/jpeg',
    'JPG': 'image/jpeg',
    'GIF': 'image/gif',
    'BMP': 'image/bmp',
    'WEBP': 'image/webp'
}

# Color matching settings
COLOR_SPACE = "LAB"  # Use LAB color space for perceptual accuracy
DISTANCE_METRIC = "CIEDE2000"  # Industry standard color difference

# Output settings
DEFAULT_GRID_LINE_COLOR = (128, 128, 128)  # Gray grid lines
DEFAULT_GRID_LINE_WIDTH = 1
DEFAULT_CELL_SIZE = 20  # Pixels per bead in preview image

# CSV export settings
CSV_DELIMITER = ","
CSV_HEADER = True  # Include column headers in CSV export

# Palette settings
PALETTES_DIR = "palettes"
DEFAULT_PALETTE = "perler.json"

# UI settings (Streamlit)
APP_TITLE = "🎨 Pixel Art Pattern Generator"
APP_ICON = "🎨"
PAGE_CONFIG = {
    "page_title": "Pixel Art Pattern Generator",
    "page_icon": "🎨",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Help text and descriptions
HELP_TEXT = {
    "grid_width": "Number of beads horizontally (width of your pegboard)",
    "grid_height": "Number of beads vertically (height of your pegboard)",
    "palette": "Choose the bead brand/colors you have available",
    "maintain_aspect": "Keep original image proportions when resizing",
    "show_grid": "Overlay grid lines on preview to see bead positions"
}

# Common pegboard sizes (width, height, name)
COMMON_SIZES = [
    (29, 29, "Standard Square (29×29)"),
    (15, 15, "Small Square (15×15)"),
    (40, 40, "Large Square (40×40)"),
    (58, 58, "Extra Large (58×58)"),
    (29, 58, "Rectangle (29×58)"),
]
