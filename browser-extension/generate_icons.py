"""Generate placeholder icons for the browser extension.

Run this script to create simple icon files:
    python generate_icons.py
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Create icons directory
icons_dir = os.path.join(os.path.dirname(__file__), 'icons')
os.makedirs(icons_dir, exist_ok=True)

# Define icon sizes
sizes = [16, 32, 48, 128]

# Colors
bg_color = (102, 126, 234)  # Purple-blue gradient color
text_color = (255, 255, 255)  # White

for size in sizes:
    # Create a new image with a colored background
    img = Image.new('RGB', (size, size), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw a simple "A" for Accessibility
    # For larger icons, we can add text
    if size >= 48:
        try:
            # Try to use a font, fall back to default if not available
            font_size = int(size * 0.6)
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        text = "A"
        # Get text bounding box for centering
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center the text
        x = (size - text_width) // 2
        y = (size - text_height) // 2 - bbox[1]
        
        draw.text((x, y), text, fill=text_color, font=font)
    else:
        # For small icons, draw a simple shape
        margin = size // 4
        draw.ellipse([margin, margin, size - margin, size - margin], 
                    fill=text_color, outline=text_color)
    
    # Save the icon
    icon_path = os.path.join(icons_dir, f'icon{size}.png')
    img.save(icon_path)
    print(f"Created {icon_path}")

print("\nIcons generated successfully!")
print("You can replace these with custom-designed icons later.")
