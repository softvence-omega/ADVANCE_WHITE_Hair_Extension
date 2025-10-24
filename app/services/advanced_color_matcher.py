import numpy as np
import cv2
from colormath.color_objects import LabColor, sRGBColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

def rgb_to_lab_color(rgb):
    """Convert RGB to LAB color object"""
    r, g, b = [x / 255.0 for x in rgb]
    rgb_color = sRGBColor(r, g, b)
    return convert_color(rgb_color, LabColor)

def rgb_to_hsv(rgb):
    """Convert RGB to HSV for hue comparison"""
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

def calculate_delta_e(user_rgb, ref_rgb):
    """Calculate Delta E 2000 with hue penalty"""
    try:
        user_lab = rgb_to_lab_color(user_rgb)
        ref_lab = rgb_to_lab_color(ref_rgb)
        delta = delta_e_cie2000(user_lab, ref_lab)
        
        # Brightness penalty
        user_brightness = user_rgb[0] * 0.299 + user_rgb[1] * 0.587 + user_rgb[2] * 0.114
        ref_brightness = ref_rgb[0] * 0.299 + ref_rgb[1] * 0.587 + ref_rgb[2] * 0.114
        brightness_diff = abs(user_brightness - ref_brightness)
        
        if user_brightness < 60 and ref_brightness < 60:
            delta += brightness_diff * 0.4
        elif user_brightness < 80 and ref_brightness < 80:
            delta += brightness_diff * 0.35
        elif user_brightness < 80 or ref_brightness < 80:
            delta += brightness_diff * 1.0
        else:
            delta += brightness_diff * 0.15
        
        # Hue penalty
        user_h, user_s, user_v = rgb_to_hsv(user_rgb)
        ref_h, ref_s, ref_v = rgb_to_hsv(ref_rgb)
        
        if user_s > 0.15 and ref_s > 0.15:
            hue_diff = min(abs(user_h - ref_h), 360 - abs(user_h - ref_h))
            if hue_diff > 20:
                delta += hue_diff * 0.2
        
        return delta
    except:
        # Fallback to weighted Euclidean distance
        user_brightness = user_rgb[0] * 0.299 + user_rgb[1] * 0.587 + user_rgb[2] * 0.114
        ref_brightness = ref_rgb[0] * 0.299 + ref_rgb[1] * 0.587 + ref_rgb[2] * 0.114
        
        rgb_dist = np.sqrt(sum((a - b) ** 2 for a, b in zip(user_rgb, ref_rgb)))
        brightness_penalty = abs(user_brightness - ref_brightness) * 0.5
        
        return rgb_dist + brightness_penalty

def match_with_delta_e(user_colors, reference_colors):
    """Match using Delta E 2000"""
    
    best_delta_e = float("inf")
    
    # Compare all user colors with all reference colors
    for user_color in user_colors:
        user_rgb = user_color["color"]
        user_weight = user_color["percentage"] / 100
        
        for ref_color in reference_colors:
            ref_rgb = ref_color["color"]
            ref_weight = ref_color["percentage"] / 100
            
            delta_e = calculate_delta_e(user_rgb, ref_rgb)
            
            # Weight by percentage
            weighted_delta = delta_e * (2 - user_weight - ref_weight)
            
            if weighted_delta < best_delta_e:
                best_delta_e = weighted_delta
    
    # Convert Delta E to score - KEEP AS FLOAT for tie-breaking
    if best_delta_e < 2:
        score = 100.0
    elif best_delta_e < 5:
        score = 98.0
    elif best_delta_e < 8:
        score = 92.0
    elif best_delta_e < 12:
        score = 82.0
    elif best_delta_e < 18:
        score = 68.0
    elif best_delta_e < 25:
        score = 48.0
    elif best_delta_e < 35:
        score = 28.0
    else:
        score = max(0.0, 15.0 - (best_delta_e - 35.0) * 0.3)
    
    # Subtract small delta_e value to break ties
    score = score - (best_delta_e * 0.01)
    
    return score

def find_best_match_advanced(user_colors, reference_shades):
    """Find best match using advanced Delta E algorithm"""
    scores = {}
    
    # Calculate average brightness of user's hair
    avg_user_brightness = sum(
        (c["color"][0] * 0.299 + c["color"][1] * 0.587 + c["color"][2] * 0.114) * c["percentage"] / 100
        for c in user_colors
    )
    
    for shade_name, shade_colors in reference_shades.items():
        score = match_with_delta_e(user_colors, shade_colors)
        
        # Calculate shade brightness
        shade_brightness = sum(
            (c["color"][0] * 0.299 + c["color"][1] * 0.587 + c["color"][2] * 0.114) * c["percentage"] / 100
            for c in shade_colors
        )
        
        # Enhanced brightness similarity bonus
        brightness_diff = abs(avg_user_brightness - shade_brightness)
        if brightness_diff < 5:
            brightness_bonus = 8.0
        elif brightness_diff < 10:
            brightness_bonus = 5.0
        elif brightness_diff < 20:
            brightness_bonus = 2.0
        else:
            brightness_bonus = 0.0
        
        # Keep precision for tie-breaking
        scores[shade_name] = round(score + brightness_bonus, 3)
    
    # Sort by score with better tie-breaking
    def sort_key(item):
        shade_name, score = item
        shade_colors = reference_shades[shade_name]
        
        # Calculate hue variance (lower = more consistent color)
        hues = []
        for c in shade_colors:
            h, s, v = rgb_to_hsv(c["color"])
            if s > 0.15:  # Only consider saturated colors
                hues.append(h)
        
        hue_variance = np.std(hues) if len(hues) > 1 else 0
        
        # Primary sort: score (descending)
        # Secondary sort: hue variance (ascending - prefer consistent colors)
        return (-score, hue_variance)
    
    sorted_scores = dict(sorted(scores.items(), key=sort_key))
    best_match = next(iter(sorted_scores)) if sorted_scores else None
    
    return best_match, sorted_scores