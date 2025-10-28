import cv2
import numpy as np
import os
import json
import warnings
from sklearn.cluster import KMeans
from collections import defaultdict

warnings.filterwarnings('ignore')

def rgb_to_hsv_simple(rgb):
    r, g, b = [x / 255.0 for x in rgb]
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    diff = max_c - min_c
    if diff == 0:
        h = 0
    elif max_c == r:
        h = (60 * ((g - b) / diff) + 360) % 360
    elif max_c == g:
        h = (60 * ((b - r) / diff) + 120) % 360
    else:
        h = (60 * ((r - g) / diff) + 240) % 360
    s = 0 if max_c == 0 else (diff / max_c)
    v = max_c
    return h, s, v

def rgb_to_lab(rgb):
    from colormath.color_objects import LabColor, sRGBColor
    from colormath.color_conversions import convert_color
    r, g, b = [x / 255.0 for x in rgb]
    rgb_color = sRGBColor(r, g, b)
    lab_color = convert_color(rgb_color, LabColor)
    return [lab_color.lab_l, lab_color.lab_a, lab_color.lab_b]

def classify_tone(rgb, h, s):
    r, g, b = rgb
    if h < 30 and s > 0.3 and r > g + 15:
        return "warm_orange"
    elif 30 <= h < 60 and s > 0.2:
        return "warm_brown"
    elif h < 40 and s < 0.2:
        return "neutral_brown"
    elif 40 <= h < 80 and s > 0.2:
        return "golden"
    elif 180 <= h < 270:
        return "cool"
    else:
        return "neutral"

def get_dominant_colors_from_hair(hair_pixels, n_clusters=6, min_percentage=5):
    if len(hair_pixels) == 0:
        return []
    
    data = np.array(hair_pixels)
    unique_colors = np.unique(data, axis=0)
    actual_clusters = min(len(unique_colors), n_clusters)

    if actual_clusters == 0:
        return []

    kmeans = KMeans(n_clusters=actual_clusters, random_state=42, n_init="auto")
    labels = kmeans.fit_predict(data)
    centers = kmeans.cluster_centers_.astype(int)
    counts = np.bincount(labels)
    total = len(labels)

    dominant_colors = []
    for i in range(actual_clusters):
        percentage = (counts[i] / total) * 100
        if percentage >= min_percentage:
            color = [max(0, min(255, int(c))) for c in centers[i]]
            brightness_val = color[0] * 0.299 + color[1] * 0.587 + color[2] * 0.114
            h, s, v = rgb_to_hsv_simple(color)
            tone = classify_tone(color, h, s)
            lab = rgb_to_lab(color)
            
            dominant_colors.append({
                "color": color,
                "rgb": color,
                "lab": [round(x, 2) for x in lab],
                "percentage": round(percentage, 2),
                "brightness": round(brightness_val, 2),
                "hue": round(h, 2),
                "saturation": round(s, 3),
                "tone": tone
            })

    dominant_colors.sort(key=lambda x: x["percentage"], reverse=True)
    return dominant_colors

def process_image(img_path):
    from app.services.hair_color_detector import detect_shade_color
    
    # Use same method as user hair detection
    colors = detect_shade_color(img_path)
    return colors

# Process all images
shade_data = {}

for file in os.listdir("new_shade"):
    if file.endswith(('.jpg', '.png', '.jpeg')):
        # Extract shade name
        shade_name = file.rsplit('.', 1)[0]
        for suffix in ['_CloseUp', '_IndoorLight', '_light', '_NaturalLight']:
            shade_name = shade_name.replace(suffix, '')
        
        img_path = os.path.join("new_shade", file)
        colors = process_image(img_path)
        
        if colors:
            shade_data[file] = {
                "shade_name": shade_name,
                "dominant_colors": colors
            }
        
        print(f"Processed: {file}")

# Save
with open("app/shade/exact_shade_signatures.json", 'w') as f:
    json.dump(shade_data, f, indent=2)

print(f"\nTotal images processed: {len(shade_data)}")
