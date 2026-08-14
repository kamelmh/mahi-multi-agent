"""
Create short signature: Mahi Kamel
"""
from PIL import Image, ImageDraw, ImageFont
import random


def create_short_signature(name, output_path="signature_short.png"):
    """Create a short handwritten-style signature."""
    width, height = 300, 80
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Try to find a good font
    font_paths = [
        "C:/Windows/Fonts/signfont.ttf",
        "C:/Windows/Fonts/scriptbl.ttf",
        "C:/Windows/Fonts/brushsci.ttf",
        "C:/Windows/Fonts/Edwardian.ttf",
        "C:/Windows/Fonts/ITCSCRIPT.TTF",
        "C:/Windows/Fonts/ScriptBl.ttf",
    ]
    
    font = None
    font_size = 36
    
    for font_path in font_paths:
        try:
            font = ImageFont.truetype(font_path, font_size)
            break
        except:
            continue
    
    # Fallback to arial if no script font found
    if font is None:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
    
    # Colors
    ink_color = (0, 0, 0)  # Black ink
    
    # Draw the signature
    x_start = 20
    y_center = height // 2
    
    # Draw name
    draw.text((x_start, y_center - 18), name, fill=ink_color, font=font)
    
    # Add decorative underline
    text_width = font.getlength(name)
    underline_y = y_center + 25
    draw.line([(x_start - 5, underline_y), (x_start + text_width + 15, underline_y)], 
              fill=ink_color, width=1)
    
    img.save(output_path)
    return output_path


if __name__ == "__main__":
    create_short_signature("Mahi Kamel", "signature_short.png")
    print("Created: signature_short.png")
