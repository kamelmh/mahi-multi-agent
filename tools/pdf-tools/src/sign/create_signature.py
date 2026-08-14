"""
Create a realistic handwritten-style signature
"""
from PIL import Image, ImageDraw, ImageFont
import random
import math


def create_handwritten_signature(name, output_path="signature.png", style="formal"):
    """
    Create a realistic handwritten-style signature.
    
    Styles:
    - formal: Clean, professional look
    - artistic: Slightly stylized
    - quick: Fast, casual look
    """
    width, height = 400, 120
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Split name into parts
    parts = name.split()
    if len(parts) >= 3:
        first = parts[0]  # Mahi
        middle = parts[1]  # Kamel
        last = parts[2]  # Abdelghani
    elif len(parts) == 2:
        first = parts[0]
        middle = ""
        last = parts[1]
    else:
        first = name
        middle = ""
        last = ""
    
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
    font_size = 42
    
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
    pen_width = 2
    
    # Draw the signature
    x_start = 30
    y_center = height // 2
    
    # Add slight randomness for realism
    def jitter(value, amount=2):
        return value + random.uniform(-amount, amount)
    
    # Draw first name with underline
    x = x_start
    
    # First name - Mahi
    if style == "formal":
        # More upright, professional
        draw.text((x, y_center - 20), first, fill=ink_color, font=font)
        x += font.getlength(first) + 15
    elif style == "artistic":
        draw.text((x, y_center - 25), first, fill=ink_color, font=font)
        x += font.getlength(first) + 15
    else:
        draw.text((x, y_center - 15), first, fill=ink_color, font=font)
        x += font.getlength(first) + 10
    
    # Middle name - Kamel (slightly smaller or different style)
    if middle:
        try:
            middle_font = ImageFont.truetype(font.path, font_size - 6)
        except:
            middle_font = font
        draw.text((x, y_center - 18), middle, fill=ink_color, font=middle_font)
        x += font.getlength(middle) + 15
    
    # Last name - Abdelghani (slightly smaller)
    if last:
        try:
            last_font = ImageFont.truetype(font.path, font_size - 8)
        except:
            last_font = font
        draw.text((x, y_center - 16), last, fill=ink_color, font=last_font)
    
    # Add decorative underline
    underline_y = y_center + 30
    draw.line([(x_start - 10, underline_y), (x + font.getlength(last) + 20, underline_y)], 
              fill=ink_color, width=1)
    
    # Add small flourish at end
    flourish_x = x + font.getlength(last) + 20
    draw.line([(flourish_x, underline_y), (flourish_x + 15, underline_y - 10)], 
              fill=ink_color, width=1)
    
    img.save(output_path)
    return output_path


def create_stamp_signature(name, output_path="stamp.png"):
    """Create a round stamp-style signature."""
    size = 150
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw circle border
    border_color = (0, 0, 180)  # Blue stamp
    draw.ellipse([5, 5, size-5, size-5], outline=border_color, width=3)
    draw.ellipse([10, 10, size-10, size-10], outline=border_color, width=1)
    
    # Add name
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 14)
    except:
        font = ImageFont.load_default()
    
    # Split name for stamp layout
    parts = name.split()
    
    # Draw text centered
    text = name
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_x = (size - text_width) // 2
    draw.text((text_x, size//2 - 10), text, fill=border_color, font=font)
    
    img.save(output_path)
    return output_path


if __name__ == "__main__":
    name = "Mahi Kamel Abdelghani"
    
    # Create formal signature
    create_handwritten_signature(name, "signature_formal.png", "formal")
    print("Created: signature_formal.png")
    
    # Create artistic signature
    create_handwritten_signature(name, "signature_artistic.png", "artistic")
    print("Created: signature_artistic.png")
    
    # Create stamp
    create_stamp_signature(name, "stamp.png")
    print("Created: stamp.png")
