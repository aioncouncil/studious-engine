#!/usr/bin/env python
"""
Script to create placeholder images for the Unified Market System
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random

# [REF:44e5f6a7-b8c9-d0e1-f2a3-b4c5d6e7f8a9:ECONOMIC_SYSTEM]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the economic_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

# Ensure the static/images directory exists
os.makedirs('static/images', exist_ok=True)

# Define colors for different economic layers
COLORS = {
    'outer': [(255, 159, 10), (255, 59, 48)],  # Orange to Red gradient
    'middle': [(94, 92, 230), (0, 113, 227)],  # Purple to Blue gradient
    'inner': [(40, 205, 65), (90, 200, 250)],  # Green to Teal gradient
}

def create_gradient_image(width, height, color1, color2, filename):
    """Create a gradient image with text."""
    image = Image.new('RGB', (width, height), color=color1)
    draw = ImageDraw.Draw(image)
    
    # Create a gradient effect
    for y in range(height):
        r = int(color1[0] + (color2[0] - color1[0]) * y / height)
        g = int(color1[1] + (color2[1] - color1[1]) * y / height)
        b = int(color1[2] + (color2[2] - color1[2]) * y / height)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Add some random shapes for visual interest
    for _ in range(5):
        shape_size = random.randint(20, 100)
        x = random.randint(0, width - shape_size)
        y = random.randint(0, height - shape_size)
        shape_type = random.choice(['circle', 'rectangle'])
        
        if shape_type == 'circle':
            draw.ellipse([(x, y), (x + shape_size, y + shape_size)], 
                        fill=(255, 255, 255, 30))
        else:
            draw.rectangle([(x, y), (x + shape_size, y + shape_size)], 
                          fill=(255, 255, 255, 30))
    
    # Add some text
    try:
        # Try to get a font - fallback to default if not available
        font = ImageFont.truetype("Arial", 36)
    except IOError:
        font = ImageFont.load_default()
    
    text = os.path.basename(filename).replace('.jpg', '').replace('-', ' ').title()
    text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:4]
    position = ((width - text_width) // 2, (height - text_height) // 2)
    
    # Draw text with a shadow effect
    draw.text((position[0]+2, position[1]+2), text, font=font, fill=(0, 0, 0, 128))
    draw.text(position, text, font=font, fill=(255, 255, 255, 200))
    
    # Apply a slight blur for a more polished look
    image = image.filter(ImageFilter.GaussianBlur(1))
    
    # Save the image
    image.save(filename)
    print(f"Created {filename}")

def create_market_item(index, layer_type, filename):
    """Create a market item image with a specific style based on layer."""
    width, height = 400, 300
    
    # Choose colors based on layer type
    if layer_type in COLORS:
        color1, color2 = COLORS[layer_type]
    else:
        # Default colors if layer type not recognized
        color1, color2 = (100, 100, 100), (200, 200, 200)
    
    # Adjust colors slightly for variety
    color1 = tuple(min(255, max(0, c + random.randint(-20, 20))) for c in color1)
    color2 = tuple(min(255, max(0, c + random.randint(-20, 20))) for c in color2)
    
    create_gradient_image(width, height, color1, color2, filename)

# Create city layer background images
for layer in ['port-city', 'middle-city', 'inner-city']:
    layer_type = layer.split('-')[0]
    if layer_type == 'port':
        layer_type = 'outer'
    
    filename = f"static/images/{layer}.jpg"
    if not os.path.exists(filename):
        color1, color2 = COLORS.get(layer_type, ((100, 100, 100), (200, 200, 200)))
        create_gradient_image(800, 500, color1, color2, filename)

# Create market item images
for i in range(1, 9):
    # Determine which layer based on index (for variety)
    if i % 3 == 0:
        layer_type = 'inner'
    elif i % 3 == 1:
        layer_type = 'outer'
    else:
        layer_type = 'middle'
    
    filename = f"static/images/market-item{i}.jpg"
    if not os.path.exists(filename):
        create_market_item(i, layer_type, filename)

print("All required market images have been created successfully.") 