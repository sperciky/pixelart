# Quick Start Guide

## Installation

1. **Clone the repository** (or download the files)
   ```bash
   cd pixelart
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Start the Streamlit app:
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Using the Application

### Step 1: Upload an Image
- Click "Browse files" in the sidebar
- Select any image (JPG, PNG, GIF, etc.)

### Step 2: Configure Grid Size
- Choose a preset size (e.g., "Standard Square 29×29")
- Or use custom dimensions with the sliders
- Toggle "Maintain aspect ratio" if desired

### Step 3: Select Color Palette
- Choose from pre-built palettes:
  - **Perler Beads Standard** (50 colors)
  - **Hama Beads Standard** (45 colors)
  - **Basic Colors** (8 colors - good for testing)
- Or upload your own custom palette JSON

### Step 4: Generate Pattern
- Click "Generate Pattern" button
- Wait for processing (usually a few seconds)

### Step 5: Download Outputs
- **Preview Image**: Visual pattern with grid overlay
- **Pattern CSV**: Grid of color codes for assembly
- **Bead Count CSV**: Shopping list for spreadsheets
- **Color Legend**: Reference guide for colors

## Creating Custom Palettes

Create a JSON file in the `palettes/` directory:

```json
{
  "name": "My Custom Palette",
  "description": "Description here",
  "colors": [
    {
      "name": "Color Name",
      "rgb": [255, 0, 0],
      "code": "C01",
      "hex": "#FF0000"
    }
  ]
}
```

Restart the app to see your new palette in the dropdown.

## Tips for Best Results

1. **Start with high-contrast images** - Portraits with plain backgrounds work best
2. **Use appropriate grid sizes**:
   - 15×15: Small projects, coasters
   - 29×29: Standard pegboard
   - 40×40+: Large detailed projects
3. **Choose the right palette** - Match your actual bead inventory
4. **Crop images before upload** - Focus on the subject
5. **Adjust brightness/contrast** - Do this before uploading for better results

## Common Issues

**"No palettes found" error**
- Make sure `palettes/` directory exists with JSON files
- Check that JSON files are valid

**Pattern looks too pixelated**
- Increase grid size (more beads = more detail)

**Colors seem off**
- Verify you selected the correct palette
- The app uses perceptual color matching (CIEDE2000) which is very accurate

**Upload fails**
- Check file format (must be image)
- Try reducing file size if very large

## Project Structure

```
pixelart/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── CONTEXT.md             # Developer documentation
├── README.md              # User guide
├── QUICKSTART.md          # This file
├── src/                   # Core modules
│   ├── models.py          # Data classes
│   ├── color_matcher.py   # Color science
│   ├── image_processor.py # Image handling
│   ├── palette_manager.py # Palette loading
│   ├── pattern_generator.py # Output generation
│   └── config.py          # Constants
└── palettes/              # Color palettes
    ├── perler.json
    ├── hama.json
    └── basic.json
```

## Next Steps

- Try different images and grid sizes
- Create custom palettes for your bead collection
- Experiment with "Maintain aspect ratio" setting
- Share your creations!

## Need Help?

- Read `CONTEXT.md` for technical details
- Read `README.md` for full documentation
- Check that all dependencies are installed
- Verify Python version (3.8+ required)

---

Happy crafting! 🎨
