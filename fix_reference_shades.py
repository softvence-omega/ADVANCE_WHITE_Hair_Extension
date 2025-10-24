import cv2
import numpy as np
import json
from pathlib import Path

def extract_pure_hair_color(image_path):
    """Extract only pure hair color, filtering grey/white strands"""
    img = cv2.imread(str(image_path))
    if img is None:
        return None
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pixels = img_rgb.reshape(-1, 3)
    
    # Filter pixels
    filtered = []
    for pixel in pixels:
        brightness = pixel[0] * 0.299 + pixel[1] * 0.587 + pixel[2] * 0.114
        max_val = max(pixel)
        min_val = min(pixel)
        
        # Skip very dark, very bright, and grey/white
        if 15 < brightness < 230:
            # Check saturation to filter grey
            if max_val > 0:
                saturation = (max_val - min_val) / max_val
                # Keep only colored pixels (not grey)
                if saturation > 0.08 or brightness < 100:
                    filtered.append(pixel)
    
    if len(filtered) < 100:
        filtered = pixels[(pixels.mean(axis=1) > 15) & (pixels.mean(axis=1) < 230)]
    
    # Get average color (simple approach)
    avg_color = [int(c) for c in np.mean(filtered, axis=0)]
    
    return [{
        "color": avg_color,
        "percentage": 100.0
    }]

# Process only problematic shades
shades_to_fix = {
    "Natural Black": "new_shade/Natural Black.jpg",
    "Dark Brown": "new_shade/Dark Brown.png",
    "Scandinavian Blonde": "new_shade/Scandinavian Blonde.jpg",
    "Champagne Blonde": "new_shade/Champagne Blonde.jpg"
}

print("Extracting correct RGB values...\n")

fixed_data = {}
for shade_name, img_path in shades_to_fix.items():
    colors = extract_pure_hair_color(img_path)
    if colors:
        fixed_data[shade_name] = colors
        rgb = colors[0]["color"]
        brightness = rgb[0] * 0.299 + rgb[1] * 0.587 + rgb[2] * 0.114
        print(f"{shade_name}: RGB{rgb} - Brightness: {brightness:.1f}")

# Load existing data
with open("app/shade/reference_shades_new.json", "r") as f:
    all_data = json.load(f)

# Update with fixed values
all_data.update(fixed_data)

# Save
with open("app/shade/reference_shades_new.json", "w") as f:
    json.dump(all_data, f, indent=2)

print(f"\nUpdated reference_shades_new.json with correct values!")