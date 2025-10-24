"""
Final Production Matcher
- Lab color space Delta E
- Tone-aware matching
- Lighting-independent
"""
import numpy as np
from colormath.color_objects import LabColor
from colormath.color_diff import delta_e_cie2000

def calculate_delta_e_lab(lab1, lab2):
    """Calculate Delta E 2000 in Lab space"""
    try:
        color1 = LabColor(lab1[0], lab1[1], lab1[2])
        color2 = LabColor(lab2[0], lab2[1], lab2[2])
        return delta_e_cie2000(color1, color2)
    except:
        return np.sqrt(sum((a - b) ** 2 for a, b in zip(lab1, lab2)))

def match_final(user_colors, shade_colors):
    """Final production matching - considers ALL colors"""
    
    # Sort by percentage
    user_sorted = sorted(user_colors, key=lambda x: x["percentage"], reverse=True)
    shade_sorted = sorted(shade_colors, key=lambda x: x["percentage"], reverse=True)
    
    # Calculate overall color profile match
    total_score = 0
    
    # Match each user color with best shade color
    for u_idx, user_color in enumerate(user_sorted):
        user_lab = user_color.get("lab", [50, 0, 0])
        user_tone = user_color["tone"]
        user_pct = user_color["percentage"]
        
        best_color_score = 0
        
        for s_idx, shade_color in enumerate(shade_sorted):
            shade_lab = shade_color.get("lab", [50, 0, 0])
            shade_tone = shade_color["tone"]
            shade_pct = shade_color["percentage"]
            
            # 1. Delta E (Lab space)
            delta_e = calculate_delta_e_lab(user_lab, shade_lab)
            
            if delta_e < 3:
                color_score = 100
            elif delta_e < 6:
                color_score = 90
            elif delta_e < 10:
                color_score = 80
            elif delta_e < 15:
                color_score = 65
            elif delta_e < 20:
                color_score = 45
            else:
                color_score = max(0, 25 - delta_e * 0.5)
            
            # 2. Tone match
            if user_tone == shade_tone:
                tone_score = 100
            elif (user_tone == "warm_orange" and shade_tone == "warm_brown") or \
                 (user_tone == "warm_brown" and shade_tone == "warm_orange"):
                tone_score = 40
            elif (user_tone == "warm_brown" and shade_tone == "golden") or \
                 (user_tone == "golden" and shade_tone == "warm_brown"):
                tone_score = 50
            else:
                tone_score = 20
            
            # Combined
            match_score = color_score * 0.75 + tone_score * 0.25
            
            # Weight by shade percentage
            weighted = match_score * (shade_pct / 100)
            
            if weighted > best_color_score:
                best_color_score = weighted
        
        # Weight by user percentage (all colors equally important)
        total_score += best_color_score * (user_pct / 100)
    
    return round(total_score, 2)

def find_final_match(user_colors, reference_shades):
    """Find best match"""
    scores = {}
    variant_scores = {}
    
    for shade_name, shade_colors in reference_shades.items():
        score = match_final(user_colors, shade_colors)
        scores[shade_name] = score
        
        # Track variants
        if "_" in shade_name:
            base = shade_name.split("_")[0]
            variant = shade_name.replace(base + "_", "")
            
            if base not in variant_scores:
                variant_scores[base] = {}
            variant_scores[base][variant] = score
        else:
            variant_scores[shade_name] = {"main": score}
    
    sorted_scores = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
    best_match = next(iter(sorted_scores)) if sorted_scores else None
    
    # Best variant
    best_variant = None
    if best_match and "_" in best_match:
        base = best_match.split("_")[0]
        if base in variant_scores:
            best_var = max(variant_scores[base], key=variant_scores[base].get)
            best_variant = f"{base}_{best_var}"
    
    return best_match, sorted_scores, best_variant, variant_scores
