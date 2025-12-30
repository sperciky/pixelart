# Pixel Art Pattern Generator - Project Context

## Project Overview
A Streamlit web application that converts uploaded images into pixel art patterns suitable for plastic bead/dot art frames (Perler beads, Hama beads, etc.).

## Purpose
This is a creative hobby tool for users who create physical pixel art with plastic beads. The tool helps them:
1. Convert any image into a gridded pattern
2. Reduce colors to match available bead colors
3. Get a shopping list of beads needed
4. Export patterns for manual recreation

## Core Features

### 1. Image Input
- User uploads an image (JPG, PNG, etc.)
- Preview original image

### 2. Grid Configuration
- User-defined width (number of beads horizontally)
- User-defined height (number of beads vertically)
- Maintains aspect ratio option

### 3. Color Palette Management
- Pre-built palettes for common bead brands (Perler, Hama)
- Custom palette upload (JSON format)
- Palette selection interface
- Future: Visual palette editor

### 4. Color Processing
- **Algorithm**: CIEDE2000 distance in LAB color space
- **Strategy**: Direct palette mapping (each pixel maps to nearest available bead color)
- No intermediate quantization step - uses exact user-selected colors

### 5. Output Formats
- **Visual Preview**: Pixelated image with optional grid overlay
- **Bead Count**: Shopping list showing quantity needed per color
- **CSV Export**: Pattern matrix for spreadsheet import
- **Image Download**: Preview image for reference

## Technical Architecture

### Design Principles
- **Separation of Concerns**: UI logic separate from core processing
- **Modularity**: Each feature in its own module
- **Reusability**: Core logic independent of Streamlit
- **Extensibility**: Easy to add new features, palettes, or export formats
- **Clarity**: Well-commented, readable code over premature optimization

### Technology Stack
- **Framework**: Streamlit (web-based GUI)
- **Language**: Python 3.8+
- **Image Processing**: Pillow (PIL)
- **Numerical Operations**: NumPy
- **Color Science**: scikit-image (for LAB conversion and CIEDE2000)
- **Data Handling**: Standard library (json)

### Project Structure
```
pixelart/
├── CONTEXT.md                  # This file - project overview
├── README.md                   # User-facing documentation
├── requirements.txt            # Python dependencies
├── app.py                      # Streamlit application entry point
├── src/                        # Core application modules
│   ├── __init__.py
│   ├── config.py              # Constants and configuration
│   ├── color_matcher.py       # Color distance algorithms (LAB/CIEDE2000)
│   ├── image_processor.py     # Image resizing and pixel grid conversion
│   ├── palette_manager.py     # Palette loading, validation, management
│   ├── pattern_generator.py   # Output generation (preview, CSV, counts)
│   └── models.py              # Data classes (Color, Palette, Pattern, etc.)
├── palettes/                   # Pre-built and custom color palettes
│   ├── perler.json
│   ├── hama.json
│   └── custom_example.json
└── tests/                      # Unit tests (future)
    └── __init__.py
```

### Module Responsibilities

#### `src/models.py`
Data classes and type definitions:
- `Color`: Represents a bead color (name, RGB, optional code)
- `Palette`: Collection of available colors
- `PixelPattern`: Grid of matched colors with metadata

#### `src/color_matcher.py`
Color distance and matching algorithms:
- RGB → LAB conversion
- CIEDE2000 distance calculation
- Find closest color from palette
- Batch pixel matching

#### `src/image_processor.py`
Image manipulation:
- Load and validate images
- Resize to target grid dimensions
- Extract pixel RGB values as array
- Aspect ratio calculations

#### `src/palette_manager.py`
Palette handling:
- Load palettes from JSON files
- Validate palette format
- List available palettes
- Save custom palettes
- Palette metadata management

#### `src/pattern_generator.py`
Output generation:
- Create visual preview with grid overlay
- Generate bead count dictionary
- Export CSV pattern file
- Color legend generation

#### `app.py`
Streamlit UI:
- File upload widget
- Grid size controls
- Palette selection dropdown
- Preview display
- Download buttons
- Thin wrapper calling core modules

## Color Matching Technical Details

### Why LAB Color Space?
- **Perceptually uniform**: Equal distances = equal perceived differences
- **Industry standard**: Used in printing, textiles, industrial color matching
- **Better for subtle colors**: Skin tones, pastels, gradients

### CIEDE2000 vs Simple RGB
```
Example: Matching a peachy skin tone
Available beads: Light Pink [255, 182, 193], Light Orange [255, 200, 150]

RGB Euclidean:
  - Might choose Light Orange (closer numerically)

CIEDE2000 in LAB:
  - Correctly chooses Light Pink (closer perceptually to human skin)
```

### Algorithm Flow
1. User uploads image
2. Image resized to target grid (e.g., 29×29 pixels)
3. For each pixel:
   - Get RGB value
   - Convert to LAB
   - Calculate CIEDE2000 distance to each available bead color
   - Assign nearest bead color
4. Generate outputs

## Palette JSON Format

```json
{
  "name": "Perler Beads Standard",
  "description": "Standard Perler bead colors",
  "colors": [
    {
      "name": "Red",
      "rgb": [203, 33, 39],
      "code": "P01",
      "hex": "#CB2127"
    },
    {
      "name": "Light Blue",
      "rgb": [84, 163, 209],
      "code": "P09",
      "hex": "#54A3D1"
    }
  ]
}
```

## Future Enhancements (Not in Initial Scope)

- [ ] Visual palette editor (add/remove colors with color picker)
- [ ] Dithering options (Floyd-Steinberg for smoother gradients)
- [ ] Multiple color matching algorithms (user choice)
- [ ] Pattern templates (common sizes: square, pegboard shapes)
- [ ] Assembly instructions (numbered steps)
- [ ] 3D preview mode
- [ ] Batch processing
- [ ] Pattern library (save/load previous designs)
- [ ] Social sharing
- [ ] Cost calculator with bead pricing
- [ ] Pattern difficulty rating

## Development Notes

### Non-Obvious Decisions

**Why direct palette mapping instead of k-means quantization?**
- User has fixed bead inventory
- Need exact match to available colors
- k-means would create arbitrary colors not in palette
- Single-step matching is simpler and more predictable

**Why Streamlit over Tkinter/Qt?**
- Faster development (10x less code for GUI)
- Modern, professional appearance
- Easily shareable (can deploy to web)
- Built-in widgets perfect for this use case
- Still runs locally

**Code organization philosophy:**
- Core modules have NO Streamlit dependencies
- Can reuse for CLI, API, or different GUI
- Easy to unit test
- Future-proof

## Usage Example

```python
# Example of core usage (without Streamlit UI)
from src.image_processor import load_and_resize_image
from src.palette_manager import load_palette
from src.color_matcher import match_image_to_palette
from src.pattern_generator import generate_preview, generate_bead_count

# Load inputs
image = load_and_resize_image("photo.jpg", width=29, height=29)
palette = load_palette("palettes/perler.json")

# Process
pattern = match_image_to_palette(image, palette)

# Generate outputs
preview_img = generate_preview(pattern, show_grid=True)
bead_count = generate_bead_count(pattern)
csv_export = generate_csv(pattern)
```

## Contributing Guidelines (Future)

- Follow PEP 8 style guide
- Add docstrings to all public functions
- Include type hints
- Write unit tests for new features
- Update this CONTEXT.md with architectural decisions

## Contact & Questions

This is a hobby project. For questions about the codebase:
- Read this CONTEXT.md file first
- Check module docstrings for implementation details
- Review README.md for user-facing documentation

---

**Last Updated**: 2025-12-30
**Python Version**: 3.8+
**Primary Developer**: Building with Claude Code
