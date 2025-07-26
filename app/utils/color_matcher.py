import json
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
import numpy as np
from pathlib import Path

if not hasattr(np, "asscalar"):
    np.asscalar = lambda x: x.item()
    
def load_shades_rgb(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Shade data file not found at: {path}")
        
    with path.open("r") as f:
        return json.load(f)

def rgb_to_lab(rgb):
    
    rgb_scaled = [x / 255.0 for x in rgb]  # Normalize RGB to 0-1
    srgb = sRGBColor(*rgb_scaled)
    lab = convert_color(srgb, LabColor)
    return lab

def delta_e_cie(user_rgb, shade_rgb):
    lab1 = rgb_to_lab(user_rgb)
    lab2 = rgb_to_lab(shade_rgb)
    return delta_e_cie2000(lab1, lab2)

def match_shade_rgb(user_rgb, shade_data):
    min_delta = float("inf")
    best_match = None
    best_rgb = None

    for name, rgb in shade_data.items():
        delta = delta_e_cie(user_rgb, rgb)
        if delta < min_delta:
            min_delta = delta
            best_match = name
            best_rgb = rgb

    return best_match, best_rgb, min_delta
