"""Image Analyzer - Extracts metadata and basic info from images.

Uses Pillow for image analysis.
For screenshots: extracts dimensions, format, color info.
For OCR: would need Tesseract (not installed yet).
"""

import os
import json
from PIL import Image


def analyze_image(image_path):
    """Analyze an image and return metadata."""
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            format_type = img.format
            mode = img.mode

            # Get file size
            file_size = os.path.getsize(image_path)

            # Determine image category based on content
            category = categorize_by_dimensions(width, height)

            return {
                "success": True,
                "width": width,
                "height": height,
                "format": format_type,
                "mode": mode,
                "file_size": file_size,
                "category": category,
                "aspect_ratio": round(width / height, 2) if height > 0 else 0,
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def categorize_by_dimensions(width, height):
    """Guess image category by dimensions."""
    ratio = width / height if height > 0 else 0

    if ratio > 2:
        return "panorama/banner"
    elif ratio < 0.5:
        return "mobile_screenshot"
    elif 0.9 < ratio < 1.1:
        return "square/screenshot"
    elif 1.5 < ratio < 2:
        return "desktop_screenshot"
    else:
        return "photo/illustration"


def batch_analyze(directory, extensions=(".jpg", ".jpeg", ".png", ".gif", ".webp")):
    """Analyze all images in a directory."""
    results = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(extensions):
                path = os.path.join(root, file)
                result = analyze_image(path)
                result["path"] = path
                result["name"] = file
                results.append(result)
    return results
