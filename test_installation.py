#!/usr/bin/env python
"""
Quick test script to verify installation and basic functionality.

Run this to check that all modules can be imported and basic operations work.
"""

import sys
from pathlib import Path


def test_imports():
    """Test that all core modules can be imported."""
    print("Testing imports...")

    try:
        from src import models, config, color_matcher, image_processor
        from src import palette_manager, pattern_generator
        print("✅ All core modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_dependencies():
    """Test that external dependencies are available."""
    print("\nTesting dependencies...")

    dependencies = {
        'streamlit': 'Streamlit',
        'PIL': 'Pillow',
        'numpy': 'NumPy',
        'skimage': 'scikit-image'
    }

    all_ok = True
    for module_name, display_name in dependencies.items():
        try:
            __import__(module_name)
            print(f"✅ {display_name} is installed")
        except ImportError:
            print(f"❌ {display_name} is NOT installed")
            all_ok = False

    return all_ok


def test_palettes():
    """Test that palette files exist and can be loaded."""
    print("\nTesting palettes...")

    from src.palette_manager import list_available_palettes

    palettes = list_available_palettes()

    if not palettes:
        print("❌ No palettes found in palettes/ directory")
        return False

    print(f"✅ Found {len(palettes)} palette(s):")
    for p in palettes:
        print(f"   - {p['name']} ({p['color_count']} colors)")

    return True


def test_basic_functionality():
    """Test basic color matching functionality."""
    print("\nTesting basic functionality...")

    try:
        from src.models import Color, Palette
        from src.color_matcher import rgb_to_lab, compute_ciede2000

        # Create test colors
        red = Color(name="Red", rgb=(255, 0, 0))
        blue = Color(name="Blue", rgb=(0, 0, 255))

        # Test RGB to LAB conversion
        red_lab = rgb_to_lab(red.rgb)
        print(f"✅ RGB to LAB conversion: {red.rgb} → {red_lab}")

        # Test color distance
        distance = compute_ciede2000(red_lab, rgb_to_lab(blue.rgb))
        print(f"✅ Color distance calculation: Red-Blue distance = {distance:.2f}")

        return True

    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Pixel Art Pattern Generator - Installation Test")
    print("=" * 60)

    tests = [
        ("Module Imports", test_imports),
        ("Dependencies", test_dependencies),
        ("Palettes", test_palettes),
        ("Basic Functionality", test_basic_functionality)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not result:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n🎉 All tests passed! You're ready to run the app.")
        print("\nRun: streamlit run app.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\nTry running: pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
