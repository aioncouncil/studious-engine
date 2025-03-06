#!/usr/bin/env python
"""
Script to generate placeholder images for the EudaimoniaGo project.
Requires Pillow (PIL): pip install Pillow
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_power_icon(name, color, size=(200, 200)):
    """Create a simple power icon with the name and color."""
    img = Image.new('RGB', size, color=color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a system font, fallback to default
    try:
        font = ImageFont.truetype("Arial", 24)
    except IOError:
        font = ImageFont.load_default()
    
    # Center the text
    text = f"Power: {name}"
    text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:4]
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    
    # Draw text in white
    draw.text(position, text, fill="white", font=font)
    
    return img

def create_background(size=(800, 600), color="darkblue"):
    """Create a simple gradient background."""
    img = Image.new('RGB', size, color=color)
    draw = ImageDraw.Draw(img)
    
    # Draw a simple pattern
    for i in range(0, size[0], 20):
        draw.line([(i, 0), (i, size[1])], fill="rgba(255, 255, 255, 30)", width=1)
    
    for i in range(0, size[1], 20):
        draw.line([(0, i), (size[0], i)], fill="rgba(255, 255, 255, 30)", width=1)
    
    # Add welcome text
    try:
        font = ImageFont.truetype("Arial", 36)
    except IOError:
        font = ImageFont.load_default()
    
    text = "Welcome to EudaimoniaGo!"
    text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:4]
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    
    # Draw text with a shadow effect
    draw.text((position[0]+2, position[1]+2), text, font=font, fill="black")
    draw.text(position, text, font=font, fill="white")
    
    return img

if __name__ == "__main__":
    # Ensure the images directory exists
    os.makedirs("static/images", exist_ok=True)
    
    # Create power icons
    power_icons = {
        "wisdom": ("purple", "power-wisdom.png"),
        "strength": ("red", "power-strength.png"),
        "leadership": ("blue", "power-leadership.png"),
        "creativity": ("green", "power-creativity.png"),
    }
    
    for power_name, (color, filename) in power_icons.items():
        img = create_power_icon(power_name, color)
        img.save(f"static/images/{filename}")
        print(f"Created {filename}")
    
    # Create welcome background
    bg = create_background()
    bg.save("static/images/welcome-background.jpg")
    print("Created welcome-background.jpg")
    
    print("All placeholder images have been created successfully.") 