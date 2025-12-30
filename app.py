"""
Pixel Art Pattern Generator - Streamlit Application

A web-based tool for converting images into bead art patterns.
"""

import streamlit as st
from PIL import Image
import io

# Import our core modules
from src.models import PixelPattern
from src.image_processor import load_and_resize_image, get_image_info, validate_image_dimensions
from src.palette_manager import list_available_palettes, load_palette_from_json, validate_palette_json
from src.color_matcher import match_image_to_palette, get_color_statistics
from src.pattern_generator import (
    create_pattern_preview,
    generate_bead_count_text,
    export_pattern_to_csv,
    export_bead_count_to_csv,
    image_to_bytes,
    create_color_legend
)
from src.config import (
    PAGE_CONFIG,
    DEFAULT_GRID_WIDTH,
    DEFAULT_GRID_HEIGHT,
    MIN_GRID_SIZE,
    MAX_GRID_SIZE,
    COMMON_SIZES,
    HELP_TEXT
)


# Configure Streamlit page
st.set_page_config(**PAGE_CONFIG)


def main():
    """Main application entry point."""

    # Title and description
    st.title("🎨 Pixel Art Pattern Generator")
    st.markdown("""
    Transform any image into a bead art pattern for **Perler beads**, **Hama beads**,
    or any plastic dot art frame!

    Upload an image, choose your grid size and available colors, then download your pattern.
    """)

    # Sidebar for configuration
    st.sidebar.header("⚙️ Configuration")

    # File upload
    st.sidebar.subheader("1. Upload Image")
    uploaded_file = st.sidebar.file_uploader(
        "Choose an image file",
        type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'],
        help="Upload any image to convert to pixel art"
    )

    # Grid size configuration
    st.sidebar.subheader("2. Grid Size")

    # Quick presets
    preset_names = [size[2] for size in COMMON_SIZES]
    preset_names.insert(0, "Custom Size")

    selected_preset = st.sidebar.selectbox(
        "Quick Presets",
        preset_names,
        help="Choose a common pegboard size or select Custom"
    )

    # Set initial values based on preset
    if selected_preset == "Custom Size":
        default_width = DEFAULT_GRID_WIDTH
        default_height = DEFAULT_GRID_HEIGHT
    else:
        # Find the selected preset
        for size in COMMON_SIZES:
            if size[2] == selected_preset:
                default_width = size[0]
                default_height = size[1]
                break

    # Grid dimension sliders
    grid_width = st.sidebar.slider(
        "Width (beads)",
        min_value=MIN_GRID_SIZE,
        max_value=MAX_GRID_SIZE,
        value=default_width,
        help=HELP_TEXT["grid_width"]
    )

    grid_height = st.sidebar.slider(
        "Height (beads)",
        min_value=MIN_GRID_SIZE,
        max_value=MAX_GRID_SIZE,
        value=default_height,
        help=HELP_TEXT["grid_height"]
    )

    # Aspect ratio option
    maintain_aspect = st.sidebar.checkbox(
        "Maintain aspect ratio",
        value=False,
        help=HELP_TEXT["maintain_aspect"]
    )

    # Palette selection
    st.sidebar.subheader("3. Select Palette")

    # List available palettes
    available_palettes = list_available_palettes()

    if not available_palettes:
        st.sidebar.error("No palettes found! Please add palette files to the 'palettes' directory.")
        st.stop()

    palette_names = [p['name'] for p in available_palettes]

    selected_palette_name = st.sidebar.selectbox(
        "Bead Color Palette",
        palette_names,
        help=HELP_TEXT["palette"]
    )

    # Load selected palette
    selected_palette_info = next(p for p in available_palettes if p['name'] == selected_palette_name)
    palette = load_palette_from_json(selected_palette_info['path'])

    # Show palette info
    st.sidebar.info(f"**{palette.name}**\n\n{palette.description or ''}\n\n{len(palette.colors)} colors available")

    # Custom palette upload (optional)
    st.sidebar.subheader("Or Upload Custom Palette")
    custom_palette_file = st.sidebar.file_uploader(
        "Upload JSON palette",
        type=['json'],
        help="Upload a custom color palette in JSON format"
    )

    if custom_palette_file is not None:
        # Save uploaded file temporarily
        with open("/tmp/custom_palette.json", "wb") as f:
            f.write(custom_palette_file.getbuffer())

        # Validate
        is_valid, error_msg = validate_palette_json("/tmp/custom_palette.json")

        if is_valid:
            palette = load_palette_from_json("/tmp/custom_palette.json")
            st.sidebar.success(f"✅ Loaded custom palette: {palette.name} ({len(palette.colors)} colors)")
        else:
            st.sidebar.error(f"❌ Invalid palette: {error_msg}")

    # Display options
    st.sidebar.subheader("4. Display Options")
    show_grid = st.sidebar.checkbox(
        "Show grid lines",
        value=True,
        help=HELP_TEXT["show_grid"]
    )

    cell_size = st.sidebar.slider(
        "Preview cell size",
        min_value=10,
        max_value=50,
        value=20,
        help="Size of each bead in the preview (pixels)"
    )

    # Main content area
    if uploaded_file is None:
        # Show instructions when no file uploaded
        st.info("👈 Upload an image using the sidebar to get started!")

        # Show example/demo section
        st.subheader("How It Works")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**1. Upload Image**")
            st.markdown("Choose any photo or image you want to convert")

        with col2:
            st.markdown("**2. Configure**")
            st.markdown("Set grid size and select your available bead colors")

        with col3:
            st.markdown("**3. Download**")
            st.markdown("Get your pattern as CSV, preview image, and bead count")

        # Show palette preview
        st.subheader("Selected Palette Preview")
        show_palette_preview(palette)

    else:
        # Process the uploaded image
        try:
            # Display original image info
            st.subheader("Original Image")

            col1, col2 = st.columns([1, 1])

            with col1:
                # Show original image
                original_image = Image.open(uploaded_file)
                st.image(original_image, caption="Uploaded Image", use_container_width=True)

            with col2:
                # Show image info
                img_info = get_image_info(original_image)
                st.markdown("**Image Information:**")
                st.markdown(f"- Dimensions: {img_info['width']} × {img_info['height']} pixels")
                st.markdown(f"- Aspect Ratio: {img_info['aspect_ratio']}")
                st.markdown(f"- Format: {img_info['format']}")

                st.markdown(f"**Pattern Configuration:**")
                st.markdown(f"- Grid Size: {grid_width} × {grid_height} beads")
                st.markdown(f"- Total Beads: {grid_width * grid_height}")
                st.markdown(f"- Palette: {palette.name}")

            # Validate dimensions
            validate_image_dimensions(grid_width, grid_height, MIN_GRID_SIZE, MAX_GRID_SIZE)

            # Process button
            if st.button("🎨 Generate Pattern", type="primary", use_container_width=True):
                with st.spinner("Converting image to pixel art pattern..."):
                    # Load and resize image
                    resized_image, image_array = load_and_resize_image(
                        uploaded_file.getvalue(),
                        grid_width,
                        grid_height,
                        maintain_aspect
                    )

                    # Get color statistics
                    stats = get_color_statistics(image_array, palette)

                    # Match to palette
                    color_grid = match_image_to_palette(image_array, palette)

                    # Create PixelPattern object
                    pattern = PixelPattern(
                        width=grid_width,
                        height=grid_height,
                        grid=color_grid,
                        palette=palette,
                        original_image=original_image,
                        metadata=stats
                    )

                    # Store in session state for downloads
                    st.session_state['pattern'] = pattern
                    st.session_state['processed'] = True

                st.success("✅ Pattern generated successfully!")
                st.rerun()

            # Display results if pattern exists
            if st.session_state.get('processed', False) and 'pattern' in st.session_state:
                pattern = st.session_state['pattern']

                st.markdown("---")
                st.subheader("🎯 Pattern Preview")

                # Generate preview
                preview_image = create_pattern_preview(
                    pattern,
                    cell_size=cell_size,
                    show_grid=show_grid
                )

                # Display preview
                st.image(preview_image, caption=f"Pixel Art Pattern ({grid_width}×{grid_height})", use_container_width=True)

                # Pattern statistics
                st.markdown("---")
                st.subheader("📊 Pattern Statistics")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Total Beads", pattern.total_beads())

                with col2:
                    st.metric("Unique Colors", pattern.unique_colors_count())

                with col3:
                    st.metric("Palette Used", f"{pattern.metadata.get('palette_utilization', 0)}%")

                with col4:
                    st.metric("Avg Color Distance", pattern.metadata.get('average_distance', 0))

                # Bead count
                st.markdown("---")
                st.subheader("🛒 Bead Shopping List")

                col1, col2 = st.columns([2, 1])

                with col1:
                    # Display bead count as text
                    bead_count_text = generate_bead_count_text(pattern)
                    st.text(bead_count_text)

                with col2:
                    # Show color legend
                    st.markdown("**Color Legend**")
                    legend_image = create_color_legend(pattern, swatch_size=25)
                    st.image(legend_image, use_container_width=True)

                # Downloads
                st.markdown("---")
                st.subheader("💾 Download Pattern")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    # Download preview image
                    preview_bytes = image_to_bytes(preview_image, format='PNG')
                    st.download_button(
                        label="📥 Preview Image",
                        data=preview_bytes,
                        file_name=f"pattern_{grid_width}x{grid_height}.png",
                        mime="image/png",
                        use_container_width=True
                    )

                with col2:
                    # Download CSV pattern
                    csv_pattern = export_pattern_to_csv(pattern, use_codes=True)
                    st.download_button(
                        label="📥 Pattern CSV",
                        data=csv_pattern,
                        file_name=f"pattern_{grid_width}x{grid_height}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

                with col3:
                    # Download bead count CSV
                    csv_bead_count = export_bead_count_to_csv(pattern)
                    st.download_button(
                        label="📥 Bead Count CSV",
                        data=csv_bead_count,
                        file_name=f"bead_count_{grid_width}x{grid_height}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

                with col4:
                    # Download color legend
                    legend_bytes = image_to_bytes(legend_image, format='PNG')
                    st.download_button(
                        label="📥 Color Legend",
                        data=legend_bytes,
                        file_name=f"legend_{grid_width}x{grid_height}.png",
                        mime="image/png",
                        use_container_width=True
                    )

        except Exception as e:
            st.error(f"Error processing image: {str(e)}")
            st.exception(e)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
        <p>Made with ❤️ for the bead art community |
        Uses CIEDE2000 color matching in LAB color space for accurate results</p>
    </div>
    """, unsafe_allow_html=True)


def show_palette_preview(palette):
    """Display a preview of the selected palette colors."""

    st.markdown(f"**{palette.name}** - {len(palette.colors)} colors")

    # Display colors in a grid
    cols_per_row = 8
    colors = palette.colors

    for i in range(0, len(colors), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < len(colors):
                color = colors[i + j]
                with col:
                    # Create a small colored box
                    color_box = f"""
                    <div style='background-color: {color.hex};
                                width: 100%;
                                height: 50px;
                                border: 1px solid #ccc;
                                border-radius: 5px;
                                margin-bottom: 5px;'></div>
                    <div style='text-align: center; font-size: 0.7em;'>{color.name}</div>
                    """
                    st.markdown(color_box, unsafe_allow_html=True)


if __name__ == "__main__":
    # Initialize session state
    if 'processed' not in st.session_state:
        st.session_state['processed'] = False

    main()
