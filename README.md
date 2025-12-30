# 🎨 Pixel Art Pattern Generator

Transform any image into a bead art pattern for Perler beads, Hama beads, or any plastic dot art frame!

## Features

✨ **Easy Image Upload** - Drag and drop any photo
🎯 **Custom Grid Sizes** - Choose your project dimensions
🌈 **Accurate Color Matching** - Uses professional CIEDE2000 color science
📊 **Bead Shopping List** - Know exactly how many of each color you need
💾 **Multiple Export Formats** - CSV patterns, visual previews, and more
🎨 **Pre-built Palettes** - Perler and Hama bead colors included
🔧 **Custom Palettes** - Upload your own color sets

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/pixelart.git
cd pixelart

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Usage

1. **Upload an Image** - Click "Browse files" or drag & drop
2. **Set Grid Size** - Use sliders to choose width and height (in beads)
3. **Select Palette** - Choose from Perler, Hama, or upload custom JSON
4. **Preview Result** - See your pixelated pattern with grid overlay
5. **Check Bead Count** - Review the shopping list
6. **Download** - Export CSV pattern or preview image

## Custom Palette Format

Create your own palette as a JSON file:

```json
{
  "name": "My Custom Palette",
  "description": "My favorite bead colors",
  "colors": [
    {
      "name": "Cherry Red",
      "rgb": [220, 20, 60],
      "code": "R01",
      "hex": "#DC143C"
    },
    {
      "name": "Ocean Blue",
      "rgb": [0, 105, 148],
      "code": "B05",
      "hex": "#006994"
    }
  ]
}
```

Save to `palettes/my_palette.json` and it will appear in the dropdown.

## Examples

### Input
Original photo (any size)

### Output
- 29×29 pixel grid pattern
- Mapped to available bead colors
- Bead count: Red (45), Blue (32), White (18)
- Downloadable CSV and preview image

## Technology

- **Python 3.8+** - Core language
- **Streamlit** - Web interface
- **Pillow** - Image processing
- **scikit-image** - Color science (LAB color space)
- **NumPy** - Numerical operations

## Color Matching Explained

This tool uses **CIEDE2000** color difference formula in **LAB color space** - the same method used by professional textile and paint industries. This ensures the bead colors chosen actually *look* closest to your image, not just closest mathematically.

## Project Structure

```
pixelart/
├── app.py                  # Streamlit application
├── src/                    # Core modules
│   ├── color_matcher.py   # Color distance algorithms
│   ├── image_processor.py # Image resizing and conversion
│   ├── palette_manager.py # Palette loading and management
│   └── pattern_generator.py # Output generation
└── palettes/              # Color palette definitions
    ├── perler.json
    └── hama.json
```

## Tips for Best Results

- **Start with simple images** - Portraits with plain backgrounds work great
- **Consider bead count** - Larger grids need more beads (and time to assemble!)
- **Test sizes** - 20×20 is good for beginners, 40×40+ for detailed work
- **High contrast helps** - Images with clear subjects convert better
- **Edit before upload** - Crop and adjust brightness/contrast in advance

## Common Grid Sizes

| Size | Difficulty | Use Case | Approx. Beads |
|------|-----------|----------|---------------|
| 15×15 | Beginner | Coasters, ornaments | ~225 |
| 29×29 | Intermediate | Standard pegboard | ~840 |
| 40×40 | Advanced | Detailed art | ~1,600 |
| 58×58 | Expert | Wall art | ~3,360 |

## Troubleshooting

**Colors look wrong?**
- Make sure you selected the correct palette for your bead brand
- Try adjusting image brightness/contrast before upload

**Pattern too detailed/blurry?**
- Adjust grid size - smaller grid = more pixelated, larger = more detail

**Upload fails?**
- Supported formats: JPG, PNG, GIF, BMP
- Try reducing file size if very large (>10MB)

## Contributing

Contributions welcome! See `CONTEXT.md` for architecture details.

## License

MIT License - free for personal and commercial use

## Credits

Built with ❤️ for the bead art community

---

**Questions?** Open an issue on GitHub
**Share your creations!** Tag #beadartgenerator
