import numpy as np
from colormath.color_objects import LabColor, sRGBColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

def rgb_to_hsv(rgb):
    """Convert RGB to HSV"""
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

def calculate_delta_e(rgb1, rgb2):
    """Calculate Delta E 2000"""
    try:
        r1, g1, b1 = [x / 255.0 for x in rgb1]
        r2, g2, b2 = [x / 255.0 for x in rgb2]
        
        lab1 = convert_color(sRGBColor(r1, g1, b1), LabColor)
        lab2 = convert_color(sRGBColor(r2, g2, b2), LabColor)
        
        return delta_e_cie2000(lab1, lab2)
    except:
        return np.sqrt(sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)))

def match_perfect(user_colors, shade_colors):
    """Perfect matching with tone, hue, brightness, saturation"""
    
    # Sort user colors by percentage (dominant first)
    user_colors_sorted = sorted(user_colors, key=lambda x: x["percentage"], reverse=True)
    
    total_score = 0
    
    for idx, user_color in enumerate(user_colors_sorted):
        user_rgb = user_color["color"]
        user_pct = user_color["percentage"]
        
        # Give more weight to dominant colors
        if idx == 0:  # Most dominant
            importance_weight = 1.5
        elif idx == 1:  # Second
            importance_weight = 1.0
        else:  # Third
            importance_weight = 0.5
        
        # Calculate user properties
        user_brightness = user_rgb[0] * 0.299 + user_rgb[1] * 0.587 + user_rgb[2] * 0.114
        user_h, user_s, user_v = rgb_to_hsv(user_rgb)
        
        # Detect user tone
        user_r, user_g, user_b = user_rgb
        if user_h < 30 and user_s > 0.3 and user_r > user_g + 15:
            user_tone = "warm_orange"  # Copper
        elif 30 <= user_h < 60 and user_s > 0.2:
            user_tone = "warm_brown"   # Autumn
        else:
            user_tone = "neutral"
        
        best_match_score = 0
        
        # Sort shade colors by percentage too
        shade_colors_sorted = sorted(shade_colors, key=lambda x: x.get("percentage", 100), reverse=True)
        
        for shade_idx, shade_color in enumerate(shade_colors_sorted):
            shade_rgb = shade_color["color"]
            shade_brightness = shade_color.get("brightness", shade_rgb[0] * 0.299 + shade_rgb[1] * 0.587 + shade_rgb[2] * 0.114)
            shade_h = shade_color.get("hue", rgb_to_hsv(shade_rgb)[0])
            shade_s = shade_color.get("saturation", rgb_to_hsv(shade_rgb)[1])
            shade_tone = shade_color.get("tone", "unknown")
            shade_pct = shade_color.get("percentage", 100)
            
            # 1. Delta E score
            delta_e = calculate_delta_e(user_rgb, shade_rgb)
            if delta_e < 5:
                color_score = 100
            elif delta_e < 10:
                color_score = 90
            elif delta_e < 15:
                color_score = 75
            elif delta_e < 25:
                color_score = 50
            else:
                color_score = max(0, 30 - delta_e)
            
            # 2. Brightness match
            brightness_diff = abs(user_brightness - shade_brightness)
            if brightness_diff < 10:
                brightness_score = 100
            elif brightness_diff < 20:
                brightness_score = 80
            elif brightness_diff < 40:
                brightness_score = 50
            else:
                brightness_score = 0
            
            # 3. Hue match (CRITICAL for Copper vs Autumn)
            hue_diff = min(abs(user_h - shade_h), 360 - abs(user_h - shade_h))
            if hue_diff < 5:
                hue_score = 100
            elif hue_diff < 10:
                hue_score = 90
            elif hue_diff < 15:
                hue_score = 70
            elif hue_diff < 25:
                hue_score = 40
            else:
                hue_score = 0
            
            # 4. Saturation match
            sat_diff = abs(user_s - shade_s)
            if sat_diff < 0.08:
                sat_score = 100
            elif sat_diff < 0.15:
                sat_score = 85
            elif sat_diff < 0.25:
                sat_score = 60
            else:
                sat_score = 30
            
            # 5. Tone match (CRITICAL)
            if user_tone == shade_tone:
                tone_score = 100
            elif user_tone == "warm_orange" and shade_tone == "warm_brown":
                tone_score = 20  # Heavy penalty
            elif user_tone == "warm_brown" and shade_tone == "warm_orange":
                tone_score = 20  # Heavy penalty
            else:
                tone_score = 50
            
            # Combined score with adjusted weights
            match_score = (
                color_score * 0.20 +      # Delta E - 20%
                hue_score * 0.25 +        # Hue - 25%
                brightness_score * 0.30 + # Brightness - 30% (INCREASED)
                sat_score * 0.10 +        # Saturation - 10%
                tone_score * 0.15         # Tone - 15%
            )
            
            # Give more weight to matching dominant colors
            if idx == 0 and shade_idx == 0:  # Both dominant colors
                dominance_bonus = 1.3
            elif idx == 0 or shade_idx == 0:  # One dominant
                dominance_bonus = 1.1
            else:
                dominance_bonus = 1.0
            
            # Weight by shade color percentage and dominance
            weighted_score = match_score * (shade_pct / 100) * dominance_bonus
            
            if weighted_score > best_match_score:
                best_match_score = weighted_score
        
        # Weight by user color percentage AND importance
        total_score += best_match_score * (user_pct / 100) * importance_weight
    
    return round(total_score, 2)

def find_perfect_match(user_colors, reference_shades):
    """Find best matching shade with variant details"""
    scores = {}
    variant_scores = {}  # Track individual variants
    
    for shade_name, shade_colors in reference_shades.items():
        score = match_perfect(user_colors, shade_colors)
        scores[shade_name] = score
        
        # Extract base name and variant
        if "_" in shade_name:
            base_name = shade_name.split("_")[0]
            variant = shade_name.replace(base_name + "_", "")
            
            if base_name not in variant_scores:
                variant_scores[base_name] = {}
            variant_scores[base_name][variant] = score
        else:
            variant_scores[shade_name] = {"merged": score}
    
    sorted_scores = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
    best_match = next(iter(sorted_scores)) if sorted_scores else None
    
    # Find best variant for top match
    best_variant = None
    if best_match and "_" in best_match:
        base = best_match.split("_")[0]
        if base in variant_scores:
            best_variant_name = max(variant_scores[base], key=variant_scores[base].get)
            best_variant = f"{base}_{best_variant_name}"
    
    return best_match, sorted_scores, best_variant, variant_scores
